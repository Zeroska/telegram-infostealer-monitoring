from telethon import TelegramClient, events, sync
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.types import Message
import fileinput
import logging
import time
import json
import os
import platform
import schedule
import threading
import asyncio
from zipfile import ZipFile
from rarfile import RarFile
from os.path import join, dirname
from dotenv import load_dotenv
import pymsteams

# Logging
logging.basicConfig(
    format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s', level=logging.INFO,
    filename="telegram_monitoring.log", encoding='utf-8')

# Env Configuration
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
api_hash = os.getenv("api_hash")
api_id = os.getenv("api_id")
phone_number = os.getenv("phone_number")
download_path = os.getenv("download_path")
webhook_url = os.getenv("webhook_url")
myTeamsMessage = pymsteams.async_connectorcard(webhook_url)

if os.path.exists("monitored_wordlist.txt"):
    with open("monitored_wordlist.txt", "r") as keyword_list:
        MONITORED_WORDLIST = keyword_list.readlines()
        MONITORED_WORDLIST = map(lambda s: s.strip(), MONITORED_WORDLIST)
else:
    print(f"Please create monitored_wordlist.txt first before running this script")
    exit()

# Start the client
client = TelegramClient('anon', int(api_id), api_hash)


def lines_that_equal(line):
    for key in MONITORED_WORDLIST:
        if key in line:
            return True
    return False


def handle_zip(file_path):
    try:
        with ZipFile(file_path) as zip:
            # Download path is global variable, extract to download_path
            zip.extractall(download_path)
        logging.info(f"ZIP extracted at: {download_path}")
    except Exception as e:
        logging.error(f"Error at handle_zip: {e}")


def handle_rar(file_path):
    try:
        with RarFile(file_path) as rar:
            if not rar.needs_password():
                rar.extractall(download_path)
        logging.info(f"RAR extracted at: {download_path}")
    except Exception as e:
        logging.error(f"Error at handle_rar: {e}")

    # This function is used after the compressed file has download,


def compress_file_handler(file_name, file_path):
    if ".rar" in file_name:
        logging.info(f"RAR file received: {file_name}")
        # If rar, on Windows then using windows rar if they have it -> extract the file using the password if needed
        handle_rar(file_path)
    elif "zip" in file_name:
        logging.info(f"ZIP file received: {file_name}")
        handle_zip(file_path)
    else:
        print("[*] Compressed file type not supported ")


# You can disable this function as you pleases, if you send your log to another place
async def output_monitored_data_leak(downloaded_files):
    try:
        logging.info("File downloaded and checking for data leak")
        print("[*] File downloaded and checking for data leak")
        list_of_leaked_creds = []
        for line in fileinput.input([downloaded_files], encoding="utf8"):
            if lines_that_equal(line):
                print(f"[*] Data leaked found: {line}")
                logging.info(f"Data leaked found: {line}")
                line.strip("\n")
                list_of_leaked_creds.append(line)
                # You can output it to another channel (teams chat, telegram chat or discord by using webhook)
                with open("leaked.txt", "w") as data:
                    data.write(str(line))
                    data.close()
        # Sadly I'm not a developer :">
        if len(list_of_leaked_creds) > 0:
            myTeamsMessage.color("#B70000")
            myTeamsMessage.title("Data Leak Found in Stealer Logs")
            myTeamsMessage.text(f"Data leaked found: {list_of_leaked_creds} Please validate it, or create a ticket")
            await myTeamsMessage.send()
        else:
            myTeamsMessage.color("#080000")
            myTeamsMessage.title("New Data Leak Downloaded")
            myTeamsMessage.text(f"Comptuter Name: {platform.node()}   \nOperating Sytem: {platform.system()}   \nFile successfully downloaded at: " + str(downloaded_files)  +  "    \nChecking successfully and found nothing")
            await myTeamsMessage.send()
            logging.info("Checking successfully and found nothing")
            print("[*] Checking successfully and found nothing")
        fileinput.close()
    except Exception as e:
        fileinput.close()
        logging.info(f"output_monitored_data_leak error: {e}")


def progress_bar(current, total):
    print('Downloaded', current, 'out of', total, 'bytes: {:.2%}'.format(current / total))


