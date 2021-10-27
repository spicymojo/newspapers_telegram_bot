from api.alldebrid import Alldebrid
from datetime import datetime
from resources.config import AlldebridAPI, TelegramApi
from telethon.sync import TelegramClient

import requests, os

errors = ""
files = []

# Telegram
def start_telegram():
    client = tlg_connect(api_id, api_hash, phone_number)
    return client

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
            self_user = None
            while self_user is None:
                code = input('Enter the code you just received: ')
                try:
                    self_user = client.sign_in(code=code)
                except SessionPasswordNeededError:
                    pw = getpass('Two step verification is enabled. Please enter your password: ')
                    self_user = client.sign_in(password=pw)
                    if self_user is None:
                        return None
    print('Sign in success.')
    print()
    return client

def isToday(date):
    return str(datetime.now().day -1) in date


# Get messages data from a chat
def get_files_from_telegram(client):

    files = []
    chat_entity = client.get_entity(chat_link)
    # Get and save messages data in a single list
    messages_list = client.get_messages(chat_entity, limit=messages_limit)
    # Build our messages data structures and add them to the list
    for message in messages_list:
        if message.message.startswith("#diarios") and isToday(message.message):
            msg = message.message.split("\n")
            msg[0] = msg[0].replace("#diarios ", "").replace("#diarios", "")
            print(msg[0])
            title, date = msg[0].split("-",1)
            for url in msg:
                if url_domains[0] in url:
                    files.append(title + "," + url)
    # Return the messages data list
    return files


def download(files):
    lines = ""
    print("Connecting to AllDebrid\n")
    alldebrid = Alldebrid()
    errors = list()

    for file in files:
        filename, url = file.split(",",1)
        print(file)
        http_response = alldebrid.download_link(url)
        filename = obtain_daily_filename(filename)

        if http_response["status"] != "error":
            converted_link = http_response["data"]["link"]
            print("Saving " + filename + " ...")
            download_file(converted_link, filename)
        else:
            errors.append(filename)
    print_results(lines,errors)


# Aux
def current_date(date):
    months = ("Enero", "Febrero", "Marzo", "Abri", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre")
    day = date.day
    month = months[date.month]
    current_date = "{} de {}".format(day, month)

    return current_date

def download_file(url,filename):
    if not os.path.isfile(filename):
        if downloads_path != "":
            path = downloads_path + "/" + filename
        else:
            path = filename
        open(path, "wb").write(requests.get(url).content)

def obtain_daily_filename(filename):
    filename = str(filename + " - " + current_date(datetime.now()) + ".pdf")
    return filename

def open_link_file(path):
    return open(path, "r")

def print_results(lines, errors):
    print("\nDone! " + str(len(lines) - len(errors)) + " files downloaded.")
    if (len(errors) > 0):
        print("Files failed: " + str(len(errors)))
        for e in errors:
            print(" * " + e)

def removePdfFiles():
    for parent, dirnames, filenames in os.walk('.'):
        for fn in filenames:
            if fn.lower().endswith('.pdf'):
                os.remove(os.path.join(fn))

def countPdfFiles():
    counter = 0
    for parent, dirnames, filenames in os.walk('.'):
        for fn in filenames:
            if fn.lower().endswith('.pdf'):
                counter = counter + 1
    return counter

def clean():
    clean = input("Done! Do you want to clean the downloaded files? (y/n)")
    if not clean.lower() == "n":
        print("Okay! Using the Roomba...")
        removePdfFiles()
        if (countPdfFiles() == 0):
            print("Done! All clean for tomorrow!")
        else:
            print("Delete error, some files are still in the folder. Please check")
    else:
        print("No problem! Have a nice day!")


def main():
    tg_client = start_telegram()
    files = get_files_from_telegram(tg_client)
    download(files)
    clean()


# Telegram
api_id = TelegramApi.api_id
api_hash = TelegramApi.api_hash
phone_number = TelegramApi.phone_number
chat_link = TelegramApi.chat_link
url_domains = TelegramApi.url_domains
messages_limit = TelegramApi.messages_limit
downloads_path = AlldebridAPI.downloads_path
files_filter = AlldebridAPI.files_filter

main()
