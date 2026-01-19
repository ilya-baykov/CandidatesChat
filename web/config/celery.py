import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web.config.settings.base")

from celery import Celery

# Создаем экземпляр Celery
app = Celery('web')

# Загружаем настройки из Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматическое обнаружение задач в приложениях Django
app.autodiscover_tasks()


# Опционально: настройка для обработки задач
@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