# This function detect message has telegram link and join that channel, if the link is not telegram, store it for
# further review or statistic
def detect_telegram_link(urls_list: list):
    # check for telegram channels link
    telegram_url_extracted_list = []
    url_need_to_be_review_list = []
    for url in urls_list:
        if "t.me/" in url:
            telegram_url_extracted_list.append(url)
        else:
            url_need_to_be_review_list.append(url)
    return telegram_url_extracted_list, url_need_to_be_review_list


def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)


async def daily_run_report():
    print("[*] Start daily report")
    lines_seen = set()
    input_file = "./need_to_review_url.txt"
    output_file = "daily_report.txt"
    with open(output_file, 'w') as out_file:
        with open(input_file, 'r') as in_file:
            for line in in_file:
                if line not in lines_seen:
                    out_file.write(line)
                    lines_seen.add(line)

    myTeamsMessage.color("")
    myTeamsMessage.title("Telegram monitoring daily statistic")
    myTeamsMessage.text("")

    return


# TODO: Filter benign URL and duplicated
def filter_url(urls_list: list[str]):
    black_list_domain = ["https://ift.tt/"]
    # Remove duplicated line first
    if os.path.exists("need_to_review_url.txt"):
        with open("need_to_review_url.txt", "r") as data:
            review_url_list = data.readlines()
            review_url_list = map(lambda s: s.strip(), review_url_list)  # Remove newline (\n) from reading the file
            for url in urls_list:
                if url in review_url_list:
                    urls_list.remove(url)
                    logging.info(f"Removed duplicated URL: {url}")
        # Remove black listed url from the list, which 
        for url in urls_list:
            if url in black_list_domain:
                urls_list.remove(url)
                logging.info(f"Removed black listed URL: {url}")
    return urls_list


def contain_url_in_message(event: Message):
    telegram_message = event.message.message.split()
    urls = []
    for i in telegram_message:
        if i.startswith("https:") or i.startswith("http:"):
            urls.append(i)
            logging.info(f"Found URL in Data Leak Message: {i}")
    return urls


async def join_telegram_channel(telegram_url_list: list):
    try:
        # If no url harvested -> just return and pass to the check
        if telegram_url_list is None:
            return
        for channel in telegram_url_list:
            updates = await client(JoinChannelRequest(channel))
            logging.info(f"Joined URL:{channel} Updates: {updates}")
    except Exception as e:
        logging.error(f"Exception in join_telegram_channel: {e}")


async def store_review_url(review_url: list):
    try:
        if review_url is None:
            return
        # Check duplicate URL and black list URL first
        filtered_review_url = filter_url(review_url)
        with open("need_to_review_url.txt", "a") as data:
            for url in filtered_review_url:
                data.write(str(url) + "\n")
            data.close()
    except Exception as e:
        logging.error(f"Error at store_review_url: {e}")


@client.on(events.NewMessage())
async def handle_new_data_leak_message(event: Message):
    try:
        print(f"[*] New Message Received")
        urls_list = contain_url_in_message(event)
        telegram_url, review_url = detect_telegram_link(urls_list)
        
        await join_telegram_channel(telegram_url)
        await store_review_url(review_url)
        if event.document is not None:
            print(event.message.media.document)
            print("File Name[0]: " + str(event.message.media.document.attributes[0].file_name))
            file_name = str(event.message.media.document.attributes[0].file_name).lower()
            
            # lower all char to normallize the data
            if file_name.endswith((".txt",".csv")):
                leak_download_path = await client.download_media(event.message.media, f"{file_name}",
                                                                 progress_callback=progress_bar)
                # Check the newest data leak downloaded file has the important credential that we care about
                # if ".rar" or ".zip" in file_name:
                # 	compress_file_handler(file_name, leak_download_path)

                print(f"[*] File Name: {file_name}")
                logging.info(f"File Name: {file_name}")
                logging.info("File successfully downloaded at: " + str(leak_download_path))

                await output_monitored_data_leak(leak_download_path)
                # Check whether the new data set just download has the monitored keyword
               
            else:
                logging.info(f"[*] New Media but not .txt, .csv, .rar, .zip: {file_name}")
    except Exception as e:
        logging.error(f"Exception: {e}")


# Start the infinite loop to wait for new messages	
async def main():
    print("[*] Telegram monitoring starting")
    # await client.run_until_disconnected()
    # schedule.every().day.at("00:00").do(daily_run_report)
    # scheduler_thread = threading.Thread(target=run_scheduler)
    # scheduler_thread.start()
    while True:
        await asyncio.sleep(1)


# TODO: Learn how to Async IO work
with client:
    client.loop.run_until_complete(main())
