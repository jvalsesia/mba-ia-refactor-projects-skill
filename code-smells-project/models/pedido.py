"""Pedido data access. Order listing uses batched queries (P-06, fixes AP-07):
a fixed number of queries regardless of how many orders/items exist, instead of
one query per item. The item-assembly logic is shared (P-07, fixes AP-08)."""
from config.constants import DISCOUNT_TIERS, STATUS_PENDENTE


class PedidoRepository:
    def __init__(self, db):
        self.db = db

    # ---- shared assembly (P-07) --------------------------------------------
    def _attach_itens(self, pedidos):
        """Given a list of pedido dicts, populate each one's `itens` with a
        fixed number of queries (no N+1)."""
        for pedido in pedidos:
            pedido["itens"] = []
        if not pedidos:
            return pedidos

        pedidos_por_id = {pedido["id"]: pedido for pedido in pedidos}
        pedido_ids = list(pedidos_por_id)
        cursor = self.db.cursor()

        # One query for every item across every order in this page.
        item_placeholders = ",".join("?" for _ in pedido_ids)
        cursor.execute(
            "SELECT * FROM itens_pedido WHERE pedido_id IN (%s) ORDER BY id"
            % item_placeholders,
            pedido_ids,
        )
        itens = cursor.fetchall()

        # One query for every product name referenced by those items.
        produto_ids = sorted({item["produto_id"] for item in itens})
        nomes_por_produto = {}
        if produto_ids:
            produto_placeholders = ",".join("?" for _ in produto_ids)
            cursor.execute(
                "SELECT id, nome FROM produtos WHERE id IN (%s)"
                % produto_placeholders,
                produto_ids,
            )
            nomes_por_produto = {row["id"]: row["nome"] for row in cursor.fetchall()}

        for item in itens:
            pedidos_por_id[item["pedido_id"]]["itens"].append({
                "produto_id": item["produto_id"],
                "produto_nome": nomes_por_produto.get(item["produto_id"], "Desconhecido"),
                "quantidade": item["quantidade"],
                "preco_unitario": item["preco_unitario"],
            })
        return pedidos

    def _pedido_dict(self, row):
        return {
            "id": row["id"],
            "usuario_id": row["usuario_id"],
            "status": row["status"],
            "total": row["total"],
            "criado_em": row["criado_em"],
        }

    # ---- reads -------------------------------------------------------------
    def get_by_usuario(self, usuario_id):
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM pedidos WHERE usuario_id = ?", (usuario_id,))
        pedidos = [self._pedido_dict(row) for row in cursor.fetchall()]
        return self._attach_itens(pedidos)

    def get_all(self):
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM pedidos")
        pedidos = [self._pedido_dict(row) for row in cursor.fetchall()]
        return self._attach_itens(pedidos)

    # ---- writes ------------------------------------------------------------
    def create(self, usuario_id, itens):
        cursor = self.db.cursor()

        # Batch-load every referenced product up front (P-06) instead of
        # querying inside the loop.
        produto_ids = [item["produto_id"] for item in itens]
        placeholders = ",".join("?" for _ in produto_ids)
        cursor.execute(
            "SELECT id, nome, preco, estoque FROM produtos WHERE id IN (%s)"
            % placeholders,
            produto_ids,
        )
        produtos = {row["id"]: row for row in cursor.fetchall()}

        total = 0
        for item in itens:
            produto = produtos.get(item["produto_id"])
            if produto is None:
                return {"erro": "Produto " + str(item["produto_id"]) + " não encontrado"}
            if produto["estoque"] < item["quantidade"]:
                return {"erro": "Estoque insuficiente para " + produto["nome"]}
            total = total + (produto["preco"] * item["quantidade"])

        cursor.execute(
            "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, ?, ?)",
            (usuario_id, STATUS_PENDENTE, total),
        )
        pedido_id = cursor.lastrowid

        for item in itens:
            produto = produtos[item["produto_id"]]
            cursor.execute(
                "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) "
                "VALUES (?, ?, ?, ?)",
                (pedido_id, item["produto_id"], item["quantidade"], produto["preco"]),
            )
            cursor.execute(
                "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
                (item["quantidade"], item["produto_id"]),
            )

        self.db.commit()
        return {"pedido_id": pedido_id, "total": total}

    def update_status(self, pedido_id, novo_status):
        cursor = self.db.cursor()
        cursor.execute(
            "UPDATE pedidos SET status = ? WHERE id = ?",
            (novo_status, pedido_id),
        )
        self.db.commit()
        return True

    # ---- reporting ---------------------------------------------------------
    def relatorio_vendas(self):
        cursor = self.db.cursor()

        cursor.execute("SELECT COUNT(*) FROM pedidos")
        total_pedidos = cursor.fetchone()[0]

        cursor.execute("SELECT SUM(total) FROM pedidos")
        faturamento = cursor.fetchone()[0] or 0

        cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'pendente'")
        pendentes = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'aprovado'")
        aprovados = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'cancelado'")
        cancelados = cursor.fetchone()[0]

        desconto = 0
        for threshold, rate in DISCOUNT_TIERS:
            if faturamento > threshold:
                desconto = faturamento * rate
                break

        return {
            "total_pedidos": total_pedidos,
            "faturamento_bruto": round(faturamento, 2),
            "desconto_aplicavel": round(desconto, 2),
            "faturamento_liquido": round(faturamento - desconto, 2),
            "pedidos_pendentes": pendentes,
            "pedidos_aprovados": aprovados,
            "pedidos_cancelados": cancelados,
            "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0,
        }
