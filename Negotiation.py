from Binance import client

def openBuyCondition(candleClose, demaLow):
    """
    Check if conditions are met to open a buy position.
    
    Args:
        candleClose (float): The closing price of the current candle
        demaLow (float): The lower DEMA (Double Exponential Moving Average) value
    
    Returns:
        bool: True if buy condition is met, None otherwise
    """
    if(candleClose < demaLow):
        return True
    else:
        pass


def closeBuyCondition(candleClose, demaHigh):
    """
    Check if conditions are met to close a buy position.
    
    Args:
        candleClose (float): The closing price of the current candle
        demaHigh (float): The higher DEMA value
    
    Returns:
        bool: True if close condition is met, None otherwise
    """
    if(candleClose > demaHigh):
        return True
    else:
        pass


def openSellCondition(candleClose, demaHigh):
    """
    Check if conditions are met to open a sell position.
    
    Args:
        candleClose (float): The closing price of the current candle
        demaHigh (float): The higher DEMA value
    
    Returns:
        bool: True if sell condition is met, None otherwise
    """
    if(candleClose > demaHigh):
        return True
    else:
        pass


def closeSellCondition(candleClose, demaLow):
    """
    Check if conditions are met to close a sell position.
    
    Args:
        candleClose (float): The closing price of the current candle
        demaLow (float): The lower DEMA value
    
    Returns:
        bool: True if close condition is met, None otherwise
    """
    if(candleClose < demaLow):
        return True
    else:
        pass


def openPosition(ticker, size, side):
    """
    Open a new position on Binance Futures.
    
    Args:
        ticker (str): The trading pair symbol (e.g., 'BTCUSDT')
        size (float): The quantity to trade
        side (str): The position side ('BUY' or 'SELL')
    
    Returns:
        Exception: Returns any exception that occurs during execution
    """
    try:
        client.futures_cancel_all_open_orders(symbol=ticker)
        client.futures_change_leverage(symbol=ticker, leverage=100)
        client.futures_create_order(
            symbol=ticker, side=side, type='MARKET', quantity=size)
    except Exception as e:
        return e


def closePosition(ticker, size, side):
    """
    Close an existing position on Binance Futures.
    
    Args:
        ticker (str): The trading pair symbol (e.g., 'BTCUSDT')
        size (float): The quantity to close
        side (str): The position side ('BUY' or 'SELL')
    
    Returns:
        dict: Order details if successful
        Exception: Returns any exception that occurs during execution
    """
    try:
        client.futures_change_leverage(symbol=ticker, leverage=100)
        orderFullfilled = client.futures_create_order(
            symbol=ticker, side=side, type='MARKET', quantity=size)
        return orderFullfilled
    except Exception as e:
        return e
