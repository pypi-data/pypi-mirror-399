"""
Context Window Manager - Core Implementation

Production-ready LLM context window optimization and management.
"""

import hashlib
import re
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union, Callable, Iterator
from datetime import datetime
from collections import deque

from .types import (
    MessageRole,
    PruningStrategy,
    CompressionMethod,
    TokenizerType,
    ContentType,
    Priority,
    TokenCount,
    Message,
    Conversation,
    ContextBudget,
    PruningResult,
    CompressionResult,
    ContextSnapshot,
    WindowConfig,
    ModelConfig,
    UsageStats,
)


class Tokenizer(ABC):
    """Abstract tokenizer interface."""
    
    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        pass
    
    @abstractmethod
    def encode(self, text: str) -> List[int]:
        """Encode text to tokens."""
        pass
    
    @abstractmethod
    def decode(self, tokens: List[int]) -> str:
        """Decode tokens to text."""
        pass


class ApproximateTokenizer(Tokenizer):
    """Approximate tokenizer using character ratio."""
    
    def __init__(self, chars_per_token: float = 4.0):
        self.chars_per_token = chars_per_token
    
    def count_tokens(self, text: str) -> int:
        """Approximate token count."""
        return max(1, int(len(text) / self.chars_per_token))
    
    def encode(self, text: str) -> List[int]:
        """Pseudo-encode (returns character codes)."""
        return [ord(c) for c in text]
    
    def decode(self, tokens: List[int]) -> str:
        """Pseudo-decode."""
        return "".join(chr(t) for t in tokens if 0 <= t < 0x110000)


class TiktokenTokenizer(Tokenizer):
    """Tiktoken-based tokenizer."""
    
    def __init__(self, encoding_name: str = "cl100k_base"):
        self.encoding_name = encoding_name
        self._encoding = None
    
    @property
    def encoding(self):
        """Lazy load tiktoken encoding."""
        if self._encoding is None:
            try:
                import tiktoken
                self._encoding = tiktoken.get_encoding(self.encoding_name)
            except ImportError:
                # Fallback to approximate
                return None
        return self._encoding
    
    def count_tokens(self, text: str) -> int:
        """Count tokens using tiktoken."""
        if self.encoding:
            return len(self.encoding.encode(text))
        # Fallback approximation
        return max(1, int(len(text) / 4))
    
    def encode(self, text: str) -> List[int]:
        """Encode text to tokens."""
        if self.encoding:
            return self.encoding.encode(text)
        return [ord(c) for c in text]
    
    def decode(self, tokens: List[int]) -> str:
        """Decode tokens to text."""
        if self.encoding:
            return self.encoding.decode(tokens)
        return "".join(chr(t) for t in tokens if 0 <= t < 0x110000)


def get_tokenizer(tokenizer_type: TokenizerType) -> Tokenizer:
    """Factory function to get appropriate tokenizer."""
    if tokenizer_type == TokenizerType.APPROXIMATE:
        return ApproximateTokenizer()
    else:
        return TiktokenTokenizer(tokenizer_type.value)


class MessageTokenCounter:
    """Count tokens in messages with overhead."""
    
    # Approximate overhead per message (role, formatting)
    MESSAGE_OVERHEAD = 4
    
    def __init__(self, tokenizer: Tokenizer):
        self.tokenizer = tokenizer
    
    def count_message(self, message: Message) -> TokenCount:
        """Count tokens in a message."""
        text_tokens = self.tokenizer.count_tokens(message.content)
        
        # Add name tokens if present
        if message.name:
            text_tokens += self.tokenizer.count_tokens(message.name)
        
        # Add tool call tokens if present
        special_tokens = 0
        if message.tool_calls:
            for tool_call in message.tool_calls:
                special_tokens += self.tokenizer.count_tokens(
                    str(tool_call)
                )
        
        overhead = self.MESSAGE_OVERHEAD
        total = text_tokens + special_tokens + overhead
        
        return TokenCount(
            total=total,
            text_tokens=text_tokens,
            special_tokens=special_tokens,
            overhead_tokens=overhead
        )
    
    def count_messages(self, messages: List[Message]) -> TokenCount:
        """Count tokens in multiple messages."""
        total = TokenCount(total=0)
        for msg in messages:
            total = total + self.count_message(msg)
        return total


