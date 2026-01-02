"""
EnkaliPrime Python SDK

A Python client library for integrating with the EnkaliPrime Chat API.
Provides RAG-enabled AI chat functionality with session management and streaming support.
"""

from .client import EnkaliPrimeClient
from .models import (
    ChatMessage,
    ChatSession,
    ResolvedConnection,
    ChatApiConfig,
    ChatRequest,
    ConversationContext,
    LoadingConfig,
    MessageStatus,
    MessageType,
    SpinnerStyle,
    ColorName,
    MessageRole,
)
from .exceptions import (
    EnkaliPrimeError,
    ConnectionError,
    AuthenticationError,
    APIError,
    StreamingError,
)
from .spinner import (
    Spinner,
    LoadingBar,
    spinner,
    loading_bar,
)
from .type_guards import (
    is_conversation_context,
    is_loading_config,
    is_spinner_style,
    is_color_name,
    is_valid_api_key,
    is_valid_session_id,
    validate_message_content,
)

__version__ = "1.2.2"
__sdk_name__ = "enkaliprime-python-sdk"

__all__ = [
    # Main client
    "EnkaliPrimeClient",
    # Models
    "ChatMessage",
    "ChatSession",
    "ResolvedConnection",
    "ChatApiConfig",
    "ChatRequest",
    "MessageStatus",
    "MessageType",
    # Type aliases
    "ConversationContext",
    "LoadingConfig",
    "SpinnerStyle",
    "ColorName",
    "MessageRole",
    # Exceptions
    "EnkaliPrimeError",
    "ConnectionError",
    "AuthenticationError",
    "APIError",
    "StreamingError",
    # Spinner utilities
    "Spinner",
    "LoadingBar",
    "spinner",
    "loading_bar",
    # Type guards
    "is_conversation_context",
    "is_loading_config",
    "is_spinner_style",
    "is_color_name",
    "is_valid_api_key",
    "is_valid_session_id",
    "validate_message_content",
    # Version info
    "__version__",
    "__sdk_name__",
]
