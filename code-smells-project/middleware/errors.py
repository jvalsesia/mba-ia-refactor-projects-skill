"""Domain error types + a single centralized error handler (P-09, fixes
AP-09). Handlers raise these; the registered handler formats every error
consistently and never leaks a stack trace or raw exception text to clients."""
from flask import jsonify


class AppError(Exception):
    """Base for expected, client-safe errors."""
    status = 400

    def __init__(self, public_message, status=None):
        super().__init__(public_message)
        self.public_message = public_message
        if status is not None:
            self.status = status


class ValidationError(AppError):
    status = 400


class NotFoundError(AppError):
    status = 404


class UnauthorizedError(AppError):
    status = 401


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def _handle_app_error(error):
        return jsonify({"erro": error.public_message, "sucesso": False}), error.status

    @app.errorhandler(Exception)
    def _handle_unexpected(error):
        # Never surface internals; log server-side, return a safe envelope.
        app.logger.exception("Erro não tratado")
        return jsonify({"erro": "Erro interno do servidor", "sucesso": False}), 500
