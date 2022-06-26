from getpass import getpass

from telethon.errors import SessionPasswordNeededError

from api.alldebrid import Alldebrid
from datetime import datetime
from resources.config import AlldebridAPI, TelegramApi
from telethon.sync import TelegramClient

import requests, os

errors = ""
downloaded_files = []
chat_list = []
NEWSPAPER = 'NEWSPAPER'
MAGAZINE = 'MAGAZINE'

# Class Message
class Message:
    def __init__(self, type, filename,url, date):
        self.type = type
        self.filename = filename.strip()
        self.url = url
        self.date = date

    def get_message(self):
        return self.filename + "," + self.date + "," + self.url

    def get_type(self):
        return self.type

    def get_dated_filename(self):
        return self.filename + ", " + self.date

    def print(self):
        return self.get_message()

# Telegram - Configuration and connection
def start_telegram():
    client = tlg_connect(api_id, api_hash, phone_number)
    return client

def get_telegram_messages(client, chat, messages_limit):
    return client.get_messages(chat, limit=messages_limit)

def get_sended_newspapers_from_today(client, chat, messages_limit):
    filtered_newspapers = []
    messages = client.get_messages(chat, limit=messages_limit)
    for message in messages:
        if (is_today(message.date) and message.file is not None):
            filtered_newspapers.append(message.file.name.split(",")[0].strip())
    return filtered_newspapers

def get_sended_magazines(client, magazines_chat, magazines_chat_limit):
    filtered_magazines = []
    telegram_sended_magazines = get_telegram_messages(client, magazines_chat, magazines_chat_limit)
    for magazine in telegram_sended_magazines:
        if (magazine.file is not None):
            filtered_magazines.append(magazine.file.name.split(",")[0].strip())
    return filtered_magazines

def wait_for_code(client):
    code = input('Enter the code you just received: ')
    try:
        self_user = client.sign_in(code=code)
    except Exception:
        pw = getpass('Two step verification is enabled. Please enter your password: ')
        self_user = client.sign_in(password=pw)
        if self_user is None:
            return None

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

# Telegram - Get messages
def get_links_from_telegram(client, source_chat):
    print("Getting links from Telegram...")
    files = []

    messages_list = get_telegram_messages(client, source_chat, source_chat_limit)

    for message in messages_list:
        try:
            if message.message is not None:
                msg = message.message.split("\n")
                if message.message.startswith("#revistas"):
                    formatted_msg = get_formatted_message(msg, "#revistas ")
                    files.append(build_message(msg, MAGAZINE, formatted_msg,  message.date))
                elif is_today(message.date) and TelegramApi.source_alias not in message.message:
                    formatted_msg = get_formatted_message(msg, "#diarios ")
                    files.append(build_message(msg, NEWSPAPER, formatted_msg, message.date))
        except TypeError as e:
            print("Error processing one of the messages:\n " + e)

    # Return the messages data list
    print(str(len(files)) + " newspapers and magazines found")
    return files

# Telegram - Chat entities
def get_chat_entity(client, chat_list, chat_id, chat_name):
    chat_entity = ''
    try:
        chat_entity = client.get_entity(chat_id)
    except Exception:
        for chat in chat_list:
            if chat_name in chat.name:
                chat_entity = client.get_entity(chat)
                print("Using chat " + chat.name)
                break
    return chat_entity

# Telegram - Find chats
def find_chat_entities(client, chat_list):
    source_chat = get_chat_entity(client,chat_list,  source_chat_id, source_chat_name)
    newspapers_chat = get_chat_entity(client,chat_list, newspapers_chat_id, newspapers_chat_name)
    magazines_chat = get_chat_entity(client,chat_list, magazines_chat_id, magazines_chat_name)
    return source_chat, newspapers_chat, magazines_chat

# Telegram - Check sended files
def get_sended_files(client, newspapers_chat,magazines_chat):
    print("Obtaining already sended files...")
    telegram_sended_newspapers = get_sended_newspapers_from_today(client, newspapers_chat, newspapers_chat_limit)
    telegram_sended_magazines = get_sended_magazines(client, magazines_chat, magazines_chat_limit)

    return telegram_sended_newspapers, telegram_sended_magazines

