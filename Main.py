from Binance import client
import json
import time
import talib
import websocket
import datetime
import numpy as np
import pandas as pd
from binance.enums import *

from Binance import client


from Negotiation import openPosition, closePosition

from Telegram import sendTelegramMessage

# this is the websocket for the 5 minute klines
SOCKET = "wss://stream.binance.com:9443/ws/btcusdt@kline_5m"


def onOpen(ws):
    print("Connection opened")


def onClose(ws):
    print("Connection closed")


def onMessage(ws, message):
    messageJson = json.loads(message)
    candle = messageJson['k']
    candleClosed = candle['x']

    if candleClosed:
        getSignal()


def binanceDataFrame(self, klines):
    df = pd.DataFrame(klines.reshape(-1, 12), dtype=float, columns=('Open Time',
                                                                    'Open',
                                                                    'High',
                                                                    'Low',
                                                                    'Close',
                                                                    'Volume',
                                                                    'Close time',
                                                                    'Quote asset volume',
                                                                    'Number of trades',
                                                                    'Taker buy base asset volume',
                                                                    'Taker buy quote asset volume',
                                                                    'Ignore'))

    df['Open Time'] = pd.to_datetime(df['Open Time'], unit='ms')

    return df


def buildDataframe(waitForClose):
    data = np.array(client.get_klines(
        symbol='BTCUSDT', interval=KLINE_INTERVAL_5MINUTE))

    df = binanceDataFrame(data, data)
    df.set_index('Open Time', inplace=True)
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']]

    if(waitForClose):
        df = df[:-1]

    high, low, close = df['High'], df['Low'], df['Close']
    demaHigh = talib.DEMA(high, 11)
    demaLow = talib.DEMA(low, 11)

    if(waitForClose):
        return high[-1], low[-1], close[-1], demaHigh[-1], demaLow[-1]
    else:
        return demaHigh[-1], demaLow[-1]


def getSignal():
    time.sleep(3)

    now = datetime.datetime.utcnow()
    formattedTime = datetime.datetime.strftime(now, '%d/%m/%Y %H:%M:00')

    info = client.futures_position_information(symbol='BTCUSDT')

    high, low, close, demaHigh, demaLow = buildDataframe(waitForClose=True)

    centsLow = float(str(low).split('.')[1])
    centsHigh = float(str(high).split('.')[1])

    if info[0]['entryPrice'] == '0.0':
        print('Waiting for signal...')
        if close < demaLow and centsLow == 0.0:
            openPosition(ativo='BTCUSDT', lote=0.01, lado='BUY')

            message = 'BOUGHT\n\nEntry time: {}'.format(formattedTime)
            sendTelegramMessage(message=message)
            print('BOUGHT')

        elif close > demaHigh and centsHigh == 0.0:
            openPosition(ativo='BTCUSDT', lote=0.01, lado='SELL')

            message = 'SOLD\n\nEntry time: {}'.format(formattedTime)
            sendTelegramMessage(message=message)
            print('SOLD')

    else:
        if float(info[0]['positionAmt']) > 0.0:
            print('Buy position still open.')
            if close > demaHigh:
                orderSent = closePosition(
                    ativo='BTCUSDT', lote=0.01, lado='SELL')
                orderFullfilled = client.futures_get_order(
                    symbol='BTCUSDT', orderId=orderSent['orderId'])

                # Divided by 100 because lot is 0.01
                resultado = (float(orderFullfilled['avgPrice']) -
                             float(info[0]['entryPrice'])) / 100

                message = 'BUY CLOSED\n\nExit time: {}\n\nResult: {}'.format(
                    formattedTime, resultado)
                sendTelegramMessage(message=message)
                print('Buy position closed.')

        elif float(info[0]['positionAmt']) < 0.0:
            print('Sell position still open.')
            if close < demaLow:
                orderSent = closePosition(
                    ativo='BTCUSDT', lote=0.01, lado='BUY')
                orderFullfilled = client.futures_get_order(
                    symbol='BTCUSDT', orderId=orderSent['orderId'])

                # Divided by 100 because lot is 0.01
                resultado = (float(info[0]['entryPrice']) -
                             float(orderFullfilled['avgPrice'])) / 100

                message = 'SELL CLOSED\n\nExit time: {}\n\nResult: {}'.format(
                    formattedTime, resultado)
                sendTelegramMessage(message=message)
                print('Sell position closed.')


ws = websocket.WebSocketApp(SOCKET, on_open=onOpen,
                            on_close=onClose, on_message=onMessage)
ws.run_forever()
