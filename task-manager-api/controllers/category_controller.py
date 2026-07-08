"""Layer 4 — Category business logic (P-04)."""
from sqlalchemy import func

from database import db
from models.task import Task
from models.category import Category
from exceptions import ApiError
from config.constants import DEFAULT_CATEGORY_COLOR


def _require_category(cat_id):
    category = Category.query.get(cat_id)
    if not category:
        raise ApiError('Categoria não encontrada', 404)
    return category


def list_categories():
    categories = Category.query.all()
    # P-06: one grouped count instead of a count query per category.
    counts = dict(
        db.session.query(Task.category_id, func.count(Task.id))
        .group_by(Task.category_id)
        .all()
    )
    result = []
    for category in categories:
        data = category.to_dict()
        data['task_count'] = counts.get(category.id, 0)
        result.append(data)
    return result


def create_category(data):
    if not data:
        raise ApiError('Dados inválidos', 400)
    name = data.get('name')
    if not name:
        raise ApiError('Nome é obrigatório', 400)

    category = Category()
    category.name = name
    category.description = data.get('description', '')
    category.color = data.get('color', DEFAULT_CATEGORY_COLOR)

    db.session.add(category)
    db.session.commit()
    return category.to_dict()


def update_category(cat_id, data):
    category = _require_category(cat_id)
    data = data or {}
    if 'name' in data:
        category.name = data['name']
    if 'description' in data:
        category.description = data['description']
    if 'color' in data:
        category.color = data['color']

    db.session.commit()
    return category.to_dict()


def delete_category(cat_id):
    category = _require_category(cat_id)
    db.session.delete(category)
    db.session.commit()
    return {'message': 'Categoria deletada'}
