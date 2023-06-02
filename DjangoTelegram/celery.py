import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoTelegram.settings')
os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')

app = Celery('DjangoTelegram')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'check_db_every-minute': {
        'task': 'my_task',
        'schedule': 60.0,
        'args': (),
        'kwargs': {},
    },
}
