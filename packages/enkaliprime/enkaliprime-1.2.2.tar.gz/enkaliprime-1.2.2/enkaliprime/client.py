"""
EnkaliPrime API Client

Main client class for interacting with the EnkaliPrime Chat API.
Supports RAG-enabled chat, streaming responses, and session management.
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime
from typing import Any, AsyncGenerator, Callable, Dict, Generator, List, Optional, Union

import httpx

from .exceptions import (
    APIError,
    AuthenticationError,
    ConnectionError,
    SessionError,
    StreamingError,
    ValidationError,
)
from .models import (
    ChatApiConfig,
    ChatMessage,
    ChatRequest,
    ChatSession,
    ContextMessage,
    ConversationContext,
    LoadingConfig,
    MessageStatus,
    MessageType,
    ResolvedConnection,
)
from .spinner import Spinner

logger = logging.getLogger(__name__)


class EnkaliPrimeClient:
    """
    EnkaliPrime Chat API Client.
    
    Provides methods to interact with the EnkaliPrime Chat API for RAG-enabled
    AI conversations with session management and streaming support.
    
    Example:
        ```python
        from enkaliprime import EnkaliPrimeClient, ChatApiConfig
        
        config = ChatApiConfig(
            unified_api_key="ek_bridge_xxxxx",
            base_url="https://sdk.enkaliprime.com"
        )
        
        client = EnkaliPrimeClient(config)
        
        # Send a message
        response = client.send_message(
            message="Hello, how can you help me?",
            session_id="session_123"
        )
        print(response)
        ```
    """
    
    def __init__(self, config: Union[ChatApiConfig, Dict[str, Any]]):
        """
        Initialize the EnkaliPrime client.
        
        Args:
            config: Either a ChatApiConfig object or a dictionary with:
                - unified_api_key: EnkaliBridge unified API key
                - base_url: EnkaliBridge gateway URL
                - user_id: Optional user identifier
                - timeout: Request timeout in seconds (default: 30)
                - max_retries: Maximum retry attempts (default: 3)
        """
        if isinstance(config, dict):
            self.config = ChatApiConfig(**config)
        else:
            self.config = config
        
        self.config.validate()
        
        self._resolved_connection: Optional[ResolvedConnection] = None
        self._resolution_lock = asyncio.Lock() if asyncio.get_event_loop().is_running() else None
        self._http_client: Optional[httpx.Client] = None
        self._async_http_client: Optional[httpx.AsyncClient] = None
        self._conversation_history: List[Dict[str, str]] = []
        self._current_session: Optional[ChatSession] = None
    
    def _get_http_client(self) -> httpx.Client:
        """Get or create synchronous HTTP client."""
        if self._http_client is None:
            self._http_client = httpx.Client(
                timeout=httpx.Timeout(self.config.timeout),
                headers={
                    "Content-Type": "application/json",
                    "X-EnkaliBridge-Key": self.config.unified_api_key,
                },
            )
        return self._http_client
    
    def _get_async_http_client(self) -> httpx.AsyncClient:
        """Get or create asynchronous HTTP client."""
        if self._async_http_client is None:
            self._async_http_client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.config.timeout),
                headers={
                    "Content-Type": "application/json",
                    "X-EnkaliBridge-Key": self.config.unified_api_key,
                },
            )
        return self._async_http_client
    
    def _resolve_connection_sync(self) -> ResolvedConnection:
        """
        Synchronously resolve the unified API key to connection details.
        
        Returns:
            ResolvedConnection with widget and endpoint information.
            
        Raises:
            AuthenticationError: If API key is invalid.
            ConnectionError: If unable to connect to the API.
        """
        if self._resolved_connection is not None:
            return self._resolved_connection
        
        try:
            resolve_url = f"{self.config.base_url}/resolve"
            params = {"unified_api_key": self.config.unified_api_key}
            
            client = self._get_http_client()
            response = client.get(resolve_url, params=params)
            
            if response.status_code == 401:
                raise AuthenticationError(
                    "Invalid API key. Please check your EnkaliBridge unified API key.",
                    details={"api_key_prefix": self.config.unified_api_key[:20] + "..."},
                )
            
            if not response.is_success:
                raise APIError(
                    f"Failed to resolve API key: {response.text}",
                    status_code=response.status_code,
                )
            
            data = response.json()
            
            if not data.get("success") or not data.get("connection"):
                raise ConnectionError(
                    "Invalid response from EnkaliBridge resolution endpoint",
                    details={"response": data},
                )
            
            self._resolved_connection = ResolvedConnection.from_dict(data["connection"])
            logger.info(f"Resolved connection to widget: {self._resolved_connection.widget_name}")
            
            return self._resolved_connection
            
        except httpx.ConnectError as e:
            raise ConnectionError(
                f"Failed to connect to EnkaliBridge: {str(e)}",
                details={"base_url": self.config.base_url},
            )
        except httpx.TimeoutException as e:
            raise ConnectionError(
                f"Connection timeout: {str(e)}",
                details={"timeout": self.config.timeout},
            )
    
    async def _resolve_connection_async(self) -> ResolvedConnection:
        """
        Asynchronously resolve the unified API key to connection details.
        
        Returns:
            ResolvedConnection with widget and endpoint information.
        """
        if self._resolved_connection is not None:
            return self._resolved_connection
        
        try:
            resolve_url = f"{self.config.base_url}/resolve"
            params = {"unified_api_key": self.config.unified_api_key}
            
            client = self._get_async_http_client()
            response = await client.get(resolve_url, params=params)
            
            if response.status_code == 401:
                raise AuthenticationError(
                    "Invalid API key. Please check your EnkaliBridge unified API key.",
                )
            
            if not response.is_success:
                raise APIError(
                    f"Failed to resolve API key: {response.text}",
                    status_code=response.status_code,
                )
            
            data = response.json()
            
            if not data.get("success") or not data.get("connection"):
                raise ConnectionError(
                    "Invalid response from EnkaliBridge resolution endpoint",
                )
            
            self._resolved_connection = ResolvedConnection.from_dict(data["connection"])
            return self._resolved_connection
            
        except httpx.ConnectError as e:
            raise ConnectionError(f"Failed to connect to EnkaliBridge: {str(e)}")
        except httpx.TimeoutException as e:
            raise ConnectionError(f"Connection timeout: {str(e)}")
    
    def send_message(
        self,
        message: str,
        session_id: str,
        context: Optional[ConversationContext] = None,
        stream: bool = False,
        on_chunk: Optional[Callable[[str], None]] = None,
        loading: LoadingConfig = False,
        show_connection: bool = True,
    ) -> str:
        """
        Send a message to the chat API and get a response.
        
        Args:
            message: The user's message text.
            session_id: Current session ID.
            context: Optional conversation history (list of {role, content} dicts).
            stream: Enable streaming response (default: False).
            on_chunk: Optional callback for streaming chunks.
            loading: Show loading animation while waiting for response.
                     - False: No animation (default)
                     - True: Unicode brain animation with "🧠 Thinking" message (recommended)
                     - str: Custom loading message (e.g., "Generating response")
                     - dict: Full config {"message": "...", "style": "dots", "color": "cyan"}
                       Styles: dots, line, dots2, bounce, pulse, moon, brain, arrows, bar
                       Colors: cyan, green, yellow, blue, magenta, white
            show_connection: Show connection animation during API key resolution (default: True)
            
        Returns:
            The AI response text.
            
        Raises:
            APIError: If the API returns an error.
            ConnectionError: If unable to connect.
            
        Example:
            ```python
            # Simple usage
            response = client.send_message(
                message="What's the weather like?",
                session_id="session_123"
            )
            
            # With loading animation
            response = client.send_message(
                message="Explain quantum physics",
                session_id="session_123",
                loading=True  # Shows "🧠 Thinking" with brain animation
            )
            
            # Custom loading message
            response = client.send_message(
                message="Write a poem",
                session_id="session_123",
                loading="Composing"
            )
            
            # Full customization
            response = client.send_message(
                message="Complex query",
                session_id="session_123",
                loading={"message": "Processing", "style": "brain", "color": "magenta"}
            )

            # Disable connection animation for subsequent calls (already connected)
            response = client.send_message(
                message="Follow-up question",
                session_id="session_123",
                show_connection=False  # Skip connection animation since already resolved
            )
            ```
        """
        if not message or not message.strip():
            raise ValidationError("Message cannot be empty")
        
        if not session_id:
            raise ValidationError("session_id is required")
        
        # Parse loading configuration
        spinner_instance = None
        if loading and not stream:  # Don't use spinner with streaming (streaming has its own visual feedback)
            if isinstance(loading, dict):
                spinner_instance = Spinner(
                    message=loading.get("message", "Thinking"),
                    style=loading.get("style", "dots"),
                    color=loading.get("color", "cyan"),
                )
            elif isinstance(loading, str):
                spinner_instance = Spinner(message=loading)
            elif loading is True:
                # Default Unicode loading animation
                spinner_instance = Spinner(
                    message="🧠 Thinking",
                    style="brain",
                    color="cyan"
                )
            else:
                spinner_instance = Spinner(message="Thinking")

        # Show connection animation during resolution (only if not already resolved and connection animation enabled)
        connection_spinner = None
        if show_connection and self._resolved_connection is None:
            connection_spinner = Spinner(
                message="🌐 Connecting to EnkaliPrime",
                style="earth",  # Cool rotating earth animation
                color="blue"
            )
            connection_spinner.start()

        try:
            # Ensure connection is resolved
            connection = self._resolve_connection_sync()
        finally:
            # Stop connection spinner after resolution
            if connection_spinner:
                connection_spinner.stop(success=True, final_message="Connected!")
        
        chat_url = f"{connection.base_url}/chat"
        
        # Prepare request
        request_data = ChatRequest(
            message=message,
            session_id=session_id,
            user_id=self.config.user_id,
            stream=stream,
            context=context or self._conversation_history,
        ).to_dict()
        
        try:
            client = self._get_http_client()
            
            if stream:
                return self._handle_streaming_sync(client, chat_url, request_data, on_chunk)
            
            # Start spinner if configured
            if spinner_instance:
                spinner_instance.start()
            
            try:
                response = client.post(chat_url, json=request_data)
                
                if not response.is_success:
                    if spinner_instance:
                        spinner_instance.stop(success=False)
                    self._handle_error_response(response)
                
                data = response.json()
                ai_response = data.get("message") or data.get("response") or data.get("reply") or ""
                
                # Stop spinner with success
                if spinner_instance:
                    spinner_instance.stop(success=True)
                
            except Exception as e:
                if spinner_instance:
                    spinner_instance.stop(success=False)
                raise
            
            # Update conversation history
            self._conversation_history.append({"role": "user", "content": message})
            self._conversation_history.append({"role": "assistant", "content": ai_response})
            
            # Keep only last 10 messages
            if len(self._conversation_history) > 20:
                self._conversation_history = self._conversation_history[-20:]
            
            return ai_response
            
        except httpx.ConnectError as e:
            raise ConnectionError(f"Failed to send message: {str(e)}")
        except httpx.TimeoutException as e:
            raise ConnectionError(f"Request timeout: {str(e)}")
    
    async def send_message_async(
        self,
        message: str,
        session_id: str,
        context: Optional[ConversationContext] = None,
        stream: bool = False,
    ) -> Union[str, AsyncGenerator[str, None]]:
        """
        Asynchronously send a message to the chat API.
        
        Args:
            message: The user's message text.
            session_id: Current session ID.
            context: Optional conversation history.
            stream: Enable streaming response.
            
        Returns:
            The AI response text, or an async generator for streaming.
            
        Example:
            ```python
            response = await client.send_message_async(
                message="Hello!",
                session_id="session_123"
            )
            ```
        """
        if not message or not message.strip():
            raise ValidationError("Message cannot be empty")
        
        connection = await self._resolve_connection_async()
        chat_url = f"{connection.base_url}/chat"
        
        request_data = ChatRequest(
            message=message,
            session_id=session_id,
            user_id=self.config.user_id,
            stream=stream,
            context=context or self._conversation_history,
        ).to_dict()
        
        try:
            client = self._get_async_http_client()
            
            if stream:
                return self._handle_streaming_async(client, chat_url, request_data)
            
            response = await client.post(chat_url, json=request_data)
            
            if not response.is_success:
                self._handle_error_response(response)
            
            data = response.json()
            ai_response = data.get("message") or data.get("response") or data.get("reply") or ""
            
            # Update conversation history
            self._conversation_history.append({"role": "user", "content": message})
            self._conversation_history.append({"role": "assistant", "content": ai_response})
            
            return ai_response
            
        except httpx.ConnectError as e:
            raise ConnectionError(f"Failed to send message: {str(e)}")
        except httpx.TimeoutException as e:
            raise ConnectionError(f"Request timeout: {str(e)}")
    
    def _handle_streaming_sync(
        self,
        client: httpx.Client,
        url: str,
        data: Dict[str, Any],
        on_chunk: Optional[Callable[[str], None]] = None,
    ) -> str:
        """Handle synchronous streaming response."""
        full_response = ""
        
        try:
            with client.stream("POST", url, json=data) as response:
                if not response.is_success:
                    self._handle_error_response(response)
                
                buffer = ""
                for chunk in response.iter_text():
                    buffer += chunk
                    lines = buffer.split("\n")
                    buffer = lines.pop()
                    
                    for line in lines:
                        if line.startswith("data: "):
                            data_str = line[6:]
                            if data_str == "[DONE]":
                                continue
                            
                            try:
                                json_data = json.loads(data_str)
                                candidates = json_data.get("candidates", [])
                                
                                for candidate in candidates:
                                    content = candidate.get("content", {})
                                    parts = content.get("parts", [])
                                    
                                    for part in parts:
                                        text = part.get("text", "")
                                        if text:
                                            full_response += text
                                            if on_chunk:
                                                on_chunk(text)
                            except json.JSONDecodeError:
                                pass
            
            return full_response
            
        except Exception as e:
            raise StreamingError(f"Error during streaming: {str(e)}")
    
    async def _handle_streaming_async(
        self,
        client: httpx.AsyncClient,
        url: str,
        data: Dict[str, Any],
    ) -> AsyncGenerator[str, None]:
        """Handle asynchronous streaming response."""
        try:
            async with client.stream("POST", url, json=data) as response:
                if not response.is_success:
                    self._handle_error_response(response)
                
                buffer = ""
                async for chunk in response.aiter_text():
                    buffer += chunk
                    lines = buffer.split("\n")
                    buffer = lines.pop()
                    
                    for line in lines:
                        if line.startswith("data: "):
                            data_str = line[6:]
                            if data_str == "[DONE]":
                                continue
                            
                            try:
                                json_data = json.loads(data_str)
                                candidates = json_data.get("candidates", [])
                                
                                for candidate in candidates:
                                    content = candidate.get("content", {})
                                    parts = content.get("parts", [])
                                    
                                    for part in parts:
                                        text = part.get("text", "")
                                        if text:
                                            yield text
                            except json.JSONDecodeError:
                                pass
                                
        except Exception as e:
            raise StreamingError(f"Error during streaming: {str(e)}")
    
    def _handle_error_response(self, response: httpx.Response) -> None:
        """Handle error responses from the API."""
        try:
            error_data = response.json()
            error_message = error_data.get("message") or error_data.get("error") or response.text
            error_code = error_data.get("code")
        except (json.JSONDecodeError, ValueError):
            error_message = response.text or "Unknown error"
            error_code = None
        
        if response.status_code == 401:
            raise AuthenticationError(error_message)
        
        raise APIError(
            message=error_message,
            status_code=response.status_code,
            code=error_code,
        )
    
    def create_session(
        self,
        agent_name: str = "Support Agent",
        agent_avatar: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ChatSession:
        """
        Create a new chat session.
        
        Args:
            agent_name: Name of the chat agent.
            agent_avatar: Optional avatar URL for the agent.
            metadata: Optional metadata to attach to the session.
            
        Returns:
            A new ChatSession object.
            
        Example:
            ```python
            session = client.create_session(
                agent_name="Sarah",
                metadata={"department": "sales"}
            )
            ```
        """
        session_id = f"session_{int(time.time() * 1000)}_{uuid.uuid4().hex[:12]}"
        
        session = ChatSession(
            id=session_id,
            user_id=self.config.user_id,
            agent_name=agent_name,
            agent_avatar=agent_avatar,
            is_active=True,
            start_time=datetime.utcnow().isoformat(),
            metadata=metadata,
        )
        
        self._current_session = session
        self._conversation_history = []
        
        logger.info(f"Created new session: {session_id}")
        return session
    
    def end_session(self) -> Optional[ChatSession]:
        """
        End the current chat session.
        
        Returns:
            The ended ChatSession, or None if no active session.
        """
        if self._current_session is None:
            return None
        
        self._current_session.is_active = False
        self._current_session.end_time = datetime.utcnow().isoformat()
        
        ended_session = self._current_session
        self._current_session = None
        self._conversation_history = []
        
        logger.info(f"Ended session: {ended_session.id}")
        return ended_session
    
    def get_connection(self) -> ResolvedConnection:
        """
        Get the resolved connection details.
        
        Returns:
            ResolvedConnection with widget and endpoint information.
        """
        return self._resolve_connection_sync()
    
    async def get_connection_async(self) -> ResolvedConnection:
        """
        Asynchronously get the resolved connection details.
        
        Returns:
            ResolvedConnection with widget and endpoint information.
        """
        return await self._resolve_connection_async()
    
    def clear_history(self) -> None:
        """Clear the conversation history."""
        self._conversation_history = []
        logger.debug("Cleared conversation history")
    
    def get_history(self) -> ConversationContext:
        """
        Get the current conversation history.

        Returns:
            List of conversation messages as {role, content} dicts.
        """
        return self._conversation_history.copy()
    
    @property
    def current_session(self) -> Optional[ChatSession]:
        """Get the current active session, if any."""
        return self._current_session
    
    def close(self) -> None:
        """Close HTTP clients and clean up resources."""
        if self._http_client is not None:
            self._http_client.close()
            self._http_client = None
        
        if self._async_http_client is not None:
            asyncio.create_task(self._async_http_client.aclose())
            self._async_http_client = None
    
    async def aclose(self) -> None:
        """Asynchronously close HTTP clients and clean up resources."""
        if self._http_client is not None:
            self._http_client.close()
            self._http_client = None
        
        if self._async_http_client is not None:
            await self._async_http_client.aclose()
            self._async_http_client = None
    
    def __enter__(self) -> "EnkaliPrimeClient":
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.close()
    
    async def __aenter__(self) -> "EnkaliPrimeClient":
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.aclose()

