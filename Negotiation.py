from Binance import client

def openBuyCondition(candleClose, demaLow):
    if(candleClose < demaLow):
        return True
    else:
        pass


def closeBuyCondition(candleClose, demaHigh):
    if(candleClose > demaHigh):
        return True
    else:
        pass


def openSellCondition(candleClose, demaHigh):
    if(candleClose > demaHigh):
        return True
    else:
        pass


def closeSellCondition(candleClose, demaLow):
    if(candleClose < demaLow):
        return True
    else:
        pass


def openPosition(ticker, size, side):

    try:

        client.futures_cancel_all_open_orders(symbol=ticker)

        client.futures_change_leverage(symbol=ticker, leverage=100)

        client.futures_create_order(
            symbol=ticker, side=side, type='MARKET', quantity=size)

    except Exception as e:
        return e


def closePosition(ticker, size, side):
    try:

        client.futures_change_leverage(symbol=ticker, leverage=100)

        orderFullfilled = client.futures_create_order(
            symbol=ticker, side=side, type='MARKET', quantity=size)

        return orderFullfilled

    except Exception as e:
        return e
