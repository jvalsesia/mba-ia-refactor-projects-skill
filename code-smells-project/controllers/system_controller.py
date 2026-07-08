"""System / admin business logic. /health no longer leaks the secret key
(fixes AP-01); admin actions are exposed only through auth-guarded routes."""
from config import settings
from controllers.validation import require_data
from middleware.errors import ValidationError


class SystemController:
    def __init__(self, repo):
        self.repo = repo

    def index(self):
        return {
            "mensagem": "Bem-vindo à API da Loja",
            "versao": settings.APP_VERSION,
            "endpoints": {
                "produtos": "/produtos",
                "usuarios": "/usuarios",
                "pedidos": "/pedidos",
                "login": "/login",
                "relatorios": "/relatorios/vendas",
                "health": "/health",
            },
        }, 200

    def health(self):
        counts = self.repo.health_counts()
        return {
            "status": "ok",
            "database": "connected",
            "counts": counts,
            "versao": settings.APP_VERSION,
            "ambiente": settings.ENVIRONMENT,
            "db_path": settings.DATABASE_PATH,
            "debug": settings.DEBUG,
        }, 200

    def reset_db(self):
        self.repo.reset_all()
        print("!!! BANCO DE DADOS RESETADO !!!")
        return {"mensagem": "Banco de dados resetado", "sucesso": True}, 200

    def admin_query(self, sql):
        if not sql:
            raise ValidationError("Query não informada")
        result = self.repo.run_admin_query(sql)
        if result["select"]:
            return {"dados": result["rows"], "sucesso": True}, 200
        return {"mensagem": "Query executada", "sucesso": True}, 200
