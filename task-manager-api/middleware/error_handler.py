"""Layer 5 — Centralized error handling (P-09).

A single place that turns exceptions into consistent JSON responses. Route
handlers no longer wrap every body in try/except or format ad-hoc errors, and
unhandled exceptions never leak a stack trace to clients.
"""
from flask import jsonify

from database import db
from exceptions import ApiError


def register_error_handlers(app):
    @app.errorhandler(ApiError)
    def handle_api_error(error):
        db.session.rollback()
        return jsonify({'error': error.message}), error.status

    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({'error': 'Recurso não encontrado'}), 404

    @app.errorhandler(Exception)
    def handle_unexpected(error):
        # Roll back any half-open transaction and return a safe, generic message.
        db.session.rollback()
        return jsonify({'error': 'Erro interno'}), 500
