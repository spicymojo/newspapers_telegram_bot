class FilesAPI(object):
    downloads_path = ''
    newspapers_filter = [""]
    magazines_filter = [""]
    telegram_url_prefix = ""
    file_dict = {}
    hypen_position = 1

class TelegramApi(object):
    api_id = ''
    api_hash = ''
    phone_number = '+'
    source_chat_id = 0
    source_chat_name = ''
    source_chat_limit = 0
    newspapers_chat_id=0
    newspapers_chat_name = ''
    newspapers_chat_limit = 0
    magazines_chat_id=0
    magazines_chat_name = ''
    magazines_chat_limit = 0
    admin_alias = ''
    admin_message = True

class GmailApi(object):
    sender_mail_user = "prensadeivaj@gmail.com"
    sender_mail_password = "qffzzlfbklkdigkf"
    admin_mail_user = "javiersantanagodoy@gmail.com"
    gmail_message = False