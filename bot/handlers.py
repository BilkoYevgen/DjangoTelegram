import json, requests
import os
from django.http import HttpRequest, request
from dotenv import load_dotenv
from .models import *
from pprint import pprint

load_dotenv()

TG_BASE_URL = "https://api.telegram.org/bot"
GEO_URL = ("https://geocoding-api.open-meteo.com/v1/search?name=")


class User:
    def __init__(self, first_name=None, id=None, is_bot=None, language_code=None, last_name=None, username=None):
        self.first_name = first_name
        self.id = id
        self.is_bot = is_bot
        self.language_code = language_code
        self.last_name = last_name
        self.username = username


class TelegramHandler:
    user = None

    def __init__(self, data):
        pprint(data)
        json_data = json.loads(data)
        pprint(json_data)

        data = {}
        if json_data.get('message') is not None:
            data = json_data.get('message')
            self.user = User(**data.get('from'))
            self.text = data.get('text')
            self.on_message()

        elif json_data.get('callback_query') is not None:
            data = json_data.get('callback_query')
            self.user = User(**data.get('from'))
            self.text = data.get('data')
            self.on_callback()

    def on_callback(self):
        if self.text == "list_phone":
            self.list_phone()
        elif self.text == "add_phone":
            self.add_phone()
        elif self.text == "del_phone":
            self.del_phone()
        elif self.text == "mistake":
            self.send_message("Biggest mistake in your life")
        elif self.text == "task_yes":
            self.send_message("Great! You can upload it now!")
            # Task.objects.create(photo=self.photo, user__user_id=self.user.id)
        elif self.text == "task_no":
            self.send_message("Ok. When do you want to do your task?")

    def send_message(self, text):
        data = {
            'chat_id': self.user.id,
            'text': text,
        }

        requests.post(f'{TG_BASE_URL}{os.getenv("BOT_TOKEN")}/sendMessage', json=data)

    def on_message(self):
        if self.text == "/start":
            self.start_message_and_keyboard()
        elif self.text == "Weather" or self.text == "weather":
            self.weather_handler()
        elif self.text == "Landing page" or self.text == "landing page":
            self.show_landing()
        elif self.text == "Phonebook" or self.text == "phonebook":
            self.my_phonebook()
        elif self.text == "My tasks" or self.text == "my tasks":
            # self.send_message("task")
            self.task_handler()
        elif self.text == "Exchange rate" or self.text == "exchange rate":
            self.currency_handler()
        else:
            self.send_message("Sorry, i can't understand you.")

    def start_message_and_keyboard(self):
        try:
            user = TgUser.objects.get(user_id=self.user.id)
        except TgUser.DoesNotExist:
            add_user = TgUser.objects.create(user_id=self.user.id, user_username=self.user.username,
                                             user_first_name=self.user.first_name, user_last_name=self.user.last_name)
        data = {
            'chat_id': self.user.id,
            'text': "Hello! I am a bot that can help you in everyday life.\n\n\n"
                    "1.)💰Maybe you are interested in the exchange rate for today?\n\n"
                    "2.)📅Or do you want me to remind you to buy cheese at the store?\n\n"
                    "3.)☀Weather - this is what you need!\n\n"
                    "4.)☎No? Then I'll be your phone book!\n\n"
                    "5.)💻Also yoy can see my Landing page",
            "reply_markup": {
                "keyboard": [
                    [
                        {
                            "text": "Exchange rate"
                        },
                        {
                            "text": "My tasks"
                        },
                        {
                            "text": "Weather"
                        }
                    ],
                    [
                        {
                            "text": "Phonebook"
                        },
                        {
                            "text": "Landing page"
                        }
                    ]
                ]
            }
        }

        requests.post(f'{TG_BASE_URL}{os.getenv("BOT_TOKEN")}/sendMessage', json=data)

    def currency_handler(self):
        try:
            req = requests.get("https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json")
            responce = req.json()
            for currency in responce:
                if currency['cc'] == 'USD':
                    self.send_message(f"USD price: {round(currency['rate'], 2)} UAH on {currency['exchangedate']}\n"
                                      f"This date and the exchange rate was taken from bank.gov.ua")
                    break
        except Exception as ex:
            print(ex)
            self.send_message("Something wrong(")

    def weather_handler(self):
        self.send_message("Please enter the city or country name:")  # TODO: not working
        city_country = self.text
        res = requests.get(f"{GEO_URL}{city_country}")
        data = res.json()
        if "results" in data:
            latitude = round(data["results"][0]["latitude"], 2)
            longitude = round(data["results"][0]["longitude"], 2)
            url_api = requests.get(
                f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly=temperature_2m&current_weather=true&past_days=1&forecast_days=1&timezone=auto")
            data_api = url_api.json()
            self.send_message(
                f"Temperature in {city_country} is {data_api['current_weather']['temperature']} degree celsius!")
        else:
            self.send_message("Sorry, I couldn't find results for this input, please try again.")

    def my_phonebook(self):
        data = {
            'chat_id': self.user.id,
            'text': "What do you want to do:",
            "reply_markup": {
                "inline_keyboard": [
                    [{
                        "text": "Contact List",
                        "callback_data": "list_phone"
                    }],
                    [{
                        "text": "Add contact",
                        "callback_data": "add_phone"
                    }],
                    [{
                        "text": "Delete contact",
                        "callback_data": "del_phone"
                    },
                    ]
                ]
            }
        }

        requests.post(f'{TG_BASE_URL}{os.getenv("BOT_TOKEN")}/sendMessage', json=data)

    def show_landing(self):
        data = {
            'chat_id': self.user.id,
            'text': "Are you ready to see the best landing page in the world?",
            "reply_markup": {
                "inline_keyboard": [
                    [
                        {
                            "text": "✅Yes",
                            "url": "https://github.com/BilkoYevgen"
                        },
                        {
                            "text": "⛔No",
                            "callback_data": "mistake"
                        },
                    ]
                ]
            }
        }

        requests.post(f'{TG_BASE_URL}{os.getenv("BOT_TOKEN")}/sendMessage', json=data)

    def list_phone(self):
        self.send_message("Here is a full list of your contacts:")
        phone_list = Phone.objects.filter(user__user_id=self.user.id)
        contacts = [f"Name: {phone.phone_name}\nPhone: {phone.phone_number}" for phone in phone_list]
        numbered_contacts = [f"{index + 1}. {contact}" for index, contact in enumerate(contacts)]
        message = "\n\n".join(numbered_contacts)
        self.send_message(message)

    def add_phone(self):
        self.send_message("Please enter phone that you want to add:")

    # def del_phone(self):
    #     self.send_message("Here is a full list of your contacts:")
    #     phone_list = Phone.objects.filter(user__user_id=self.user.id)
    #     contacts = [f"Name: {phone.phone_name}" for phone in phone_list]
    #     message = "\n\n".join(contacts)
    #     self.send_message(message)
    #
    #     self.send_message("Enter name of contact to delete:")
    #
    #         #TODO: удалять по номеру или имени - user input + del_contact = Phone.objects.get(phone_name= ,
    #
    #     try:
    #         del_contact = Phone.objects.get(phone_name= , user__user_id=self.user.id)
    #         del_contact.delete()
    #         self.send_message("Contact deleted!")
    #     except Phone.DoesNotExist:
    #         self.send_message("Contact not found!")
    #
    #     self.my_phonebook()

    def task_handler(self):
        self.send_message("Please enter what you need to do:")
        # to_do = Task.objects.create(task= , user__user_id=self.user.id)
        data = {
            'chat_id': self.user.id,
            'text': "Do you want to add any photo? I will send it to you with notification.",
            "reply_markup": {
                "inline_keyboard": [
                    [
                        {
                            "text": "✅Yes",
                            "callback_data": "task_yes"
                        },
                        {
                            "text": "⛔No",
                            "callback_data": "task_no"
                        },
                    ]
                ]
            }
        }
        requests.post(f'{TG_BASE_URL}{os.getenv("BOT_TOKEN")}/sendMessage', json=data)
