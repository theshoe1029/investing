import numpy as np
import pandas as pd

RISK_FREE_RETURN = 0.05


def rolling_prod_norm(df: pd.DataFrame, col: str, days: int = 30) -> pd.Series:
    change = np.ones((1, df.shape[0])) + df[col].pct_change().to_numpy()
    return (
        pd.Series(change[0], index=df.index).rolling(days).apply(lambda s: np.prod(s))
    )


def norm_pairs(df: pd.DataFrame, col_1: str, col_2: str, days: int = 30) -> pd.Series:
    norm_x = rolling_prod_norm(df, col_1, days=days)
    norm_y = rolling_prod_norm(df, col_2, days=days)
    return norm_x / norm_y


def flag_outlier(v: np.float64, s: pd.Series, threshold: int) -> pd.Series:
    if v <= s.mean() - threshold * s.std():
        return -1
    elif v >= s.mean() + threshold * s.std():
        return 1
    return 0


def sharpe_ratio(return_rates, freq):
    R = np.matmul(return_rates.to_numpy(), w)
    return np.sqrt(freq) * (R.mean() - RISK_FREE_RETURN) / R.std()


def get_return_rate(s: pd.series, shift):
    gain = s - s.shift(shift)
    return np.power(1 + (gain / s.shift(shift)), 1 / shift) - 1
