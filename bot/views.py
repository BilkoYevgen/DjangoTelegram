import json
from pprint import pprint
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .handlers import TelegramHandler
from django.http import HttpResponse
from .models import TgUser


@csrf_exempt
def index(request):
    if request.method == 'POST':
        handler = TelegramHandler(request.body.decode('utf-8'))
        return HttpResponse('Hi')

    if request.method == 'GET':
        return HttpResponse('Hi')

