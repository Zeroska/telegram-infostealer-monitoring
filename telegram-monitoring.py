from telethon import TelegramClient, events, sync
from telethon.tl.types import DocumentAttributeFilename, Message, MessageMediaDocument
import fileinput
import asyncio
import logging
import os
from zipfile import ZipFile
from os.path import join, dirname
from dotenv import load_dotenv


# Logging 
logging.basicConfig(
	format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s', level=logging.INFO,filename="running.log",encoding='utf-8')

# Env Configuration
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
api_hash = os.getenv("api_hash")
api_id = os.getenv("api_id")
phone_number = os.getenv("phone_number")
download_path = os.getenv("download_path")
rarexe = "C:\Program Files\WinRAR\Rar.exe"


# Start the client
client = TelegramClient('anon', api_id, api_hash)

channels = [""]
team_webhook = ""

# Filter keywords

keywords_filter_list = []


def lines_that_equal(line):
	word_list = ['opswat.com','@hdbank.com','zeroska.dev@gmail.com','@rootgroup','eolianenergy.com']
	for key in word_list:
		if key in line:
			return True
	return False

async def send_telegram_channel_notification():
	logging.info("Sending notification to telegram channels")


# This function is use to check the content of compressed file, whether if it is 
def compress_file_content_checker():
	print("[*] Read content file to pass to the compress file handler ")


def handle_zip(file_path):
	with ZipFile("") as zip:
		# Download path is global varible, extract to download_path 
		zip.extractall(download_path)

def handle_rar(file):
	print("")

# This function is used after the compressed file has download, in order to pr
def compress_file_handler(file_name, file_path):
	if ".rar" in file_name:
		os.system(rarexe)
		print("")
	elif "zip" in file_name:
		handle_zip(file_path)
	else:
		print("[*] Compressed file type not supported ")

# You can disable this function as you plesase, if you send your log to another place - Khuong
async def output_monitored_dataleak(downloaded_files):
	try: 
		for line in fileinput.input([downloaded_files]):
				if lines_that_equal(line):
					print("[*] Data leaked Found")

					# You can output it to another channel (teams chat, telegram chat or discord by using webhook)
					with open("leaked.txt","w") as data:
						data.write(str(line))
	except Exception as e:
		logging.info(f"Error: {e}")

def callback(current, total):
    print('Downloaded', current, 'out of', total, 'bytes: {:.2%}'.format(current / total))

@client.on(events.NewMessage())
async def downloadTXTFile(event: Message):
	try: 
		# we use event.message.media.document because we only want the file not other media such as Photo or anything just file 
		print("[*] New Message Recieved")
		if event.message.media is not None:
			print(event.message.media.document)
			print("File Name[0]: " + str(event.message.media.document.attributes[0].file_name))
			
			file_name = event.message.media.document.attributes[0].file_name

			if ".txt" or ".csv" or ".rar" or ".zip "in event.message.media.document.attributes[0].file_name:
				chat = await event.get_chat()
				leak_download_path = await client.download_media(event.message.media,f"{download_path}{file_name}",progress_callback=callback)
				# Check the newest data leak downloaded file has the important credential that we care about
				
				# if ".rar" or ".zip" in file_name:
				# 	compress_file_handler(file_name, leak_download_path)
				
				await output_monitored_dataleak(leak_download_path)
				logging.info("File success fully downloaded at " + str(leak_download_path))
			else:
				logging.info("[*] New Media but not .txt or .csv")
				logging.info(f"File Name: {file_name}")
	except Exception as e:
		logging.error(f"Exception: {e}" )
	


# Start the infinite loop to wait for new messages	
async def main():
	print("[*] Telegram monitoring starting")
	await client.run_until_disconnected()

# TODO: Learn how to Async IO work
with client:
	client.loop.run_until_complete(main())
