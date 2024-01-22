import logging
from zipfile import ZipFile
from rarfile import RarFile
import os, time, platform
from os.path import join, dirname
from dotenv import load_dotenv


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
