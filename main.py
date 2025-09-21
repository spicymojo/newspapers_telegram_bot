import notifications, telegram, files

def main():
    tg_client = telegram.start_telegram()
    source_chats, newspapers_chat, magazines_chat = telegram.find_chat_entities(tg_client)

    for source_chat in source_chats.values():
        files_to_send = telegram.get_links_from_telegram(tg_client, source_chat)

        if (len(files_to_send) == 0):
            print("No new files to download. Stopping")
            return;

        sent_newspapers = telegram.get_sended_files_from_today(tg_client, newspapers_chat, messages_limit=20)
        sent_magazines = telegram.get_sended_files_from_today(tg_client, magazines_chat, messages_limit=20)
        files_to_send = files.clean_list(files_to_send, sent_newspapers, sent_magazines)

        if (len(files_to_send) > 0):
            telegram.send_files(tg_client, files_to_send,  newspapers_chat, magazines_chat)
            notifications.send_message_to_admin(tg_client, files_to_send)
            files.clean()
        else:
            notifications.send_not_new_files_message(tg_client)

main()