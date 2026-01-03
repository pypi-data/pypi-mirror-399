"""
Context Window Manager

Production-ready LLM context window optimization and management.
"""

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

from .manager import (
    Tokenizer,
    ApproximateTokenizer,
    TiktokenTokenizer,
    get_tokenizer,
    MessageTokenCounter,
    PruningEngine,
    CompressionEngine,
    ContextWindowManager,
    ConversationBuffer,
    create_manager,
)

__version__ = "0.1.0"
__author__ = "Pranay M"

__all__ = [
    # Enums
    "MessageRole",
    "PruningStrategy",
    "CompressionMethod",
    "TokenizerType",
    "ContentType",
    "Priority",
    # Data classes
    "TokenCount",
    "Message",
    "Conversation",
    "ContextBudget",
    "PruningResult",
    "CompressionResult",
    "ContextSnapshot",
    "WindowConfig",
    "ModelConfig",
    "UsageStats",
    # Core classes
    "Tokenizer",
    "ApproximateTokenizer",
    "TiktokenTokenizer",
    "get_tokenizer",
    "MessageTokenCounter",
    "PruningEngine",
    "CompressionEngine",
    "ContextWindowManager",
    "ConversationBuffer",
    "create_manager",
]
