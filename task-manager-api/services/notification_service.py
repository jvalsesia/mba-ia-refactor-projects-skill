"""Notification service.

SMTP configuration is injected (P-05) rather than hardcoded in ``__init__``
(previously the source of hardcoded credentials, AP-01). Callers may pass
explicit settings for testing; by default it reads from the config layer.
"""
import smtplib

from config import settings
from utils.timeutils import now_utc


class NotificationService:
    def __init__(self, host=None, port=None, user=None, password=None):
        self.notifications = []
        self.email_host = host if host is not None else settings.SMTP_HOST
        self.email_port = port if port is not None else settings.SMTP_PORT
        self.email_user = user if user is not None else settings.SMTP_USER
        self.email_password = password if password is not None else settings.SMTP_PASSWORD

    def send_email(self, to, subject, body):
        try:
            server = smtplib.SMTP(self.email_host, self.email_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            message = f"Subject: {subject}\n\n{body}"
            server.sendmail(self.email_user, to, message)
            server.quit()
            print(f"Email enviado para {to}")
            return True
        except Exception as error:
            print(f"Erro ao enviar email: {str(error)}")
            return False

    def notify_task_assigned(self, user, task):
        subject = f"Nova task atribuída: {task.title}"
        body = (
            f"Olá {user.name},\n\nA task '{task.title}' foi atribuída a você.\n\n"
            f"Prioridade: {task.priority}\nStatus: {task.status}"
        )
        self.send_email(user.email, subject, body)
        self.notifications.append({
            'type': 'task_assigned',
            'user_id': user.id,
            'task_id': task.id,
            'timestamp': now_utc(),
        })

    def notify_task_overdue(self, user, task):
        subject = f"Task atrasada: {task.title}"
        body = (
            f"Olá {user.name},\n\nA task '{task.title}' está atrasada!\n\n"
            f"Data limite: {task.due_date}"
        )
        self.send_email(user.email, subject, body)

    def get_notifications(self, user_id):
        return [n for n in self.notifications if n['user_id'] == user_id]
