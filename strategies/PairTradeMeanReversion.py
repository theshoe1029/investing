from backtesting import Strategy
import pandas as pd

import common.util as util

class PairTradeMeanReversion(Strategy):
    rolling_days = 30

    def init(self):
        print(self.sig)
        self.ratio = util.norm_pairs(self.data, 'Close_x', 'Close_y').dropna().copy()

    def next(self):
        print(self)