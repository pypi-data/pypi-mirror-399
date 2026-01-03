"""Tests for Context Window Manager."""

import pytest
from context_window_manager import (
    ContextWindowManager,
    ConversationBuffer,
    WindowConfig,
    ModelConfig,
    PruningStrategy,
    CompressionMethod,
    TokenizerType,
    MessageRole,
    Priority,
    Message,
    Conversation,
    TokenCount,
    ApproximateTokenizer,
    PruningEngine,
    CompressionEngine,
    create_manager,
)


class TestApproximateTokenizer:
    """Test ApproximateTokenizer class."""
    
    def test_count_tokens(self):
        """Test token counting."""
        tokenizer = ApproximateTokenizer(chars_per_token=4.0)
        
        # 20 chars = ~5 tokens
        text = "12345678901234567890"
        count = tokenizer.count_tokens(text)
        assert count == 5
    
    def test_count_empty(self):
        """Test counting empty string."""
        tokenizer = ApproximateTokenizer()
        count = tokenizer.count_tokens("")
        assert count >= 0
    
    def test_encode_decode(self):
        """Test encoding and decoding."""
        tokenizer = ApproximateTokenizer()
        text = "Hello"
        encoded = tokenizer.encode(text)
        decoded = tokenizer.decode(encoded)
        assert decoded == text


class TestMessage:
    """Test Message class."""
    
    def test_create_message(self):
        """Test creating a message."""
        msg = Message(
            role=MessageRole.USER,
            content="Hello, world!"
        )
        
        assert msg.role == MessageRole.USER
        assert msg.content == "Hello, world!"
        assert msg.priority == Priority.MEDIUM
    
    def test_message_to_dict(self):
        """Test converting message to dict."""
        msg = Message(
            role=MessageRole.ASSISTANT,
            content="Hi there!"
        )
        
        d = msg.to_dict()
        assert d["role"] == "assistant"
        assert d["content"] == "Hi there!"
    
    def test_message_with_name(self):
        """Test message with name."""
        msg = Message(
            role=MessageRole.USER,
            content="Hello",
            name="Alice"
        )
        
        d = msg.to_dict()
        assert d["name"] == "Alice"


class TestConversation:
    """Test Conversation class."""
    
    def test_create_conversation(self):
        """Test creating a conversation."""
        conv = Conversation()
        
        assert conv.message_count == 0
        assert conv.total_tokens == 0
    
    def test_add_messages(self):
        """Test adding messages."""
        conv = Conversation()
        conv.messages.append(Message(role=MessageRole.USER, content="Hi"))
        conv.messages.append(Message(role=MessageRole.ASSISTANT, content="Hello"))
        
        assert conv.message_count == 2
    
    def test_utilization(self):
        """Test utilization calculation."""
        conv = Conversation(max_tokens=1000)
        conv.total_tokens = 500
        
        assert conv.utilization == 0.5
    
    def test_to_messages(self):
        """Test converting to message list."""
        conv = Conversation()
        conv.system_message = Message(role=MessageRole.SYSTEM, content="You are helpful.")
        conv.messages.append(Message(role=MessageRole.USER, content="Hi"))
        
        messages = conv.to_messages()
        assert len(messages) == 2
        assert messages[0]["role"] == "system"


class TestTokenCount:
    """Test TokenCount class."""
    
    def test_create_token_count(self):
        """Test creating token count."""
        tc = TokenCount(total=100, text_tokens=90, overhead_tokens=10)
        
        assert tc.total == 100
        assert tc.content_tokens == 90
    
    def test_add_token_counts(self):
        """Test adding token counts."""
        tc1 = TokenCount(total=50, text_tokens=45)
        tc2 = TokenCount(total=30, text_tokens=25)
        
        tc3 = tc1 + tc2
        assert tc3.total == 80
        assert tc3.text_tokens == 70


class TestWindowConfig:
    """Test WindowConfig class."""
    
    def test_default_config(self):
        """Test default configuration."""
        config = WindowConfig()
        
        assert config.max_tokens == 128000
        assert config.pruning_strategy == PruningStrategy.RECENCY_WEIGHTED
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = WindowConfig(
            max_tokens=16000,
            pruning_strategy=PruningStrategy.FIFO,
            pruning_threshold=0.9
        )
        
        assert config.max_tokens == 16000
        assert config.pruning_strategy == PruningStrategy.FIFO


