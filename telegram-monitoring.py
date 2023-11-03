from telethon import TelegramClient, events, sync
from telethon.tl.types import Message
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


if os.path.exists("C:\Program Files\WinRAR\Rar.exe"):
	rarexe="C:\Program Files\WinRAR\Rar.exe"
else: 
	print("[*] There are no RAR binary found on this machine")
	rarexe=None

# Start the client
client = TelegramClient('anon', api_id, api_hash)

channels = [""]
team_webhook = ""

# Filter keywords

keywords_filter_list = []


def lines_that_equal(line):
	# TODO: Allow user to specify the keyword by using .env or by using argument to the script not by modify the code 
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
	try:
		with ZipFile(file_path) as zip:
		# Download path is global varible, extract to download_path 
			zip.extractall(download_path)
		logging.info(f"ZIP extracted at: {download_path}")
	except Exception as e:
		logging.error(f"Error at handle_zip: {e}")

def handle_rar(file_path):
	try:
		logging.info(f"RAR extracted at: {download_path}")
	except Exception as e:
		logging.error(f"Error at handle_rar: {e}") 

# This function is used after the compressed file has download, 
def compress_file_handler(file_name, file_path):
	if ".rar" in file_name:
		logging.info(f"RAR file recieved: {file_name}")
		# If rar, on Windows then using windows rar if they have it -> extract the file using the password if needed
		if rarexe is not None:
			handle_rar(file_path)
		else:
			logging.error("Don't have RAR binary -> will no perfomr unrar")
	elif "zip" in file_name:
		logging.info(f"ZIP file recieved: {file_name}")
		handle_zip(file_path)
	else:
		print("[*] Compressed file type not supported ")

# You can disable this function as you plesase, if you send your log to another place - Khuong
async def output_monitored_dataleak(downloaded_files):
	try: 
		logging.info("File downloaded and checking for data leak")
		print("[*] File downloaded and checking for data leak")
		for line in fileinput.input([downloaded_files], encoding="utf8"):
				if lines_that_equal(line):
					print(f"[*] Data leaked found: {line}")
					logging.info(f"Data leaked found: {line}")
					# You can output it to another channel (teams chat, telegram chat or discord by using webhook)
					with open("leaked.txt","w") as data:
						data.write(str(line))
						data.close()
		fileinput.close()
		logging.info("Checking successfully and found nothing")
		print("[*] Checking successfully and found nothing")
	except Exception as e:
		fileinput.close()
		logging.info(f"output_monitored_dataleak error: {e}")

def progress_bar(current, total):
    print('Downloaded', current, 'out of', total, 'bytes: {:.2%}'.format(current / total))

@client.on(events.NewMessage())
async def downloadTXTFile(event: Message):
	try: 
		# we use event.message.media.document because we only want the file not other media such as Photo or anything just file 
		print(f"[*] New Message Recieved")
		if event.message.media is not None:
			print(event.message.media.document)
			print("File Name[0]: " + str(event.message.media.document.attributes[0].file_name))
			
			file_name = event.message.media.document.attributes[0].file_name

			if ".txt" or ".csv" or ".rar" or ".zip "in event.message.media.document.attributes[0].file_name:
				chat = await event.get_chat()
				leak_download_path = await client.download_media(event.message.media,f"{download_path}{file_name}",progress_callback=progress_bar)
				# Check the newest data leak downloaded file has the important credential that we care about
				
				# if ".rar" or ".zip" in file_name:
				# 	compress_file_handler(file_name, leak_download_path)
		
				print(f"[*] File Name: {file_name}")
				logging.info(f"File Name: {file_name}")
				logging.info("File successfully downloaded at: " + str(leak_download_path))		

				await output_monitored_dataleak(leak_download_path)		
			else:
				logging.info("[*] New Media but not .txt, .csv, .rar, .zip")
				
	except Exception as e:
		logging.error(f"Exception: {e}" )
	


# Start the infinite loop to wait for new messages	
async def main():
	print("[*] Telegram monitoring starting")
	await client.run_until_disconnected()

# TODO: Learn how to Async IO work
with client:
	client.loop.run_until_complete(main())
