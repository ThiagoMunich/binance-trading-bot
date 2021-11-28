
from Binance import cliente
import json
import time
import talib
import websocket
import datetime
import numpy as np
import pandas as pd
from binance.enums import *

from Binance import cliente


from Negociacao import abrirPosicao, fecharPosicao, condicaoAbrirCompra, condicaoFecharCompra, condicaoAbrirVenda, condicaoFecharVenda, operacoesAbertas

from Telegram import mensagemTelegram

# SOCKET = "wss://fstream.binance.com/ws/btcusdt@kline_1m"
SOCKET = "wss://stream.binance.com:9443/ws/btcusdt@kline_5m"

demaLow = 0.0
stopLoss = 0.0
demaHigh = 0.0
precoEntrada = 0.0
parcialVenda = False
parcialCompra = False
resultadoAcumulado = 0.0

agora = datetime.datetime.utcnow()
teste = datetime.datetime.strftime(agora, '%Y/%m/%d %H:%M:00')


def onOpen(ws):
    print("Conexão aberta")


def onClose(ws):
    print("Conexão fechada")


def onMessage(ws, mensagem):
    global stopLoss
    global precoEntrada
    global parcialVenda
    global parcialCompra
    global resultadoAcumulado

    mensagemJson = json.loads(mensagem)

    candle = mensagemJson['k']

    candleFechado = candle['x']

    # info = cliente.futures_position_information(symbol='BTCUSDT')

    # print(info[0])

    # info = cliente.futures_account_trades(symbol='BTCUSDT')

    # print(info)

    if candleFechado:

        obterSinal()


def mensagemSaidaOperacao(preco, atual, lado):

    horarioFormatado = datetime.datetime.strftime(agora, '%d/%m/%Y %H:%M:00')

    print('---------------------------------------------')
    print("OPERAÇÃO DE {} FINALIZADA".format(lado))
    print("PREÇO: {}".format(preco))
    print("HORÁRIO: {}".format(horarioFormatado))
    print("RESULTADO ACUMULADO: {}".format(resultadoAcumulado))
    print("RESULTADO DA OPERAÇÃO: {}".format(atual))
    print('---------------------------------------------')


def mensagemEntradaOperacao(preco, lado):

    horarioFormatado = datetime.datetime.strftime(agora, '%d/%m/%Y %H:%M:00')

    print('----------------------------------')
    print("OPERAÇÃO DE {} ABERTA".format(lado))
    print("PREÇO: {}".format(preco))
    print("SL: {}".format(stopLoss))
    print("HORÁRIO: {}".format(horarioFormatado))
    print('----------------------------------')


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


def montarDataframe(esperarFechamento):

    dados = np.array(cliente.get_klines(
        symbol='BTCUSDT', interval=KLINE_INTERVAL_5MINUTE))

    df = binanceDataFrame(dados, dados)

    df.set_index('Open Time', inplace=True)

    df = df[['Open', 'High', 'Low', 'Close', 'Volume']]

    if(esperarFechamento):
        df = df[:-1]

    high, low, close = df['High'], df['Low'], df['Close']

    demaHigh = talib.DEMA(high, 11)

    demaLow = talib.DEMA(low, 11)

    if(esperarFechamento):
        return high[-1], low[-1], close[-1], demaHigh[-1], demaLow[-1]
    else:
        return demaHigh[-1], demaLow[-1]


def obterSinal():
    global stopLoss
    global precoEntrada
    global parcialVenda
    global parcialCompra
    global resultadoAcumulado

    # pra dar tempo de pegar os dados do candle que tá aberto, e depois removê-lo
    # mantendo assim somente até o ultimo candle fechado
    time.sleep(3)

    agora = datetime.datetime.utcnow()
    horarioFormatado = datetime.datetime.strftime(agora, '%d/%m/%Y %H:%M:00')

    info = cliente.futures_position_information(symbol='BTCUSDT')

    high, low, close, demaHigh, demaLow = montarDataframe(
        esperarFechamento=True)

    centavosLow = float(str(low).split('.')[1])
    centavosHigh = float(str(high).split('.')[1])

    if info[0]['entryPrice'] == '0.0':
        print('Aguardando sinal...')
        if close < demaLow and centavosLow == 0.0:
            abrirPosicao(ativo='BTCUSDT', lote=0.01, lado='BUY')

            mensagem = 'COMPRADO\n\nHorário entrada: {}'.format(
                horarioFormatado)

            mensagemTelegram(mensagem=mensagem)

            mensagemEntradaOperacao(preco=close, lado='COMPRA')

        elif close > demaHigh and centavosHigh == 0.0:
            abrirPosicao(ativo='BTCUSDT', lote=0.01, lado='SELL')

            mensagem = 'VENDIDO\n\nHorário entrada: {}'.format(
                horarioFormatado)

            mensagemTelegram(mensagem=mensagem)

            mensagemEntradaOperacao(preco=close, lado='VENDA')

    else:
        posicaoAtual = cliente.futures_account_trades(symbol='BTCUSDT')

        if posicaoAtual[0]['side'] == 'BUY':
            print('Posição de compra ainda aberta.')
            if close > demaHigh:

                fecharPosicao(ativo='BTCUSDT', lote=0.01, lado='SELL')

                mensagem = 'COMPRA FECHADA\n\nHorário saída: {}'.format(
                    horarioFormatado)

                mensagemTelegram(mensagem=mensagem)

        elif posicaoAtual[0]['side'] == 'SELL':
            print('Posição de venda ainda aberta.')
            if close < demaLow:

                fecharPosicao(ativo='BTCUSDT', lote=0.01, lado='BUY')

                mensagem = 'VENDA FECHADA\n\nHorário saída: {}'.format(
                    horarioFormatado)

                mensagemTelegram(mensagem=mensagem)


ws = websocket.WebSocketApp(SOCKET, on_open=onOpen,
                            on_close=onClose, on_message=onMessage)
ws.run_forever()