class PruningEngine:
    """Engine for pruning context."""
    
    def __init__(
        self,
        tokenizer: Tokenizer,
        config: WindowConfig
    ):
        self.tokenizer = tokenizer
        self.config = config
        self.counter = MessageTokenCounter(tokenizer)
    
    def prune(
        self,
        messages: List[Message],
        target_tokens: int,
        strategy: Optional[PruningStrategy] = None
    ) -> Tuple[List[Message], PruningResult]:
        """
        Prune messages to fit within token budget.
        
        Args:
            messages: Messages to prune
            target_tokens: Target token count
            strategy: Pruning strategy (uses config default if not specified)
            
        Returns:
            Tuple of (pruned messages, pruning result)
        """
        strategy = strategy or self.config.pruning_strategy
        
        # Calculate current tokens
        current_tokens = self.counter.count_messages(messages).total
        
        if current_tokens <= target_tokens:
            return messages, PruningResult(
                original_messages=len(messages),
                pruned_messages=len(messages),
                removed_messages=0,
                original_tokens=current_tokens,
                final_tokens=current_tokens,
                tokens_saved=0,
                strategy_used=strategy
            )
        
        # Apply strategy
        if strategy == PruningStrategy.FIFO:
            return self._prune_fifo(messages, target_tokens, current_tokens)
        elif strategy == PruningStrategy.LIFO:
            return self._prune_lifo(messages, target_tokens, current_tokens)
        elif strategy == PruningStrategy.SLIDING_WINDOW:
            return self._prune_sliding_window(messages, target_tokens, current_tokens)
        elif strategy == PruningStrategy.RELEVANCE:
            return self._prune_by_relevance(messages, target_tokens, current_tokens)
        elif strategy == PruningStrategy.IMPORTANCE:
            return self._prune_by_importance(messages, target_tokens, current_tokens)
        elif strategy == PruningStrategy.RECENCY_WEIGHTED:
            return self._prune_recency_weighted(messages, target_tokens, current_tokens)
        else:
            # Default to FIFO
            return self._prune_fifo(messages, target_tokens, current_tokens)
    
    def _prune_fifo(
        self,
        messages: List[Message],
        target_tokens: int,
        current_tokens: int
    ) -> Tuple[List[Message], PruningResult]:
        """Remove oldest messages first."""
        result_messages = list(messages)
        removed_indices = []
        
        idx = 0
        while current_tokens > target_tokens and idx < len(result_messages):
            msg = result_messages[idx]
            
            # Skip pinned messages
            if msg.is_pinned:
                idx += 1
                continue
            
            # Skip critical priority
            if msg.priority == Priority.CRITICAL:
                idx += 1
                continue
            
            # Remove message
            msg_tokens = self.counter.count_message(msg).total
            current_tokens -= msg_tokens
            removed_indices.append(idx)
            result_messages.pop(idx)
        
        final_tokens = self.counter.count_messages(result_messages).total
        
        return result_messages, PruningResult(
            original_messages=len(messages),
            pruned_messages=len(result_messages),
            removed_messages=len(removed_indices),
            original_tokens=self.counter.count_messages(messages).total,
            final_tokens=final_tokens,
            tokens_saved=self.counter.count_messages(messages).total - final_tokens,
            strategy_used=PruningStrategy.FIFO,
            removed_indices=removed_indices
        )
    
    def _prune_lifo(
        self,
        messages: List[Message],
        target_tokens: int,
        current_tokens: int
    ) -> Tuple[List[Message], PruningResult]:
        """Remove newest messages first (except most recent turn)."""
        result_messages = list(messages)
        removed_indices = []
        
        # Keep at least the most recent messages
        keep_recent = self.config.preserve_recent_turns * 2  # User + assistant
        
        idx = len(result_messages) - keep_recent - 1
        while current_tokens > target_tokens and idx >= 0:
            msg = result_messages[idx]
            
            if msg.is_pinned or msg.priority == Priority.CRITICAL:
                idx -= 1
                continue
            
            msg_tokens = self.counter.count_message(msg).total
            current_tokens -= msg_tokens
            removed_indices.append(idx)
            result_messages.pop(idx)
            idx -= 1
        
        final_tokens = self.counter.count_messages(result_messages).total
        
        return result_messages, PruningResult(
            original_messages=len(messages),
            pruned_messages=len(result_messages),
            removed_messages=len(removed_indices),
            original_tokens=self.counter.count_messages(messages).total,
            final_tokens=final_tokens,
            tokens_saved=self.counter.count_messages(messages).total - final_tokens,
            strategy_used=PruningStrategy.LIFO,
            removed_indices=removed_indices
        )
    
    def _prune_sliding_window(
        self,
        messages: List[Message],
        target_tokens: int,
        current_tokens: int
    ) -> Tuple[List[Message], PruningResult]:
        """Keep only the most recent N messages that fit."""
        original_tokens = current_tokens
        result_messages = []
        
        # Start from most recent
        for msg in reversed(messages):
            msg_tokens = self.counter.count_message(msg).total
            
            if current_tokens - msg_tokens <= target_tokens or msg.is_pinned:
                result_messages.insert(0, msg)
            else:
                current_tokens -= msg_tokens
        
        # Ensure minimum messages
        while len(result_messages) < self.config.min_messages_to_keep and messages:
            # Add back oldest non-included messages
            for msg in messages:
                if msg not in result_messages:
                    result_messages.insert(0, msg)
                    break
            else:
                break
        
        final_tokens = self.counter.count_messages(result_messages).total
        removed = len(messages) - len(result_messages)
        
        return result_messages, PruningResult(
            original_messages=len(messages),
            pruned_messages=len(result_messages),
            removed_messages=removed,
            original_tokens=original_tokens,
            final_tokens=final_tokens,
            tokens_saved=original_tokens - final_tokens,
            strategy_used=PruningStrategy.SLIDING_WINDOW
        )
    
    def _prune_by_relevance(
        self,
        messages: List[Message],
        target_tokens: int,
        current_tokens: int
    ) -> Tuple[List[Message], PruningResult]:
        """Remove least relevant messages first."""
        # Sort by relevance (ascending, so least relevant first)
        scored_messages = [
            (i, msg, msg.relevance_score)
            for i, msg in enumerate(messages)
        ]
        scored_messages.sort(key=lambda x: x[2])
        
        removed_indices = []
        remaining_tokens = current_tokens
        
        for idx, msg, score in scored_messages:
            if remaining_tokens <= target_tokens:
                break
            
            if msg.is_pinned or msg.priority == Priority.CRITICAL:
                continue
            
            msg_tokens = self.counter.count_message(msg).total
            remaining_tokens -= msg_tokens
            removed_indices.append(idx)
        
        result_messages = [
            msg for i, msg in enumerate(messages)
            if i not in removed_indices
        ]
        
        final_tokens = self.counter.count_messages(result_messages).total
        
        return result_messages, PruningResult(
            original_messages=len(messages),
            pruned_messages=len(result_messages),
            removed_messages=len(removed_indices),
            original_tokens=current_tokens,
            final_tokens=final_tokens,
            tokens_saved=current_tokens - final_tokens,
            strategy_used=PruningStrategy.RELEVANCE,
            removed_indices=sorted(removed_indices)
        )
    
    def _prune_by_importance(
        self,
        messages: List[Message],
        target_tokens: int,
        current_tokens: int
    ) -> Tuple[List[Message], PruningResult]:
        """Remove least important messages first."""
        # Sort by importance (ascending)
        scored_messages = [
            (i, msg, msg.importance_score)
            for i, msg in enumerate(messages)
        ]
        scored_messages.sort(key=lambda x: x[2])
        
        removed_indices = []
        remaining_tokens = current_tokens
        
        for idx, msg, score in scored_messages:
            if remaining_tokens <= target_tokens:
                break
            
            if msg.is_pinned or msg.priority == Priority.CRITICAL:
                continue
            
            msg_tokens = self.counter.count_message(msg).total
            remaining_tokens -= msg_tokens
            removed_indices.append(idx)
        
        result_messages = [
            msg for i, msg in enumerate(messages)
            if i not in removed_indices
        ]
        
        final_tokens = self.counter.count_messages(result_messages).total
        
        return result_messages, PruningResult(
            original_messages=len(messages),
            pruned_messages=len(result_messages),
            removed_messages=len(removed_indices),
            original_tokens=current_tokens,
            final_tokens=final_tokens,
            tokens_saved=current_tokens - final_tokens,
            strategy_used=PruningStrategy.IMPORTANCE,
            removed_indices=sorted(removed_indices)
        )
    
    def _prune_recency_weighted(
        self,
        messages: List[Message],
        target_tokens: int,
        current_tokens: int
    ) -> Tuple[List[Message], PruningResult]:
        """Combine recency and relevance for pruning."""
        n = len(messages)
        
        # Calculate combined scores
        scored_messages = []
        for i, msg in enumerate(messages):
            # Recency score (0-1, higher for more recent)
            recency = i / n if n > 0 else 0
            
            # Combined score
            combined = 0.5 * recency + 0.3 * msg.relevance_score + 0.2 * msg.importance_score
            scored_messages.append((i, msg, combined))
        
        # Sort by combined score (ascending, remove lowest first)
        scored_messages.sort(key=lambda x: x[2])
        
        removed_indices = []
        remaining_tokens = current_tokens
        
        # Keep recent turns
        protected_indices = set(range(n - self.config.preserve_recent_turns * 2, n))
        
        for idx, msg, score in scored_messages:
            if remaining_tokens <= target_tokens:
                break
            
            if msg.is_pinned or msg.priority == Priority.CRITICAL:
                continue
            
            if idx in protected_indices:
                continue
            
            msg_tokens = self.counter.count_message(msg).total
            remaining_tokens -= msg_tokens
            removed_indices.append(idx)
        
        result_messages = [
            msg for i, msg in enumerate(messages)
            if i not in removed_indices
        ]
        
        final_tokens = self.counter.count_messages(result_messages).total
        
        return result_messages, PruningResult(
            original_messages=len(messages),
            pruned_messages=len(result_messages),
            removed_messages=len(removed_indices),
            original_tokens=current_tokens,
            final_tokens=final_tokens,
            tokens_saved=current_tokens - final_tokens,
            strategy_used=PruningStrategy.RECENCY_WEIGHTED,
            removed_indices=sorted(removed_indices)
        )


