"""Shared validation helpers (P-07, fixes AP-08). Raise ValidationError so the
central error handler formats the response consistently."""
from middleware.errors import ValidationError


def require_data(data):
    if not data:
        raise ValidationError("Dados inválidos")


def require_fields(data, field_messages):
    """field_messages: list of (field_name, error_message)."""
    for field, message in field_messages:
        if field not in data:
            raise ValidationError(message)


def require_non_negative(preco, estoque):
    if preco < 0:
        raise ValidationError("Preço não pode ser negativo")
    if estoque < 0:
        raise ValidationError("Estoque não pode ser negativo")
