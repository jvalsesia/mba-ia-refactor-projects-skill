"""Layer 1 — Config. All environment-specific values and secrets are read from
the environment here (P-01). No secret or environment-specific literal appears
anywhere else in the codebase."""
import os


def _as_bool(value, default=False):
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


# Secrets / security — never hardcoded, never returned to clients.
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-insecure-change-me")
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "")

# Runtime / server.
DEBUG = _as_bool(os.environ.get("DEBUG"), default=False)
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "5000"))
ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")

# Persistence.
DATABASE_PATH = os.environ.get("DATABASE_PATH", "loja.db")

# Static metadata.
APP_VERSION = "1.0.0"
