from getpass import getpass
from datetime import datetime
from resources.config import DownloaderAPI, TelegramApi
from telethon.sync import TelegramClient

import requests, os, glob

errors = ""
NEWSPAPER = 'NEWSPAPER'
MAGAZINE = 'MAGAZINE'
TMP_PATH = 'tmp/'

# Class Message
class TelegramFile:

    def __init__(self, name, type,id,date, media):
        self.name = name
        self.type = type
        self.id = id
        self.date = date
        self.media = media

    def get_message(self):
        return self.filename + "," + self.date + "," + self.url

    def get_type(self):
        return self.type

    def get_dated_filename(self):
        return self.name + ", " + self.date

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
def append_file_message(file, file_name,file_type, message_date, file_list):
    file_list.append(build_file_message(file_name, file_type, file.media.id, message_date, file.media))

def is_pdf(file):
    try:
        return file.media.mime_type == "application/pdf"
    except AttributeError:
        return False


def get_filename_from_id(file_id):
    file_id = file_id.split("-")[3].upper()
    return DownloaderAPI.file_dict[file_id]

def get_links_from_telegram(client, source_chat):
    print("Getting links from Telegram...")
    files = []

    messages_list = get_telegram_messages(client, source_chat, source_chat_limit)

    for message in messages_list:
        try:
            if (is_today(message.date) and is_pdf(message.file)):
                file = message.file
                wanted, file_type = we_want(file.name)
                if wanted:
                    filename = get_filename_from_id(file.name)
                    append_file_message(file, filename,file_type, message.date, files)
        except TypeError as e:
            print("Error processing one of the messages:\n " + e)

    # Return the messages data list
    if (len(files)) != 0:
        print(str(len(files)) + " newspapers and magazines found")
    return files

# Telegram - Chat entities
def get_chat_entity(chat_list, chat_name):
    for chat in chat_list:
        if chat_name in chat.name:
            return chat.id

# Telegram - Find chats
def find_chat_entities(client):
    chat_list = client.iter_dialogs()
    source_chat = get_chat_entity(chat_list, source_chat_name)
    newspapers_chat = get_chat_entity(chat_list, newspapers_chat_name)
    magazines_chat = get_chat_entity(chat_list, magazines_chat_name)
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
        if is_today(message.date) and "#" in message.message:
            return;
    tg_client.send_message(newspapers_chat, "# " + str(pretty_print_date(datetime.now())))


def check_tmp_folder():
    if not os.path.isdir(TMP_PATH):
        os.makedirs(TMP_PATH)
        print("Created TMP folder")

def download_and_send_file(tg_client, chat,file):

    path = TMP_PATH + file.get_dated_filename() + ".pdf"
    if not (os.path.exists(path)):
        print("Downloading " + file.name)

        tg_client.download_file(file.media, path)
        print("Downloaded. Sending...")
        tg_client.send_file(chat, path)

        print("Sended " + file.name)
    else:
        print(file.name + "already downloaded, so skipped")

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

def send_message_to_admin(tg_client, files_to_send):
    newspapers = str(len(files_to_send))

    file_list = []
    for file in files_to_send:
        file_list.append(file.name)

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

# Downloads
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
        clean_filenames.append(file.name)
    return clean_filenames


def remove_files_from_filenames(clean_files, clean_names):
    filtered_clean_files = []
    for file in clean_files:
        if file.name in clean_names:
            filtered_clean_files.append(file)
    return filtered_clean_files


def remove_already_sended_files(files_that_we_want, sended_newspapers, sended_magazines):
    print("We want to download " + str(len(files_that_we_want)) + " files")
    print("Check already sended files...")
    not_filtered_files = len(files_that_we_want)
    names = get_filenames_from_wanted_files(files_that_we_want)

    filtered_clean_names = []
    for name in names:
        if name not in sended_newspapers and name not in sended_magazines:
            filtered_clean_names.append(name)

    files_that_we_want = remove_files_from_filenames(files_that_we_want, filtered_clean_names)
    print((str(not_filtered_files - len(files_that_we_want)) + " files already sended, removed"))
    return files_that_we_want

def clean_list(files, sended_newspapers, sended_magazines):
    files_that_we_want = []
    if files:
        for f in files:
            if f is not None and f not in files_that_we_want:
                files_that_we_want.append(f)

    files_that_we_want = remove_already_sended_files(files_that_we_want, sended_newspapers, sended_magazines)
    return files_that_we_want

# Find char for splitting
def find_separation_char(formatted_msg):
    char = None
    if "+" in formatted_msg:
        char = "+"
    elif "-" in formatted_msg:
        char = "-"
    elif "/" in formatted_msg:
        char = "/"
    return char

# Building message for file
def build_file_message(file_name, file_type, file_id, date, file_media):
    return TelegramFile(file_name, file_type, file_id, pretty_print_date(date), file_media)

# Aux - Make decissions
def we_want(filename):
    filename = filename.split("-")[3].upper()

    if filename in newspapers_filter:
        return True, NEWSPAPER
    elif filename in magazines_filter:
        return True, MAGAZINE
    return False, None

def print_results(ok, errors):
    print("\nDone! " + str(ok - len(errors)) + " files downloaded.")
    if (len(errors) > 0):
        print("Files failed: " + str(len(errors)))
        for e in errors:
            print(" * " + e)

# Files maganement
def remove_pdf_files():
    files = glob.glob(TMP_PATH + '*')
    for f in files:
        try:
            os.remove(f)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (f, e))


def count_pdf_files():
    files = glob.glob('')
    return len(files)

# Cleaning methods
def clean():
        print("Cleaning the files...")
        remove_pdf_files()
        if (count_pdf_files() == 0):
            print("Done! All clean for tomorrow!")
        else:
            print("Error deleting files, please delete them manually")


def main():
    tg_client = start_telegram()
    source_chat, newspapers_chat, magazines_chat = find_chat_entities(tg_client)
    files_to_send = get_links_from_telegram(tg_client, source_chat)
    if (len(files_to_send) == 0):
        print("No new files to download. Stopping")
        return;
    sended_newspapers, sended_magazines = get_sended_files(tg_client, newspapers_chat, magazines_chat)
    files_to_send = clean_list(files_to_send, sended_newspapers, sended_magazines)

    if (len(files_to_send) > 0):
        send_files(tg_client, files_to_send,  newspapers_chat, magazines_chat)
        send_message_to_admin(tg_client,files_to_send)
        clean()
    else:
        send_not_new_files_message(tg_client)

# General config
url_domains = TelegramApi.url_domains
admin_alias = TelegramApi.admin_alias
downloads_path = DownloaderAPI.downloads_path

# Telegram
api_id = TelegramApi.api_id
api_hash = TelegramApi.api_hash
phone_number = TelegramApi.phone_number

# Source chat
source_chat_name = TelegramApi.source_chat_name
source_chat_limit = TelegramApi.source_chat_limit

# Newspapers chat
newspapers_chat_name = TelegramApi.newspapers_chat_name
newspapers_chat_limit = TelegramApi.newspapers_chat_limit
newspapers_filter = DownloaderAPI.newspapers_filter

# Magazines chat
magazines_chat_name = TelegramApi.magazines_chat_name
magazines_chat_limit = TelegramApi.magazines_chat_limit
magazines_filter = DownloaderAPI.magazines_filter

main()