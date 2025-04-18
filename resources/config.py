import json
import os
from dotenv import load_dotenv
load_dotenv()


class FilesAPI(object):
    downloads_path = os.getenv("FILES_DOWNLOADS_PATH", "")
    newspapers_filter = json.loads(os.getenv("NEWSPAPERS_FILTER", "[]"))
    magazines_filter = json.loads(os.getenv("MAGAZINES_FILTER", "[]"))
    file_dict = json.loads(os.getenv("FILE_DICT", "{}"))
    hyphen_position = int(os.getenv("HYPHEN_POSITION", 1))

class TelegramApi:
    api_id = int(os.getenv("TELEGRAM_API_ID", 0))  # Convert to integer
    api_hash = os.getenv("TELEGRAM_API_HASH", "")
    phone_number = os.getenv("TELEGRAM_PHONE_NUMBER", "")
    source_chat_name = os.getenv("TELEGRAM_SOURCE_CHAT_NAME", "")
    source_chat_limit = int(os.getenv("TELEGRAM_SOURCE_CHAT_LIMIT", 0))  # Convert to integer
    newspapers_chat_name = os.getenv("TELEGRAM_NEWSPAPERS_CHAT_NAME", "")
    newspapers_chat_limit = int(os.getenv("TELEGRAM_NEWSPAPERS_CHAT_LIMIT", 0))  # Convert to integer
    magazines_chat_name = os.getenv("TELEGRAM_MAGAZINES_CHAT_NAME", "")
    magazines_chat_limit = int(os.getenv("TELEGRAM_MAGAZINES_CHAT_LIMIT", 0))  # Convert to integer
    admin_alias = os.getenv("TELEGRAM_ADMIN_ALIAS", "")
    admin_message = os.getenv("TELEGRAM_ADMIN_MESSAGE", "False").lower() in ("true", "1", "yes")  # Convert to boolean

class Chat(object):
    chat_1_id = os.getenv("CHAT_1_ID", "")
    chat_1_name = os.getenv("CHAT_1_NAME", "")
    chat_2_id = os.getenv("CHAT_2_ID", "")
    chat_2_name = os.getenv("CHAT_2_NAME", "")
    chat_limit = os.getenv("CHAT_LIMIT", "")
