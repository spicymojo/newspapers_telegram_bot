from resources.config import TelegramApi, GmailApi
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


def send_admin_message_in_gmail(message):
    if gmail:
        # Creates session and start security
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()

        # Auth
        s.login(sender_mail_user, sender_mail_password)

        # Adapts message to Gmail
        message = "From: %s\nTo: %s\nSubject: %s\n\n%s" % (sender_mail_user, admin_mail_user, "Resumen diario " +
                                                           utils.pretty_print_date(datetime.now()), message)

        # Mail sending and closing session
        s.sendmail(sender_mail_user, admin_mail_user, message)

        s.quit()


def send_message_to_admin(tg_client, files_to_send):
    message = build_admin_message(files_to_send)
    send_admin_message_in_telegram(tg_client, message)
    send_admin_message_in_gmail(message)

def send_not_new_files_message(tg_client):
    tg_client.send_message(admin_alias,"Hello! Your bot here! Nothing new on sight, so I didnt do shit")
    print("Nothing new to download, stopping")

# Configs

# Telegram
admin_alias = TelegramApi.admin_alias
admin_message = TelegramApi.admin_message

# Gmail
sender_mail_user = GmailApi.sender_mail_user
sender_mail_password = GmailApi.sender_mail_password
admin_mail_user = GmailApi.admin_mail_user
gmail = GmailApi.gmail_message
