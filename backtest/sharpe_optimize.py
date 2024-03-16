import backtrader as bt
import numpy as np
import pandas as pd
from scipy.optimize import minimize
import yfinance as yf


class SharpeOptimize(bt.Strategy):
    _RISK_FREE = 0.05
    params = dict()

    def __init__(self):
        self.m_hist = []
        self.pf = np.array([1/len(self.datas)]*len(self.datas))

    def next(self):
        self.m_hist.append([self.datas[i][0] for i in range(len(self.datas))])
        if len(self) > 24:
            self.optimize_shrp()
        for i, w in enumerate(self.pf):
            stake = self.broker.get_cash()*w//self.datas[i][0]
            self.buy(self.datas[i], size=stake)

    def shrp(self, return_rates, w):
        R = np.matmul(return_rates.to_numpy(), w)
        return np.sqrt(12)*(R.mean()-self._RISK_FREE)/R.std()

    def optimize_shrp(self):
        return_rates = pd.DataFrame(self.m_hist).pct_change().dropna()
        w0 = self.pf.copy()
        bounds = [(0, 1) for _ in range(len(w0))]
        result = minimize(lambda w: -self.shrp(return_rates, w), w0, bounds=bounds, constraints={'type': 'eq', 'fun': lambda x: sum(x)-1})
        print(-result.fun)
        self.pf = np.array(result.x)


def gen_portfolio(tickers, start, interval):
    index = pd.Series()
    data = []
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
                data.append(hist)
    return data


def init_cerebro(data: list[pd.DataFrame]) -> bt.Cerebro:
    cerebro = bt.Cerebro()
    cerebro.addanalyzer(bt.analyzers.AnnualReturn, _name="anr")
    cerebro.addanalyzer(bt.analyzers.Returns, _name="r")
    for row in data:
        cerebro.adddata(bt.feeds.PandasData(dataname=row))
    return cerebro


def main():
    pf_sp_500 = gen_portfolio(
        pd.read_csv("../data/sp500_members.csv").Symbol, "2013-01-01", "1mo"
    )
    cerebro = init_cerebro(pf_sp_500)
    cerebro.broker.setcash(100000.0)
    cerebro.addstrategy(SharpeOptimize)
    results = cerebro.run()
    annual_returns = results[0].analyzers.anr.get_analysis().values()
    anr100 = list(map(lambda x: x * 100, annual_returns))
    returns = results[0].analyzers.r.get_analysis()
    print(f"Returns y/y: {anr100}")
    print(f"Normalized return %: {returns['rnorm100']}")


if __name__ == "__main__":
    main()
