# Импортируем Celery при старте Django
# Чтобы Django знал о существовании Celery
from .celery import app as celery_app

__all__ = ("celery_app",)
