from telethon import TelegramClient, events, sync
from telethon import errors
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.types import Message
import fileinput
import logging
import re
import os, time, platform
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


def search_keyword(line):
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


def compress_file_handler(file_name: str, file_path: str):
    if file_name.lower().endswith(".rar"):
        logging.info(f"RAR file received: {file_name}")
        # If rar, on Windows then using windows rar if they have it -> extract the file using the password if needed
        handle_rar(file_path)
    elif file_name.lower().endswith(".zip"):
        logging.info(f"ZIP file received: {file_name}")
        handle_zip(file_path)
    else:
        print("[*] Compressed file type not supported ")


async def send_ms_team_dataleak_found(list_of_leaked_creds):
    myTeamsMessage.color("#B70000")
    myTeamsMessage.title("Data Leak Found in Stealer Logs")
    myTeamsMessage.text(
        f"Data leaked found: {list_of_leaked_creds} Please validate it, or create a ticket")
    await myTeamsMessage.send()


async def send_ms_team_dataleak_downloaded(downloaded_files):
    myTeamsMessage.color("#0000FF")
    myTeamsMessage.title("New Data Leak Downloaded")
    myTeamsMessage.text(f"Comptuter Name: {platform.node()}   \nOperating Sytem: {platform.system()}   \nFile successfully downloaded at: " + str(
        downloaded_files) + "    \nChecking successfully and found nothing")
    await myTeamsMessage.send()

# You can disable this function as you pleases, if you send your log to another place


async def output_monitored_data_leak(downloaded_files):
    # If the downloaded file extentions is .rar or .zip we pass we don't check the content of it
    if downloaded_files.endswith((".rar", ".zip")):
        return
    try:
        logging.info("File downloaded and checking for data leak")
        list_of_leaked_creds = []
        with open(downloaded_files, "rb", encoding="ISO-8859-1") as data_leak_file:
            for line in data_leak_file.readlines():
                line = line.rstrip()
                # Search keyword in the line if true then found the data that leaked
                if search_keyword(line):
                    logging.info(f"Data leaked found: {line}")
                    list_of_leaked_creds.append(line)
                    with open("leaked.txt", "w") as data:
                        data.write(str(line))
                        data.close()
        number_of_leaked_creds_found = len(list_of_leaked_creds)
        if number_of_leaked_creds_found > 0:
            await send_ms_team_dataleak_found(list_of_leaked_creds)
        else:
            await send_ms_team_dataleak_downloaded(downloaded_files)
            logging.info("Checking successfully and found nothing")
    except UnicodeDecodeError:
        logging.error(f"Error: Unable to read file {downloaded_files}. Skipping...")
    except Exception as e:
        logging.error(f"output_monitored_data_leak error: {e}")


def progress_bar(current, total):
    print('Downloaded', current, 'out of', total,
          'bytes: {:.2%}'.format(current / total))


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


def format_line(data):
    # format_line() is use for filter and parse the stealer logs to nicely formatted event which is
    # { "username": "", "password": "", "url": ""} and push this information to any SIEM
    def check_back_url(content):
        url_pattern = r'\w+\.(?:com|net|org|edu|gov|int|mil|biz|info|name|pro|aero|coop|museum|[a-z]{2})\b'
        if re.match(url_pattern, content):
            return True
        return False
    event = {
        "username": "",
        "password": "",
        "url": "",
    }
    line = str(data)
    if line.startswith("http") or line.startswith("www"):
        match = re.search(
            r'(?P<url>https?://[^\s]+)?[: ](?P<username>[^:]+)?:(?P<password>[^:]+)?', line)
        if match:
            event["url"] = match.group('url')
            event["username"] = match.group('username')
            event["password"] = match.group('password')
            return event
        else:
            return line
    else:
        match = re.search(
            r'(?P<username>[^:]+)?:(?P<password>[^:]+)?:(?P<url>[^\s]+)?', line)
        if match:
            if check_back_url(match.group('username')):
                event["url"] = match.group('username')
                event["username"] = match.group('password')
                event["password"] = match.group('url')
                return event
            else:
                event["url"] = match.group('url')
                event["username"] = match.group('username')
                event["password"] = match.group('password')
                return event
        else:
            return line


# This need to be tested againa
def filter_url(urls_list: list[str]):
    black_list_domains = ["https://ift.tt/"]
    if os.path.exists("need_to_review_url.txt"):
        with open("need_to_review_url.txt", "r") as data:
            review_url_list = data.readlines()
            # Remove newline (\n) from reading the file
            review_url_list = map(lambda s: s.strip(), review_url_list)
            for url in urls_list:
                if url in review_url_list:
                    urls_list.remove(url)
                    logging.info(f"Removed duplicated URL: {url}")
        # Remove black listed url from the list, which
        for url in urls_list:
            for domain in black_list_domains:
                if domain in url:
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
        urls_list = contain_url_in_message(event)
        telegram_url, review_url = detect_telegram_link(urls_list)

        # await join_telegram_channel(telegram_url)
        await store_review_url(review_url)
        if event.document is not None:
            print(event.message.media.document)
            print(
                "File Name[0]: " + str(event.message.media.document.attributes[0].file_name))
            file_name = str(
                event.message.media.document.attributes[0].file_name).lower()

            # lower all char to normallize the data, this is the Linux file path
            if file_name.endswith((".txt", ".csv", ".rar", "zip")):
                if file_name.endswith(".rar"):
                    file_name = "leaked_rar/"+file_name
                if file_name.endswith(".zip"):
                    file_name = "leaked_zip/"+file_name
                # download path is in the .env file and the path should end with a splash "/" or "\\" base on the OS
                leak_download_path = await client.download_media(event.message.media, f"{download_path}{file_name}")

                print(f"[*] File Name: {file_name}")
                logging.info(f"File Name: {file_name}")
                logging.info("File successfully downloaded at: " +
                             str(leak_download_path))

                # Check whether the new data set just download has the monitored keyword
                await output_monitored_data_leak(leak_download_path)

            else:
                logging.info(
                    f"[*] New Media but not .txt, .csv, .rar, .zip: {file_name}")
    except errors.FloodWaitError as e:
        print('Flood wait for ', e.seconds)
        time.sleep(e.seconds)
    except Exception as e:
        logging.error(f"Exception: {e}")


# Start the infinite loop to wait for new messages
async def main():
    print("[*] Telegram monitoring starting")
    await client.run_until_disconnected()

with client:
    client.loop.run_until_complete(main())
