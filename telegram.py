from getpass import getpass
from datetime import datetime
from resources.config import FilesAPI, TelegramApi
from telethon.sync import TelegramClient

import os
import utils
import files

errors = ""
NEWSPAPER = 'NEWSPAPER'
MAGAZINE = 'MAGAZINE'
TMP_PATH = 'tmp/'

#  Configuration and connection
def start_telegram():
    client = tlg_connect(api_id, api_hash, phone_number)
    return client

def get_telegram_messages(client, chat, messages_limit):
    return client.get_messages(chat, limit=messages_limit)

def get_sended_files_from_today(client, chat, messages_limit):
    filtered_newspapers = []
    messages = client.get_messages(chat, limit=messages_limit)
    for message in messages:
        if (utils.is_today(message.date) and message.file is not None):
            filtered_newspapers.append(message.file.name.split(",")[0].strip())
    return filtered_newspapers

def wait_for_code(client):
    code = input('Enter the code you just received: ')
    try:
        self_user = client.sign_in(code=code)
    except Exception:
        pw = getpass('Two step verification is enabled. Please enter your password: ')
        self_user = client.sign_in(password=pw)
        if self_user is None:
            return None

# Session
def tlg_connect(api_id, api_hash, phone_number):
    print('Trying to connect to Telegram...')
    client = TelegramClient("Session", api_id, api_hash)
    if not client.start():
        print('Could not connect to Telegram servers.')
        return None
    else:
        if not client.is_user_authorized():
            print('Session file not found. This is the first run, sending code request...')
            client.sign_in(phone_number)
            client = wait_for_code(client)

    print('Sign in success.')
    print()
    return client

# Messages handling and processing
def append_file_message(file, file_name,file_type, message_date, file_list):
    file_list.append(utils.build_file_message(file_name, file_type, file.media.id, message_date, file.media))

def get_filename_from_id(file_id):
    file_id = file_id.split("-")[3].upper()
    return FilesAPI.file_dict[file_id]

def get_links_from_telegram(client, source_chat):
    print("Getting links from Telegram...")
    telegram_files = []

    messages_list = get_telegram_messages(client, source_chat, source_chat_limit)

    for message in messages_list:
        try:
            if (utils.is_today(message.date) and files.is_pdf(message.file)):
                file = message.file
                wanted, file_type = files.we_want(file.name)
                if wanted:
                    filename = get_filename_from_id(file.name)
                    append_file_message(file, filename,file_type, message.date, telegram_files)
        except TypeError as e:
            print("Error processing one of the messages:\n " + str(e))

    # Return the messages data list
    if (len(telegram_files)) != 0:
        print(str(len(telegram_files)) + " newspapers and magazines found")
    return telegram_files

# Chat entities
def get_chat_entity(chat_list, chat_name):
    for chat in chat_list:
        if chat_name in chat.name:
            return chat.id

# Find chats
def find_chat_entities(client):
    chat_list = client.iter_dialogs()
    source_chat = get_chat_entity(chat_list, source_chat_name)
    newspapers_chat = get_chat_entity(chat_list, newspapers_chat_name)
    magazines_chat = get_chat_entity(chat_list, magazines_chat_name)
    return source_chat, newspapers_chat, magazines_chat

# Check sended files
def get_sended_files(client, newspapers_chat,magazines_chat):
    print("Obtaining already sended files...")
    telegram_sended_newspapers = get_sended_files_from_today(client, newspapers_chat, newspapers_chat_limit)
    telegram_sended_magazines = get_sended_files_from_today(client, magazines_chat, magazines_chat_limit)

    return telegram_sended_newspapers, telegram_sended_magazines

# Send files and messages
def send_day_message(tg_client, newspapers_chat):
    messages = tg_client.get_messages(newspapers_chat, limit=newspapers_chat_limit)
    for message in messages:
        if utils.is_today(message.date) and "#" in message.message:
            return
    tg_client.send_message(newspapers_chat, "# " + utils.pretty_print_date(datetime.now()))

# Download and send files
def send_files(tg_client, files_to_send,  newspapers_chat, magazines_chat):
    print("\nStart sending files to Telegram...")
    print(str(len(files_to_send)) + " files to send")
    sended_files = []

    send_day_message(tg_client, newspapers_chat)

    for file in files_to_send:
        if file.name not in sended_files:
            try:
                if file.type == NEWSPAPER:
                    download_and_send_file(tg_client, newspapers_chat,file)
                elif file.type == MAGAZINE:
                    download_and_send_file(tg_client, magazines_chat,file)
                sended_files.append(file.name)
            except Exception:
                print("Error while sending " + file.name)

    print("Files sended!\n")

def download_and_send_file(tg_client, chat,file):

    path = files.TMP_PATH + file.get_dated_filename() + ".pdf"
    if not (os.path.exists(path)):
        print("Downloading " + file.name)

        tg_client.download_file(file.media, path)
        print("Downloaded. Sending...")
        tg_client.send_file(chat, path)

        print("Sended " + file.name)
    else:
        print(file.name + "already downloaded, so skipped")


# Telegram
api_id = TelegramApi.api_id
api_hash = TelegramApi.api_hash
phone_number = TelegramApi.phone_number

# Telegram - Source chat
source_chat_name = TelegramApi.source_chat_name
source_chat_limit = TelegramApi.source_chat_limit

# Telegram - Newspapers chat
newspapers_chat_name = TelegramApi.newspapers_chat_name
newspapers_chat_limit = TelegramApi.newspapers_chat_limit

# Telegram - Magazines chat
magazines_chat_name = TelegramApi.magazines_chat_name
magazines_chat_limit = TelegramApi.magazines_chat_limit