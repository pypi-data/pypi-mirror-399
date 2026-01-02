"""Chat service for handling agent interactions."""

from collections.abc import AsyncIterator
from datetime import datetime

from miu_studio.models.api import Session, SessionMessage, StreamChunk
from miu_studio.services.session_manager import SessionManager


class ChatService:
    """Service for chat interactions with sessions."""

    def __init__(self, session_manager: SessionManager | None = None) -> None:
        """Initialize chat service."""
        self._session_manager = session_manager or SessionManager()

    async def chat(self, session_id: str, message: str) -> tuple[str, Session]:
        """Send a message and get response (non-streaming).

        Args:
            session_id: Session ID (UUID format)
            message: User message

        Returns:
            Tuple of (response_text, updated_session)

        Raises:
            ValueError: If session not found or invalid ID
        """
        session = await self._session_manager.get_session(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        # Add user message
        user_msg = SessionMessage(
            role="user",
            content=message,
            timestamp=datetime.utcnow(),
        )
        session.messages.append(user_msg)

        # Generate response (mock for now - will integrate with miu_core agent)
        response_text = await self._generate_response(session, message)

        # Add assistant message
        assistant_msg = SessionMessage(
            role="assistant",
            content=response_text,
            timestamp=datetime.utcnow(),
        )
        session.messages.append(assistant_msg)

        # Save session
        await self._session_manager.update_session(session)

        return response_text, session

    async def chat_stream(self, session_id: str, message: str) -> AsyncIterator[StreamChunk]:
        """Send a message and stream response.

        Args:
            session_id: Session ID (UUID format)
            message: User message

        Yields:
            StreamChunk objects with response text

        Raises:
            ValueError: If session not found or invalid ID
        """
        session = await self._session_manager.get_session(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        # Add user message
        user_msg = SessionMessage(
            role="user",
            content=message,
            timestamp=datetime.utcnow(),
        )
        session.messages.append(user_msg)

        # Generate and stream response
        full_response = ""
        async for chunk in self._generate_response_stream(session, message):
            full_response += chunk
            yield StreamChunk(type="chunk", content=chunk)

        # Add assistant message
        assistant_msg = SessionMessage(
            role="assistant",
            content=full_response,
            timestamp=datetime.utcnow(),
        )
        session.messages.append(assistant_msg)

        # Save session
        await self._session_manager.update_session(session)

        yield StreamChunk(type="done", content="")

    async def _generate_response(self, session: Session, message: str) -> str:
        """Generate response for message.

        TODO: Integrate with miu_core ReActAgent when available.
        For now, returns echo response for testing.
        """
        # Mock response for MVP testing
        # In production: use miu_core agent
        return f"Echo from session '{session.name or session.id[:8]}': {message}"

    async def _generate_response_stream(self, session: Session, message: str) -> AsyncIterator[str]:
        """Generate streaming response for message.

        TODO: Integrate with miu_core streaming when available.
        For now, yields words as chunks for testing.
        """
        # Mock streaming for MVP testing
        response = f"Streaming from '{session.name or session.id[:8]}': {message}"
        words = response.split()
        for word in words:
            yield word + " "


def get_chat_service() -> ChatService:
    """Dependency injection for ChatService."""
    return ChatService()
