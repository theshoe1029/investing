import os
import pandas as pd
import pmdarima
from sklearn.metrics import mean_squared_error
import dolt
from dataclasses import dataclass
import numpy as np

import warnings
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

warnings.simplefilter(action="ignore", category=FutureWarning)


@dataclass
class Prediction:
    vals: list[float]
    error: float


def forecast_net_income(ticker: str) -> Prediction:
    logger.info("Starting forecasting for %s", ticker)
    net_income = dolt.quarterly_ticker_data(
        ticker, dolt.StatementType.INCOME_STATEMENT
    )["net_income"].astype(np.float64)
    if net_income.empty:
        logger.warning("Not enough data for %s", ticker)
        return Prediction(vals=[], error=float("inf"))

    norm_factor = max(net_income)
    net_income_norm = net_income / norm_factor

    test_size = int(os.environ["FORECAST_SIZE"])
    income_train = net_income_norm.iloc[:-test_size]
    income_test = net_income_norm.iloc[-test_size:]

    try:
        arima = pmdarima.arima.auto_arima(
            income_train, start_q=1, start_d=1, m=4, seasonal=True
        )
    except ValueError:
        logger.error("Failed to forecast %s", ticker)
        return Prediction(vals=[], error=float("inf"))

    fcast_size = int(os.environ["FORECAST_SIZE"])
    fcast = arima.predict(n_periods=fcast_size)
    logger.info("Completed forecast for %s", ticker)
    return Prediction(
        vals=(fcast * norm_factor).to_list(),
        error=mean_squared_error(income_test, fcast),
    )


rs3000 = pd.read_csv("../data/russell3000_holdings.csv")
predictions = {ticker: forecast_net_income(ticker) for ticker in rs3000["Ticker"]}
valid_predictions = {}
errors = {}
for ticker, prediction in predictions.items():
    if len(prediction.vals) > 0 and len(set(prediction.vals)) > 1:
        valid_predictions[ticker] = prediction.vals
        errors[ticker] = prediction.error
pd.DataFrame(valid_predictions).to_csv("rs3000.csv")
pd.Series(errors).to_csv("rs3000_error.csv")
