Telegram-Bot-on-Django


The TelegramHandler class initializes with incoming data from the Telegram API and determines the type of data (message or callback). Depending on the type, it calls the appropriate method (on_message or on_callback) to handle the data.

The on_message method handles incoming messages and checks for specific commands or keywords. For example, if the message is "/weather" or "weather," it sets the state to 'weather' and prompts the user to enter a city or country name for weather information.

The send_message method sends a message to the user using the Telegram API by making a POST request to the Telegram bot API's sendMessage endpoint.

The weather_handler method sends a request to the Open-Meteo geocoding API to retrieve latitude and longitude data for a given city or country name. It then uses the latitude and longitude to fetch weather data from the Open-Meteo weather API.

The weather_buttons method creates inline keyboard buttons based on the geocoding data received and sends them to the user. The user can select a location from the buttons, and the corresponding weather data will be fetched and sent back.

The my_phonebook_and_buttons method displays a keyboard with options for managing a phonebook: listing contacts, adding a contact, deleting a contact, or going back.

The list_all_phones method retrieves all contacts from the database and sends them as a message to the user.

The add_name_handler and add_phone_handler methods handle the addition of a new contact to the phonebook. The user is prompted to enter the name and phone number, and the data is saved in the database.

The print_del_phone_input and del_phone_handler methods handle the deletion of a contact from the phonebook. The user is prompted to enter the name of the contact to delete, and the corresponding contact is removed from the database.

The task_list_and_buttons method displays a list of tasks associated with the user and provides options for adding or deleting tasks.

The send_commands_list method sends a message to the user with a list of available commands and their descriptions.
