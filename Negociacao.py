from Binance import cliente

operacoesAbertas = []


def condicaoAbrirCompra(fechamento, demaLow, centavosLow):
    if(fechamento < demaLow):
        return True
    else:
        pass


def condicaoFecharCompra(fechamento, demaHigh):
    if(fechamento > demaHigh):
        return True
    else:
        pass


def condicaoAbrirVenda(fechamento, demaHigh, centavosHigh):
    if(fechamento > demaHigh):
        return True
    else:
        pass


def condicaoFecharVenda(fechamento, demaLow):
    if(fechamento < demaLow):
        return True
    else:
        pass


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