class CompressionEngine:
    """Engine for compressing content."""
    
    def __init__(self, tokenizer: Tokenizer):
        self.tokenizer = tokenizer
    
    def compress(
        self,
        content: str,
        target_tokens: int,
        method: CompressionMethod = CompressionMethod.TRUNCATE
    ) -> CompressionResult:
        """
        Compress content to fit within token budget.
        
        Args:
            content: Content to compress
            target_tokens: Target token count
            method: Compression method
            
        Returns:
            CompressionResult
        """
        original_tokens = self.tokenizer.count_tokens(content)
        
        if original_tokens <= target_tokens:
            return CompressionResult(
                original_content=content,
                compressed_content=content,
                original_tokens=original_tokens,
                compressed_tokens=original_tokens,
                compression_ratio=1.0,
                method_used=method,
                information_preserved=1.0
            )
        
        if method == CompressionMethod.TRUNCATE:
            return self._truncate(content, target_tokens, original_tokens)
        elif method == CompressionMethod.BULLET_POINTS:
            return self._to_bullet_points(content, target_tokens, original_tokens)
        elif method == CompressionMethod.EXTRACT_KEY_INFO:
            return self._extract_key_info(content, target_tokens, original_tokens)
        else:
            return self._truncate(content, target_tokens, original_tokens)
    
    def _truncate(
        self,
        content: str,
        target_tokens: int,
        original_tokens: int
    ) -> CompressionResult:
        """Truncate content to target length."""
        # Approximate character position
        ratio = target_tokens / original_tokens
        target_chars = int(len(content) * ratio * 0.95)  # Safety margin
        
        truncated = content[:target_chars]
        
        # Find last complete sentence
        last_period = truncated.rfind('.')
        last_newline = truncated.rfind('\n')
        cut_point = max(last_period, last_newline)
        
        if cut_point > target_chars * 0.5:
            truncated = truncated[:cut_point + 1]
        
        truncated += "\n[...truncated...]"
        
        compressed_tokens = self.tokenizer.count_tokens(truncated)
        
        return CompressionResult(
            original_content=content,
            compressed_content=truncated,
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            compression_ratio=compressed_tokens / original_tokens,
            method_used=CompressionMethod.TRUNCATE,
            information_preserved=ratio
        )
    
    def _to_bullet_points(
        self,
        content: str,
        target_tokens: int,
        original_tokens: int
    ) -> CompressionResult:
        """Convert content to bullet points."""
        # Split into sentences
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Take key sentences as bullet points
        bullets = []
        current_tokens = 0
        
        for sentence in sentences:
            bullet = f"• {sentence}"
            bullet_tokens = self.tokenizer.count_tokens(bullet)
            
            if current_tokens + bullet_tokens <= target_tokens:
                bullets.append(bullet)
                current_tokens += bullet_tokens
            else:
                break
        
        compressed = "\n".join(bullets)
        compressed_tokens = self.tokenizer.count_tokens(compressed)
        
        return CompressionResult(
            original_content=content,
            compressed_content=compressed,
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            compression_ratio=compressed_tokens / original_tokens,
            method_used=CompressionMethod.BULLET_POINTS,
            information_preserved=len(bullets) / len(sentences) if sentences else 0
        )
    
    def _extract_key_info(
        self,
        content: str,
        target_tokens: int,
        original_tokens: int
    ) -> CompressionResult:
        """Extract key information from content."""
        # Simple extraction: first and last paragraphs + key sentences
        paragraphs = content.split('\n\n')
        
        if len(paragraphs) <= 2:
            return self._truncate(content, target_tokens, original_tokens)
        
        # Keep first and last paragraphs
        key_parts = [paragraphs[0]]
        
        # Add middle summary
        middle = paragraphs[1:-1]
        if middle:
            key_parts.append(f"[{len(middle)} paragraphs summarized]")
        
        key_parts.append(paragraphs[-1])
        
        compressed = "\n\n".join(key_parts)
        compressed_tokens = self.tokenizer.count_tokens(compressed)
        
        # Truncate if still too long
        if compressed_tokens > target_tokens:
            return self._truncate(compressed, target_tokens, compressed_tokens)
        
        return CompressionResult(
            original_content=content,
            compressed_content=compressed,
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            compression_ratio=compressed_tokens / original_tokens,
            method_used=CompressionMethod.EXTRACT_KEY_INFO,
            information_preserved=0.6  # Approximate
        )


