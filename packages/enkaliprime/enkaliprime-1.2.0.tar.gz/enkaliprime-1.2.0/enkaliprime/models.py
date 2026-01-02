"""
Data models for the EnkaliPrime Python SDK.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from typing_extensions import Literal


class MessageStatus(str, Enum):
    """Status of a chat message."""
    SENDING = "sending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"


class MessageType(str, Enum):
    """Type of chat message."""
    TEXT = "text"
    SYSTEM = "system"
    QUICK_REPLY = "quick_reply"
    WIDGET = "widget"


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
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary format."""
        return {
            "id": self.id,
            "text": self.text,
            "isUser": self.is_user,
            "timestamp": self.timestamp,
            "status": self.status.value,
            "type": self.type.value,
            "quickReplies": self.quick_replies,
            "sessionId": self.session_id,
            "userId": self.user_id,
            "widget": self.widget,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatMessage":
        """Create message from dictionary format."""
        return cls(
            id=data.get("id", ""),
            text=data.get("text", ""),
            is_user=data.get("isUser", False),
            timestamp=data.get("timestamp", datetime.utcnow().isoformat()),
            status=MessageStatus(data.get("status", "sent")),
            session_id=data.get("sessionId", ""),
            type=MessageType(data.get("type", "text")),
            quick_replies=data.get("quickReplies"),
            user_id=data.get("userId"),
            widget=data.get("widget"),
        )


@dataclass
class ChatSession:
    """Represents a chat session."""
    
    id: str
    agent_name: str
    is_active: bool
    start_time: str
    user_id: Optional[str] = None
    agent_avatar: Optional[str] = None
    end_time: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary format."""
        return {
            "id": self.id,
            "userId": self.user_id,
            "agentName": self.agent_name,
            "agentAvatar": self.agent_avatar,
            "isActive": self.is_active,
            "startTime": self.start_time,
            "endTime": self.end_time,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatSession":
        """Create session from dictionary format."""
        return cls(
            id=data.get("id", ""),
            user_id=data.get("userId"),
            agent_name=data.get("agentName", "Support Agent"),
            agent_avatar=data.get("agentAvatar"),
            is_active=data.get("isActive", True),
            start_time=data.get("startTime", datetime.utcnow().isoformat()),
            end_time=data.get("endTime"),
            metadata=data.get("metadata"),
        )


@dataclass
class ResolvedConnection:
    """Represents a resolved API connection."""
    
    connection_id: str
    widget_id: str
    widget_name: str
    base_url: str
    is_active: bool
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert connection to dictionary format."""
        return {
            "connectionId": self.connection_id,
            "widgetId": self.widget_id,
            "widgetName": self.widget_name,
            "baseUrl": self.base_url,
            "isActive": self.is_active,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ResolvedConnection":
        """Create connection from dictionary format."""
        return cls(
            connection_id=data.get("connectionId", ""),
            widget_id=data.get("widgetId", ""),
            widget_name=data.get("widgetName", ""),
            base_url=data.get("baseUrl", ""),
            is_active=data.get("isActive", False),
        )


@dataclass
class ChatApiConfig:
    """Configuration for the EnkaliPrime API client."""
    
    unified_api_key: str
    base_url: str
    user_id: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    
    def validate(self) -> None:
        """Validate the configuration."""
        if not self.unified_api_key:
            raise ValueError("unified_api_key is required")
        if not self.base_url:
            raise ValueError("base_url is required")
        if not self.unified_api_key.startswith("ek_bridge_"):
            raise ValueError("unified_api_key must start with 'ek_bridge_'")


@dataclass
class ChatRequest:
    """Represents a chat request to be sent to the API."""
    
    message: str
    session_id: str
    user_id: Optional[str] = None
    stream: bool = False
    context: List[Dict[str, str]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert request to dictionary format for API."""
        return {
            "message": self.message,
            "sessionId": self.session_id,
            "userId": self.user_id,
            "stream": self.stream,
            "context": self.context[-10:],  # Last 10 messages for context
        }


@dataclass
class ContextMessage:
    """Represents a context message for conversation history."""
    
    role: str  # 'user' or 'assistant'
    content: str
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary format."""
        return {"role": self.role, "content": self.content}


# Type aliases for better type safety and autocomplete
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

