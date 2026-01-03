"""
Cerebras Model Enum Module.

This module defines the `CerebrasModel` enum, which lists the supported AI models
available from the Cerebras provider via langchain-cerebras.
"""

from enum import Enum


class CerebrasModel(str, Enum):
    """
    Enum for Cerebras AI models.

    This enum represents the various AI models available through Cerebras.
    Cerebras offers extremely fast inference using their Wafer-Scale Engine.

    Attributes:
        LLAMA_3_1_8B (str): Llama 3.1 8B - excels in speed-critical scenarios.
        LLAMA_3_3_70B (str): Llama 3.3 70B - enhanced performance for chat, coding,
                            instruction following, mathematics, and reasoning.
        QWEN_3_32B (str): Qwen 3 32B - hybrid reasoning model that can operate
                          with or without thinking tokens.
        GPT_OSS_120B (str): GPT OSS 120B - efficient reasoning model for science,
                            math, and coding applications (OpenAI OSS model).

    Example:
        >>> from lib.enums.cerebras_model_enum import CerebrasModel
        >>> model = CerebrasModel.GPT_OSS_120B
        >>> print(model)
        gpt-oss-120b

        >>> if model == CerebrasModel.GPT_OSS_120B:
        ...     print("Using GPT OSS 120B model.")
        Using GPT OSS 120B model.
    """

    LLAMA_3_1_8B = "llama3.1-8b"
    LLAMA_3_3_70B = "llama-3.3-70b"
    QWEN_3_32B = "qwen-3-32b"
    GPT_OSS_120B = "gpt-oss-120b"
