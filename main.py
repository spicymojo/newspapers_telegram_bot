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
        self.filename = filename
        self.url = url
        self.date = date

    def get_message(self):
        return self.filename + "," + self.date + "," + self.url

    def get_type(self):
        return self.type

    def get_dated_filename(self):
        if not self.date or self.type == 'NEWSPAPER':
            return self.filename + ", " + pretty_print_date(datetime.now())
        else:
            return self.filename + ", " + self.date

    def print(self):
        return self.get_message()

# Telegram - Configuration and connection
def start_telegram():
    client = tlg_connect(api_id, api_hash, phone_number)
    return client

def get_telegram_messages(client, chat, messages_limit):
    return client.get_messages(chat, limit=messages_limit)

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
            msg = message.message.split("\n")
            if message.message.startswith("#diarios") and is_today(message.date):
                formatted_msg = get_formatted_message(msg, "#diarios ")
                files.append(build_message(msg, NEWSPAPER, formatted_msg))
            elif message.message.startswith("#revistas"):
                formatted_msg = get_formatted_message(msg, "#revistas ")
                files.append(build_message(msg, MAGAZINE, formatted_msg))
        except TypeError as e:
            print("Error processing one of the messages:\n " + e)

    # Return the messages data list
    print(str(len(files)) + " newspapers and magazines found")
    return files

# Telegram - Chat entities
def get_chat_entity(client,chat_list, chat_url, chat_name):
    chat_entity = ''
    try:
        chat_entity = client.get_entity(chat_url)
    except Exception:
        print("Cannot retrieve chat by link. Searching your chats..")
        for chat in chat_list:
            if chat.name == chat_name:
                chat_entity = client.get_entity(chat)
                print("Using chat " + chat.name)
                break
    return chat_entity


def find_chat_entities(client, chat_list):
    source_chat = get_chat_entity(client,chat_list,  source_chat_url, source_chat_name)
    newspapers_chat = get_chat_entity(client,chat_list, newspapers_chat_url, newspapers_chat_name)
    magazines_chat = get_chat_entity(client,chat_list, magazines_chat_url, magazines_chat_name)
    return source_chat, newspapers_chat, magazines_chat

# Telegram - Check sended files
def get_sended_files(client, newspapers_chat,magazines_chat):
    print("Obtaining already sended files...")
    telegram_sended_newspapers = get_telegram_messages(client, newspapers_chat, newspapers_chat_limit)
    telegram_sended_magazines = get_telegram_messages(client, magazines_chat, magazines_chat_limit)
    sended_newspapers = []
    sended_magazines = []

    for message in telegram_sended_newspapers:
        if message and message.file and message.date.day == datetime.now().day:
            sended_newspapers.append(message.file.name)
    for message in telegram_sended_magazines:
        if message and message.file and message.date.day:
            sended_magazines.append(message.file.name)
    return sended_newspapers, sended_magazines

# Telegram - Send files and messages
def send_files(tg_client, newspapers_chat, magazines_chat):
    print("\nStart sending files to Telegram...")
    print(str(len(downloaded_files)) + " files to send")
    sended_files = []

    tg_client.send_message(newspapers_chat, "# " + str(pretty_print_date(datetime.now())))
    for file in downloaded_files:
        if file.filename not in sended_files:
            try:
                if file.type =="NEWSPAPER":
                    tg_client.send_file(newspapers_chat, file.filename, force_document=True)
                elif file.type == "MAGAZINE":
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


# Date methods
def is_today(date):
    return date.day == datetime.now().day

def pretty_print_date(date):
    months = ("Enero", "Febrero", "Marzo", "Abri", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre")
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
            print("  Downloading " + file.filename + " ...")
            download_file(file)
            downloaded_files.append(file)
            ok = ok + 1
        else:
            errors.append(file.filename)
    print_results(ok,errors)

def download_file(file):

    if not os.path.isfile(file.filename):
        if downloads_path != "":
            path = downloads_path + "/" + file.filename
        else:
            path = file.filename
        open(path, "wb").write(requests.get(file.url).content)

# File management
def open_link_file(path):
    return open(path, "r")

def remove_already_sended_files(clean_files, sended_newspapers, sended_magazines):
    print("We want to download " + str(len(clean_files)) + " files")
    print("Checking for already sended files...")
    not_filtered_files = len(clean_files)

    for newspaper in sended_newspapers:
        if newspaper in clean_files:
            clean_files.remove(newspaper)

    for magazine in sended_magazines:
        if magazine in clean_files:
            clean_files.remove(newspaper)
    print("We removed " + (str(not_filtered_files - len(clean_files)) + " files"))
    return clean_files

def clean_list(files, sended_newspapers, sended_magazines):
    clean_files = []
    if files:
        for f in files:
            if f is not None:
                if f in clean_files:
                    clean_files.remove(f)
                if we_want(f.filename):
                    clean_files.append(f)

    clean_files = remove_already_sended_files(clean_files, sended_newspapers, sended_magazines)
    return clean_files

def remove_pdf_files():
    for parent, dirnames, filenames in os.walk('.'):
        for fn in filenames:
            if fn.lower().endswith('.pdf'):
                try:
                    os.remove(os.path.join(fn))
                except Exception:
                    print("Error removingex " + fn)

def count_pdf_files():
    counter = 0
    for parent, dirnames, filenames in os.walk('.'):
        for fn in filenames:
            if fn.lower().endswith('.pdf'):
                counter = counter + 1
    return counter

# Aux
def get_formatted_message(msg, key):
    return msg[0].replace(key, "")

def build_message(msg, type, formatted_msg):
    char = None
    if "-" in formatted_msg:
        char = "-"
    elif "/" in formatted_msg:
        char = "/"

    title, date = formatted_msg.rsplit(char, 1)

    if "-" in formatted_msg and "/" in formatted_msg:
        trash, date = formatted_msg.rsplit('/', 1)

    for url in msg:
        if url_domains[0] in url:
            return Message(type, title, url, date)

def we_want(filename):
    filename = filename.strip().upper()
    if filename in newspapers_filter or filename in magazines_filter:
        return True
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
    download(files_to_download)
    send_files(tg_client, newspapers_chat, magazines_chat)
    send_message_to_admin(tg_client)
    clean()


# General config
url_domains = TelegramApi.url_domains
admin_alias = TelegramApi.admin_alias
downloads_path = AlldebridAPI.downloads_path
interactive_mode = AlldebridAPI.interactive_mode

# Telegram
api_id = TelegramApi.api_id
api_hash = TelegramApi.api_hash
phone_number = TelegramApi.phone_number

# Source chat
source_chat_url = TelegramApi.source_chat_url
source_chat_name = TelegramApi.source_chat_name
source_chat_limit = TelegramApi.source_chat_limit

# Newspapers chat
newspapers_chat_url = TelegramApi.newspapers_chat_url
newspapers_chat_name = TelegramApi.newspapers_chat_name
newspapers_chat_limit = TelegramApi.newspapers_chat_limit
newspapers_filter = AlldebridAPI.newspapers_filter

# Magazines chat
magazines_chat_url = TelegramApi.magazines_chat_url
magazines_chat_name = TelegramApi.magazines_chat_name
magazines_chat_limit = TelegramApi.magazines_chat_limit
magazines_filter = AlldebridAPI.magazines_filter

main()