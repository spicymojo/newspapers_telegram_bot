class AlldebridAPI(object):
    agent = ''
    key = ''
    downloads_path = ''
    newspapers_filter = ['']
    magazines_filter = ['']
    interactive_mode = ''
    pastebin_url = ""
    telegram_url_prefix = ""

class TelegramApi(object):
    api_id = ''
    api_hash = ''
    phone_number = ''
    source_chat_id = ''
    source_chat_name = ''
    source_chat_limit = 0
    newspapers_chat_id = ''
    newspapers_chat_name = ''
    newspapers_chat_limit = 0
    magazines_chat_id = ''
    magazines_chat_name = ''
    magazines_chat_limit = 0
    admin_alias = ''
    source_alias = ''
    url_domains = ['']