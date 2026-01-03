"""Session management service for miu-studio."""

import json
import uuid
from datetime import datetime
from pathlib import Path

import aiofiles

from miu_studio.core.config import settings
from miu_studio.models.api import CreateSessionRequest, Session, SessionSummary


class SessionManager:
    """Manages session lifecycle and persistence."""

    def __init__(self, session_dir: str | None = None) -> None:
        """Initialize session manager.

        Args:
            session_dir: Directory for session storage. Defaults to config.
        """
        self._session_dir = Path(session_dir or settings.session_dir)
        self._session_dir.mkdir(parents=True, exist_ok=True)

    def _validate_session_id(self, session_id: str) -> bool:
        """Validate session ID is a valid UUID to prevent path traversal."""
        try:
            uuid.UUID(session_id)
            return True
        except ValueError:
            return False

    def _session_path(self, session_id: str) -> Path:
        """Get path to session file. Validates session_id first."""
        if not self._validate_session_id(session_id):
            raise ValueError(f"Invalid session ID: {session_id}")
        return self._session_dir / f"{session_id}.json"

    async def list_sessions(self) -> list[SessionSummary]:
        """List all sessions."""
        sessions = []
        for path in self._session_dir.glob("*.json"):
            try:
                async with aiofiles.open(path) as f:
                    data = json.loads(await f.read())
                    session = Session.model_validate(data)
                    sessions.append(session.to_summary())
            except (json.JSONDecodeError, ValueError):
                continue
        return sorted(sessions, key=lambda s: s.updated_at, reverse=True)

    async def create_session(self, request: CreateSessionRequest | None = None) -> Session:
        """Create a new session."""
        now = datetime.utcnow()
        session = Session(
            id=str(uuid.uuid4()),
            name=request.name if request else None,
            model=request.model if request and request.model else settings.default_model,
            system_prompt=request.system_prompt if request else None,
            created_at=now,
            updated_at=now,
            messages=[],
        )
        await self._save_session(session)
        return session

    async def get_session(self, session_id: str) -> Session | None:
        """Get a session by ID."""
        path = self._session_path(session_id)
        if not path.exists():
            return None
        try:
            async with aiofiles.open(path) as f:
                data = json.loads(await f.read())
                return Session.model_validate(data)
        except (json.JSONDecodeError, ValueError):
            return None

    async def update_session(self, session: Session) -> Session:
        """Update a session."""
        session.updated_at = datetime.utcnow()
        await self._save_session(session)
        return session

    async def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        path = self._session_path(session_id)
        if path.exists():
            path.unlink()
            return True
        return False

    async def _save_session(self, session: Session) -> None:
        """Save session to file."""
        path = self._session_path(session.id)
        async with aiofiles.open(path, "w") as f:
            await f.write(session.model_dump_json(indent=2))


def get_session_manager() -> SessionManager:
    """Dependency injection for SessionManager."""
    return SessionManager()
