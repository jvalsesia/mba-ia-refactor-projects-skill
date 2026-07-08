"""Assorted helpers.

Domain constants now live in ``config.constants`` (P-10) and are re-exported
here for backward compatibility; the duplicate literal definitions that used to
sit at the bottom of this file were removed.
"""
import re
import uuid
from datetime import datetime

from utils.timeutils import now_utc
from config.constants import (
    VALID_TASK_STATUSES,
    VALID_USER_ROLES,
    MAX_TITLE_LENGTH,
    MIN_TITLE_LENGTH,
    MIN_PASSWORD_LENGTH,
    DEFAULT_PRIORITY,
    DEFAULT_CATEGORY_COLOR,
    MIN_PRIORITY,
    MAX_PRIORITY,
    EMAIL_REGEX,
)

# Backward-compatible aliases (kept so existing imports don't break).
VALID_STATUSES = VALID_TASK_STATUSES
VALID_ROLES = VALID_USER_ROLES
DEFAULT_COLOR = DEFAULT_CATEGORY_COLOR


def format_date(date_obj):
    return str(date_obj) if date_obj else None


def calculate_percentage(part, total):
    if total == 0:
        return 0
    return round((part / total) * 100, 2)


def validate_email(email):
    return bool(re.match(EMAIL_REGEX, email))


def sanitize_string(value):
    return value.strip() if value else value


def generate_id():
    return str(uuid.uuid4())


def log_action(action, details=None):
    print(f"[{now_utc()}] ACTION: {action}")
    if details:
        print(f"  DETAILS: {details}")


def parse_date(date_string):
    for date_format in ('%Y-%m-%d', '%d/%m/%Y'):
        try:
            return datetime.strptime(date_string, date_format)
        except (ValueError, TypeError):
            continue
    return None


def is_valid_color(color):
    return bool(color) and len(color) == 7 and color[0] == '#'


def process_task_data(data, existing_task=None):
    result = {}

    if 'title' in data:
        title = data['title']
        if not title:
            return None, 'Título não pode ser vazio'
        title = title.strip()
        if MIN_TITLE_LENGTH <= len(title) <= MAX_TITLE_LENGTH:
            result['title'] = title
        else:
            return None, 'Título deve ter entre 3 e 200 caracteres'

    if 'description' in data:
        result['description'] = data['description']

    if 'status' in data:
        if data['status'] in VALID_TASK_STATUSES:
            result['status'] = data['status']
        else:
            return None, 'Status inválido'

    if 'priority' in data:
        try:
            priority = int(data['priority'])
        except (ValueError, TypeError):
            return None, 'Prioridade inválida'
        if MIN_PRIORITY <= priority <= MAX_PRIORITY:
            result['priority'] = priority
        else:
            return None, 'Prioridade deve ser entre 1 e 5'

    if 'due_date' in data:
        if data['due_date']:
            parsed = parse_date(data['due_date'])
            if parsed:
                result['due_date'] = parsed
            else:
                return None, 'Data inválida'
        else:
            result['due_date'] = None

    if 'tags' in data:
        tags = data['tags']
        result['tags'] = ','.join(tags) if isinstance(tags, list) else tags

    return result, None
