
import ta
import json
import time
import websocket
import numpy as np
import pandas as pd
from binance.enums import *
from binance.client import Client, requests
# import config

# SOCKET = "wss://fstream.binance.com/ws/btcusdt@kline_1m"
SOCKET = "wss://stream.binance.com:9443/ws/btcusdt@kline_1m"

cliente = Client('o1Q5E6C5rpqYBm5NcXimI75Y3nbcim9wXq3sH3O76TSg6vrTwBSRMx1yCGOiHdOo',
                 'Hlpmd3TlY0H8LsPD4PZOaO5CUZnibIONTHFF3cO12ADSLz5FDRbXRZyM41ArRHCw')

operacoesAbertas = []


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

        obterSinal(minima=candle['l'], fechamento=candle['c'], horario=horario)

    else:

        infoPosicao = cliente.futures_position_information(symbol='BTCUSDT')

        pnl = float(infoPosicao[0]['unRealizedProfit'])
        quantidade = infoPosicao[0]['positionAmt']

        if pnl >= 100.00:
            fecharPosicao(ativo='BTCUSDT', lote=quantidade, lado=SIDE_SELL)
            operacoesAbertas.remove('BTCUSDT')


def abrirPosicao(ativo, lote, lado, preco):

    try:

        cliente.futures_cancel_all_open_orders(symbol=ativo)

        cliente.futures_change_leverage(symbol=ativo, leverage=100)

        ordem = cliente.futures_create_order(
            symbol=ativo, side=lado, type='LIMIT', quantity=lote, timeInForce='GTC', price=preco)

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


def condicaoCompra(fechamento, ma21Fechamento, ma3Minimas, centavos):
    if(fechamento < ma3Minimas[-1]):
        return True
    else:
        pass


cesta = ['BTCUSDT']


def obterSinal(minima, fechamento, horario):

    for ativoCesta in cesta:

        dados = np.array(cliente.futures_klines(
            symbol=ativoCesta, interval=KLINE_INTERVAL_1MINUTE))

        df = binanceDataFrame(dados, dados)

        df.set_index('Open Time', inplace=True)

        df = df[['High', 'Low', 'Close']]

        high, low, close = df['High'], df['Low'], df['Close']

        mediaMovelVinteUmFechamentos = ta.trend.sma_indicator(close, 21)

        mediaMovelTresUltimasMinimas = ta.trend.sma_indicator(low, 3)

        mediaMovelTresUltimasMaximas = ta.trend.sma_indicator(high, 3)

        precoLimit = float(fechamento) - 1.00

        centavos = minima.split('.')

        file = open("operacoes.txt", "a")
        file.write("Horário entrada: %s" % horario)
        file.close()

        print('Fechamento: {} | Centavos {} | Horário: {}'.format(
            fechamento, float(centavos[1]), horario))

        if len(operacoesAbertas) == 0:
            if condicaoCompra(fechamento=float(fechamento), ma21Fechamento=mediaMovelVinteUmFechamentos, ma3Minimas=mediaMovelTresUltimasMinimas, centavos=float(centavos[1])):
                # abrirPosicao(ativo=ativoCesta, lote=0.5,
                #              lado=SIDE_BUY, preco=precoLimit)

                # remover quando for operar em conta real
                operacoesAbertas.append(ativoCesta)

                file = open("operacoes.txt", "a")

                file.write("Horário entrada: %d" % 1)

                print('----------------------------------')
                print("COMPRADO EM: {}".format(ativoCesta))
                print("PREÇO: {}".format(precoLimit))
                print("HORÁRIO: {}".format(horario))
                print('----------------------------------')

                file.close()

        else:
            for operacao in operacoesAbertas:
                if operacao == ativoCesta:

                    infoPosicao = cliente.futures_position_information(
                        symbol=operacao)
                    tick = cliente.futures_symbol_ticker(symbol=operacao)

                    quantidade = infoPosicao[0]['positionAmt']

                    if float(fechamento) > mediaMovelTresUltimasMaximas[-1]:
                        # fecharPosicao(ativo=operacao,
                        #               lote=quantidade, lado=SIDE_SELL)
                        operacoesAbertas.remove(operacao)
                        print('---------------------------------------------')
                        print("OPERAÇÃO FINALIZADA EM: {}".format(operacao))
                        print("PREÇO: {}".format(float(fechamento)))
                        print("HORÁRIO: {}".format(horario))
                        print('---------------------------------------------')

            if condicaoCompra(fechamento=fechamento, ma21Fechamento=mediaMovelVinteUmFechamentos, ma3Minimas=mediaMovelTresUltimasMinimas, centavos=centavos):
                infoPosicao = cliente.futures_position_information(
                    symbol=ativoCesta)

                quantidade = float(infoPosicao[0]['positionAmt'])

                if quantidade != 0.0:
                    print("Condição de compra acionada, mas já existe uma posição aberta em {}".format(
                        ativoCesta))
                else:
                    # abrirPosicao(ativo=ativoCesta, lote=0.5,
                    #              lado=SIDE_BUY, preco=precoLimit)
                    print('----------------------------------')
                    print("COMPRADO EM: {}".format(ativoCesta))
                    print('----------------------------------')


ws = websocket.WebSocketApp(SOCKET, on_open=onOpen,
                            on_close=onClose, on_message=onMessage)
ws.run_forever()
