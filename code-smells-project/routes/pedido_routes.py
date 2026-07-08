"""Pedido routes (Layer 3)."""
from flask import Blueprint, request, jsonify


def make_pedido_blueprint(controller):
    bp = Blueprint("pedidos", __name__)

    @bp.post("/pedidos")
    def criar_pedido():
        payload, status = controller.create(request.get_json(silent=True))
        return jsonify(payload), status

    @bp.get("/pedidos")
    def listar_todos_pedidos():
        payload, status = controller.list_all()
        return jsonify(payload), status

    @bp.get("/pedidos/usuario/<int:usuario_id>")
    def listar_pedidos_usuario(usuario_id):
        payload, status = controller.list_by_usuario(usuario_id)
        return jsonify(payload), status

    @bp.put("/pedidos/<int:pedido_id>/status")
    def atualizar_status_pedido(pedido_id):
        payload, status = controller.update_status(pedido_id, request.get_json(silent=True))
        return jsonify(payload), status

    return bp
