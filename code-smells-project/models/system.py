"""System / admin data access — health counts, DB reset, and the guarded
admin query utility. Table names below are fixed internal identifiers, never
request input."""

_COUNT_TABLES = ("produtos", "usuarios", "pedidos")
_RESET_TABLES = ("itens_pedido", "pedidos", "produtos", "usuarios")


class SystemRepository:
    def __init__(self, db):
        self.db = db

    def health_counts(self):
        cursor = self.db.cursor()
        cursor.execute("SELECT 1")
        counts = {}
        for table in _COUNT_TABLES:
            cursor.execute("SELECT COUNT(*) FROM " + table)
            counts[table] = cursor.fetchone()[0]
        return counts

    def reset_all(self):
        cursor = self.db.cursor()
        for table in _RESET_TABLES:
            cursor.execute("DELETE FROM " + table)
        self.db.commit()

    def run_admin_query(self, sql):
        """Execute an admin-supplied statement. Reachable only behind the
        admin-auth guard (P-08)."""
        cursor = self.db.cursor()
        cursor.execute(sql)
        if sql.strip().upper().startswith("SELECT"):
            rows = cursor.fetchall()
            return {"select": True, "rows": [dict(row) for row in rows]}
        self.db.commit()
        return {"select": False, "rows": None}
