"""Layer 5 — Authentication mechanism (P-08).

Provides a single reusable ``require_auth`` decorator so authentication is
declared centrally rather than re-implemented per route. See the audit report
(AP-03): enforcing this decorator on the existing endpoints changes their
public contract (anonymous callers would receive 401), so wiring it onto routes
is intentionally left to a follow-up that also defines token issuance and the
client auth flow. The mechanism lives here, ready to adopt.
"""
from functools import wraps

from flask import request

from exceptions import ApiError


def valid_token(req):
    """Placeholder token validation — replace with real verification on adoption."""
    auth_header = req.headers.get('Authorization', '')
    return auth_header.startswith('Bearer ')


def require_auth(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not valid_token(request):
            raise ApiError('Autenticação necessária', 401)
        return fn(*args, **kwargs)

    return wrapper
