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
    state = None
    state_user_id = None

    def __init__(self, data):
        json_data = json.loads(data)

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
            TelegramHandler.state = 'name'
            TelegramHandler.state_user_id = self.user.id
            self.print_add_name()
        elif TelegramHandler.state == "phone":
            self.print_add_phone()
        elif self.text == "del_phone":
            TelegramHandler.state = 'delete'
            TelegramHandler.state_user_id = self.user.id
            self.print_del_phone()
        elif self.text == "mistake":
            self.send_message("Biggest mistake in your life")
        elif self.text == "task_yes":
            self.send_message("Great! You can upload it now!")
        elif self.text == "task_no":
            self.send_message("Ok. When do you want to do your task?")
        elif self.text == "go_back":
            self.start_message_and_keyboard()

    def send_message(self, text):
        data = {
            'chat_id': self.user.id,
            'text': text,
        }

        requests.post(f'{TG_BASE_URL}{os.getenv("BOT_TOKEN")}/sendMessage', json=data)

    def on_message(self):
        if TelegramHandler.state == 'weather' and TelegramHandler.state_user_id == self.user.id:
            self.weather_handler()
            TelegramHandler.state = None
            return

        if TelegramHandler.state == 'name' and TelegramHandler.state_user_id == self.user.id:
            self.add_name()

        if TelegramHandler.state == 'phone' and TelegramHandler.state_user_id == self.user.id:
            self.add_phone()
            TelegramHandler.state = None
            return

        if TelegramHandler.state == 'delete' and TelegramHandler.state_user_id == self.user.id:
            self.del_phone()
            TelegramHandler.state = None
            return

        if TelegramHandler.state == 'task' and TelegramHandler.state_user_id == self.user.id:
            self.task_handler()
            TelegramHandler.state = None
            return

        if self.text == "/start":
            self.start_message_and_keyboard()
        elif self.text == "Weather" or self.text == "weather":
            TelegramHandler.state = 'weather'
            TelegramHandler.state_user_id = self.user.id
            self.print_weather_handler()
        elif self.text == "Landing page" or self.text == "landing page":
            self.show_landing()
        elif self.text == "Phonebook" or self.text == "phonebook":
            self.my_phonebook()
        elif self.text == "My tasks" or self.text == "my tasks":
            TelegramHandler.state = 'task'
            TelegramHandler.state_user_id = self.user.id
            self.print_task_handler()
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

    def print_weather_handler(self):
        self.send_message("Please enter the city or country name:")

    def weather_handler(self):
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
        self.my_phonebook()

    def print_add_name(self):
        self.send_message("Please enter NAME that you want to add:")

    def add_name(self):
        contact_name = self.text
        name = Phone.objects.create(phone_name=contact_name, user_id=self.user.id)
        self.send_message("Name added")
        self.print_add_phone()
        TelegramHandler.state = "phone"

    def print_add_phone(self):
        self.send_message("Please enter PHONE that you want to add:")

    def add_phone(self):
        contact_phone = self.text
        phone = Phone.objects.filter(phone_number=contact_phone).last()  # TODO: phone_number не  записывается

    def print_del_phone(self):
        self.send_message("Here is a full list of your contacts:")
        phone_list = Phone.objects.filter(user__user_id=self.user.id)
        contacts = [f"Name: {phone.phone_name}" for phone in phone_list]
        numbered_contacts = [f"{index + 1}. {contact}" for index, contact in enumerate(contacts)]
        message = "\n\n".join(numbered_contacts)
        self.send_message(message)
        self.send_message("Enter name of the contact to delete:\n"
                          "Or just write 'quit' to go back")

    def del_phone(self):
        del_text = self.text
        if del_text.lower() == "quit":
            self.my_phonebook()
            return

        try:
            del_contact = Phone.objects.get(phone_name=del_text, user__user_id=self.user.id)
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

        self.my_phonebook()

    def print_task_handler(self):
        self.send_message("Here is a list of your tasks:")
        my_tasks = Task.objects.filter(user__user_id=self.user.id)

        if my_tasks.exists():
            tasks = [f"{index + 1}. {task.task}" for index, task in enumerate(my_tasks)]
            tasks_message = "\n\n".join(tasks)
            self.send_message(tasks_message)
        else:
            self.send_message("You don't have any tasks")

        self.send_message("Please add a task\n"
                          "or enter 'quit' if you don't want to add a new task:")

    def task_handler(self):
        task_text = self.text
        if task_text.lower() == 'quit':
            self.send_message("Okay. What do you need now?")
            self.start_message_and_keyboard()
        else:
            to_do = Task.objects.create(task=task_text, user_id=self.user.id)
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

    # Add a callback handler for receiving the photo
    def handle_photo(self, file_id):
        # Get the file path using the file ID
        file_response = requests.get(f'{TG_BASE_URL}{os.getenv("BOT_TOKEN")}/getFile?file_id={file_id}')
        file_data = file_response.json()
        if 'result' in file_data:
            file_path = file_data['result']['file_path']
            # Download the photo
            download_url = f'{TG_BASE_URL}file/bot{os.getenv("BOT_TOKEN")}/{file_path}'
            photo_response = requests.get(download_url)
            if photo_response.status_code == 200:
                # Save the photo to the database
                photo_data = photo_response.content  # Store or process the photo data as needed
                # Add the photo data to the corresponding task
                to_do = Task.objects.get(user_id=self.user.id)
                to_do.photo = photo_data
                to_do.save()
                self.send_message("Photo added successfully.")