class ContextWindowManager:
    """
    Main context window manager.
    
    Manages conversation context with automatic pruning and compression
    to stay within token limits.
    """
    
    def __init__(
        self,
        config: Optional[WindowConfig] = None,
        model_config: Optional[ModelConfig] = None
    ):
        """
        Initialize context window manager.
        
        Args:
            config: Window configuration
            model_config: Model-specific configuration
        """
        self.config = config or WindowConfig()
        self.model_config = model_config
        
        # Apply model config if provided
        if model_config:
            self.config.max_tokens = model_config.max_context_tokens
            self.config.reserved_output_tokens = min(
                model_config.max_output_tokens,
                self.config.reserved_output_tokens
            )
            self.config.tokenizer_type = model_config.tokenizer
        
        # Initialize components
        self.tokenizer = get_tokenizer(self.config.tokenizer_type)
        self.counter = MessageTokenCounter(self.tokenizer)
        self.pruning_engine = PruningEngine(self.tokenizer, self.config)
        self.compression_engine = CompressionEngine(self.tokenizer)
        
        # State
        self.conversation = Conversation(max_tokens=self.config.max_tokens)
        self.stats = UsageStats()
        self._snapshots: List[ContextSnapshot] = []
    
    def add_message(
        self,
        role: Union[MessageRole, str],
        content: str,
        **kwargs
    ) -> Message:
        """
        Add a message to the conversation.
        
        Args:
            role: Message role
            content: Message content
            **kwargs: Additional message attributes
            
        Returns:
            Added message
        """
        if isinstance(role, str):
            role = MessageRole(role)
        
        message = Message(
            role=role,
            content=content,
            timestamp=datetime.now(),
            **kwargs
        )
        
        # Count tokens
        message.token_count = self.counter.count_message(message)
        
        # Handle system message
        if role == MessageRole.SYSTEM:
            self.conversation.system_message = message
        else:
            self.conversation.messages.append(message)
        
        # Update total tokens
        self._update_token_count()
        
        # Check if pruning needed
        self._maybe_prune()
        
        return message
    
    def add_messages(self, messages: List[Dict[str, Any]]) -> List[Message]:
        """Add multiple messages."""
        result = []
        for msg_dict in messages:
            role = msg_dict.get("role", "user")
            content = msg_dict.get("content", "")
            msg = self.add_message(role, content)
            result.append(msg)
        return result
    
    def set_system_message(self, content: str, **kwargs) -> Message:
        """Set or update system message."""
        return self.add_message(MessageRole.SYSTEM, content, **kwargs)
    
    def get_messages(self) -> List[Dict[str, Any]]:
        """Get messages in API-compatible format."""
        return self.conversation.to_messages()
    
    def get_budget(self) -> ContextBudget:
        """Get current context budget."""
        system_tokens = 0
        if self.conversation.system_message:
            tc = self.counter.count_message(self.conversation.system_message)
            system_tokens = tc.total
        
        history_tokens = self.counter.count_messages(
            self.conversation.messages
        ).total
        
        return ContextBudget(
            total_tokens=self.config.max_tokens,
            system_tokens=system_tokens,
            history_tokens=history_tokens,
            reserved_output_tokens=self.config.reserved_output_tokens
        )
    
    def get_snapshot(self) -> ContextSnapshot:
        """Get current context snapshot."""
        budget = self.get_budget()
        
        return ContextSnapshot(
            timestamp=datetime.now(),
            total_tokens=self.conversation.total_tokens,
            message_count=self.conversation.message_count,
            system_tokens=budget.system_tokens,
            history_tokens=budget.history_tokens,
            utilization=self.conversation.utilization,
            budget=budget
        )
    
    def prune(
        self,
        target_tokens: Optional[int] = None,
        strategy: Optional[PruningStrategy] = None
    ) -> PruningResult:
        """
        Manually trigger pruning.
        
        Args:
            target_tokens: Target token count
            strategy: Pruning strategy
            
        Returns:
            PruningResult
        """
        if target_tokens is None:
            budget = self.get_budget()
            target_tokens = budget.available_for_history
        
        pruned_messages, result = self.pruning_engine.prune(
            self.conversation.messages,
            target_tokens,
            strategy
        )
        
        self.conversation.messages = pruned_messages
        self._update_token_count()
        
        # Record stats
        self.stats.record_operation(
            result.original_tokens,
            result.tokens_saved,
            self.conversation.utilization,
            was_prune=True
        )
        
        # Callback
        if self.config.on_prune:
            self.config.on_prune(result)
        
        return result
    
    def compress_message(
        self,
        message_index: int,
        target_tokens: Optional[int] = None,
        method: Optional[CompressionMethod] = None
    ) -> CompressionResult:
        """
        Compress a specific message.
        
        Args:
            message_index: Index of message to compress
            target_tokens: Target token count for message
            method: Compression method
            
        Returns:
            CompressionResult
        """
        if message_index < 0 or message_index >= len(self.conversation.messages):
            raise IndexError(f"Invalid message index: {message_index}")
        
        message = self.conversation.messages[message_index]
        method = method or self.config.compression_method
        
        if target_tokens is None:
            # Compress to half current size
            current = self.counter.count_message(message).total
            target_tokens = current // 2
        
        result = self.compression_engine.compress(
            message.content,
            target_tokens,
            method
        )
        
        # Update message
        message.original_content = message.content
        message.content = result.compressed_content
        message.is_summarized = True
        message.token_count = self.counter.count_message(message)
        
        self._update_token_count()
        
        # Record stats
        self.stats.record_operation(
            result.original_tokens,
            result.original_tokens - result.compressed_tokens,
            self.conversation.utilization,
            was_prune=False
        )
        
        # Callback
        if self.config.on_compress:
            self.config.on_compress(result)
        
        return result
    
    def pin_message(self, message_index: int) -> None:
        """Pin a message to prevent pruning."""
        if 0 <= message_index < len(self.conversation.messages):
            self.conversation.messages[message_index].is_pinned = True
    
    def unpin_message(self, message_index: int) -> None:
        """Unpin a message."""
        if 0 <= message_index < len(self.conversation.messages):
            self.conversation.messages[message_index].is_pinned = False
    
    def set_priority(self, message_index: int, priority: Priority) -> None:
        """Set message priority."""
        if 0 <= message_index < len(self.conversation.messages):
            self.conversation.messages[message_index].priority = priority
    
    def clear(self, keep_system: bool = True) -> None:
        """Clear conversation history."""
        if not keep_system:
            self.conversation.system_message = None
        self.conversation.messages.clear()
        self._update_token_count()
    
    def fits(self, content: str) -> bool:
        """Check if content fits in remaining budget."""
        tokens = self.tokenizer.count_tokens(content)
        return tokens <= self.conversation.available_tokens
    
    def tokens_for(self, content: str) -> int:
        """Get token count for content."""
        return self.tokenizer.count_tokens(content)
    
    def _update_token_count(self) -> None:
        """Update total token count."""
        total = 0
        
        if self.conversation.system_message:
            tc = self.counter.count_message(self.conversation.system_message)
            total += tc.total
        
        total += self.counter.count_messages(self.conversation.messages).total
        
        self.conversation.total_tokens = total
    
    def _maybe_prune(self) -> None:
        """Automatically prune if over threshold."""
        utilization = self.conversation.utilization
        
        if utilization >= self.config.pruning_threshold:
            budget = self.get_budget()
            self.prune(budget.available_for_history)
            self.stats.overflow_prevented += 1


