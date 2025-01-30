# Binance Trading Bot

A Python-based cryptocurrency trading bot that automatically trades BTC/USDT futures on Binance using DEMA (Double Exponential Moving Average) strategy.
*Note: you can trade other pairs besides BTC/USDT. Just change the ticker param.*

## Features

- Real-time BTC price monitoring via WebSocket
- Automated trading based on DEMA crossover strategy
- Telegram notifications for trade entries and exits
- Position management with leverage
- Error handling and automatic reconnection

## Prerequisites

- Python 3.8+
- Binance Futures account
- Binance API keys ([How to create Binance API keys](https://www.binance.com/en/support/faq/how-to-create-api-360002502072))
- Telegram bot token and chat ID

## Installation

1. Clone the repository:
```
git clone https://github.com/thiagomunich/BinanceBot.git
cd BinanceBot
```

2. Install required packages:
```
pip3 install -r requirements.txt
```

3. Rename the `.env.example` file to `.env` and fill in your credentials:
```
BINANCE_API_KEY="your-binance-api-key"
BINANCE_API_SECRET="your-binance-api-secret"
TELEGRAM_TOKEN="your-telegram-bot-token"
TELEGRAM_CHAT_ID="your-telegram-chat-id"
```
