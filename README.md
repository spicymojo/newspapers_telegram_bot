# alldebrid_downloader

Python 3 script that scrapes a Telegram group that shares newspapers and magazines, downloads the files using Alldebrid to convert the links and send the downloaded files to another Telegram group. Who said leecher?

Needed Python Packages:
* Telethon
* telethon-tgcrypto

# What do you need to know?
1. Install the dependencies
2. Fill the config file (Not self-explanatory parameters explained) :

AllDebrid API
| Parameter | Description |
| ------ | ------ |
| agent | Agent name for Alldebrid |
| key | Api-Key for Alldebrid |
| downloads_path | Path for downloads, could be blank on a Raspberry Pi |
| newspapers_filter | Newspapers that you want to download  (List, uppercase) |
| magazines_filter | Magazines that you want to download (List, uppercase)|

TelegramApi

| Parameter | Description |
| ------ | ------ |
| API id, API hash | Telegram bot parameters |
| Phone number | Number of the bot (Could be your own) |
| Source chat id, name and limit | Telegram ID and name of the origin of the links, and limit for retrieving messages |
| Newspaper chat id, name and limit |Telegram ID and name of the newspapers destination, and limit for retrieving messages |
| Magazines id, name and limit | Telegram ID and name of the magazines destination, and limit for retrieving messages|
| Source alias | Alias of the provider of the links (Source channel owner, usually) |
| URL domains | URL that works with Alldebrid that you want to use (ul.to works well) |

After that, you are all set. On the first run, Telegram will ask for a confirmation code, and after that can run on his own. The bot would send a message to your saved messages to tell you what's happening with your execution. Good luck!

Probably your use case is not the same, but you can reuse the structure, at least the channel reading and link extraction
