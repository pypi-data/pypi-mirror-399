"""
Plugins Module.

This module defines the `Plugins` TypedDict, which encapsulates additional
configurations and integrations for extending the functionality of the agent.
"""

# Standard library imports
from dataclasses import asdict, is_dataclass
from typing import Any, Callable, List, Optional, Union

# Third-party imports
from pydantic import BaseModel, Field, field_validator

from crypto_com_agent_client.lib.types.memory_config import MemoryConfig

# Internal application imports
from crypto_com_agent_client.lib.utils.storage import Storage
from crypto_com_agent_client.plugins.base import AgentPlugin
from crypto_com_agent_client.plugins.storage.sqllite_plugin import SQLitePlugin


class PluginsConfig(BaseModel):
    """
    TypedDict for Plugins configuration.

    Attributes:
        personality (Optional[dict]): Personality settings for the agent. Includes tone, language, and verbosity.
            Example:
                {
                    "tone": "friendly",
                    "language": "English",
                    "verbosity": "high"
                }
        instructions (Optional[str]): Custom instructions to guide the agent's behavior.
            Example:
                "You are a humorous assistant that includes a joke in every response."
        storage (Optional[Storage]): A custom storage implementation for persisting state.
            Example:
                storage = SQLitePlugin(db_path="state.db")
        langfuse (Optional[LangchainCallbackHandler]): A LangFuse handler for monitoring interactions.
            Example:
                langfuse = LangchainCallbackHandler(
                    public_key="public-key",
                    secret_key="secret-key",
                    host="https://langfuse.example.com",
                )
        tools (Optional[List[Callable[..., Any]]]): A list of callable tool functions for extending agent functionality.
            Example:
                tools = [greet_user, calculate_sum]
        memory_config (Optional[MemoryConfig]): Configuration for advanced memory management.
            Example:
                from crypto_com_agent_client.lib.types.memory_config import DefaultMemoryConfigs
                memory_config = DefaultMemoryConfigs.balanced()

    Example:
        >>> from lib.types.plugins import Plugins
        >>> plugins: Plugins = {
        ...     "personality": {
        ...         "tone": "friendly",
        ...         "language": "English",
        ...         "verbosity": "high"
        ...     },
        ...     "instructions": "You are a humorous assistant.",
        ...     "storage": SQLitePlugin(db_path="state.db"),
        ...     "langfuse": LangchainCallbackHandler(
        ...         public_key="public-key",
        ...         secret_key="secret-key",
        ...         host="https://langfuse.example.com",
        ...     ),
        ...     "tools": [greet_user, calculate_sum]
        ...     "telegram": {"bot_token": os.getenv("TELEGRAM_BOT_TOKEN")} {"bot_token": os.getenv("TELEGRAM_BOT_TOKEN")}
        ... }
    """

    personality: Optional[dict] = Field(
        default={
            "tone": "professional",
            "language": "English",
            "verbosity": "medium",
        }
    )
    instructions: Optional[str] = Field(
        default="You are an AI assistant designed to provide helpful, accurate, and professional responses."
    )
    storage: Optional[Union[SQLitePlugin, Storage]] = Field(default_factory=Storage)
    langfuse: Optional[dict] = Field(default=None)
    tools: Optional[List[Callable[..., Any]]] = Field(default=[])
    telegram: Optional[AgentPlugin] = None
    discord: Optional[AgentPlugin] = None
    memory_config: Optional[MemoryConfig] = Field(default=None)

    @field_validator("memory_config", mode="before")
    @classmethod
    def validate_memory_config(cls, memory_config_value):
        """Convert dataclass MemoryConfig to dict for Pydantic validation."""
        if memory_config_value is None:
            return None
        if is_dataclass(memory_config_value) and not isinstance(
            memory_config_value, type
        ):
            return asdict(memory_config_value)
        return memory_config_value

    class Config:
        arbitrary_types_allowed = True

    def collect_all_plugins(self) -> List[AgentPlugin]:
        plugins = []
        if self.telegram:
            plugins.append(self.telegram)
        if self.discord:
            plugins.append(self.discord)
        return plugins
