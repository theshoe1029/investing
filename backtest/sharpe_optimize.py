import warnings

import backtrader as bt
import numpy as np
import pandas as pd
import yfinance as yf
from pyfolio.tears import create_full_tear_sheet
from scipy.optimize import minimize

warnings.simplefilter(action="ignore", category=FutureWarning)


class SharpeOptimize(bt.Strategy):
    _RISK_FREE = 0.05
    params = dict()

    def __init__(self):
        self.m_hist = []
        self.pf = np.array([1 / len(self.datas)] * len(self.datas))

    def next(self):
        buy = []
        self.m_hist.append([self.datas[i][0] for i in range(len(self.datas))])
        if len(self) > 24:
            self.optimize_shrp()
            for i, w in enumerate(self.pf):
                curr_stake = self.getposition(self.datas[i], self.broker).size
                new_stake = self.broker.get_value(self.datas) * w // self.datas[i][0]
                if new_stake > curr_stake:
                    buy.append([self.datas[i], new_stake - curr_stake])
                if new_stake < curr_stake:
                    self.sell(self.datas[i], size=curr_stake - new_stake)
            for b in buy:
                self.buy(b[0], b[1])

    def shrp(self, return_rates, w):
        R = np.matmul(return_rates.to_numpy(), w)
        return np.sqrt(12) * (R.mean() - self._RISK_FREE) / R.std()

    def optimize_shrp(self):
        return_rates = pd.DataFrame(self.m_hist).pct_change().dropna()
        w0 = self.pf.copy()
        bounds = [(0, 1) for _ in range(len(w0))]
        result = minimize(
            lambda w: -self.shrp(return_rates, w),
            w0,
            bounds=bounds,
            constraints={"type": "eq", "fun": lambda x: sum(x) - 1},
        )
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
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name="pyfolio")
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
    strat = results[0]
    pyfoliozer = strat.analyzers.getbyname("pyfolio")
    returns, positions, transactions, gross_lev = pyfoliozer.get_pf_items()
    create_full_tear_sheet(
        returns,
        positions=positions,
        transactions=transactions,
        estimate_intraday=False,
        live_start_date="2015-01-01",
    )
    cerebro.plot()


if __name__ == "__main__":
    main()
