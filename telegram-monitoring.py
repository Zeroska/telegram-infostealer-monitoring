from telethon import TelegramClient, events, sync
import asyncio
import logging

logging.basicConfig(
	format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s', level=logging.WARNING)

api_hash = ""
api_id = ""
phonenumber = ""

client = TelegramClient('anon', api_id, api_hash)
# Start the client

channels = [""]
team_webhook = ""


async def download_file():
	try:
		print("[*] Getting file from the leak channel")
		async for message in client.iter_messages('me'):
			print(message.id, message.text)
			task = client.loop.create_task(message.download_media())
	except Exception as e:
		print(e)


@client.on(events.NewMessage(chats=channels))
async def handler(event):
	print("[*] Start handle new message")
	message = event.message
	sender = message.sender
	text = message.text
	print(f'{sender} and {text}')

@client.on(events.NewMessage)
async def downloadTXTFile(event):
	print("[*] Detect File Txt and download it")
	if event.message.media:
		if ".txt" in event:
			print("Found TXT")



# Start the infinite loop to wait for new messages
async def main():
	me = await client.get_me()
	print(me.stringify())

	# Get all the chat ID
	async for dialog in client.iter_dialogs():
		print(dialog.name, 'has ID', dialog.id)	
	async for message in client.iter_messages('me'):
		print(message.id, message.text)

		# You can download media from messages, too!
		# The method will return the path where the file was saved.
		if message.files:
			path = await message.download_media()
			print('File saved to', path)  # printed after download is done
		
	await client.run_until_disconnected()

# TODO: Learn how to Async IO work
with client:
	client.loop.run_until_complete(main())
