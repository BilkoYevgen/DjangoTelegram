from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE, DjangoTelegram.settings')

app = Celery('name')
app.config_from_object('django.conf:settings', namespace='celery')
app.autodiscover_tasks()
