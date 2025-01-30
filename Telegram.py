import requests
import os
from dotenv import load_dotenv

load_dotenv()  

"""
A simple Telegram messaging module that provides functionality to send messages
to a specified Telegram chat using a bot token.

Requires environment variables:
    TELEGRAM_TOKEN: Your Telegram bot father token
    TELEGRAM_CHAT_ID: The chat ID where messages will be sent
"""

def sendTelegramMessage(message):
    """
    Sends a message to a Telegram chat using bot credentials from environment variables.
    
    Args:
        message (str): The message text to be sent
        
    Returns:
        None
        
    Raises:
        Exception: If there's an error sending the message
    """
    token = os.getenv('TELEGRAM_TOKEN')
    chatId = os.getenv("TELEGRAM_CHAT_ID")

    try:
        data = {"chat_id": chatId, "text": message}
        url = "https://api.telegram.org/bot{}/sendMessage".format(token)
        requests.post(url, data)
    except Exception as e:
        print("Error while sending message:", e)
