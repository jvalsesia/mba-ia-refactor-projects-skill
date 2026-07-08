"""Named constants extracted from inline literals (P-10, fixes AP-10)."""

# Product validation bounds.
NOME_MIN_LENGTH = 2
NOME_MAX_LENGTH = 200
CATEGORIAS_VALIDAS = [
    "informatica", "moveis", "vestuario", "geral", "eletronicos", "livros",
]

# Order lifecycle.
STATUS_PENDENTE = "pendente"
STATUS_APROVADO = "aprovado"
STATUS_CANCELADO = "cancelado"
STATUS_VALIDOS = ["pendente", "aprovado", "enviado", "entregue", "cancelado"]

# Sales-report discount tiers: (faturamento threshold, discount rate).
# Evaluated high-to-low; the first threshold the revenue exceeds wins.
DISCOUNT_TIERS = [
    (10000, 0.10),
    (5000, 0.05),
    (1000, 0.02),
]
