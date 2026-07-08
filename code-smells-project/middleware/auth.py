"""Central admin-auth guard (P-08, fixes AP-03). Destructive/administrative
routes are wrapped with `require_admin` instead of being reachable anonymously."""
from functools import wraps
from flask import request

from middleware.errors import UnauthorizedError


def make_require_admin(admin_token):
    """Build a decorator that rejects requests lacking the admin bearer token.

    If no admin token is configured, access is denied outright — an
    unconfigured guard fails closed rather than open."""

    def require_admin(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            header = request.headers.get("Authorization", "")
            token = header[len("Bearer "):] if header.startswith("Bearer ") else ""
            if not admin_token or token != admin_token:
                raise UnauthorizedError("Não autorizado", status=401)
            return view(*args, **kwargs)
        return wrapper

    return require_admin
