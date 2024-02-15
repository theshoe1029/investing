import numpy as np
import pandas as pd

def RMA(close: pd.Series, n: int) -> pd.Series:
    '''
    Implementation of tradingview Relative Moving Average (RMA).
    https://www.tradingview.com/pine-script-reference/v5/#fun_ta.rma
    '''

    alpha = 1/n
    avg = pd.Series(np.nan, index=range(len(close)))
    avg[0] = close[0]
    for i in range(1, len(close)):
        avg[i] = alpha*close[i]+(1-alpha)*avg[i-1]
    return avg

def RSI(up: pd.Series, down: pd.Series, period: int) -> pd.Series:
    '''
    Relative Strength Index (RSI) implementation. Used to measure speed and magnitude of price changes.
    https://www.investopedia.com/terms/r/rsi.asp
    '''

    strength = pd.Series(np.nan, index=range(len(up)))
    for i in range(period, len(up)):
        if down[i] == 0:
            strength[i] = 100
        elif up[i] == 0:
            strength[i] = 0
        else:
            strength[i] = 100-(100/(1+up[i]/down[i]))
    return strength