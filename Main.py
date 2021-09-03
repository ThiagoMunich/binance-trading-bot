
from numpy.core.fromnumeric import take
from Binance import cliente
import json
import time
import talib
import websocket
import datetime
import numpy as np
import pandas as pd
from binance.enums import *

from Negociacao import abrirPosicao, condicaoAbrirCompra, condicaoFecharCompra, condicaoAbrirVenda, condicaoFecharVenda, operacoesAbertas

from Telegram import mensagemTelegram

# SOCKET = "wss://fstream.binance.com/ws/btcusdt@kline_1m"
SOCKET = "wss://stream.binance.com:9443/ws/btcusdt@kline_5m"

precoEntrada = 0.0
resultadoAcumulado = 0.0
stopLoss = 0.0

agora = datetime.datetime.utcnow()
teste = datetime.datetime.strftime(agora, '%Y/%m/%d %H:%M:00')


def onOpen(ws):
    print("Conexão aberta")


def onClose(ws):
    print("Conexão fechada")


def onMessage(ws, mensagem):
    global resultadoAcumulado
    global precoEntrada

    horarioFormatado = datetime.datetime.strftime(agora, '%d/%m/%Y %H:%M:00')

    mensagemJson = json.loads(mensagem)

    candle = mensagemJson['k']

    candleFechado = candle['x']

    if candleFechado:

        obterSinal()
    else:
        tick = float(candle['c'])

        if operacoesAbertas[0] == 'comprado':
            if tick < stopLoss:
                print('Stop loss de compra acionado.')

                resultadoAtual = tick - precoEntrada

                resultadoAcumulado += tick - precoEntrada

                msg = 'STOP LOSS COMPRA\n\nHorário saída: {}\n\nResultado da operação: {} USD\n\nResultado acumulado: {} USD'.format(
                    horarioFormatado, round(resultadoAtual, 2), round(resultadoAcumulado, 2))

                mensagemTelegram(mensagem=msg)

                operacoesAbertas.pop()

        elif operacoesAbertas[0] == 'vendido':
            if tick > stopLoss:
                print('Stop loss de venda acionado.')

                resultadoAtual = precoEntrada - tick

                resultadoAcumulado += precoEntrada - tick

                msg = 'STOP LOSS VENDA\n\nHorário saída: {}\n\nResultado da operação: {} USD\n\nResultado acumulado: {} USD'.format(
                    horarioFormatado, round(resultadoAtual, 2), round(resultadoAcumulado, 2))

                mensagemTelegram(mensagem=msg)

                operacoesAbertas.pop()


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


def obterSinal():
    global stopLoss
    global precoEntrada
    global resultadoAcumulado

    # pra dar tempo de pegar os dados do candle que tá aberto, e depois removê-lo
    # mantendo assim somente até o ultimo candle fechado
    time.sleep(3)

    agora = datetime.datetime.utcnow()
    horarioFormatado = datetime.datetime.strftime(agora, '%d/%m/%Y %H:%M:00')

    dados = np.array(cliente.get_klines(
        symbol='BTCUSDT', interval=KLINE_INTERVAL_5MINUTE))

    df = binanceDataFrame(dados, dados)

    df.set_index('Open Time', inplace=True)

    df = df[['Open', 'High', 'Low', 'Close', 'Volume']]

    df = df[:-1]

    high, low, close = df['High'], df['Low'], df['Close']

    demaHigh = talib.DEMA(high, 11)

    demaLow = talib.DEMA(low, 11)

    atr = talib.ATR(high, low, close, 11)

    differeceBetweenCloseAndLow = close[-1] - low[-1]
    differeceBetweenCloseAndHigh = high[-1] - close[-1]

    centavosLow = float(str(low[-1]).split('.')[1])
    centavosHigh = float(str(high[-1]).split('.')[1])

    # print('Fechamento: {} | DemaHigh: {} | DemaLow: {} | Horário: {}'.format(
    #     close[-1], demaHigh[-1], demaLow[-1], horario))

    if len(operacoesAbertas) == 0:
        print('Aguardando sinal...')
        if close[-1] < demaLow[-1] and centavosLow == 0 and differeceBetweenCloseAndLow < 100:
            # abrirPosicao(ativo=ativoCesta, lote=0.5,
            #              lado=SIDE_BUY, preco=precoLimit)

            # remover quando for operar em conta real
            operacoesAbertas.append('comprado')
            precoEntrada = close[-1]
            stopLoss = low[-1] - atr[-1] * 0.1

            mensagem = 'COMPRADO\n\nHorário entrada: {}'.format(
                horarioFormatado)

            mensagemTelegram(mensagem=mensagem)

            mensagemEntradaOperacao(preco=close[-1], lado='COMPRA')

        elif close[-1] > demaHigh[-1] and centavosHigh == 0 and differeceBetweenCloseAndHigh < 100:
            # abrirPosicao(ativo=ativoCesta, lote=0.5,
            #              lado=SIDE_BUY, preco=precoLimit)

            # remover quando for operar em conta real
            operacoesAbertas.append('vendido')
            precoEntrada = close[-1]
            stopLoss = high[-1] + atr[-1] * 0.1

            mensagem = 'VENDIDO\n\nHorário entrada: {}'.format(
                horarioFormatado)

            mensagemTelegram(mensagem=mensagem)

            mensagemEntradaOperacao(preco=close[-1], lado='VENDA')

    else:
        if operacoesAbertas[0] == 'comprado':
            print('Posição de compra ainda aberta.')
            if close[-1] > demaHigh[-1]:

                operacoesAbertas.pop()

                resultadoAtual = close[-1] - precoEntrada
                resultadoAcumulado += close[-1] - precoEntrada

                mensagem = 'COMPRA FECHADA\n\nHorário saída: {}\n\nResultado da operação: {} USD\n\nResultado acumulado: {} USD'.format(
                    horarioFormatado, round(resultadoAtual, 2), round(resultadoAcumulado, 2))

                mensagemTelegram(mensagem=mensagem)

                mensagemSaidaOperacao(
                    preco=close[-1], atual=resultadoAtual, lado='COMPRA')

        elif operacoesAbertas[0] == 'vendido':
            print('Posição de venda ainda aberta.')
            if close[-1] < demaLow[-1]:

                operacoesAbertas.pop()

                resultadoAtual = precoEntrada - close[-1]
                resultadoAcumulado += precoEntrada - close[-1]

                mensagem = 'VENDA FECHADA\n\nHorário saída: {}\n\nResultado da operação: {} USD\n\nResultado acumulado: {} USD'.format(
                    horarioFormatado, round(resultadoAtual, 2), round(resultadoAcumulado, 2))

                mensagemTelegram(mensagem=mensagem)

                mensagemSaidaOperacao(
                    preco=close[-1], atual=resultadoAtual, lado='VENDA')


ws = websocket.WebSocketApp(SOCKET, on_open=onOpen,
                            on_close=onClose, on_message=onMessage)
ws.run_forever()
