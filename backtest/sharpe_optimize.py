import backtrader as bt
import numpy as np
import pandas as pd
import yfinance as yf


class SharpeOptimize(bt.Strategy):
    _RISK_FREE = 0.05
    params = dict()

    def __init__(self):
        print(len(self.data))


def gen_portfolio(tickers, start, interval):
    index = pd.Series()
    data = {}
    for tkr in tickers:
        if interval == "1y":
            hist = yf.Ticker(tkr).history(start=start, interval="1mo").iloc[::12]
        else:
            hist = yf.Ticker(tkr).history(start=start, interval=interval)
        if not hist.Close.empty:
            hist = hist.dropna()
            if len(index) > 0 and hist.shape[0] < len(index):
                print(f"Skipping ticker {tkr} due to insufficient data")
            else:
                index = hist.index
                data[tkr] = hist
    return pd.DataFrame(data, index=index)


def init_cerebro(data: list[pd.DataFrame]) -> bt.Cerebro:
    cerebro = bt.Cerebro()
    cerebro.addanalyzer(bt.analyzers.AnnualReturn, _name="anr")
    cerebro.addanalyzer(bt.analyzers.Returns, _name="r")

    return cerebro


def backtest_pair(df_1: pd.DataFrame, df_2: pd.DataFrame, tst_id: any):
    print(f"--------- Mean reversion {tst_id} ---------")
    pair_df = create_pair(df_1, df_2)
    ratio = util.norm_pairs(pair_df, "Close_n", "Close_d")

    cerebro = init_cerebro(df_1, df_2)
    cerebro.addstrategy(SharpeOptimize)
    cerebro.addsizer(bt.sizers.FixedSize, stake=250)
    cerebro.addobserver(bt.observers.Trades)

    run_test(cerebro)


def run_test(cerebro: bt.Cerebro):
    cerebro.broker.setcash(100000.0)
    results = cerebro.run()
    annual_returns = results[0].analyzers.anr.get_analysis().values()
    anr100 = list(map(lambda x: x * 100, annual_returns))
    returns = results[0].analyzers.r.get_analysis()
    print(f"Returns y/y: {anr100}")
    print(f"Normalized return %: {returns['rnorm100']}")


def main():
    pf_sp_500 = gen_portfolio(
        pd.read_csv("../data/sp500_members.csv").Symbol, "2010-01-01", "1mo"
    )
    pf_sp_500.to_csv("../data/sp500_monthly.csv")


if __name__ == "__main__":
    main()
