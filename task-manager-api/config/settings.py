"""Layer 1 — Config.

All externalized configuration and secrets are read from environment variables
here (P-01). No literal secret or credential lives anywhere else in the source.
Non-sensitive local defaults (the dev SQLite path, SMTP host/port) are allowed;
secrets (SECRET_KEY, SMTP credentials) have no in-source default.
"""
import os

from dotenv import load_dotenv

# Load a local .env if present (never committed). See .env.example.
load_dotenv()

# --- Flask / app ---------------------------------------------------------
SECRET_KEY = os.environ.get("SECRET_KEY")  # no hardcoded default — supply via env
SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI", "sqlite:///tasks.db")
SQLALCHEMY_TRACK_MODIFICATIONS = False
DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() in ("1", "true", "yes")
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "5000"))

# --- Email / notifications ----------------------------------------------
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER")          # no hardcoded default
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")  # no hardcoded default
