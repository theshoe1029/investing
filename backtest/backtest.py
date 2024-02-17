import os
import sys
nb_dir = os.path.split(os.getcwd())[0]
if nb_dir not in sys.path:
    sys.path.append(nb_dir)
import warnings
warnings.filterwarnings('ignore')

from backtesting import Backtest, Strategy
from strategies import PairTradeMeanReversion
import numpy as np
import pandas as pd
import numpy as np
import yfinance as yf
np.int = int
import backtrader as bt

import common.util as util

def create_pair(df_1: str, df_2: str) -> pd.DataFrame:
    df_1.index = pd.DatetimeIndex(df_1.index)
    df_2.index = pd.DatetimeIndex(df_2.index)
    pair_df = df_1.join(df_2, rsuffix='_y').dropna()
    pair_df.index = pair_df.index.tz_localize(None).astype('datetime64[ns]')
    return pair_df.reset_index()

class FixedRerverser(bt.SizerFix):

    def _getsizing(self, comminfo, cash, data, isbuy):
        position = self.broker.getposition(data)
        size = self.p.stake * (1 + (position.size != 0))
        return size

class PairTradeMeanReversion(bt.Strategy):
    params = dict(ratio=pd.Series())

    def __init__(self):
        self.trade_time = None
        self.close_1 = self.datas[0].close
        self.close_2 = self.datas[1].close

    def next(self):
        i = len(self.close_1)-1
        if i < 60:
            return
        
        is_outlier = 0
        hist = pd.Series(self.p.ratio[30:i])
        if (self.p.ratio[i] < hist.mean()-2*hist.std()):
            is_outlier = -1
        if (self.p.ratio[i] > hist.mean()+2*hist.std()):
            is_outlier = 1

        t_delta = i-self.trade_time if self.trade_time else float('inf')
        if t_delta > 14:
            # ratio denom has much larger price than numerator, sell denominator buy numerator
            if is_outlier < 0:
                self.trade_time = i
                self.buy(data=self.datas[0])
                self.sell(data=self.datas[1])
            # ratio numerator has much larger price than denominator, sell numerator buy denominator
            if is_outlier > 0:
                self.trade_time = i
                self.sell(data=self.datas[0])
                self.buy(data=self.datas[1])
        if abs(self.p.ratio[i]-hist.mean()) < (hist.std()/2):
            self.close(data=self.datas[0])
            self.close(data=self.datas[1])

pairs = [
    ['AAPL', 'MSFT', ['2020-01-01', None]],
    # ['META', 'GOOG', ['2020-01-01', None]],
    # ['F', 'GM', ['2012-01-01', None]],
    # ['BA', 'LMT', ['2012-01-01', None]],
    # ['MRK', 'LLY', ['2007-01-01', '2018-01-01']],
]

for pair in pairs:
    print(pair)
    tkr_1 = pair[0]
    tkr_2 = pair[1]
    e_start = 5000

    df_1 = yf.Ticker(tkr_1).history(start=pair[2][0], end=pair[2][1])
    df_2 = yf.Ticker(tkr_2).history(start=pair[2][0], end=pair[2][1])
    pair_df = create_pair(df_1, df_2)
    ratio = util.norm_pairs(pair_df, 'Close', 'Close_y')

    cerebro = bt.Cerebro()
    cerebro.addstrategy(PairTradeMeanReversion, ratio=ratio)
    cerebro.addsizer(FixedRerverser, stake=20)
    cerebro.adddata(bt.feeds.PandasData(dataname=df_1))
    cerebro.adddata(bt.feeds.PandasData(dataname=df_2))

    cerebro.broker.setcash(100000.0)
    start_cash = cerebro.broker.getvalue()
    cerebro.run()
    end_cash = cerebro.broker.getvalue()

    print(f"Pair return %: {end_cash/start_cash*100}")
    bh_1 = df_1['Close'][-1]-df_1['Close'][0]
    bh_2 = df_2['Close'][-1]-df_2['Close'][0]
    print(f"Buy and hold return %: {(bh_1+bh_2)/(df_1['Close'][0]+df_2['Close'][0])*100}\n")

    cerebro.plot()