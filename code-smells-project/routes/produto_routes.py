"""Produto routes (Layer 3). Thin: parse request, call controller, return."""
from flask import Blueprint, request, jsonify


def make_produto_blueprint(controller):
    bp = Blueprint("produtos", __name__)

    @bp.get("/produtos")
    def listar_produtos():
        payload, status = controller.list()
        return jsonify(payload), status

    @bp.get("/produtos/busca")
    def buscar_produtos():
        payload, status = controller.search(
            request.args.get("q", ""),
            request.args.get("categoria", None),
            request.args.get("preco_min", None),
            request.args.get("preco_max", None),
        )
        return jsonify(payload), status

    @bp.get("/produtos/<int:produto_id>")
    def buscar_produto(produto_id):
        payload, status = controller.get(produto_id)
        return jsonify(payload), status

    @bp.post("/produtos")
    def criar_produto():
        payload, status = controller.create(request.get_json(silent=True))
        return jsonify(payload), status

    @bp.put("/produtos/<int:produto_id>")
    def atualizar_produto(produto_id):
        payload, status = controller.update(produto_id, request.get_json(silent=True))
        return jsonify(payload), status

    @bp.delete("/produtos/<int:produto_id>")
    def deletar_produto(produto_id):
        payload, status = controller.delete(produto_id)
        return jsonify(payload), status

    return bp
