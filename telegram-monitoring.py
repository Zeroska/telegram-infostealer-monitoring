from telethon import TelegramClient, events, sync
from telethon.tl.types import DocumentAttributeFilename, Message, MessageMediaDocument

import asyncio
import logging
import os
from os.path import join, dirname
from dotenv import load_dotenv

logging.basicConfig(
	format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s', level=logging.WARNING)

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

api_hash = os.getenv("api_hash")
api_id = os.getenv("api_id")
phone_number = os.getenv("phone_number")
download_path = os.getenv("download_path")

client = TelegramClient('anon', api_id, api_hash)
# Start the client

channels = [""]
team_webhook = ""

def callback(current, total):
    print('Downloaded', current, 'out of', total, 'bytes: {:.2%}'.format(current / total))

@client.on(events.NewMessage())
async def downloadTXTFile(event):
	try: 
		# we use event.message.media.document because we only want the file not other media such as Photo or anything just file 
		print("[*] New Message Recieved")
		if event.message.media is not None:
			print(event.message.media.document)
			print("File Name[0]: " + str(event.message.media.document.attributes[0].file_name))
			
			file_name = event.message.media.document.attributes[0].file_name
			if ".txt" in event.message.media.document.attributes[0].file_name:
				chat = await event.get_chat()
				path = await client.download_media(event.message.media,f"{download_path}{file_name}",progress_callback=callback)
				print("File success fully downloaded at " + str(path))
			else:
				print("[*] New Media but not .txt")
				print(f"File Name: {file_name}")
	except Exception as e:
		print("Into Exception")
		print(e)


def donwload_mediafiles_by_channelId(id):
	print("[*] Start downloading ")

# Start the infinite loop to wait for new messages
async def main():
	print("[*] Telegram monitoring starting")


	# Get all the chat ID
	# async for dialog in client.iter_dialogs():
	# 	print(dialog.name, 'has ID', dialog.id)	
	# 	# For each chat id check for new mesage
	# 	async for message in client.iter_messages(dialog.id):
	# 	# You can download media from messages, too!
	# 	# The method will return the path where the file was saved.
	# 		if message.files:
	# 			path = await message.download_media()
	# 			print('File saved to', path)  # printed after download is done
		
	await client.run_until_disconnected()

# TODO: Learn how to Async IO work
with client:
	client.loop.run_until_complete(main())
