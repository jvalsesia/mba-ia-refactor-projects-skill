"""Usuario + auth routes (Layer 3)."""
from flask import Blueprint, request, jsonify


def make_usuario_blueprint(controller):
    bp = Blueprint("usuarios", __name__)

    @bp.get("/usuarios")
    def listar_usuarios():
        payload, status = controller.list()
        return jsonify(payload), status

    @bp.get("/usuarios/<int:usuario_id>")
    def buscar_usuario(usuario_id):
        payload, status = controller.get(usuario_id)
        return jsonify(payload), status

    @bp.post("/usuarios")
    def criar_usuario():
        payload, status = controller.create(request.get_json(silent=True))
        return jsonify(payload), status

    @bp.post("/login")
    def login():
        payload, status = controller.login(request.get_json(silent=True))
        return jsonify(payload), status

    return bp
