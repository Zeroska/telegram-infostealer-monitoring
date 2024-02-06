from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from os.path import join, dirname
import os 
from dotenv import load_dotenv

# Was recommend

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
api_hash = os.getenv("api_hash")
api_id = os.getenv("api_id")
phone_number = os.getenv("phone_number")


with TelegramClient(StringSession(), api_id, api_hash) as client:
    print(client.session.save())