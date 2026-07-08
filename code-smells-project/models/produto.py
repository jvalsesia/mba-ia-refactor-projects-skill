"""Produto data access. All queries are parameterized (P-02, fixes AP-02);
this repository owns every produtos query (no SQL leaks into routes)."""

PRODUTO_COLUMNS = (
    "id", "nome", "descricao", "preco", "estoque", "categoria", "ativo", "criado_em",
)


def _to_dict(row):
    return {column: row[column] for column in PRODUTO_COLUMNS}


class ProdutoRepository:
    def __init__(self, db):
        self.db = db

    def get_all(self):
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM produtos")
        return [_to_dict(row) for row in cursor.fetchall()]

    def get_by_id(self, produto_id):
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))
        row = cursor.fetchone()
        return _to_dict(row) if row else None

    def create(self, nome, descricao, preco, estoque, categoria):
        cursor = self.db.cursor()
        cursor.execute(
            "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) "
            "VALUES (?, ?, ?, ?, ?)",
            (nome, descricao, preco, estoque, categoria),
        )
        self.db.commit()
        return cursor.lastrowid

    def update(self, produto_id, nome, descricao, preco, estoque, categoria):
        cursor = self.db.cursor()
        cursor.execute(
            "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, "
            "estoque = ?, categoria = ? WHERE id = ?",
            (nome, descricao, preco, estoque, categoria, produto_id),
        )
        self.db.commit()
        return True

    def delete(self, produto_id):
        cursor = self.db.cursor()
        cursor.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
        self.db.commit()
        return True

    def search(self, termo, categoria=None, preco_min=None, preco_max=None):
        clauses = ["1=1"]
        params = []
        if termo:
            clauses.append("(nome LIKE ? OR descricao LIKE ?)")
            like = "%" + termo + "%"
            params.extend([like, like])
        if categoria:
            clauses.append("categoria = ?")
            params.append(categoria)
        if preco_min:
            clauses.append("preco >= ?")
            params.append(preco_min)
        if preco_max:
            clauses.append("preco <= ?")
            params.append(preco_max)

        query = "SELECT * FROM produtos WHERE " + " AND ".join(clauses)
        cursor = self.db.cursor()
        cursor.execute(query, params)
        return [_to_dict(row) for row in cursor.fetchall()]
