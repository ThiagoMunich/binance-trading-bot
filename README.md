# Binance Trading Bot 🤖

A Python-based cryptocurrency trading bot that automatically trades BTC/USDT futures on Binance using DEMA (Double Exponential Moving Average) strategy.

*Note: you can trade other pairs besides BTC/USDT. Just change the ticker param.*

## ✨ Features

- Real-time BTC price monitoring via WebSocket
- Automated trading based on DEMA crossover strategy
- Telegram notifications for trade entries and exits
- Position management with leverage
- Error handling and automatic reconnection

## ⚙️ Prerequisites

- Python 3.8+
- Binance Futures account
- Binance API keys ([How to create Binance API keys](https://www.binance.com/en/support/faq/how-to-create-api-360002502072))
- Telegram bot token and chat ID ([How to create a Telegram Bot for FREE in Python - Bot Father](https://www.youtube.com/watch?v=URPIZZNr_2M&ab_channel=Indently))

## 🛠️ Installation and running

1. Clone the repository and navigate to the folder:
```
git clone https://github.com/thiagomunich/BinanceBot.git && cd BinanceBot
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

4. Finally run the bot:
```
python3 Main.py
```

## 🔎 How It Works

The bot operates using the following strategy:

1. Monitors BTC/USDT price movements in real-time using 1-minute candles
2. Calculates DEMA indicators for both high and low prices
3. Opens long positions when:
   - Price closes below the low DEMA
   - The cents of the low price are 0.00
4. Opens short positions when:
   - Price closes above the high DEMA
   - The cents of the high price are 0.00
5. Closes positions when price crosses the opposite DEMA
6. Uses 100x leverage for all trades
7. Sends notifications via Telegram for all trade actions

## ⚠️ Risk Warning

This bot is for educational purposes only. Cryptocurrency trading involves substantial risk and may not be suitable for everyone. Never trade with money you cannot afford to lose.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
