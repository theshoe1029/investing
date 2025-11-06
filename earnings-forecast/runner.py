import stats
import pandas as pd
import yfinance as yf
import numpy as np
import fred

predict = pd.read_csv("rs3000.csv").iloc[:, 1:]
benchmark_close = (
    yf.Ticker("SPY").history(period="10y", interval="1mo").Close.reset_index(drop=True)
)
rf_rate = np.float64(fred.rf_rate())
scores = []
for ticker in predict.columns[:25]:
    try:
        scores.append(
            stats.value_score(ticker, predict.loc[:, ticker], benchmark_close, rf_rate)
        )
    except Exception:
        print(f"{ticker} failed")
pd.DataFrame(scores).to_csv("scores2.csv")
