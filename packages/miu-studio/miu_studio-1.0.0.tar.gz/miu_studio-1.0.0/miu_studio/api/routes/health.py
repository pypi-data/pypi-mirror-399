"""Health check endpoints."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Check server health."""
    return {"status": "ok"}


@router.get("/ready")
async def readiness_check() -> dict[str, str]:
    """Check if server is ready to handle requests."""
    return {"status": "ready"}
