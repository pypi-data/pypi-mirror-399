"""
Type guard functions for runtime type checking.
Provides additional type safety for the EnkaliPrime SDK.
"""

from typing import Any, Dict, List, Union
from typing_extensions import TypeGuard

from .models import ConversationContext, LoadingConfig, SpinnerStyle, ColorName


def is_conversation_context(obj: Any) -> TypeGuard[ConversationContext]:
    """Check if object is a valid conversation context."""
    if not isinstance(obj, list):
        return False

    for item in obj:
        if not isinstance(item, dict):
            return False
        if not all(isinstance(k, str) and isinstance(v, str) for k, v in item.items()):
            return False
    return True


def is_loading_config(obj: Any) -> TypeGuard[LoadingConfig]:
    """Check if object is a valid loading configuration."""
    if isinstance(obj, (bool, str)):
        return True

    if isinstance(obj, dict):
        valid_keys = {'message', 'style', 'color'}
        if not all(key in valid_keys for key in obj.keys()):
            return False

        # Check message type
        if 'message' in obj and not isinstance(obj['message'], str):
            return False

        # Check style type
        if 'style' in obj and not isinstance(obj['style'], str):
            return False

        # Check color type
        if 'color' in obj and not isinstance(obj['color'], str):
            return False

        return True

    return False


def is_spinner_style(obj: Any) -> TypeGuard[SpinnerStyle]:
    """Check if object is a valid spinner style."""
    valid_styles = {
        'dots', 'line', 'dots2', 'bounce', 'pulse',
        'moon', 'earth', 'clock', 'brain', 'arrows', 'bar', 'simple'
    }
    return isinstance(obj, str) and obj in valid_styles


def is_color_name(obj: Any) -> TypeGuard[ColorName]:
    """Check if object is a valid color name."""
    valid_colors = {'cyan', 'green', 'yellow', 'blue', 'magenta', 'white', 'reset'}
    return isinstance(obj, str) and obj in valid_colors


def is_valid_api_key(api_key: str) -> bool:
    """Check if API key has valid format."""
    return (
        isinstance(api_key, str) and
        api_key.startswith('ek_bridge_') and
        len(api_key) > 20
    )


def is_valid_session_id(session_id: str) -> bool:
    """Check if session ID has valid format."""
    return (
        isinstance(session_id, str) and
        len(session_id.strip()) > 0 and
        not session_id.isspace()
    )


def validate_message_content(content: str) -> bool:
    """Validate message content for basic safety."""
    if not isinstance(content, str):
        return False

    content = content.strip()
    return len(content) > 0 and not content.isspace()


__all__ = [
    'is_conversation_context',
    'is_loading_config',
    'is_spinner_style',
    'is_color_name',
    'is_valid_api_key',
    'is_valid_session_id',
    'validate_message_content',
]
