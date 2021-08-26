
from Binance import cliente
import ta
import json
import time
import talib
import websocket
import numpy as np
import pandas as pd
from binance.enums import *

from Negociacao import abrirPosicao, condicaoAbrirCompra, condicaoFecharCompra, condicaoAbrirVenda, condicaoFecharVenda, operacoesAbertas

# SOCKET = "wss://fstream.binance.com/ws/btcusdt@kline_1m"
SOCKET = "wss://stream.binance.com:9443/ws/btcusdt@kline_1m"

precoEntrada = 0.0
resultadoAcumulado = 0.0


def onOpen(ws):
    print("Conexão aberta")


def onClose(ws):
    print("Conexão fechada")


def onMessage(ws, mensagem):
    mensagemJson = json.loads(mensagem)

    candle = mensagemJson['k']

    candleFechado = candle['x']

    if candleFechado:

        horario = pd.to_datetime(candle['T'], unit='ms')

        obterSinal(minima=candle['l'], maxima=candle['h'],
                   fechamento=candle['c'], horario=horario)


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


def obterSinal(minima, maxima, fechamento, horario):
    global precoEntrada
    global resultadoAcumulado

    dados = np.array(cliente.get_klines(
        symbol='BTCUSDT', interval=KLINE_INTERVAL_1MINUTE))

    df = binanceDataFrame(dados, dados)

    df.set_index('Open Time', inplace=True)

    df = df[['Open', 'High', 'Low', 'Close']]

    df = df[:-1]

    high, low = df['High'], df['Low']

    demaHigh = talib.DEMA(high, 11)

    demaLow = talib.DEMA(low, 11)

    centavosLow = float(minima.split('.')[1])
    centavosHigh = float(maxima.split('.')[1])

    print('Fechamento: {} | DemaHigh: {} | DemaLow: {} | Horário: {}'.format(
        fechamento, demaHigh[-1], demaLow[-1], horario))

    if len(operacoesAbertas) == 0:
        # print('Aguardando sinal...')
        if float(fechamento) < demaLow[-1] and centavosLow == 0:
            # abrirPosicao(ativo=ativoCesta, lote=0.5,
            #              lado=SIDE_BUY, preco=precoLimit)

            # remover quando for operar em conta real
            operacoesAbertas.append('comprado')
            precoEntrada = float(fechamento)

            file = open("operacoes.txt", "a")
            file.write("COMPRADO - Horário entrada: %s" % horario)
            file.write("\n")
            file.close()

            print('----------------------------------')
            print("OPERAÇÃO DE COMPRA ABERTA")
            print("PREÇO: {}".format(fechamento))
            print("HORÁRIO: {}".format(horario))
            print('----------------------------------')

        elif float(fechamento) > demaHigh[-1] and centavosHigh == 0:
            # abrirPosicao(ativo=ativoCesta, lote=0.5,
            #              lado=SIDE_BUY, preco=precoLimit)

            # remover quando for operar em conta real
            operacoesAbertas.append('vendido')
            precoEntrada = float(fechamento)

            file = open("operacoes.txt", "a")
            file.write("VENDIDO - Horário entrada: %s" % horario)
            file.write("\n")
            file.close()

            print('----------------------------------')
            print("OPERAÇÃO DE VENDA ABERTA")
            print("PREÇO: {}".format(fechamento))
            print("HORÁRIO: {}".format(horario))
            print('----------------------------------')

    else:
        if operacoesAbertas[0] == 'comprado':
            if float(fechamento) > demaHigh[-1]:

                operacoesAbertas.pop()

                resultadoAcumulado += float(fechamento) - precoEntrada

                file = open("operacoes.txt", "a")
                file.write("COMPRA FECHADA - Horário saída: %s" % horario)
                file.write("\n")
                file.close()

                print('---------------------------------------------')
                print("OPERAÇÃO DE COMPRA FINALIZADA")
                print("PREÇO: {}".format(float(fechamento)))
                print("HORÁRIO: {}".format(horario))
                print("RESULTADO ACUMULADO: {}".format(resultadoAcumulado))
                print('---------------------------------------------')

        elif operacoesAbertas[0] == 'vendido':
            if float(fechamento) < demaLow[-1]:

                operacoesAbertas.pop()

                resultadoAcumulado += precoEntrada - float(fechamento)

                file = open("operacoes.txt", "a")
                file.write("VENDA FECHADA - Horário saída: %s" % horario)
                file.write("\n")
                file.close()

                print('---------------------------------------------')
                print("OPERAÇÃO DE VENDA FINALIZADA")
                print("PREÇO: {}".format(float(fechamento)))
                print("HORÁRIO: {}".format(horario))
                print("RESULTADO ACUMULADO: {}".format(resultadoAcumulado))
                print('---------------------------------------------')


ws = websocket.WebSocketApp(SOCKET, on_open=onOpen,
                            on_close=onClose, on_message=onMessage)
ws.run_forever()
