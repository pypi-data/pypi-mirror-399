"""Tests for chat API endpoints."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from miu_studio.main import create_app
from miu_studio.services.chat_service import ChatService
from miu_studio.services.session_manager import SessionManager


@pytest.fixture
def temp_session_dir() -> Path:
    """Create temporary directory for sessions."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def session_manager(temp_session_dir: Path) -> SessionManager:
    """Create session manager with temp directory."""
    return SessionManager(session_dir=str(temp_session_dir))


@pytest.fixture
def chat_service(session_manager: SessionManager) -> ChatService:
    """Create chat service with test session manager."""
    return ChatService(session_manager=session_manager)


@pytest.fixture
def client(session_manager: SessionManager, chat_service: ChatService) -> TestClient:
    """Create test client with injected services."""
    with (
        patch("miu_studio.api.routes.sessions._session_manager", session_manager),
        patch("miu_studio.api.routes.chat._chat_service", chat_service),
    ):
        app = create_app()
        yield TestClient(app)


@pytest.fixture
def session_id(client: TestClient) -> str:
    """Create a session and return its ID."""
    response = client.post("/api/v1/sessions/", json={"name": "Test Chat"})
    return response.json()["id"]


# ============================================================================
# Chat Invoke Tests
# ============================================================================


def test_chat_invoke_success(client: TestClient, session_id: str) -> None:
    """Test successful chat invoke."""
    response = client.post(
        "/api/v1/chat/invoke",
        json={"session_id": session_id, "message": "Hello, world!"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == session_id
    assert "Hello, world!" in data["response"]
    assert data["message_count"] == 2  # user + assistant


def test_chat_invoke_invalid_session_id(client: TestClient) -> None:
    """Test chat invoke with invalid session ID format."""
    response = client.post(
        "/api/v1/chat/invoke",
        json={"session_id": "invalid-id", "message": "Hello"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid session ID format"


def test_chat_invoke_session_not_found(client: TestClient) -> None:
    """Test chat invoke with non-existent session."""
    response = client.post(
        "/api/v1/chat/invoke",
        json={
            "session_id": "00000000-0000-0000-0000-000000000000",
            "message": "Hello",
        },
    )
    assert response.status_code == 404


def test_chat_invoke_multiple_messages(client: TestClient, session_id: str) -> None:
    """Test multiple messages accumulate in session."""
    # First message
    response1 = client.post(
        "/api/v1/chat/invoke",
        json={"session_id": session_id, "message": "First"},
    )
    assert response1.json()["message_count"] == 2

    # Second message
    response2 = client.post(
        "/api/v1/chat/invoke",
        json={"session_id": session_id, "message": "Second"},
    )
    assert response2.json()["message_count"] == 4  # 2 + 2


# ============================================================================
# Chat Stream Tests
# ============================================================================


def test_chat_stream_success(client: TestClient, session_id: str) -> None:
    """Test successful chat stream."""
    response = client.post(
        "/api/v1/chat/stream",
        json={"session_id": session_id, "message": "Hello, stream!"},
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/event-stream; charset=utf-8"

    # Check we got data
    content = response.text
    assert "data:" in content
    assert '"type": "chunk"' in content or '"type":"chunk"' in content
    assert '"type": "done"' in content or '"type":"done"' in content


def test_chat_stream_invalid_session_id(client: TestClient) -> None:
    """Test chat stream with invalid session ID format."""
    response = client.post(
        "/api/v1/chat/stream",
        json={"session_id": "invalid-id", "message": "Hello"},
    )
    assert response.status_code == 400


# ============================================================================
# WebSocket Tests
# ============================================================================


def test_websocket_chat_success(client: TestClient, session_id: str) -> None:
    """Test successful WebSocket chat."""
    with client.websocket_connect(f"/api/v1/chat/ws/{session_id}") as websocket:
        # Send message
        websocket.send_json({"message": "Hello WebSocket!"})

        # Receive chunks
        messages = []
        while True:
            data = websocket.receive_json()
            messages.append(data)
            if data["type"] == "done":
                break

        # Verify we got chunks and done
        assert len(messages) >= 1
        assert messages[-1]["type"] == "done"
        chunk_messages = [m for m in messages if m["type"] == "chunk"]
        assert len(chunk_messages) > 0


def test_websocket_invalid_session_id(client: TestClient) -> None:
    """Test WebSocket with invalid session ID."""
    from starlette.websockets import WebSocketDisconnect

    with pytest.raises(WebSocketDisconnect):  # WebSocket close exception
        with client.websocket_connect("/api/v1/chat/ws/invalid-id") as websocket:
            websocket.receive_json()


def test_websocket_empty_message(client: TestClient, session_id: str) -> None:
    """Test WebSocket with empty message."""
    with client.websocket_connect(f"/api/v1/chat/ws/{session_id}") as websocket:
        # Send empty message
        websocket.send_json({"message": ""})

        # Should get error
        data = websocket.receive_json()
        assert data["type"] == "error"
        assert "required" in data["content"].lower()


def test_websocket_session_not_found(client: TestClient) -> None:
    """Test WebSocket with non-existent session."""
    fake_uuid = "00000000-0000-0000-0000-000000000000"
    with client.websocket_connect(f"/api/v1/chat/ws/{fake_uuid}") as websocket:
        websocket.send_json({"message": "Hello"})
        data = websocket.receive_json()
        assert data["type"] == "error"


def test_websocket_message_too_large(client: TestClient, session_id: str) -> None:
    """Test WebSocket rejects oversized messages."""
    with client.websocket_connect(f"/api/v1/chat/ws/{session_id}") as websocket:
        # Send message larger than 64KB limit
        large_message = "x" * (64 * 1024 + 1)
        websocket.send_json({"message": large_message})

        # Should get error
        data = websocket.receive_json()
        assert data["type"] == "error"
        assert "too large" in data["content"].lower()
