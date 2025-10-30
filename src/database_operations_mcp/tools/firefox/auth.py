"""Authentication and security utilities for Firefox bookmark tools."""

import hashlib
import hmac
import os
import time
from datetime import datetime, timedelta
from typing import Any

from . import mcp  # Import the mcp instance from __init__

# In-memory session store (use a proper database in production)
_sessions = {}
SECRET_KEY = os.getenv("FIREFOX_TOOLS_SECRET", "dev-secret-key-please-change")


def generate_session_id(username: str) -> str:
    """Generate a secure session ID with timestamp and signature."""
    timestamp = str(int(time.time()))
    signature = hmac.new(
        SECRET_KEY.encode(), f"{username}:{timestamp}".encode(), hashlib.sha256
    ).hexdigest()
    return f"{username}:{timestamp}:{signature}"


@mcp.tool()
async def create_session(username: str, password: str) -> dict[str, Any]:
    """Create a new authenticated session."""
    if not username or not password:
        return {"status": "error", "message": "Username and password required"}

    session_id = generate_session_id(username)
    _sessions[session_id] = {
        "username": username,
        "created_at": datetime.utcnow().isoformat(),
        "expires_at": (datetime.utcnow() + timedelta(days=1)).isoformat(),
    }

    return {
        "status": "success",
        "session_id": session_id,
        "expires_at": _sessions[session_id]["expires_at"],
    }


@mcp.tool
async def validate_session(session_id: str) -> dict[str, Any]:
    """Validate a session and return session data if valid."""
    if not session_id or session_id not in _sessions:
        return {"status": "error", "valid": False, "message": "Invalid session"}

    session = _sessions[session_id]
    if datetime.fromisoformat(session["expires_at"]) < datetime.utcnow():
        del _sessions[session_id]
        return {"status": "error", "valid": False, "message": "Session expired"}

    return {"status": "success", "valid": True, "session": session}
