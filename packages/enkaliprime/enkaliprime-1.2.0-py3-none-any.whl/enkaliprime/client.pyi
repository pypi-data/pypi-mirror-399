"""
Type stubs for EnkaliPrime client.
Provides comprehensive type information for the main API client.
"""

import asyncio
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional, Union
from typing_extensions import Literal, overload

from .models import (
    ChatApiConfig,
    ChatMessage,
    ChatRequest,
    ChatSession,
    ResolvedConnection,
    ConversationContext,
    LoadingConfig,
    SpinnerStyle,
    ColorName,
    MessageRole,
)

class EnkaliPrimeClient:
    """
    EnkaliPrime Chat API Client.

    Provides methods to interact with the EnkaliPrime Chat API for RAG-enabled
    AI conversations with session management and streaming support.
    """

    def __init__(
        self,
        config: Union[ChatApiConfig, Dict[str, Any]]
    ) -> None: ...

    # Synchronous methods
    def send_message(
        self,
        message: str,
        session_id: str,
        context: Optional[ConversationContext] = None,
        stream: bool = False,
        on_chunk: Optional[Callable[[str], None]] = None,
        loading: LoadingConfig = False,
    ) -> str: ...

    def create_session(
        self,
        agent_name: str = "Support Agent",
        agent_avatar: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ChatSession: ...

    def end_session(self) -> Optional[ChatSession]: ...

    def get_connection(self) -> ResolvedConnection: ...

    def clear_history(self) -> None: ...

    def get_history(self) -> ConversationContext: ...

    # Asynchronous methods
    async def send_message_async(
        self,
        message: str,
        session_id: str,
        context: Optional[ConversationContext] = None,
        stream: bool = False,
    ) -> Union[str, AsyncGenerator[str, None]]: ...

    async def get_connection_async(self) -> ResolvedConnection: ...

    # Properties
    @property
    def current_session(self) -> Optional[ChatSession]: ...

    # Context manager support
    def __enter__(self) -> 'EnkaliPrimeClient': ...

    def __exit__(
        self,
        exc_type: Any,
        exc_val: Any,
        exc_tb: Any
    ) -> None: ...

    # Async context manager support
    async def __aenter__(self) -> 'EnkaliPrimeClient': ...

    async def __aexit__(
        self,
        exc_type: Any,
        exc_val: Any,
        exc_tb: Any
    ) -> None: ...

    def close(self) -> None: ...

    async def aclose(self) -> None: ...
