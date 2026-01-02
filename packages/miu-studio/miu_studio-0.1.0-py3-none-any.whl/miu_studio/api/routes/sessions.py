"""Session management API routes."""

from fastapi import APIRouter, HTTPException

from miu_studio.models.api import CreateSessionRequest, Session, SessionSummary
from miu_studio.services.session_manager import get_session_manager

router = APIRouter(tags=["sessions"])

_session_manager = get_session_manager()


@router.get("/", response_model=list[SessionSummary])
async def list_sessions() -> list[SessionSummary]:
    """List all sessions."""
    return await _session_manager.list_sessions()


@router.post("/", response_model=Session)
async def create_session(
    request: CreateSessionRequest | None = None,
) -> Session:
    """Create a new session."""
    return await _session_manager.create_session(request)


@router.get("/{session_id}", response_model=Session)
async def get_session(
    session_id: str,
) -> Session:
    """Get a session by ID."""
    try:
        session = await _session_manager.get_session(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format") from None
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.delete("/{session_id}")
async def delete_session(
    session_id: str,
) -> dict[str, str]:
    """Delete a session."""
    try:
        deleted = await _session_manager.delete_session(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format") from None
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"deleted": session_id}