# Telegram - Send files and messages
def send_day_message(tg_client, newspapers_chat):
    messages = tg_client.get_messages(newspapers_chat, limit=newspapers_chat_limit)
    for message in messages:
        if "#" in message.message:
            return;
    tg_client.send_message(newspapers_chat, "# " + str(pretty_print_date(datetime.now())))


def send_files(tg_client, newspapers_chat, magazines_chat):
    print("\nStart sending files to Telegram...")
    print(str(len(downloaded_files)) + " files to send")
    sended_files = []

    send_day_message(tg_client, newspapers_chat)

    for file in downloaded_files:
        if file.filename not in sended_files:
            try:
                if file.type == NEWSPAPER:
                    tg_client.send_file(newspapers_chat, file.filename, force_document=True)
                elif file.type == MAGAZINE:
                    tg_client.send_file(magazines_chat, file.filename, force_document=True)
                sended_files.append(file.filename)
                print("Just sended " + file.filename)
            except Exception:
                print("Error while sending " + file.filename)

    print("Files sended!\n")

def send_message_to_admin(tg_client):
    newspapers = str(len(downloaded_files))

    file_list = []
    for file in downloaded_files:
        file_list.append(file.filename)

    tg_client.send_message(admin_alias,"Hello! Your bot here\n" + newspapers + " files sended to Telegram Group:\n " + str(file_list))

def send_not_new_files_message(tg_client):
    tg_client.send_message(admin_alias,"Hello! Your bot here! Nothing new on sight, so I didnt do shit")
    print("Nothing new to download, stopping")

# Date methods
def is_today(date):
    return date.day == datetime.now().day

def pretty_print_date(date):
    months = ("Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre")
    day = date.day
    month = months[date.month-1]
    current_date = "{} de {}".format(day, month)

    return current_date

# Alldebrid & Downloads
def download(files):
    print("\nConnecting to AllDebrid\n")
    alldebrid = Alldebrid()
    errors = list()
    ok = 0

    for file in files:
        http_response = alldebrid.download_link(file.url)
        file.filename = file.get_dated_filename() + ".pdf"
        if http_response["status"] != "error":
            converted_link = http_response["data"]["link"]
            file.url = converted_link

            while "  " in file.filename:
                file.filename = file.filename.replace("  "," ")

            download_file(file)
            downloaded_files.append(file)
            ok = ok + 1
        else:
            errors.append(file.filename)
    print_results(ok,errors)

def download_file(file):

    if not os.path.isfile(file.filename):
        try:
            if downloads_path != "":
                file.filename = downloads_path + "/" + file.filename
            else:
                file.filename = file.filename.replace(r"/"," ")
            print("  Downloading " + file.filename + " ...")
            open(file.filename, "wb").write(requests.get(file.url).content)
        except Exception:
            print("Error downloading " + file.filename)

# File management
def open_link_file(path):
    return open(path, "r")

def get_filenames_from_wanted_files(clean_files):
    clean_filenames = []
    for file in clean_files:
        clean_filenames.append(file.filename.strip())
    return clean_filenames


def remove_files_from_filenames(clean_files, clean_names):
    filtered_clean_files = []
    for file in clean_files:
        if file.filename in clean_names:
            filtered_clean_files.append(file)
    return filtered_clean_files


def remove_already_sended_files(files_that_we_want, sended_newspapers, sended_magazines):
    print("We want to download " + str(len(files_that_we_want)) + " files")
    print("Checking for already sended files...")
    not_filtered_files = len(files_that_we_want)
    clean_names = get_filenames_from_wanted_files(files_that_we_want)

    filtered_clean_names = []
    for name in clean_names:
        if name not in sended_newspapers and name not in sended_magazines:
            filtered_clean_names.append(name)

    files_that_we_want = remove_files_from_filenames(files_that_we_want, filtered_clean_names)
    print((str(not_filtered_files - len(files_that_we_want)) + " files already sended, so we removed them"))
    return files_that_we_want

def clean_list(files, sended_newspapers, sended_magazines):
    files_that_we_want = []
    if files:
        for f in files:
            if f is not None and we_want(f) and f not in files_that_we_want:
                files_that_we_want.append(f)

    files_that_we_want = remove_already_sended_files(files_that_we_want, sended_newspapers, sended_magazines)
    return files_that_we_want

# Aux - Messages
def get_formatted_message(msg, key):
    return msg[0].replace(key, "")

