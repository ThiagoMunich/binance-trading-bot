import os
from dotenv import load_dotenv
from binance.client import Client

load_dotenv()  

client = Client(
    os.getenv('BINANCE_API_KEY'),
    os.getenv('BINANCE_API_SECRET')
)