class ConversationBuffer:
    """
    Ring buffer for conversation history with automatic management.
    
    Provides a simple interface for managing conversation with
    automatic context window management.
    """
    
    def __init__(
        self,
        max_tokens: int = 128000,
        max_messages: Optional[int] = None,
        **kwargs
    ):
        """
        Initialize conversation buffer.
        
        Args:
            max_tokens: Maximum token budget
            max_messages: Optional maximum number of messages
            **kwargs: Additional WindowConfig options
        """
        self.max_messages = max_messages
        self.config = WindowConfig(max_tokens=max_tokens, **kwargs)
        self.manager = ContextWindowManager(self.config)
    
    def add(self, role: str, content: str) -> None:
        """Add a message to the buffer."""
        self.manager.add_message(role, content)
        
        # Check message count limit
        if self.max_messages and len(self.manager.conversation.messages) > self.max_messages:
            excess = len(self.manager.conversation.messages) - self.max_messages
            self.manager.conversation.messages = self.manager.conversation.messages[excess:]
    
    def get_messages(self) -> List[Dict[str, Any]]:
        """Get all messages."""
        return self.manager.get_messages()
    
    def clear(self) -> None:
        """Clear the buffer."""
        self.manager.clear()
    
    @property
    def token_count(self) -> int:
        """Current token count."""
        return self.manager.conversation.total_tokens
    
    @property
    def message_count(self) -> int:
        """Current message count."""
        return self.manager.conversation.message_count


def create_manager(
    model: str = "gpt-4",
    **kwargs
) -> ContextWindowManager:
    """
    Factory function to create a context manager for a specific model.
    
    Args:
        model: Model name
        **kwargs: Additional configuration
        
    Returns:
        Configured ContextWindowManager
    """
    model_configs = {
        "gpt-4": ModelConfig.gpt4(),
        "gpt-4o": ModelConfig.gpt4o(),
        "gpt-3.5-turbo": ModelConfig.gpt35_turbo(),
        "claude-3": ModelConfig.claude3(),
    }
    
    model_config = model_configs.get(model)
    config = WindowConfig(**kwargs)
    
    return ContextWindowManager(config=config, model_config=model_config)
