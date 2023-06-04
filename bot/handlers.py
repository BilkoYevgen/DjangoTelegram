import json, requests
import os
from django.http import HttpRequest, HttpResponse
from dotenv import load_dotenv
from .models import *
from pprint import pprint
from datetime import datetime
import re

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
    state = None
    state_user_id = None

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
            self.list_all_phones()
        elif self.text == "add_phone":
            TelegramHandler.state = 'name'
            TelegramHandler.state_user_id = self.user.id
            self.print_name_input()
        elif TelegramHandler.state == "phone":
            self.print_phone_input()
        elif self.text == "del_phone":
            TelegramHandler.state = 'delete'
            TelegramHandler.state_user_id = self.user.id
            self.print_del_phone_input()
        elif self.text == "mistake":
            self.send_message("Biggest mistake in your life")
        elif self.text == "go_back":
            TelegramHandler.state = None
            self.start_message_and_keyboard()
        elif self.text == 'add_task':
            self.task_handler_input()
        elif self.text == 'del_task':
            TelegramHandler.state = 'delete_task'
            self.task_del_input()
        else:
            self.weather_callback_handler()

    def send_message(self, text):
        data = {
            'chat_id': self.user.id,
            'text': text,
        }

        requests.post(f'{TG_BASE_URL}{os.getenv("BOT_TOKEN")}/sendMessage', json=data)

    def on_message(self):
        if TelegramHandler.state == 'weather' and TelegramHandler.state_user_id == self.user.id:
            self.weather_buttons()
            TelegramHandler.state = None
            return

        if TelegramHandler.state == 'delete_task' and TelegramHandler.state_user_id == self.user.id:
            self.delete_task_handler()
            TelegramHandler.state = None
            return

        if TelegramHandler.state == 'name' and TelegramHandler.state_user_id == self.user.id:
            self.add_name_handler()
            return

        if TelegramHandler.state == 'phone' and TelegramHandler.state_user_id == self.user.id:
            self.add_phone_handler()
            TelegramHandler.state = None
            return

        if TelegramHandler.state == 'delete' and TelegramHandler.state_user_id == self.user.id:
            self.del_phone_handler()
            TelegramHandler.state = None
            return

        if TelegramHandler.state == 'task' and TelegramHandler.state_user_id == self.user.id:
            self.task_date_input()
            TelegramHandler.state = 'second_task'
            return

        if TelegramHandler.state == 'second_task' and TelegramHandler.state_user_id == self.user.id:
            self.task_date_validator()
            TelegramHandler.state = None
            return

        if self.text == "/start":
            self.start_message_and_keyboard()

        elif self.text == "/commands":
            self.send_commands_list()

        elif self.text.lower() in ["weather", "/weather"]:
            TelegramHandler.state = 'weather'
            TelegramHandler.state_user_id = self.user.id
            self.print_weather_input()

        elif self.text.lower() in ["landing page", "/landingpage"]:
            self.show_landing_page()

        elif self.text.lower() in ["phonebook", "/phonebook"]:
            self.my_phonebook_and_buttons()

        elif self.text.lower() in ["my tasks", "/mytasks"]:
            TelegramHandler.state = 'task'
            TelegramHandler.state_user_id = self.user.id
            self.task_list_and_buttons()

        elif self.text.lower() in ["exchange rate", "/exchangerate"]:
            self.currency_handler()

        else:
            self.send_message("Sorry, i can't understand you.")

    def send_commands_list(self):
        command_list = [
            {'command': '/weather', 'description': 'Get weather information'},
            {'command': '/landingpage', 'description': 'Show landing page'},
            {'command': '/phonebook', 'description': 'Access the phonebook'},
            {'command': '/mytasks', 'description': 'Manage your tasks'},
            {'command': '/exchangerate', 'description': 'Get exchange rates'}
        ]
        command_text = "Available commands:\n\n"
        for command in command_list:
            command_text += f"{command['command']} - {command['description']}\n"
        self.send_message(command_text)

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

    def print_weather_input(self):
        self.send_message("Please enter the city or country name:")

    def weather_handler(self, city_name):
        params = {
            'name': city_name
        }
        res = requests.get(f'{GEO_URL}', params=params)
        if res.status_code != 200:
            raise Exception('Error status code')
        data = res.json()
        if not data.get('results'):
            raise Exception("Error, no results")
        return data['results']

    def weather_buttons(self):
        city = self.text
        try:
            geo_data = self.weather_handler(city)
            buttons = []
            for item in geo_data:
                test_button = {
                    'text': f'{item.get("name")} - {item.get("country_code")}',
                    'callback_data': json.dumps({'lat': item.get('latitude'), 'lon': item.get('longitude')})
                }
                buttons.append([test_button])
            markup = {
                'inline_keyboard': buttons
            }
            self.send_weather("Please select a location:", markup)
        except Exception:
            self.send_message("Error weather_buttons")

    def weather_callback_handler(self):
        callback_data = self.text
        data = json.loads(callback_data)
        latitude = round(data['lat'], 2)
        longitude = round(data['lon'], 2)
        url_api = requests.get(
            f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly=temperature_2m&current_weather=true&past_days=1&forecast_days=1&timezone=auto")
        data_api = url_api.json()
        temperature = data_api['current_weather']['temperature']
        self.send_message(f"The temperature is {temperature} degrees Celsius!")

    def send_weather(self, text, markup):
        data = {
            'chat_id': self.user.id,
            'text': text,
            "reply_markup": markup
        }
        requests.post(f'{TG_BASE_URL}{os.getenv("BOT_TOKEN")}/sendMessage', json=data)

    def my_phonebook_and_buttons(self):
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
                    }],
                    [{
                        "text": "Go Back",
                        "callback_data": "go_back"
                    },
                    ]
                ]
            }
        }

        requests.post(f'{TG_BASE_URL}{os.getenv("BOT_TOKEN")}/sendMessage', json=data)

    def show_landing_page(self):
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

    def list_all_phones(self):
        self.send_message("Here is a full list of your contacts:")
        phone_list = Phone.objects.filter(user__user_id=self.user.id)
        contacts = [f"Name: {phone.phone_name}\nPhone: {phone.phone_number}" for phone in phone_list]
        numbered_contacts = [f"{index + 1}. {contact}" for index, contact in enumerate(contacts)]
        message = "\n\n".join(numbered_contacts)
        self.send_message(message)
        self.my_phonebook_and_buttons()

    def print_name_input(self):
        self.send_message("Please enter NAME that you want to add:")

    def add_name_handler(self):
        contact_name = self.text
        name = Phone.objects.create(phone_name=contact_name, user_id=self.user.id)
        self.send_message("Name added")
        self.print_phone_input()
        TelegramHandler.state = "phone"

    def print_phone_input(self):
        self.send_message("Please enter PHONE that you want to add:")

    def add_phone_handler(self):
        contact_phone = self.text

        if Phone.objects.filter(phone_number=contact_phone).exists():
            self.send_message("Contact with this phone number already exists.")
            del_name = Phone.objects.last()
            del_name.delete()
            self.my_phonebook_and_buttons()
            return

        phone = Phone(phone_number=contact_phone, user_id=self.user.id)
        phone.save()

        self.send_message("Contact added successfully")
        self.send_message("Here is an updated list of your contacts:")

        phone_list = Phone.objects.filter(user_id=self.user.id)
        contacts = [f"Name: {phone.phone_name}\nPhone: {phone.phone_number}" for phone in phone_list]
        numbered_contacts = [f"{index + 1}. {contact}" for index, contact in enumerate(contacts)]
        message = "\n\n".join(numbered_contacts)
        self.send_message(message)

        self.my_phonebook_and_buttons()
        return

    def print_del_phone_input(self):
        self.send_message("Here is a full list of your contacts:")
        phone_list = Phone.objects.filter(user__user_id=self.user.id)
        contacts = [f"Name: {phone.phone_name}" for phone in phone_list]
        numbered_contacts = [f"{index + 1}. {contact}" for index, contact in enumerate(contacts)]
        message = "\n\n".join(numbered_contacts)
        self.send_message(message)
        self.send_message("Enter name of the contact to delete:\n"
                          "Or just write 'quit' to go back\n"
                          "If you have few phones with same name, last contact with this name will be deleted!\n"
                          "Please give different names to your contacts.")

    def del_phone_handler(self):
        del_text = self.text
        if del_text.lower() == "quit":
            self.my_phonebook_and_buttons()
            return

        try:
            del_contact = Phone.objects.filter(phone_name=del_text, user__user_id=self.user.id).last()
            del_contact.delete()
            self.send_message("Contact deleted!")
            self.send_message("Here is a UPDATED list of your contacts:")
            phone_list = Phone.objects.filter(user__user_id=self.user.id)
            contacts = [f"Name: {phone.phone_name}" for phone in phone_list]
            numbered_contacts = [f"{index + 1}. {contact}" for index, contact in enumerate(contacts)]
            message = "\n\n".join(numbered_contacts)
            self.send_message(message)
        except Phone.DoesNotExist:
            self.send_message("Contact not found!")

        self.my_phonebook_and_buttons()

    def task_list_and_buttons(self):
        self.send_message("Here is a list of your tasks:")
        my_tasks = Task.objects.filter(user__user_id=self.user.id)

        if my_tasks.exists():
            tasks = [f"{index + 1}. {task.task}" for index, task in enumerate(my_tasks)]
            tasks_message = "\n\n".join(tasks)
            self.send_message(tasks_message)
        else:
            self.send_message("You don't have any tasks")

        data = {
            'chat_id': self.user.id,
            'text': "What we will do now ?\nYou can add your task here or choose your option",
            "reply_markup": {
                "inline_keyboard": [
                    [
                        {
                            "text": "Add task",
                            "callback_data": "add_task"
                        },
                        {
                            "text": "Del task",
                            "callback_data": "del_task"
                        },
                        {
                            "text": "Go back",
                            "callback_data": "go_back"
                        },
                    ]
                ]
            }
        }

        requests.post(f'{TG_BASE_URL}{os.getenv("BOT_TOKEN")}/sendMessage', json=data)

    def task_handler_input(self):
        self.send_message("Please enter your task here:")

    def task_date_input(self):
        task_text = self.text
        if task_text.lower() == 'quit':
            self.start_message_and_keyboard()
        else:
            id = Task.objects.create(task=task_text, user_id=self.user.id).id

            self.send_message("Task added successfully")
            self.send_message("Please enter the date and time when you need to be reminded of this task.\nThe input "
                              "format should be:  Year-month-day Hour:Minute\nFor example: 2023-06-01 20:45\nIf you "
                              "want to leave, just enter 'quit'")

    def task_date_validator(self):
        datetime_string = self.text
        pattern = r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$'
        match = re.match(pattern, datetime_string)
        if match:
            self.send_message(f"Great! Notification will be sent on {datetime_string}")
            last_task = Task.objects.filter(user_id=self.user.id).last()
            if last_task:
                last_task.date = datetime.strptime(datetime_string, '%Y-%m-%d %H:%M')
                last_task.save()
            else:
                self.send_message("No tasks found for the user.")
        else:
            self.send_message("Sorry, the format of your input is wrong. Please try again.")
            self.task_list_and_buttons()

    def task_del_input(self):
        self.send_message("Please enter task which you want to delete:\n"
                          "If you have few tasks with same name, last task will be deleted!\n"
                          "Please give different names to your tasks.")

    def delete_task_handler(self):
        del_task = self.text
        if del_task.lower() == "quit":
            self.task_list_and_buttons()
            return

        try:
            task_erase = Task.objects.filter(task=del_task, user__user_id=self.user.id).last()
            task_erase.delete()
            self.send_message("Task deleted!")
            self.send_message("Here is a UPDATED list of your tasks:")
            my_tasks = Task.objects.filter(user__user_id=self.user.id)
            if my_tasks.exists():
                tasks = [f"{index + 1}. {task.task}" for index, task in enumerate(my_tasks)]
                tasks_message = "\n\n".join(tasks)
                self.send_message(tasks_message)
            else:
                self.send_message("You don't have any tasks")
        except Task.DoesNotExist:
            self.send_message("Task not found!")