class TestModelConfig:
    """Test ModelConfig class."""
    
    def test_gpt4_preset(self):
        """Test GPT-4 preset."""
        config = ModelConfig.gpt4()
        
        assert config.name == "gpt-4"
        assert config.max_context_tokens == 128000
        assert config.supports_images is True
    
    def test_gpt35_preset(self):
        """Test GPT-3.5 preset."""
        config = ModelConfig.gpt35_turbo()
        
        assert config.name == "gpt-3.5-turbo"
        assert config.max_context_tokens == 16385
    
    def test_claude_preset(self):
        """Test Claude preset."""
        config = ModelConfig.claude3()
        
        assert config.name == "claude-3"
        assert config.max_context_tokens == 200000


class TestPruningEngine:
    """Test PruningEngine class."""
    
    def test_prune_fifo(self):
        """Test FIFO pruning."""
        tokenizer = ApproximateTokenizer()
        config = WindowConfig(pruning_strategy=PruningStrategy.FIFO)
        engine = PruningEngine(tokenizer, config)
        
        messages = [
            Message(role=MessageRole.USER, content="Message " + "x" * 100)
            for _ in range(10)
        ]
        
        pruned, result = engine.prune(messages, 100, PruningStrategy.FIFO)
        
        assert len(pruned) < len(messages)
        assert result.removed_messages > 0
    
    def test_prune_respects_pinned(self):
        """Test that pinned messages are not pruned."""
        tokenizer = ApproximateTokenizer()
        config = WindowConfig()
        engine = PruningEngine(tokenizer, config)
        
        messages = [
            Message(role=MessageRole.USER, content="x" * 100, is_pinned=True),
            Message(role=MessageRole.USER, content="y" * 100),
        ]
        
        pruned, result = engine.prune(messages, 50, PruningStrategy.FIFO)
        
        # Pinned message should remain
        assert any(m.is_pinned for m in pruned)
    
    def test_no_prune_needed(self):
        """Test when no pruning needed."""
        tokenizer = ApproximateTokenizer()
        config = WindowConfig()
        engine = PruningEngine(tokenizer, config)
        
        messages = [Message(role=MessageRole.USER, content="Hi")]
        
        pruned, result = engine.prune(messages, 10000)
        
        assert len(pruned) == 1
        assert result.removed_messages == 0


class TestCompressionEngine:
    """Test CompressionEngine class."""
    
    def test_truncate(self):
        """Test truncation compression."""
        tokenizer = ApproximateTokenizer()
        engine = CompressionEngine(tokenizer)
        
        content = "This is a long text. " * 50
        result = engine.compress(content, 50, CompressionMethod.TRUNCATE)
        
        assert result.compressed_tokens <= 60  # Allow some margin
        assert result.compression_ratio < 1.0
    
    def test_bullet_points(self):
        """Test bullet point compression."""
        tokenizer = ApproximateTokenizer()
        engine = CompressionEngine(tokenizer)
        
        content = "First sentence. Second sentence. Third sentence. Fourth sentence."
        result = engine.compress(content, 50, CompressionMethod.BULLET_POINTS)
        
        assert "•" in result.compressed_content
    
    def test_no_compression_needed(self):
        """Test when no compression needed."""
        tokenizer = ApproximateTokenizer()
        engine = CompressionEngine(tokenizer)
        
        content = "Short text."
        result = engine.compress(content, 1000)
        
        assert result.compressed_content == content
        assert result.compression_ratio == 1.0


