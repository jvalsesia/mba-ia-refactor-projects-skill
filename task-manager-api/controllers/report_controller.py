"""Layer 4 — Reporting business logic (P-04).

The large aggregation that used to live inside the report view functions now
lives here, with the per-user N+1 replaced by a single grouped scan (P-06).
"""
from datetime import timedelta

from models.task import Task
from models.user import User
from models.category import Category
from exceptions import ApiError
from utils.timeutils import now_utc, is_overdue
from config.constants import (
    RECENT_ACTIVITY_DAYS,
    HIGH_PRIORITY_THRESHOLD,
    TERMINAL_STATUSES,
)


def _count_by_status(status):
    return Task.query.filter_by(status=status).count()


def _count_by_priority(priority):
    return Task.query.filter_by(priority=priority).count()


def summary_report():
    all_tasks = Task.query.all()

    overdue_count = 0
    overdue_list = []
    for task in all_tasks:
        if is_overdue(task.due_date, task.status):
            overdue_count += 1
            overdue_list.append({
                'id': task.id,
                'title': task.title,
                'due_date': str(task.due_date),
                'days_overdue': (now_utc() - task.due_date).days,
            })

    window_start = now_utc() - timedelta(days=RECENT_ACTIVITY_DAYS)
    recent_tasks = Task.query.filter(Task.created_at >= window_start).count()
    recent_done = Task.query.filter(
        Task.status == 'done',
        Task.updated_at >= window_start,
    ).count()

    # P-06: group the tasks we already loaded by user instead of querying per user.
    tasks_by_user = {}
    for task in all_tasks:
        tasks_by_user.setdefault(task.user_id, []).append(task)

    user_stats = []
    for user in User.query.all():
        user_tasks = tasks_by_user.get(user.id, [])
        total = len(user_tasks)
        completed = sum(1 for t in user_tasks if t.status == 'done')
        user_stats.append({
            'user_id': user.id,
            'user_name': user.name,
            'total_tasks': total,
            'completed_tasks': completed,
            'completion_rate': round((completed / total) * 100, 2) if total > 0 else 0,
        })

    return {
        'generated_at': str(now_utc()),
        'overview': {
            'total_tasks': Task.query.count(),
            'total_users': User.query.count(),
            'total_categories': Category.query.count(),
        },
        'tasks_by_status': {
            'pending': _count_by_status('pending'),
            'in_progress': _count_by_status('in_progress'),
            'done': _count_by_status('done'),
            'cancelled': _count_by_status('cancelled'),
        },
        'tasks_by_priority': {
            'critical': _count_by_priority(1),
            'high': _count_by_priority(2),
            'medium': _count_by_priority(3),
            'low': _count_by_priority(4),
            'minimal': _count_by_priority(5),
        },
        'overdue': {
            'count': overdue_count,
            'tasks': overdue_list,
        },
        'recent_activity': {
            'tasks_created_last_7_days': recent_tasks,
            'tasks_completed_last_7_days': recent_done,
        },
        'user_productivity': user_stats,
    }


def user_report(user_id):
    user = User.query.get(user_id)
    if not user:
        raise ApiError('Usuário não encontrado', 404)

    tasks = Task.query.filter_by(user_id=user_id).all()
    counts = {'done': 0, 'pending': 0, 'in_progress': 0, 'cancelled': 0}
    high_priority = 0
    overdue = 0
    for task in tasks:
        if task.status in counts:
            counts[task.status] += 1
        if task.priority <= HIGH_PRIORITY_THRESHOLD:
            high_priority += 1
        if is_overdue(task.due_date, task.status):
            overdue += 1

    total = len(tasks)
    return {
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
        },
        'statistics': {
            'total_tasks': total,
            'done': counts['done'],
            'pending': counts['pending'],
            'in_progress': counts['in_progress'],
            'cancelled': counts['cancelled'],
            'overdue': overdue,
            'high_priority': high_priority,
            'completion_rate': round((counts['done'] / total) * 100, 2) if total > 0 else 0,
        },
    }
