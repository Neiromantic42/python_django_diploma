import os
from celery import Celery

# 1. Указываем Django settings для Celery
# Celery должен знать где настройки Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'diploma_backend.settings')

# 2. Создаем приложение Celery
# 'diploma_backend' - название проекта
app = Celery('diploma_backend')

# 3. Загружаем настройки из settings.py
# namespace='CELERY' значит ищем переменные начинающиеся с CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# 4. Автоматически находит tasks.py во всех приложениях
# Ищет файлы tasks.py в каждом app (payment/tasks.py, orders/tasks.py и т.д.)
app.autodiscover_tasks()