class TestContextWindowManager:
    """Test ContextWindowManager class."""
    
    def test_create_manager(self):
        """Test creating manager."""
        manager = ContextWindowManager()
        assert manager is not None
    
    def test_add_message(self):
        """Test adding messages."""
        manager = ContextWindowManager()
        
        msg = manager.add_message("user", "Hello!")
        
        assert msg.role == MessageRole.USER
        assert msg.content == "Hello!"
        assert manager.conversation.message_count == 1
    
    def test_add_system_message(self):
        """Test adding system message."""
        manager = ContextWindowManager()
        
        manager.set_system_message("You are helpful.")
        
        assert manager.conversation.system_message is not None
        assert manager.conversation.system_message.content == "You are helpful."
    
    def test_get_messages(self):
        """Test getting messages."""
        manager = ContextWindowManager()
        
        manager.set_system_message("System prompt")
        manager.add_message("user", "Hello")
        manager.add_message("assistant", "Hi!")
        
        messages = manager.get_messages()
        
        assert len(messages) == 3
        assert messages[0]["role"] == "system"
    
    def test_get_budget(self):
        """Test getting budget."""
        manager = ContextWindowManager()
        
        manager.add_message("user", "Hello")
        
        budget = manager.get_budget()
        
        assert budget.total_tokens > 0
        assert budget.history_tokens > 0
    
    def test_manual_prune(self):
        """Test manual pruning."""
        config = WindowConfig(max_tokens=1000)
        manager = ContextWindowManager(config)
        
        # Add many messages
        for i in range(20):
            manager.add_message("user", f"Message {i}: " + "x" * 100)
        
        result = manager.prune(target_tokens=200)
        
        assert result.removed_messages > 0
    
    def test_pin_message(self):
        """Test pinning messages."""
        manager = ContextWindowManager()
        
        manager.add_message("user", "Important!")
        manager.pin_message(0)
        
        assert manager.conversation.messages[0].is_pinned is True
    
    def test_set_priority(self):
        """Test setting priority."""
        manager = ContextWindowManager()
        
        manager.add_message("user", "Hello")
        manager.set_priority(0, Priority.CRITICAL)
        
        assert manager.conversation.messages[0].priority == Priority.CRITICAL
    
    def test_clear(self):
        """Test clearing conversation."""
        manager = ContextWindowManager()
        
        manager.set_system_message("System")
        manager.add_message("user", "Hello")
        
        manager.clear(keep_system=True)
        
        assert manager.conversation.message_count == 1  # Only system
        assert manager.conversation.system_message is not None
    
    def test_fits(self):
        """Test fits check."""
        config = WindowConfig(max_tokens=100)
        manager = ContextWindowManager(config)
        
        assert manager.fits("Short text")
        assert not manager.fits("x" * 10000)
    
    def test_tokens_for(self):
        """Test token counting."""
        manager = ContextWindowManager()
        
        tokens = manager.tokens_for("Hello, world!")
        
        assert tokens > 0


class TestConversationBuffer:
    """Test ConversationBuffer class."""
    
    def test_create_buffer(self):
        """Test creating buffer."""
        buffer = ConversationBuffer()
        assert buffer is not None
    
    def test_add_and_get(self):
        """Test adding and getting messages."""
        buffer = ConversationBuffer()
        
        buffer.add("user", "Hello")
        buffer.add("assistant", "Hi!")
        
        messages = buffer.get_messages()
        assert len(messages) == 2
    
    def test_message_limit(self):
        """Test message count limit."""
        buffer = ConversationBuffer(max_messages=5)
        
        for i in range(10):
            buffer.add("user", f"Message {i}")
        
        assert buffer.message_count <= 5
    
    def test_clear_buffer(self):
        """Test clearing buffer."""
        buffer = ConversationBuffer()
        
        buffer.add("user", "Hello")
        buffer.clear()
        
        assert buffer.message_count == 0


class TestCreateManager:
    """Test create_manager factory function."""
    
    def test_create_gpt4(self):
        """Test creating GPT-4 manager."""
        manager = create_manager("gpt-4")
        
        assert manager.config.max_tokens == 128000
    
    def test_create_gpt35(self):
        """Test creating GPT-3.5 manager."""
        manager = create_manager("gpt-3.5-turbo")
        
        assert manager.config.max_tokens == 16385
    
    def test_create_unknown_model(self):
        """Test creating manager for unknown model."""
        manager = create_manager("unknown-model")
        
        # Should still work with defaults
        assert manager is not None


class TestEdgeCases:
    """Test edge cases."""
    
    def test_empty_conversation(self):
        """Test with empty conversation."""
        manager = ContextWindowManager()
        
        messages = manager.get_messages()
        assert messages == []
        
        budget = manager.get_budget()
        assert budget.history_tokens == 0
    
    def test_unicode_content(self):
        """Test with unicode content."""
        manager = ContextWindowManager()
        
        msg = manager.add_message("user", "Hello 世界! 🌍")
        
        assert "世界" in msg.content
        assert msg.token_count is not None
    
    def test_very_long_message(self):
        """Test with very long message."""
        manager = ContextWindowManager()
        
        long_content = "x" * 100000
        msg = manager.add_message("user", long_content)
        
        assert msg.token_count.total > 0
    
    def test_auto_prune_on_threshold(self):
        """Test automatic pruning at threshold."""
        config = WindowConfig(
            max_tokens=500,
            pruning_threshold=0.5
        )
        manager = ContextWindowManager(config)
        
        # Add messages until pruning triggers
        for i in range(50):
            manager.add_message("user", f"Msg {i}: " + "x" * 20)
        
        # Should have auto-pruned
        assert manager.conversation.utilization <= 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
