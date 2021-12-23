
class AlldebridAPI(object):
    agent = ''
    key = ''
    downloads_path = ''
    newspapers_filter = [""]
    magazines_filter = [""]
    interactive_mode = "False"

class TelegramApi(object):
    api_id = ''
    api_hash = ''
    phone_number = ''
    source_chat = ''
    newspapers_chat = ''
    magazines_chat = ''
    source_chat_limit = 100
    newspapers_chat_limit = 10
    magazines_chat_limit = 20
    admin_alias = ''
    url_domains = ['']