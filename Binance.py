
import ta
import json
import time
import websocket
import numpy as np
import pandas as pd
from binance.enums import *
from binance.client import Client, requests

SOCKET = "wss://stream.binance.com:9443/ws/btcusdt@kline_1m"

cliente = Client('o1Q5E6C5rpqYBm5NcXimI75Y3nbcim9wXq3sH3O76TSg6vrTwBSRMx1yCGOiHdOo',
                 'Hlpmd3TlY0H8LsPD4PZOaO5CUZnibIONTHFF3cO12ADSLz5FDRbXRZyM41ArRHCw')

operacoesAbertas = []


def abrirPosicao(ativo, lote, lado):

    try:

        cliente.futures_change_leverage(symbol=ativo, leverage=100)

        ordem = cliente.futures_create_order(
            symbol=ativo, side=lado, type='MARKET', quantity=lote)

        operacoesAbertas.append(ativo)

    except Exception as e:
        return e


def fecharPosicao(ativo, lote, lado):
    try:

        cliente.futures_change_leverage(symbol=ativo, leverage=100)

        cliente.futures_create_order(
            symbol=ativo, quantity=lote, side=lado, type='MARKET')

    except Exception as e:
        return e


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


cesta = ['ETHUSDT']


def obterSinal():

    for ativoCesta in cesta:

        dados = np.array(cliente.futures_klines(
            symbol=ativoCesta, interval=KLINE_INTERVAL_1MINUTE))
        df = binanceDataFrame(dados, dados)
        df.set_index('Open Time', inplace=True)
        df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
        open, high, low, close = df['Open'], df['High'], df['Low'], df['Close']

        rsi = ta.momentum.rsi(close, 2)

        mediaMovel = ta.trend.sma_indicator(close, 5)

        tick = cliente.futures_symbol_ticker(symbol=ativoCesta)

        print(tick)

        precoAtual = float(tick['price'])
        centavos = tick['price'].split('.')

        if len(operacoesAbertas) == 0:
            if rsi[-1] <= 5.0 and centavos[1] == '0':
                abrirPosicao(ativo=ativoCesta, lote=10, lado=SIDE_BUY)
                print('----------------------------------')
                print("COMPRADO EM: {}".format(ativoCesta))
                print('----------------------------------')

        else:
            for operacao in operacoesAbertas:
                if operacao == ativoCesta:

                    infoPosicao = cliente.futures_position_information(
                        symbol=operacao)
                    tick = cliente.futures_symbol_ticker(symbol=operacao)

                    precoAtual = float(tick['price'])
                    quantidade = infoPosicao[0]['positionAmt']

                    if precoAtual > mediaMovel[-1]:
                        fecharPosicao(ativo=operacao,
                                      lote=quantidade, lado=SIDE_SELL)
                        operacoesAbertas.remove(operacao)
                        print('---------------------------------------------')
                        print("OPERAÇÃO FINALIZADA EM: {}".format(operacao))
                        print('---------------------------------------------')

            if rsi[-1] <= 5.0 and centavos[1] == '0':
                infoPosicao = cliente.futures_position_information(
                    symbol=ativoCesta)

                quantidade = float(infoPosicao[0]['positionAmt'])

                if quantidade != 0.0:
                    print("Condição de compra acionada, mas já existe uma posição aberta em {}".format(
                        ativoCesta))
                else:
                    abrirPosicao(ativo=ativoCesta, lote=0.5, lado=SIDE_BUY)
                    print('----------------------------------')
                    print("COMPRADO EM: {}".format(ativoCesta))
                    print('----------------------------------')


def onOpen(ws):
    print("Conexão aberta")


def onClose(ws):
    print("Conexão fechada")


def onMessage(ws, mensagem):
    mensagemJson = json.loads(mensagem)

    candle = mensagemJson['k']

    candleFechado = candle['x']  # retorna True se o candle acabou de fechar

    if candleFechado:

        horarioNegociacao = pd.to_datetime(candle['T'], unit='ms')

        obterSinal()


ws = websocket.WebSocketApp(SOCKET, on_open=onOpen,
                            on_close=onClose, on_message=onMessage)
ws.run_forever()
