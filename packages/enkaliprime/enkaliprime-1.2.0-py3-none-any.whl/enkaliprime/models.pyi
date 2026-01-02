"""
Type stubs for EnkaliPrime data models.
Provides comprehensive type information for better IDE support.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from typing_extensions import Literal

# Enums
class MessageStatus(str, Enum):
    """Status of a chat message."""
    SENDING: str = "sending"
    SENT: str = "sent"
    DELIVERED: str = "delivered"
    READ: str = "read"

class MessageType(str, Enum):
    """Type of chat message."""
    TEXT: str = "text"
    SYSTEM: str = "system"
    QUICK_REPLY: str = "quick_reply"
    WIDGET: str = "widget"

# Data Classes
@dataclass
class ChatMessage:
    """Represents a chat message in a conversation."""
    id: str
    text: str
    is_user: bool
    timestamp: str
    status: MessageStatus
    session_id: str
    type: MessageType = MessageType.TEXT
    quick_replies: Optional[List[str]] = None
    user_id: Optional[str] = None
    widget: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]: ...

@dataclass
class ChatSession:
    """Represents a chat session."""
    id: str
    user_id: Optional[str]
    agent_name: str
    agent_avatar: Optional[str]
    is_active: bool
    start_time: str
    end_time: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]: ...

@dataclass
class ResolvedConnection:
    """Connection details resolved from API key."""
    connection_id: str
    widget_id: str
    widget_name: str
    base_url: str
    is_active: bool
    metadata: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ResolvedConnection': ...

@dataclass
class ChatApiConfig:
    """Configuration for EnkaliPrime API client."""
    unified_api_key: str
    base_url: str
    user_id: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3

    def validate(self) -> None: ...

@dataclass
class ChatRequest:
    """Request payload for chat API."""
    message: str
    session_id: str
    user_id: Optional[str] = None
    stream: bool = False
    context: Optional[List[Dict[str, str]]] = None

    def to_dict(self) -> Dict[str, Any]: ...

# Type aliases for better readability
ConversationContext = List[Dict[str, str]]
LoadingConfig = Union[bool, str, Dict[str, Union[str, 'SpinnerStyle', 'ColorName']]]
SpinnerStyle = Literal[
    'dots', 'line', 'dots2', 'bounce', 'pulse',
    'moon', 'earth', 'clock', 'brain', 'arrows', 'bar', 'simple'
]
ColorName = Literal[
    'cyan', 'green', 'yellow', 'blue', 'magenta', 'white', 'reset'
]
MessageRole = Literal['user', 'assistant', 'system']

__all__ = [
    'MessageStatus',
    'MessageType',
    'ChatMessage',
    'ChatSession',
    'ResolvedConnection',
    'ChatApiConfig',
    'ChatRequest',
    'ConversationContext',
    'LoadingConfig',
    'SpinnerStyle',
    'ColorName',
    'MessageRole',
]
