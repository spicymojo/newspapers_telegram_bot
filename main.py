from api.alldebrid import Alldebrid
from datetime import datetime
from resources.config import AlldebridAPI, TelegramApi
from telethon.sync import TelegramClient

import requests, os

errors = ""
downloaded_files = []

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
    return str(datetime.now().day) in date

# Get messages data from a chat
def get_links_from_telegram(client):
    print("Obteniendo links de Telegram...")
    files = []
    chat_entity = client.get_entity(source_chat)
    # Get and save messages data in a single list
    messages_list = client.get_messages(chat_entity, limit=messages_limit)
    # Build our messages data structures and add them to the list
    for message in messages_list:
        if message.message.startswith("#diarios") and isToday(message.message):
            msg = message.message.split("\n")
            msg[0] = msg[0].replace("#diarios ", "").replace("#diarios", "")
            title, date = msg[0].split("-",1)
            for url in msg:
                if url_domains[0] in url:
                    files.append(title + "," + url)
    # Return the messages data list
    print(str(len(files)) + " magazines found")
    return files

def we_want(filename):
    filename = filename.strip().upper()
    return filename in newspapers_filter

def download(files):
    print("\nConnecting to AllDebrid\n")
    alldebrid = Alldebrid()
    errors = list()
    ok = 0

    for file in files:
        filename, url = file.split(",",1)
        if we_want(filename):
            http_response = alldebrid.download_link(url)
            filename = obtain_daily_filename(filename)
            if http_response["status"] != "error":
                converted_link = http_response["data"]["link"]
                print("  Downloading " + filename + " ...")
                download_file(converted_link, filename)
                downloaded_files.append(filename)
                ok = ok + 1
            else:
                errors.append(filename)
    print_results(ok,errors)

# Aux
def current_date(date):
    months = ("Enero", "Febrero", "Marzo", "Abri", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre")
    day = date.day
    month = months[date.month-1]
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

def print_results(ok, errors):
    print("\nDone! " + str(ok - len(errors)) + " files downloaded.")
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

def send_files(tg_client):
    print("\nStart sending files to Telegram...")
    print(str(len(downloaded_files)) + " files to send")
    sended_files = []

    tg_client.send_message(destinatary_chat, "# " + str(current_date(datetime.now())))
    for file in downloaded_files:
        if file not in sended_files:
            tg_client.send_file(destinatary_chat, file, force_document=True)
            sended_files.append(file)
    print("Files sended!\n")

def send_message_to_admin(tg_client):
    newspapers = str(len(downloaded_files))
    tg_client.send_message(admin_alias,"Hello! Your bot here\n" + newspapers + " newspapers sended to Telegram Group:\n " + str(downloaded_files))

def clean():
    if (interactive_mode == True) :
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
    else:
        print("Cleaning the files...")
        removePdfFiles()
        if (countPdfFiles() == 0):
            print("Done! All clean for tomorrow!")
        else:
            print("Delete error, some files are still in the folder. Please check")


def main():
    tg_client = start_telegram()
    files = get_links_from_telegram(tg_client)
    download(files)
    send_files(tg_client)
    send_message_to_admin(tg_client)
    clean()


# Telegram
api_id = TelegramApi.api_id
api_hash = TelegramApi.api_hash
phone_number = TelegramApi.phone_number
source_chat = TelegramApi.source_chat
destinatary_chat = TelegramApi.destinatary_chat
url_domains = TelegramApi.url_domains
messages_limit = TelegramApi.messages_limit
admin_alias = TelegramApi.admin_alias
downloads_path = AlldebridAPI.downloads_path
newspapers_filter = AlldebridAPI.newspapers_filter
interactive_mode = AlldebridAPI.interactive_mode

main()