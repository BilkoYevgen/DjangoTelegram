from celery import shared_task
import datetime
from .models import *
import requests
import os
from datetime import datetime
from dotenv import load_dotenv
from django.utils.timezone import now

load_dotenv()

TG_BASE_URL = "https://api.telegram.org/bot"


@shared_task
def process_tasks():
    result = Task.objects.filter(date__lte=now(), is_done=False)

    for task in result:
        user_id = task.user.user_id
        data = {
            'chat_id': user_id,
            'text': task.task,
        }
        requests.post(f'{TG_BASE_URL}{os.getenv("BOT_TOKEN")}/sendMessage', json=data)
        task.is_done = True
        task.save()
