"""Produto business logic (P-04, fixes AP-05). Framework-decoupled: receives
plain data, returns (payload, status), raises domain errors."""
from config.constants import NOME_MIN_LENGTH, NOME_MAX_LENGTH, CATEGORIAS_VALIDAS
from controllers.validation import require_data, require_fields, require_non_negative
from middleware.errors import ValidationError, NotFoundError

_PRODUTO_FIELDS = [
    ("nome", "Nome é obrigatório"),
    ("preco", "Preço é obrigatório"),
    ("estoque", "Estoque é obrigatório"),
]


class ProdutoController:
    def __init__(self, repo):
        self.repo = repo

    def list(self):
        produtos = self.repo.get_all()
        print("Listando " + str(len(produtos)) + " produtos")
        return {"dados": produtos, "sucesso": True}, 200

    def get(self, produto_id):
        produto = self.repo.get_by_id(produto_id)
        if not produto:
            raise NotFoundError("Produto não encontrado")
        return {"dados": produto, "sucesso": True}, 200

    def create(self, data):
        require_data(data)
        require_fields(data, _PRODUTO_FIELDS)

        nome = data["nome"]
        descricao = data.get("descricao", "")
        preco = data["preco"]
        estoque = data["estoque"]
        categoria = data.get("categoria", "geral")

        require_non_negative(preco, estoque)
        if len(nome) < NOME_MIN_LENGTH:
            raise ValidationError("Nome muito curto")
        if len(nome) > NOME_MAX_LENGTH:
            raise ValidationError("Nome muito longo")
        if categoria not in CATEGORIAS_VALIDAS:
            raise ValidationError("Categoria inválida. Válidas: " + str(CATEGORIAS_VALIDAS))

        produto_id = self.repo.create(nome, descricao, preco, estoque, categoria)
        print("Produto criado com ID: " + str(produto_id))
        return {"dados": {"id": produto_id}, "sucesso": True, "mensagem": "Produto criado"}, 201

    def update(self, produto_id, data):
        if not self.repo.get_by_id(produto_id):
            raise NotFoundError("Produto não encontrado")

        require_data(data)
        require_fields(data, _PRODUTO_FIELDS)

        nome = data["nome"]
        descricao = data.get("descricao", "")
        preco = data["preco"]
        estoque = data["estoque"]
        categoria = data.get("categoria", "geral")

        require_non_negative(preco, estoque)

        self.repo.update(produto_id, nome, descricao, preco, estoque, categoria)
        return {"sucesso": True, "mensagem": "Produto atualizado"}, 200

    def delete(self, produto_id):
        if not self.repo.get_by_id(produto_id):
            raise NotFoundError("Produto não encontrado")
        self.repo.delete(produto_id)
        print("Produto " + str(produto_id) + " deletado")
        return {"sucesso": True, "mensagem": "Produto deletado"}, 200

    def search(self, termo, categoria, preco_min, preco_max):
        preco_min = float(preco_min) if preco_min else None
        preco_max = float(preco_max) if preco_max else None
        resultados = self.repo.search(termo, categoria, preco_min, preco_max)
        return {"dados": resultados, "total": len(resultados), "sucesso": True}, 200
