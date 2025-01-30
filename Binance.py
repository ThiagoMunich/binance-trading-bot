"""
Binance API Client Configuration

This module initializes the Binance API client using credentials stored in environment variables.
It provides a configured client instance for interacting with the Binance cryptocurrency exchange.

Requirements:
    - python-binance package
    - python-dotenv package
    - .env file containing BINANCE_API_KEY and BINANCE_API_SECRET

Usage:
    Import the configured client in other modules:
    from Binance import client
"""

import os
from dotenv import load_dotenv
from binance.client import Client

load_dotenv()  

# Initialize Binance client with API credentials from environment variables
client = Client(
    os.getenv('BINANCE_API_KEY'),
    os.getenv('BINANCE_API_SECRET')
)