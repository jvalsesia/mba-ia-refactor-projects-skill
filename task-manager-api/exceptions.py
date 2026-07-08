"""Shared application exceptions.

Controllers raise ``ApiError`` for expected domain failures (validation, not
found, conflicts) and the centralized error handler (P-09) turns them into a
consistent JSON response. Handlers therefore never format their own errors.
"""


class ApiError(Exception):
    """An expected, client-facing error carrying an HTTP status and message."""

    def __init__(self, message, status=400):
        super().__init__(message)
        self.message = message
        self.status = status
