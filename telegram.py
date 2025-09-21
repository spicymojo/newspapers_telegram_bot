from getpass import getpass
from datetime import datetime
from resources.config import FilesAPI, TelegramApi, Chat
from telethon.sync import TelegramClient
import os, utils, files

errors = ""
NEWSPAPER = 'NEWSPAPER'
MAGAZINE = 'MAGAZINE'
TMP_PATH = 'tmp/'

#  Configuration and connection
def start_telegram():
    client = tlg_connect(api_id, api_hash, phone_number)
    return client

def get_telegram_messages(client, chat, messages_limit):
    messages = client.get_messages(chat, limit=messages_limit)
    today_messages = [msg for msg in messages if utils.is_today(msg.date)]
    today_pdf_messages = [msg for msg in today_messages if files.is_pdf(msg)]
    return today_pdf_messages

def get_sended_files_from_today(client, chat, messages_limit):
    filtered_files = []

    messages = client.get_messages(chat, limit=messages_limit)
    for message in messages:
        if (utils.is_today(message.date) and message.file is not None):
            filtered_files.append(message.file.name.split(",")[0].strip())
    return filtered_files

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
    file_id = file_id.split("-")[hyphen_position].upper()
    return FilesAPI.file_dict[file_id]

def get_links_from_telegram(client, source_chat) -> list:
    """
    Fetch and process today's PDF messages from a Telegram chat.
    Returns a list of file message data.
    """
    telegram_files = []
    messages_list = get_telegram_messages(client, source_chat, chat_limit)

    for message in messages_list:
        file = getattr(message, "file", None)
        if not file or not hasattr(file, "name"):
            continue
        try:
            wanted, file_type = files.we_want(file.name)
            if wanted:
                filename = get_filename_from_id(file.name)
                append_file_message(file, filename, file_type, message.date, telegram_files)
        except Exception as e:
            print(f"Error processing message: {e}")

    if telegram_files:
        print(f"{len(telegram_files)} newspapers and magazines found")
    return telegram_files

# Chat entities
def get_chat_entity(chat_list, chat_name):
    for chat in chat_list:
        if chat_name in chat.name:
            return chat.id

# Find chats
def find_chat_entities(client):
    chat_list = client.iter_dialogs()

    source_chats = {
        "source_chat_1": get_chat_entity(chat_list, Chat.chat_1_name)
    }

    newspapers_chat = get_chat_entity(chat_list, newspapers_chat_name)
    magazines_chat = get_chat_entity(chat_list, magazines_chat_name)
    return source_chats, newspapers_chat, magazines_chat

# Check sended files
def send_day_message(tg_client: TelegramClient, newspapers_chat) -> None:
    """
    Sends a day marker message to the newspapers chat if not already sent today.
    """
    messages = tg_client.get_messages(newspapers_chat, limit=newspapers_chat_limit)
    if any(utils.is_today(message.date) and "#" in getattr(message, "message", "") for message in messages):
        return
    tg_client.send_message(newspapers_chat, "# " + utils.pretty_print_date(datetime.now()))

# Send files and messages
def send_day_message(tg_client, newspapers_chat):
    messages = tg_client.get_messages(newspapers_chat, limit=newspapers_chat_limit)
    for message in messages:
        if utils.is_today(message.date) and "#" in message.message:
            return
    tg_client.send_message(newspapers_chat, "# " + utils.pretty_print_date(datetime.now()))

# Download and send files
def send_files(
    tg_client: TelegramClient,
    files_to_send: list,
    newspapers_chat,
    magazines_chat
) -> None:
    """
    Send files to the appropriate Telegram chats, avoiding duplicates.
    """
    print("\nStart sending files to Telegram...")
    print(f"{len(files_to_send)} files to send")
    sended_files = set()

    send_day_message(tg_client, newspapers_chat)

    for file in files_to_send:
        if file.name in sended_files:
            continue
        try:
            if file.type == NEWSPAPER:
                download_and_send_file(tg_client, newspapers_chat, file)
            elif file.type == MAGAZINE:
                download_and_send_file(tg_client, magazines_chat, file)
            sended_files.add(file.name)
        except Exception as e:
            print(f"Error while sending {file.name}: {e}")

    print("Files sent!\n")

def download_and_send_file(
    tg_client: TelegramClient,
    chat,
    file
) -> None:
    """
    Download a file from Telegram and send it to the specified chat if not already sent today.
    Skips download and send if the file exists or was already sent.
    """
    path = files.TMP_PATH + file.get_dated_filename() + ".pdf"
    if not os.path.exists(path):
        print("Downloading " + file.name)
        tg_client.download_file(file.media, path)
        print("Downloaded. Sending...")

        # Recheck if the file was already sent by another server
        today_messages = get_sended_files_from_today(tg_client, chat, chat_limit)
        if file.name in today_messages:
            print(file.name + " already sent, skipping")
            return
        tg_client.send_file(chat, path)
        print("Sended " + file.name)
    else:
        print(file.name + " already downloaded, so skipped")


# Telegram
api_id = TelegramApi.api_id
api_hash = TelegramApi.api_hash
phone_number = TelegramApi.phone_number

# Telegram - Newspapers chat
newspapers_chat_name = TelegramApi.newspapers_chat_name
newspapers_chat_limit = int(TelegramApi.newspapers_chat_limit)

# Telegram - Magazines chat
magazines_chat_name = TelegramApi.magazines_chat_name
magazines_chat_limit = int(TelegramApi.newspapers_chat_limit)

# Config - Hypen position
hyphen_position = FilesAPI.hyphen_position

# Chat - Chat limit
chat_limit = int(Chat.chat_limit)