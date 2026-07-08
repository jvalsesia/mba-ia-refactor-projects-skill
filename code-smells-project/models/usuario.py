"""Usuario data access. Queries are parameterized (P-02). API serialization
never includes the `senha` column (fixes the AP-03 password exposure); the
raw password is only ever touched inside `authenticate`."""


def _public_dict(row):
    # Note: `senha` is deliberately excluded from any client-facing payload.
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "tipo": row["tipo"],
        "criado_em": row["criado_em"],
    }


class UsuarioRepository:
    def __init__(self, db):
        self.db = db

    def get_all(self):
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM usuarios")
        return [_public_dict(row) for row in cursor.fetchall()]

    def get_by_id(self, usuario_id):
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,))
        row = cursor.fetchone()
        return _public_dict(row) if row else None

    def create(self, nome, email, senha, tipo="cliente"):
        cursor = self.db.cursor()
        cursor.execute(
            "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
            (nome, email, senha, tipo),
        )
        self.db.commit()
        return cursor.lastrowid

    def authenticate(self, email, senha):
        cursor = self.db.cursor()
        cursor.execute(
            "SELECT * FROM usuarios WHERE email = ? AND senha = ?",
            (email, senha),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return {
            "id": row["id"],
            "nome": row["nome"],
            "email": row["email"],
            "tipo": row["tipo"],
        }
