import os
import secrets
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def _flag(name, default="0"):
    return os.environ.get(name, default).strip().lower() in ("1", "true", "yes", "on")


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    DATABASE = os.environ.get("DATABASE_PATH", str(BASE_DIR / "instance" / "legal_assistant.db"))

    # First admin account, created on startup if it does not exist yet (FR-04).
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")
    ADMIN_NAME = os.environ.get("ADMIN_NAME", "Administrator")

    # AI summaries are optional: without a key the app answers from the knowledge base.
    AI_ENABLED = _flag("AI_ENABLED", "1") and bool(os.environ.get("ANTHROPIC_API_KEY"))
    AI_MODEL = os.environ.get("AI_MODEL", "claude-opus-5-5")
    AI_TIMEOUT_SECONDS = float(os.environ.get("AI_TIMEOUT_SECONDS", "30"))

    # Production (NFR-10): redirect HTTP to HTTPS and send cookies only over HTTPS.
    FORCE_HTTPS = _flag("FORCE_HTTPS")
    SESSION_COOKIE_SECURE = FORCE_HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    MAX_QUERY_LENGTH = 2000
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024
