"""
Context Window Manager - Type Definitions

Comprehensive type definitions for LLM context window optimization.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union, Callable
from enum import Enum
from datetime import datetime


class MessageRole(Enum):
    """Message roles in conversation."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"
    FUNCTION = "function"


class PruningStrategy(Enum):
    """Strategies for pruning context."""
    FIFO = "fifo"                    # First in, first out
    LIFO = "lifo"                    # Last in, first out
    RELEVANCE = "relevance"          # By relevance score
    RECENCY_WEIGHTED = "recency_weighted"  # Recency + relevance
    IMPORTANCE = "importance"         # By importance score
    SUMMARIZE = "summarize"          # Summarize old messages
    SLIDING_WINDOW = "sliding_window"  # Keep last N messages
    SEMANTIC_DEDUP = "semantic_dedup"  # Remove semantic duplicates
    HYBRID = "hybrid"                # Combination of strategies


class CompressionMethod(Enum):
    """Methods for compressing content."""
    NONE = "none"
    SUMMARIZE = "summarize"
    TRUNCATE = "truncate"
    EXTRACT_KEY_INFO = "extract_key_info"
    SEMANTIC_COMPRESS = "semantic_compress"
    BULLET_POINTS = "bullet_points"


class TokenizerType(Enum):
    """Supported tokenizer types."""
    TIKTOKEN_CL100K = "cl100k_base"      # GPT-4, GPT-3.5-turbo
    TIKTOKEN_P50K = "p50k_base"          # Codex
    TIKTOKEN_R50K = "r50k_base"          # GPT-3
    TIKTOKEN_O200K = "o200k_base"        # GPT-4o
    APPROXIMATE = "approximate"           # ~4 chars per token
    CUSTOM = "custom"


class ContentType(Enum):
    """Types of content in messages."""
    TEXT = "text"
    CODE = "code"
    JSON = "json"
    MARKDOWN = "markdown"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    IMAGE_URL = "image_url"
    FILE_CONTENT = "file_content"


class Priority(Enum):
    """Priority levels for content retention."""
    CRITICAL = 5    # Never remove
    HIGH = 4        # Remove only if necessary
    MEDIUM = 3      # Default priority
    LOW = 2         # Remove early
    EPHEMERAL = 1   # Remove first


@dataclass
class TokenCount:
    """Token count breakdown."""
    total: int
    text_tokens: int = 0
    special_tokens: int = 0
    image_tokens: int = 0
    overhead_tokens: int = 0  # Message formatting overhead
    
    @property
    def content_tokens(self) -> int:
        return self.text_tokens + self.image_tokens
    
    def __add__(self, other: "TokenCount") -> "TokenCount":
        return TokenCount(
            total=self.total + other.total,
            text_tokens=self.text_tokens + other.text_tokens,
            special_tokens=self.special_tokens + other.special_tokens,
            image_tokens=self.image_tokens + other.image_tokens,
            overhead_tokens=self.overhead_tokens + other.overhead_tokens
        )


