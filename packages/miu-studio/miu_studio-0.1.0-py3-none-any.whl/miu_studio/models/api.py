"""API models for miu-studio sessions and chat."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

# ============================================================================
# Chat Models
# ============================================================================


class ChatRequest(BaseModel):
    """Request for chat invoke/stream endpoints."""

    session_id: str = Field(description="Session ID (UUID format)")
    message: str = Field(description="User message to send")


class ChatResponse(BaseModel):
    """Response from chat invoke endpoint."""

    session_id: str
    response: str
    message_count: int


class StreamChunk(BaseModel):
    """Streaming chunk for SSE."""

    type: Literal["chunk", "done", "error"] = "chunk"
    content: str = ""


class WebSocketMessage(BaseModel):
    """WebSocket message format."""

    type: Literal["message", "chunk", "done", "error"]
    content: str = ""


# ============================================================================
# Session Models
# ============================================================================


class SessionMessage(BaseModel):
    """A message in a session."""

    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class CreateSessionRequest(BaseModel):
    """Request to create a new session."""

    name: str | None = Field(None, description="Optional session name")
    model: str | None = Field(None, description="Model to use (default from config)")
    system_prompt: str | None = Field(None, description="Custom system prompt")


class SessionSummary(BaseModel):
    """Summary of a session for listing."""

    id: str
    name: str | None = None
    created_at: datetime
    updated_at: datetime
    message_count: int = 0


class Session(BaseModel):
    """Full session with messages."""

    id: str
    name: str | None = None
    model: str
    system_prompt: str | None = None
    created_at: datetime
    updated_at: datetime
    messages: list[SessionMessage] = Field(default_factory=list)

    @property
    def message_count(self) -> int:
        """Get message count."""
        return len(self.messages)

    def to_summary(self) -> SessionSummary:
        """Convert to summary for listing."""
        return SessionSummary(
            id=self.id,
            name=self.name,
            created_at=self.created_at,
            updated_at=self.updated_at,
            message_count=self.message_count,
        )
