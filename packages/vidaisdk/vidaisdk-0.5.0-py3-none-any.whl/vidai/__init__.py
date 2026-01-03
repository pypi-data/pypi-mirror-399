"""Vidai: Drop-in OpenAI SDK replacement with structured output guarantees."""

from .client import Vidai, Vidai as Client
from .config import VidaiConfig
from .exceptions import (
    VidaiClientError,
    VidaiError,
    StructuredOutputError,
    JSONRepairError,
    ValidationError,
    ConfigurationError,
    PerformanceError
)
from .models import (
    EnhancedChatCompletionMessage,
    JsonRepairInfo,
    PerformanceInfo,
    StructuredOutputRequest,
    ProxyHeaders
)

__version__ = "0.5.0"
__all__ = [
    "Vidai",
    "Client",
    "VidaiConfig",
    "VidaiClientError",
    "VidaiError",
    "StructuredOutputError",
    "JSONRepairError",
    "ValidationError",
    "ConfigurationError",
    "PerformanceError",
    "EnhancedChatCompletionMessage",
    "JsonRepairInfo",
    "PerformanceInfo",
    "StructuredOutputRequest",
    "ProxyHeaders",
]