def build_message(msg, type, formatted_msg, date):
    char = None
    if "+" in formatted_msg:
        char = "+"
    elif "-" in formatted_msg:
        char = "-"
    elif "/" in formatted_msg:
        char = "/"

    title = formatted_msg.rsplit(char)[0]
    while char in title:
        title = formatted_msg.rsplit(char)[0]

    for url in msg:
        if url_domains[0] in url:
            if (type == MAGAZINE):
                if msg[0].rsplit("-")[1] is not None:
                    date = msg[0].rsplit("-")[1]
                else:
                    date = msg[0].rsplit("-")
                return Message(type, title, url, date)
            return Message(type, title, url, pretty_print_date(date))

# Aux - Make decissions
def we_want(file):
    filename = file.filename.strip().upper()
    if file.type == NEWSPAPER:
        return filename in newspapers_filter
    elif file.type == MAGAZINE:
        return filename in magazines_filter
    return False

def obtain_daily_filename(filename):
    filename = str(filename + " - " + pretty_print_date(datetime.now()) + ".pdf")
    return filename

def print_results(ok, errors):
    print("\nDone! " + str(ok - len(errors)) + " files downloaded.")
    if (len(errors) > 0):
        print("Files failed: " + str(len(errors)))
        for e in errors:
            print(" * " + e)

# Files maganement
def remove_pdf_files():
    for parent, dirnames, filenames in os.walk('.'):
        for fn in filenames:
            if fn.lower().endswith('.pdf'):
                try:
                    os.remove(os.path.join(fn))
                except Exception:
                    print("Error removing file " + fn)

def count_pdf_files():
    counter = 0
    for parent, dirnames, filenames in os.walk('.'):
        for fn in filenames:
            if fn.lower().endswith('.pdf'):
                counter = counter + 1
    return counter

# Cleaning methods
def clean():
    if (interactive_mode == True) :
        clean = input("Done! Do you want to clean the downloaded files? (y/n)")
        if not clean.lower() == "n":
            print("Okay! Using the Roomyba...")
            remove_pdf_files()
            if (count_pdf_files() == 0):
                print("Done! All clean for tomorrow!")
            else:
                print("Delete error, some files are still in the folder. Please check")
        else:
            print("No problem! Have a nice day!")
    else:
        print("Cleaning the files...")
        remove_pdf_files()
        if (count_pdf_files() == 0):
            print("Done! All clean for tomorrow!")
        else:
            print("Delete error, some files are still in the folder. Please check")

def main():
    tg_client = start_telegram()
    chat_list = tg_client.get_dialogs()
    source_chat, newspapers_chat, magazines_chat = find_chat_entities(tg_client, chat_list)
    files_to_download = get_links_from_telegram(tg_client, source_chat)
    sended_newspapers, sended_magazines = get_sended_files(tg_client, newspapers_chat, magazines_chat)
    files_to_download = clean_list(files_to_download, sended_newspapers, sended_magazines)

    if (len(files_to_download) > 0):
        download(files_to_download)
        send_files(tg_client, newspapers_chat, magazines_chat)
        send_message_to_admin(tg_client)
        clean()
    else:
        send_not_new_files_message(tg_client)

# General config
url_domains = TelegramApi.url_domains
admin_alias = TelegramApi.admin_alias
source_alias = TelegramApi.source_alias
downloads_path = AlldebridAPI.downloads_path
interactive_mode = AlldebridAPI.interactive_mode

# Telegram
api_id = TelegramApi.api_id
api_hash = TelegramApi.api_hash
phone_number = TelegramApi.phone_number

# Source chat
source_chat_id = TelegramApi.source_chat_id
source_chat_name = TelegramApi.source_chat_name
source_chat_limit = TelegramApi.source_chat_limit

# Newspapers chat
newspapers_chat_id = TelegramApi.newspapers_chat_id
newspapers_chat_name = TelegramApi.newspapers_chat_name
newspapers_chat_limit = TelegramApi.newspapers_chat_limit
newspapers_filter = AlldebridAPI.newspapers_filter

# Magazines chat
magazines_chat_id = TelegramApi.magazines_chat_id
magazines_chat_name = TelegramApi.magazines_chat_name
magazines_chat_limit = TelegramApi.magazines_chat_limit
magazines_filter = AlldebridAPI.magazines_filter

main()