import notifications, telegram, files

def main():
    tg_client = telegram.start_telegram()
    source_chat, newspapers_chat, magazines_chat = telegram.find_chat_entities(tg_client)
    files_to_send = telegram.get_links_from_telegram(tg_client, source_chat)

    if (len(files_to_send) == 0):
        print("No new files to download. Stopping")
        return;

    sended_newspapers, sended_magazines = telegram.get_sended_files(tg_client, newspapers_chat, magazines_chat)
    files_to_send = files.clean_list(files_to_send, sended_newspapers, sended_magazines)

    if (len(files_to_send) > 0):
        telegram.send_files(tg_client, files_to_send,  newspapers_chat, magazines_chat)
        notifications.send_message_to_admin(tg_client, files_to_send)
        files.clean()
    else:
        notifications.send_not_new_files_message(tg_client)

main()