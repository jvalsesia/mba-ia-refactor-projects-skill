"""Relatório routes (Layer 3)."""
from flask import Blueprint, jsonify


def make_relatorio_blueprint(controller):
    bp = Blueprint("relatorios", __name__)

    @bp.get("/relatorios/vendas")
    def relatorio_vendas():
        payload, status = controller.relatorio()
        return jsonify(payload), status

    return bp
