"""Layer 4 — User business logic (P-04)."""
import re

from database import db
from models.user import User
from models.task import Task
from exceptions import ApiError
from utils.timeutils import is_overdue
from config.constants import (
    EMAIL_REGEX,
    MIN_PASSWORD_LENGTH,
    VALID_USER_ROLES,
    DEFAULT_USER_ROLE,
)


def _valid_email(email):
    return bool(re.match(EMAIL_REGEX, email))


def _require_user(user_id):
    user = User.query.get(user_id)
    if not user:
        raise ApiError('Usuário não encontrado', 404)
    return user


def list_users():
    users = User.query.all()
    return [
        {**user.public_dict(), 'task_count': len(user.tasks)}
        for user in users
    ]


def get_user(user_id):
    user = _require_user(user_id)
    data = user.to_dict()
    tasks = Task.query.filter_by(user_id=user_id).all()
    data['tasks'] = [task.to_dict() for task in tasks]
    return data


def create_user(data):
    if not data:
        raise ApiError('Dados inválidos', 400)

    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', DEFAULT_USER_ROLE)

    if not name:
        raise ApiError('Nome é obrigatório', 400)
    if not email:
        raise ApiError('Email é obrigatório', 400)
    if not password:
        raise ApiError('Senha é obrigatória', 400)
    if not _valid_email(email):
        raise ApiError('Email inválido', 400)
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ApiError('Senha deve ter no mínimo 4 caracteres', 400)
    if User.query.filter_by(email=email).first():
        raise ApiError('Email já cadastrado', 409)
    if role not in VALID_USER_ROLES:
        raise ApiError('Role inválido', 400)

    user = User()
    user.name = name
    user.email = email
    user.set_password(password)
    user.role = role

    db.session.add(user)
    db.session.commit()
    return user.to_dict()


def update_user(user_id, data):
    user = _require_user(user_id)
    if not data:
        raise ApiError('Dados inválidos', 400)

    if 'name' in data:
        user.name = data['name']

    if 'email' in data:
        if not _valid_email(data['email']):
            raise ApiError('Email inválido', 400)
        existing = User.query.filter_by(email=data['email']).first()
        if existing and existing.id != user_id:
            raise ApiError('Email já cadastrado', 409)
        user.email = data['email']

    if 'password' in data:
        if len(data['password']) < MIN_PASSWORD_LENGTH:
            raise ApiError('Senha muito curta', 400)
        user.set_password(data['password'])

    if 'role' in data:
        if data['role'] not in VALID_USER_ROLES:
            raise ApiError('Role inválido', 400)
        user.role = data['role']

    if 'active' in data:
        user.active = data['active']

    db.session.commit()
    return user.to_dict()


def delete_user(user_id):
    user = _require_user(user_id)
    for task in Task.query.filter_by(user_id=user_id).all():
        db.session.delete(task)
    db.session.delete(user)
    db.session.commit()
    return {'message': 'Usuário deletado com sucesso'}


def get_user_tasks(user_id):
    _require_user(user_id)
    tasks = Task.query.filter_by(user_id=user_id).all()
    result = []
    for task in tasks:
        result.append({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'status': task.status,
            'priority': task.priority,
            'created_at': str(task.created_at),
            'due_date': str(task.due_date) if task.due_date else None,
            'overdue': is_overdue(task.due_date, task.status),
        })
    return result


def login(data):
    if not data:
        raise ApiError('Dados inválidos', 400)

    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        raise ApiError('Email e senha são obrigatórios', 400)

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        raise ApiError('Credenciais inválidas', 401)
    if not user.active:
        raise ApiError('Usuário inativo', 403)

    return {
        'message': 'Login realizado com sucesso',
        'user': user.to_dict(),
        'token': 'fake-jwt-token-' + str(user.id),
    }