@dataclass
class Message:
    """Single message in conversation."""
    role: MessageRole
    content: str
    name: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None
    
    # Metadata
    id: Optional[str] = None
    timestamp: Optional[datetime] = None
    priority: Priority = Priority.MEDIUM
    content_type: ContentType = ContentType.TEXT
    
    # Computed fields
    token_count: Optional[TokenCount] = None
    relevance_score: float = 1.0
    importance_score: float = 1.0
    
    # Context management
    is_pinned: bool = False
    is_summarized: bool = False
    original_content: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to API-compatible dict."""
        result = {
            "role": self.role.value,
            "content": self.content
        }
        if self.name:
            result["name"] = self.name
        if self.tool_calls:
            result["tool_calls"] = self.tool_calls
        if self.tool_call_id:
            result["tool_call_id"] = self.tool_call_id
        return result


@dataclass
class Conversation:
    """Collection of messages forming a conversation."""
    messages: List[Message] = field(default_factory=list)
    system_message: Optional[Message] = None
    
    # Token tracking
    total_tokens: int = 0
    max_tokens: int = 128000  # Default context window
    
    # Metadata
    id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def message_count(self) -> int:
        return len(self.messages) + (1 if self.system_message else 0)
    
    @property
    def available_tokens(self) -> int:
        return self.max_tokens - self.total_tokens
    
    @property
    def utilization(self) -> float:
        return self.total_tokens / self.max_tokens if self.max_tokens > 0 else 0
    
    def to_messages(self) -> List[Dict[str, Any]]:
        """Convert to API-compatible message list."""
        result = []
        if self.system_message:
            result.append(self.system_message.to_dict())
        result.extend(m.to_dict() for m in self.messages)
        return result


@dataclass
class ContextBudget:
    """Budget allocation for context window."""
    total_tokens: int
    system_tokens: int = 0
    history_tokens: int = 0
    current_turn_tokens: int = 0
    tools_tokens: int = 0
    reserved_output_tokens: int = 4096
    
    @property
    def available_for_history(self) -> int:
        used = self.system_tokens + self.current_turn_tokens + self.tools_tokens
        return max(0, self.total_tokens - used - self.reserved_output_tokens)
    
    @property
    def used_tokens(self) -> int:
        return (self.system_tokens + self.history_tokens + 
                self.current_turn_tokens + self.tools_tokens)
    
    @property
    def remaining_tokens(self) -> int:
        return max(0, self.total_tokens - self.used_tokens - self.reserved_output_tokens)


@dataclass
class PruningResult:
    """Result of context pruning."""
    original_messages: int
    pruned_messages: int
    removed_messages: int
    original_tokens: int
    final_tokens: int
    tokens_saved: int
    strategy_used: PruningStrategy
    removed_indices: List[int] = field(default_factory=list)
    summarized_content: Optional[str] = None
    warnings: List[str] = field(default_factory=list)


@dataclass
class CompressionResult:
    """Result of content compression."""
    original_content: str
    compressed_content: str
    original_tokens: int
    compressed_tokens: int
    compression_ratio: float
    method_used: CompressionMethod
    information_preserved: float  # 0-1 estimate
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContextSnapshot:
    """Snapshot of context state."""
    timestamp: datetime
    total_tokens: int
    message_count: int
    system_tokens: int
    history_tokens: int
    utilization: float
    budget: ContextBudget
    warnings: List[str] = field(default_factory=list)


@dataclass
class WindowConfig:
    """Context window configuration."""
    max_tokens: int = 128000
    reserved_output_tokens: int = 4096
    max_history_ratio: float = 0.7
    pruning_strategy: PruningStrategy = PruningStrategy.RECENCY_WEIGHTED
    compression_method: CompressionMethod = CompressionMethod.NONE
    tokenizer_type: TokenizerType = TokenizerType.TIKTOKEN_CL100K
    
    # Pruning settings
    min_messages_to_keep: int = 2
    always_keep_system: bool = True
    preserve_tool_pairs: bool = True
    preserve_recent_turns: int = 2
    
    # Thresholds
    pruning_threshold: float = 0.85  # Start pruning at 85% utilization
    compression_threshold: float = 0.9  # Start compressing at 90%
    
    # Callbacks
    on_prune: Optional[Callable[[PruningResult], None]] = None
    on_compress: Optional[Callable[[CompressionResult], None]] = None
    
    def __post_init__(self):
        self.available_for_content = int(
            self.max_tokens * self.max_history_ratio
        )


@dataclass
class ModelConfig:
    """Model-specific configuration."""
    name: str
    max_context_tokens: int
    max_output_tokens: int
    tokenizer: TokenizerType
    supports_images: bool = False
    supports_tools: bool = True
    tokens_per_image: int = 85  # Base tokens for image
    
    @classmethod
    def gpt4(cls) -> "ModelConfig":
        return cls(
            name="gpt-4",
            max_context_tokens=128000,
            max_output_tokens=4096,
            tokenizer=TokenizerType.TIKTOKEN_CL100K,
            supports_images=True
        )
    
    @classmethod
    def gpt4o(cls) -> "ModelConfig":
        return cls(
            name="gpt-4o",
            max_context_tokens=128000,
            max_output_tokens=16384,
            tokenizer=TokenizerType.TIKTOKEN_O200K,
            supports_images=True
        )
    
    @classmethod
    def gpt35_turbo(cls) -> "ModelConfig":
        return cls(
            name="gpt-3.5-turbo",
            max_context_tokens=16385,
            max_output_tokens=4096,
            tokenizer=TokenizerType.TIKTOKEN_CL100K,
            supports_images=False
        )
    
    @classmethod
    def claude3(cls) -> "ModelConfig":
        return cls(
            name="claude-3",
            max_context_tokens=200000,
            max_output_tokens=4096,
            tokenizer=TokenizerType.APPROXIMATE,
            supports_images=True
        )


@dataclass
class UsageStats:
    """Usage statistics for monitoring."""
    total_tokens_processed: int = 0
    total_tokens_pruned: int = 0
    total_tokens_compressed: int = 0
    prune_operations: int = 0
    compress_operations: int = 0
    average_utilization: float = 0.0
    peak_utilization: float = 0.0
    overflow_prevented: int = 0
    
    def record_operation(
        self,
        tokens_processed: int,
        tokens_saved: int,
        utilization: float,
        was_prune: bool = True
    ):
        """Record an operation."""
        self.total_tokens_processed += tokens_processed
        
        if was_prune:
            self.total_tokens_pruned += tokens_saved
            self.prune_operations += 1
        else:
            self.total_tokens_compressed += tokens_saved
            self.compress_operations += 1
        
        # Update utilization stats
        n = self.prune_operations + self.compress_operations
        self.average_utilization = (
            (self.average_utilization * (n - 1) + utilization) / n
        )
        self.peak_utilization = max(self.peak_utilization, utilization)
