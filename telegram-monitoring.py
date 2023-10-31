from telethon import TelegramClient, events, sync
import asyncio
import logging


logging.basicConfig(
	format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s', level=logging.WARNING)

api_hash = ""
api_id = ""
phone_number = ""

client = TelegramClient('anon', api_id, api_hash)
# Start the client

channels = [""]
team_webhook = ""

def callback(current, total):
    print('Downloaded', current, 'out of', total, 'bytes: {:.2%}'.format(current / total))

@client.on(events.NewMessage())
async def downloadTXTFile(event):
	try: 
		if event.message.media:
			print(event.message.media.document)
			print(event.message.media)
			print(event.message.media.document.attributes[0].file_name)
			print(event.message.media.document.attributes.file_name)
			if ".txt" in event.message.media.document.attributes[0].file_name:
				chat = await event.get_chat()
				print(chat)
				
				path = await client.download_media(event.message.media,f"D:\\Leaked Data Logs\\{event.message.media.document.attributes[0].file_name}",progress_callback=callback)
				print("File success fully downloaded at " + str(path))
			else:
				print("[*] New Message but not .txt")
		else:
			print("New Message - Not contain Media")
	except Exception as e:
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
