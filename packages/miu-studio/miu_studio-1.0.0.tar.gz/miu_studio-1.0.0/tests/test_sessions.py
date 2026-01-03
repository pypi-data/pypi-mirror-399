"""Tests for session management API."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from miu_studio.main import create_app
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
def client(session_manager: SessionManager) -> TestClient:
    """Create test client with injected session manager."""
    with patch("miu_studio.api.routes.sessions._session_manager", session_manager):
        app = create_app()
        yield TestClient(app)


def test_list_sessions_empty(client: TestClient) -> None:
    """Test listing sessions when empty."""
    response = client.get("/api/v1/sessions/")
    assert response.status_code == 200
    assert response.json() == []


def test_create_session(client: TestClient) -> None:
    """Test creating a session."""
    response = client.post("/api/v1/sessions/")
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data
    assert data["messages"] == []


def test_create_session_with_name(client: TestClient) -> None:
    """Test creating a session with name."""
    response = client.post(
        "/api/v1/sessions/",
        json={"name": "Test Session"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Session"


def test_get_session(client: TestClient) -> None:
    """Test getting a session by ID."""
    # Create session
    create_response = client.post("/api/v1/sessions/")
    session_id = create_response.json()["id"]

    # Get session
    response = client.get(f"/api/v1/sessions/{session_id}")
    assert response.status_code == 200
    assert response.json()["id"] == session_id


def test_get_session_not_found(client: TestClient) -> None:
    """Test getting non-existent session with valid UUID format."""
    # Use valid UUID format that doesn't exist
    response = client.get("/api/v1/sessions/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found"


def test_get_session_invalid_id(client: TestClient) -> None:
    """Test getting session with invalid ID returns 400."""
    response = client.get("/api/v1/sessions/invalid-id")
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid session ID format"


def test_path_traversal_blocked(client: TestClient) -> None:
    """Test path traversal attack is blocked via UUID validation."""
    # UUID validation rejects any non-UUID strings, preventing path manipulation
    # Even if attacker provides malformed session IDs that look like paths
    malicious_ids = [
        "passwd",  # Simple file name
        "etc-passwd",  # Dashed attempt
        "a" * 36,  # Wrong format (not UUID)
        "00000000-0000-0000-0000-00000000000g",  # Invalid UUID char
    ]
    for malicious_id in malicious_ids:
        response = client.get(f"/api/v1/sessions/{malicious_id}")
        assert response.status_code == 400, f"Failed for: {malicious_id}"
        assert response.json()["detail"] == "Invalid session ID format"


def test_delete_session(client: TestClient) -> None:
    """Test deleting a session."""
    # Create session
    create_response = client.post("/api/v1/sessions/")
    session_id = create_response.json()["id"]

    # Delete session
    response = client.delete(f"/api/v1/sessions/{session_id}")
    assert response.status_code == 200
    assert response.json()["deleted"] == session_id

    # Verify deleted
    get_response = client.get(f"/api/v1/sessions/{session_id}")
    assert get_response.status_code == 404


def test_delete_session_not_found(client: TestClient) -> None:
    """Test deleting non-existent session with valid UUID format."""
    response = client.delete("/api/v1/sessions/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_delete_session_invalid_id(client: TestClient) -> None:
    """Test deleting session with invalid ID returns 400."""
    response = client.delete("/api/v1/sessions/invalid-id")
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid session ID format"


def test_list_sessions_with_data(client: TestClient) -> None:
    """Test listing sessions after creating some."""
    # Create sessions
    client.post("/api/v1/sessions/", json={"name": "Session 1"})
    client.post("/api/v1/sessions/", json={"name": "Session 2"})

    # List sessions
    response = client.get("/api/v1/sessions/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    # Should be sorted by updated_at descending
    assert data[0]["name"] == "Session 2"
    assert data[1]["name"] == "Session 1"
