"""System + admin routes (Layer 3). Admin routes are wrapped with the
auth guard (P-08)."""
from flask import Blueprint, request, jsonify


def make_system_blueprint(controller, require_admin):
    bp = Blueprint("system", __name__)

    @bp.get("/")
    def index():
        payload, status = controller.index()
        return jsonify(payload), status

    @bp.get("/health")
    def health_check():
        payload, status = controller.health()
        return jsonify(payload), status

    @bp.post("/admin/reset-db")
    @require_admin
    def reset_database():
        payload, status = controller.reset_db()
        return jsonify(payload), status

    @bp.post("/admin/query")
    @require_admin
    def executar_query():
        data = request.get_json(silent=True) or {}
        payload, status = controller.admin_query(data.get("sql", ""))
        return jsonify(payload), status

    return bp
