"""Chat API routes for miu-studio."""

import uuid
from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse

from miu_studio.models.api import ChatRequest, ChatResponse, StreamChunk
from miu_studio.services.chat_service import get_chat_service

if TYPE_CHECKING:
    pass

router = APIRouter(tags=["chat"])

_chat_service = get_chat_service()

# Security: Max message size to prevent DoS (64KB)
MAX_MESSAGE_SIZE = 64 * 1024


def _validate_session_id(session_id: str) -> None:
    """Validate session ID is a valid UUID."""
    try:
        uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format") from None


@router.post("/invoke", response_model=ChatResponse)
async def invoke(request: ChatRequest) -> ChatResponse:
    """Synchronous chat - returns full response."""
    _validate_session_id(request.session_id)

    try:
        response_text, session = await _chat_service.chat(request.session_id, request.message)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from None

    return ChatResponse(
        session_id=session.id,
        response=response_text,
        message_count=session.message_count,
    )


@router.post("/stream")
async def stream(request: ChatRequest) -> StreamingResponse:
    """Server-Sent Events streaming chat."""
    _validate_session_id(request.session_id)

    async def generate() -> AsyncGenerator[bytes, None]:
        try:
            async for chunk in _chat_service.chat_stream(request.session_id, request.message):
                yield f"data: {chunk.model_dump_json()}\n\n".encode()
        except ValueError as e:
            error_chunk = StreamChunk(type="error", content=str(e))
            yield f"data: {error_chunk.model_dump_json()}\n\n".encode()

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@router.websocket("/ws/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str) -> None:
    """WebSocket for real-time chat."""
    # Validate session ID
    try:
        uuid.UUID(session_id)
    except ValueError:
        await websocket.close(code=4000, reason="Invalid session ID format")
        return

    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_json()
            message = data.get("message", "")

            if not message:
                await websocket.send_json(
                    {
                        "type": "error",
                        "content": "Message is required",
                    }
                )
                continue

            # Security: Check message size to prevent DoS
            if len(message) > MAX_MESSAGE_SIZE:
                await websocket.send_json(
                    {
                        "type": "error",
                        "content": "Message too large (max 64KB)",
                    }
                )
                continue

            try:
                async for chunk in _chat_service.chat_stream(session_id, message):
                    await websocket.send_json(
                        {
                            "type": chunk.type,
                            "content": chunk.content,
                        }
                    )
            except ValueError as e:
                await websocket.send_json(
                    {
                        "type": "error",
                        "content": str(e),
                    }
                )

    except WebSocketDisconnect:
        pass  # Client disconnected normally
