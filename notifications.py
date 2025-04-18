from resources.config import TelegramApi
from datetime import datetime

import smtplib
import utils

def build_admin_message(files_to_send):
    newspapers = str(len(files_to_send))

    file_list = []
    for file in files_to_send:
        file_list.append(file.name)

    return "Hello! Your bot here\n" + newspapers + " files sended to Telegram Group:\n " + str(file_list)

def send_admin_message_in_telegram(tg_client, message):
    if admin_message:
        tg_client.send_message(admin_alias,message)


def send_message_to_admin(tg_client, files_to_send):
    message = build_admin_message(files_to_send)
    send_admin_message_in_telegram(tg_client, message)

def send_not_new_files_message(tg_client):
    tg_client.send_message(admin_alias,"Hello! Your bot here! Nothing new on sight, so I didnt do shit")
    print("Nothing new to download, stopping")

# Configs

# Telegram
admin_alias = TelegramApi.admin_alias
admin_message = TelegramApi.admin_message