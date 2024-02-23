import os
import sys
nb_dir = os.path.split(os.getcwd())[0]
if nb_dir not in sys.path:
    sys.path.append(nb_dir)
import warnings
warnings.filterwarnings('ignore')

import backtrader as bt
import numpy as np
np.int = int
import pandas as pd
import yfinance as yf

import common.util as util

def create_pair(df_1: str, df_2: str) -> pd.DataFrame:
    df_1.index = pd.DatetimeIndex(df_1.index)
    df_2.index = pd.DatetimeIndex(df_2.index)
    pair_df = df_1.join(df_2, lsuffix='_n', rsuffix='_d').dropna()
    pair_df.index = pair_df.index.tz_localize(None).astype('datetime64[ns]')
    return pair_df.reset_index()

class BuyAndHold(bt.Strategy):
    def nextstart(self):
        self.buy(data=self.datas[0])
        self.buy(data=self.datas[1])

class PairTradeMeanReversion(bt.Strategy):
    params = dict(window_size=30, outlier_threshold=2, 
                  ratio=pd.Series(), norm_1=pd.Series(), norm_2=pd.Series())

    def __init__(self):
        self.exp = 0
        self.ret = 0

    def next(self):
        i = len(self)-1
        if i < 2*self.p.window_size:
            return

        hist = pd.Series(self.p.ratio[i-90:i])
        hist_norm_1 = pd.Series(self.p.norm_1[i-90:i])
        hist_norm_2 = pd.Series(self.p.norm_2[i-90:i])
        is_outlier = util.flag_outlier(self.p.ratio[i], hist, self.p.outlier_threshold)

        # ratio denom has much larger price than numerator, sell denominator buy numerator
        if is_outlier < 0:
            self.buy(data=self.data)
            self.sell(data=self.data1)            

        # ratio numerator has much larger price than denominator, sell numerator buy denominator
        if is_outlier > 0:
            self.sell(data=self.data)
            self.buy(data=self.data1)

        # exit position when individual price has reverted to within 1 standard deviation of the mean
        if abs(self.p.norm_1[i]-hist_norm_1.mean()) < hist_norm_1.std():
            self.close(data=self.data)
        if abs(self.p.norm_2[i]-hist_norm_2.mean()) < hist_norm_2.std():
            self.close(data=self.data1)

def run_test(cerebro: bt.Cerebro):
    cerebro.broker.setcash(100000.0)
    results = cerebro.run()
    annual_returns = results[0].analyzers.anr.get_analysis().values()
    anr100 = list(map(lambda x: x*100, annual_returns))
    returns = results[0].analyzers.r.get_analysis()
    print(f"Returns y/y: {anr100}")
    print(f"Normalized return %: {returns['rnorm100']}")

def init_cerebro(df_1: pd.DataFrame, df_2: pd.DataFrame) -> bt.Cerebro:
    cerebro = bt.Cerebro()
    cerebro.addanalyzer(bt.analyzers.AnnualReturn, _name='anr')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='r')
    cerebro.adddata(bt.feeds.PandasData(dataname=df_1))
    cerebro.adddata(bt.feeds.PandasData(dataname=df_2))
    return cerebro

def backtest_baseline(df_1: pd.DataFrame, df_2: pd.DataFrame, tst_id: any):
    print(f"--------- Baseline {tst_id} ---------")
    cerebro = init_cerebro(df_1, df_2)
    cerebro.addstrategy(BuyAndHold)
    cerebro.addsizer(bt.sizers.AllInSizer, percents=97)
    run_test(cerebro)

def backtest_pair(df_1: pd.DataFrame, df_2: pd.DataFrame, tst_id: any):
    print(f"--------- Mean reversion {tst_id} ---------")
    pair_df = create_pair(df_1, df_2)
    ratio = util.norm_pairs(pair_df, 'Close_n', 'Close_d')

    cerebro = init_cerebro(df_1, df_2)
    cerebro.addstrategy(PairTradeMeanReversion, window_size=30, outlier_threshold=2, 
                        ratio=ratio, 
                        norm_1=util.rolling_prod_norm(df_1, 'Close'),
                        norm_2=util.rolling_prod_norm(df_2, 'Close'))
    cerebro.addsizer(bt.sizers.FixedSize, stake=250)
    cerebro.addobserver(bt.observers.Trades)

    run_test(cerebro)

pairs = [
    ('AAPL', 'MSFT', ['2022-01-01', '2023-06-01']),
    ('META', 'GOOG', ['2020-06-01', '2022-01-01']),
    ('FDX', 'UPS', ['2021-01-01', '2022-06-01']),
    ('F', 'GM', ['2022-06-01', None]),
    ('MGM', 'WYNN', ['2022-01-01', None]),
]

for pair in pairs:
    tkr_1, tkr_2, date_range = pair

    print(f"{tkr_1} | {tkr_2}")

    df_1 = yf.Ticker(tkr_1).history(start=date_range[0], end=date_range[1])
    df_2 = yf.Ticker(tkr_2).history(start=date_range[0], end=date_range[1])
    backtest_baseline(df_1, df_2, date_range)
    backtest_pair(df_1, df_2, date_range)
    print()

    df_1 = yf.Ticker(tkr_1).history(start='2013-01-01', end=None)
    df_2 = yf.Ticker(tkr_2).history(start='2013-01-01', end=None)
    backtest_baseline(df_1, df_2, '10y')
    backtest_pair(df_1, df_2, '10y')
    print()