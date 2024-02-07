from backtesting import Strategy
import pandas as pd

from indicators import RMA, RSI

class TrendReversal(Strategy):
    '''
    Trend reversal strategy that uses RSI to determine momentum of price changes.
    An RSI above `up_thresh` for a number of data points equal to `confirm_bars` is a sell signal.
    An RSI below `down_thresh` for a number of data points equal to `confirm_bars` is a buy signal.
    '''

    rsi_period = 14
    up_thresh = 70
    down_thresh = 30
    confirm_bars = 3

    def init(self):
        close = self.data.Close
        pd_close = pd.Series(close)
        up = RMA(pd.Series([max(c, 0) for c in pd_close.diff().fillna(0)]), self.rsi_period)
        down = RMA(-1*pd.Series([min(c, 0) for c in pd_close.diff().fillna(0)]), self.rsi_period)
        self.rsi = self.I(RSI, up, down, self.rsi_period)
        self.count_up = 0
        self.count_down = 0

    def next(self):
        if self.rsi[-1] > self.up_thresh:
            self.count_up += 1
        else:
            self.count_up = 0
        if self.rsi[-1] < self.down_thresh:
            self.count_down += 1
        else:
            self.count_down = 0

        if self.count_up >= self.confirm_bars:
            for trade in self.trades:
                trade.close()
        if self.count_down >= self.confirm_bars:
            self.buy()