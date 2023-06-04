import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoTelegram.settings')

app = Celery('DjangoTelegram')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'check_db_every-minute': {
        'task': 'bot.tasks.process_tasks',
        'schedule': 20.0,
        'args': (),
        'kwargs': {},
    },
}
