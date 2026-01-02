"""
Type stubs for EnkaliPrime type guard functions.
Provides comprehensive type information for runtime type checking.
"""

from typing import Any
from typing_extensions import TypeGuard

from .models import ConversationContext, LoadingConfig, SpinnerStyle, ColorName


def is_conversation_context(obj: Any) -> TypeGuard[ConversationContext]: ...

def is_loading_config(obj: Any) -> TypeGuard[LoadingConfig]: ...

def is_spinner_style(obj: Any) -> TypeGuard[SpinnerStyle]: ...

def is_color_name(obj: Any) -> TypeGuard[ColorName]: ...

def is_valid_api_key(api_key: str) -> bool: ...

def is_valid_session_id(session_id: str) -> bool: ...

def validate_message_content(content: str) -> bool: ...

__all__ = [
    'is_conversation_context',
    'is_loading_config',
    'is_spinner_style',
    'is_color_name',
    'is_valid_api_key',
    'is_valid_session_id',
    'validate_message_content',
]
