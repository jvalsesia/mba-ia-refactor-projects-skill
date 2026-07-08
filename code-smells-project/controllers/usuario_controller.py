"""Usuario business logic (P-04). Passwords are never echoed back."""
from controllers.validation import require_data
from middleware.errors import ValidationError, NotFoundError, UnauthorizedError


class UsuarioController:
    def __init__(self, repo):
        self.repo = repo

    def list(self):
        return {"dados": self.repo.get_all(), "sucesso": True}, 200

    def get(self, usuario_id):
        usuario = self.repo.get_by_id(usuario_id)
        if not usuario:
            raise NotFoundError("Usuário não encontrado")
        return {"dados": usuario, "sucesso": True}, 200

    def create(self, data):
        require_data(data)
        nome = data.get("nome", "")
        email = data.get("email", "")
        senha = data.get("senha", "")
        if not nome or not email or not senha:
            raise ValidationError("Nome, email e senha são obrigatórios")

        usuario_id = self.repo.create(nome, email, senha)
        print("Usuário criado: " + email)
        return {"dados": {"id": usuario_id}, "sucesso": True}, 201

    def login(self, data):
        require_data(data)
        email = data.get("email", "")
        senha = data.get("senha", "")
        if not email or not senha:
            raise ValidationError("Email e senha são obrigatórios")

        usuario = self.repo.authenticate(email, senha)
        if not usuario:
            print("Login falhou: " + email)
            raise UnauthorizedError("Email ou senha inválidos", status=401)

        print("Login bem-sucedido: " + email)
        return {"dados": usuario, "sucesso": True, "mensagem": "Login OK"}, 200
