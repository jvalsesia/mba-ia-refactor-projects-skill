"""Layer 4 — Task business logic (P-04).

All validation, orchestration and response shaping for tasks lives here,
decoupled from the Flask request/response objects. Routes stay thin.
"""
from datetime import datetime

from database import db
from models.task import Task
from models.user import User
from models.category import Category
from exceptions import ApiError
from utils.timeutils import now_utc, is_overdue
from config.constants import (
    VALID_TASK_STATUSES,
    DEFAULT_TASK_STATUS,
    DEFAULT_PRIORITY,
    MIN_PRIORITY,
    MAX_PRIORITY,
    MIN_TITLE_LENGTH,
    MAX_TITLE_LENGTH,
    TERMINAL_STATUSES,
)

DATE_FORMAT = '%Y-%m-%d'


def _user_name_map():
    return {user.id: user.name for user in User.query.all()}


def _category_name_map():
    return {category.id: category.name for category in Category.query.all()}


def _serialize_with_context(task, user_names, category_names):
    data = task.to_dict()
    data['overdue'] = is_overdue(task.due_date, task.status)
    data['user_name'] = user_names.get(task.user_id)
    data['category_name'] = category_names.get(task.category_id)
    return data


def _validate_title(title):
    if len(title) < MIN_TITLE_LENGTH:
        raise ApiError('Título muito curto', 400)
    if len(title) > MAX_TITLE_LENGTH:
        raise ApiError('Título muito longo', 400)


def _parse_due_date(value):
    try:
        return datetime.strptime(value, DATE_FORMAT)
    except (ValueError, TypeError):
        raise ApiError('Formato de data inválido. Use YYYY-MM-DD', 400)


def _normalize_tags(tags):
    return ','.join(tags) if isinstance(tags, list) else tags


def list_tasks():
    # P-06: fetch users/categories once instead of a query per task (no N+1).
    tasks = Task.query.all()
    user_names = _user_name_map()
    category_names = _category_name_map()
    return [_serialize_with_context(t, user_names, category_names) for t in tasks]


def get_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        raise ApiError('Task não encontrada', 404)
    data = task.to_dict()
    data['overdue'] = is_overdue(task.due_date, task.status)
    return data


def create_task(data):
    if not data:
        raise ApiError('Dados inválidos', 400)

    title = data.get('title')
    if not title:
        raise ApiError('Título é obrigatório', 400)
    _validate_title(title)

    status = data.get('status', DEFAULT_TASK_STATUS)
    if status not in VALID_TASK_STATUSES:
        raise ApiError('Status inválido', 400)

    priority = data.get('priority', DEFAULT_PRIORITY)
    if priority < MIN_PRIORITY or priority > MAX_PRIORITY:
        raise ApiError('Prioridade deve ser entre 1 e 5', 400)

    user_id = data.get('user_id')
    if user_id and not User.query.get(user_id):
        raise ApiError('Usuário não encontrado', 404)

    category_id = data.get('category_id')
    if category_id and not Category.query.get(category_id):
        raise ApiError('Categoria não encontrada', 404)

    task = Task()
    task.title = title
    task.description = data.get('description', '')
    task.status = status
    task.priority = priority
    task.user_id = user_id
    task.category_id = category_id

    due_date = data.get('due_date')
    if due_date:
        task.due_date = _parse_due_date(due_date)

    tags = data.get('tags')
    if tags:
        task.tags = _normalize_tags(tags)

    db.session.add(task)
    db.session.commit()
    return task.to_dict()


def update_task(task_id, data):
    task = Task.query.get(task_id)
    if not task:
        raise ApiError('Task não encontrada', 404)
    if not data:
        raise ApiError('Dados inválidos', 400)

    if 'title' in data:
        _validate_title(data['title'])
        task.title = data['title']

    if 'description' in data:
        task.description = data['description']

    if 'status' in data:
        if data['status'] not in VALID_TASK_STATUSES:
            raise ApiError('Status inválido', 400)
        task.status = data['status']

    if 'priority' in data:
        if data['priority'] < MIN_PRIORITY or data['priority'] > MAX_PRIORITY:
            raise ApiError('Prioridade deve ser entre 1 e 5', 400)
        task.priority = data['priority']

    if 'user_id' in data:
        if data['user_id'] and not User.query.get(data['user_id']):
            raise ApiError('Usuário não encontrado', 404)
        task.user_id = data['user_id']

    if 'category_id' in data:
        if data['category_id'] and not Category.query.get(data['category_id']):
            raise ApiError('Categoria não encontrada', 404)
        task.category_id = data['category_id']

    if 'due_date' in data:
        task.due_date = _parse_due_date(data['due_date']) if data['due_date'] else None

    if 'tags' in data:
        task.tags = _normalize_tags(data['tags'])

    task.updated_at = now_utc()
    db.session.commit()
    return task.to_dict()


def delete_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        raise ApiError('Task não encontrada', 404)
    db.session.delete(task)
    db.session.commit()
    return {'message': 'Task deletada com sucesso'}


def search_tasks(query='', status='', priority='', user_id=''):
    tasks = Task.query
    if query:
        tasks = tasks.filter(
            db.or_(
                Task.title.like(f'%{query}%'),
                Task.description.like(f'%{query}%'),
            )
        )
    if status:
        tasks = tasks.filter(Task.status == status)
    if priority:
        tasks = tasks.filter(Task.priority == int(priority))
    if user_id:
        tasks = tasks.filter(Task.user_id == int(user_id))
    return [t.to_dict() for t in tasks.all()]


def task_stats():
    total = Task.query.count()
    done = Task.query.filter_by(status='done').count()
    # P-06/P-07: single scan, shared overdue rule.
    overdue_count = sum(1 for t in Task.query.all() if is_overdue(t.due_date, t.status))
    return {
        'total': total,
        'pending': Task.query.filter_by(status='pending').count(),
        'in_progress': Task.query.filter_by(status='in_progress').count(),
        'done': done,
        'cancelled': Task.query.filter_by(status='cancelled').count(),
        'overdue': overdue_count,
        'completion_rate': round((done / total) * 100, 2) if total > 0 else 0,
    }
