import requests
import os
from dotenv import load_dotenv

load_dotenv()  

def sendTelegramMessage(message):
    token = os.getenv('TELEGRAM_TOKEN')
    chatId = os.getenv("TELEGRAM_CHAT_ID")

    try:
        data = {"chat_id": chatId, "text": message}
        url = "https://api.telegram.org/bot{}/sendMessage".format(token)
        requests.post(url, data)
    except Exception as e:
        print("Error while sending message:", e)
