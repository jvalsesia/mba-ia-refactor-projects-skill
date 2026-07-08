"""Pedido business logic (P-04). Side-effect notifications live here, not in
the routing layer."""
from config.constants import STATUS_VALIDOS, STATUS_APROVADO, STATUS_CANCELADO
from controllers.validation import require_data
from middleware.errors import ValidationError


class PedidoController:
    def __init__(self, repo):
        self.repo = repo

    def create(self, data):
        require_data(data)
        usuario_id = data.get("usuario_id")
        itens = data.get("itens", [])
        if not usuario_id:
            raise ValidationError("Usuario ID é obrigatório")
        if not itens or len(itens) == 0:
            raise ValidationError("Pedido deve ter pelo menos 1 item")

        resultado = self.repo.create(usuario_id, itens)
        if "erro" in resultado:
            raise ValidationError(resultado["erro"])

        self._notify_pedido_criado(resultado["pedido_id"], usuario_id)
        return {
            "dados": resultado,
            "sucesso": True,
            "mensagem": "Pedido criado com sucesso",
        }, 201

    def list_by_usuario(self, usuario_id):
        return {"dados": self.repo.get_by_usuario(usuario_id), "sucesso": True}, 200

    def list_all(self):
        return {"dados": self.repo.get_all(), "sucesso": True}, 200

    def update_status(self, pedido_id, data):
        novo_status = (data or {}).get("status", "")
        if novo_status not in STATUS_VALIDOS:
            raise ValidationError("Status inválido")

        self.repo.update_status(pedido_id, novo_status)
        self._notify_status(pedido_id, novo_status)
        return {"sucesso": True, "mensagem": "Status atualizado"}, 200

    def relatorio(self):
        return {"dados": self.repo.relatorio_vendas(), "sucesso": True}, 200

    # ---- notifications -----------------------------------------------------
    def _notify_pedido_criado(self, pedido_id, usuario_id):
        print("ENVIANDO EMAIL: Pedido " + str(pedido_id) + " criado para usuario " + str(usuario_id))
        print("ENVIANDO SMS: Seu pedido foi recebido!")
        print("ENVIANDO PUSH: Novo pedido recebido pelo sistema")

    def _notify_status(self, pedido_id, novo_status):
        if novo_status == STATUS_APROVADO:
            print("NOTIFICAÇÃO: Pedido " + str(pedido_id) + " foi aprovado! Preparar envio.")
        if novo_status == STATUS_CANCELADO:
            print("NOTIFICAÇÃO: Pedido " + str(pedido_id) + " cancelado. Devolver estoque.")
