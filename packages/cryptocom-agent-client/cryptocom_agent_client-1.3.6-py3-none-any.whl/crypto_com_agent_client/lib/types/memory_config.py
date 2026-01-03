"""
Memory Configuration Types.

This module defines configuration types for advanced memory management,
including token limits and pruning policies.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class MemoryConfig:
    """
    Configuration class for memory management settings.

    This class defines parameters for optimizing token usage and managing
    conversation memory in AI agents.

    Attributes:
        max_context_tokens (int): Maximum tokens to send to LLM in a single request
        max_conversation_tokens (int): Maximum tokens to store in full conversation history
        message_compression_threshold (int): Min tokens in Q&A pair to trigger compression
        compression_target_ratio (float): Target compression ratio (0.3 = compress to 30%)
        preserve_recent_messages (int): Number of most recent messages to always preserve
        max_recent_message_tokens (int): Max tokens for recent messages before forced processing
        allow_recent_summarization (bool): Allow summarization of recent messages if needed
        enable_semantic_features (bool): Enable semantic deduplication and diversity features

    Example:
        >>> from crypto_com_agent_client.lib.types.memory_config import MemoryConfig
        >>> config = MemoryConfig(
        ...     max_context_tokens=8192,
        ...     max_conversation_tokens=32768
        ... )
    """

    # Token limits (optimal defaults for GPT-4 class models)
    max_context_tokens: int = 8192  # Good balance for most LLMs
    max_conversation_tokens: int = 32768  # 4x context for history retention

    # Compression settings (optimal for cost/quality balance)
    message_compression_threshold: int = 100  # Compress Q&A pairs over 100 tokens
    compression_target_ratio: float = 0.3  # Compress to 30% of original (70% reduction)

    # Message preservation (optimal for conversation continuity)
    preserve_recent_messages: int = 10  # Keep last 10 messages for context
    max_recent_message_tokens: int = 500  # Allow up to 500 tokens in recent messages
    allow_recent_summarization: bool = True  # Summarize recent if they're too large

    # Semantic features (optimal for quality, disabled by default for speed)
    enable_semantic_features: bool = False  # Enable for better deduplication

    def __post_init__(self):
        """Validate configuration values."""
        if self.max_context_tokens <= 0:
            raise ValueError("max_context_tokens must be positive")
        if self.max_conversation_tokens < self.max_context_tokens:
            raise ValueError("max_conversation_tokens must be >= max_context_tokens")
        if self.message_compression_threshold <= 0:
            raise ValueError("message_compression_threshold must be positive")
        if not 0.0 < self.compression_target_ratio <= 1.0:
            raise ValueError("compression_target_ratio must be between 0.0 and 1.0")
        if self.preserve_recent_messages < 0:
            raise ValueError("preserve_recent_messages must be non-negative")
        if self.max_recent_message_tokens <= 0:
            raise ValueError("max_recent_message_tokens must be positive")


@dataclass
class DefaultMemoryConfigs:
    """Default memory configurations for different use cases."""

    @staticmethod
    def conservative() -> MemoryConfig:
        """Conservative configuration for limited resources (GPT-3.5 optimal)."""
        return MemoryConfig(
            max_context_tokens=4096,
            max_conversation_tokens=16384,
            message_compression_threshold=80,  # More aggressive compression
            compression_target_ratio=0.25,  # Compress to 25%
            preserve_recent_messages=1,
            max_recent_message_tokens=300,
            allow_recent_summarization=False,
            enable_semantic_features=False,  # Save compute
        )

    @staticmethod
    def balanced() -> MemoryConfig:
        """Balanced configuration for general use (Default - GPT-4 optimal)."""
        return MemoryConfig(
            max_context_tokens=8192,
            max_conversation_tokens=32768,
            message_compression_threshold=100,
            compression_target_ratio=0.3,
            preserve_recent_messages=2,
            max_recent_message_tokens=500,
            allow_recent_summarization=True,
            enable_semantic_features=False,  # Can enable if needed
        )

    @staticmethod
    def aggressive() -> MemoryConfig:
        """Aggressive configuration for maximum retention (Claude/GPT-4 Turbo optimal)."""
        return MemoryConfig(
            max_context_tokens=16384,
            max_conversation_tokens=65536,
            message_compression_threshold=150,  # Less aggressive compression
            compression_target_ratio=0.4,  # Keep more detail
            preserve_recent_messages=3,
            max_recent_message_tokens=1000,
            allow_recent_summarization=True,
            enable_semantic_features=True,  # Use all features
        )

    @staticmethod
    def no_pruning() -> MemoryConfig:
        """No pruning configuration - behaves like traditional chatbot."""
        return MemoryConfig(
            max_context_tokens=1000000,  # Very high limit to disable pruning
            max_conversation_tokens=1000000,  # Very high limit to disable pruning
            message_compression_threshold=1000000,  # Never compress
            compression_target_ratio=1.0,  # No compression
            preserve_recent_messages=0,
            max_recent_message_tokens=1000000,
            allow_recent_summarization=False,
            enable_semantic_features=False,
        )
