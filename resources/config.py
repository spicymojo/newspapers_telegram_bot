class FilesAPI(object):
    downloads_path = ''
    newspapers_filter = [""]
    magazines_filter = [""]
    telegram_url_prefix = ""
    file_dict = {}

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
    sender_mail_user = ""
    sender_mail_password = ""
    admin_mail_user = ""
    gmail_message = True
