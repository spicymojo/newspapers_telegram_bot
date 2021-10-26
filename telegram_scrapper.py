####################################################################################################

### Libraries/Modules ###

from telethon import TelegramClient, sync
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch

from collections import OrderedDict
from os import path, stat, remove, makedirs

import json

####################################################################################################

### Constants ###

# Client parameters
API_ID   = 'API_ID'
API_HASH = 'API_HASH'
PHONE_NUM    = 'phone'

# Chat to inspect
CHAT_LINK  = "CHAT_LINK"

URL_DOMAINS = ["URL_DOMAINS"]
####################################################################################################

### Telegram basic functions ###

# Connect and Log-in/Sign-in to telegram API
def tlg_connect(api_id, api_hash, phone_number):
	'''Connect and Log-in/Sign-in to Telegram API. Request Sign-in code for first execution'''
	print('Trying to connect to Telegram...')
	client = TelegramClient("Session", api_id, api_hash)
	if not client.start():
		print('Could not connect to Telegram servers.')
		return None
	else:
		if not client.is_user_authorized():
			print('Session file not found. This is the first run, sending code request...')
			client.sign_in(phone_number)
			self_user = None
			while self_user is None:
				code = input('Enter the code you just received: ')
				try:
					self_user = client.sign_in(code=code)
				except SessionPasswordNeededError:
					pw = getpass('Two step verification is enabled. Please enter your password: ')
					self_user = client.sign_in(password=pw)
					if self_user is None:
						return None
	print('Sign in success.')
	print()
	return client




# Get messages data from a chat
def tlg_get_messages(client, chat, num_msg):
	'''Get all members information from a group/channel/chat'''
	# Set the result list
	messages = []
	# Get the corresponding chat entity
	chat_entity = client.get_entity(chat)
	# Get and save messages data in a single list
	messages_list = client.get_messages(chat_entity, limit=num_msg)
	# Build our messages data structures and add them to the list
	for message in messages_list:
		if message.message.startswith("#diarios") and '25' in message.message:
			msg = message.message.split("\n")
			msg[0] = msg[0].replace("#diarios ","").replace("#diarios","")
			title,date = msg[0].split("-")
			for m in msg:
				if URL_DOMAINS[0] in m:
					print(title + "," + m)
	# Return the messages data list
	return messages


####################################################################################################

### Json files handle functions ###

def json_write(file, data):
	'''Write element data to content of JSON file'''
	# Add the data to a empty list and use the write_list function implementation
	data_list = []
	data_list.append(data)
	json_write_list(file, data_list)


def json_write_list(file, list):
	'''Write all the list elements data to content of JSON file'''
	try:
		# Create the directories of the file path if them does not exists
		directory = path.dirname(file)
		if not path.exists(directory):
			makedirs(directory)
		# If the file does not exists or is empty, write the JSON content skeleton
		if not path.exists(file) or not stat(file).st_size:
			with open(file, "w", encoding="utf-8") as f:
				f.write('\n{\n    "Content": []\n}\n')
		# Read file content structure
		with open(file, "r", encoding="utf-8") as f:
			content = json.load(f, object_pairs_hook=OrderedDict)
		# For each data in list, add to the json content structure
		for data in list:
			if data:
				content['Content'].append(data) # Añadir los nuevos datos al contenido del json
		# Overwrite the JSON file with the modified content data
		with open(file, "w", encoding="utf-8") as f:
			json.dump(content, fp=f, ensure_ascii=False, indent=4)
	# Catch and handle errors
	except IOError as e:
		print("    I/O error({0}): {1}".format(e.errno, e.strerror))
	except ValueError:
		print("    Error: Can't convert data value to write in the file")
	except MemoryError:
		print("    Error: You are trying to write too much data")

####################################################################################################

### Main function ###
def main():
		# Get all messages data from the chat and save to the output file
		client = tlg_connect(API_ID, API_HASH, PHONE_NUM)
		print('Getting chat messages info...')
		messages = tlg_get_messages(client, CHAT_LINK, 100)
		print(messages)
		print('Proccess completed')
		print()

####################################################################################################

### Execute the main function if the file is not an imported module ###
if __name__ == "__main__":
	main()

