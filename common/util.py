import numpy as np
import pandas as pd

def rolling_prod_norm(df: pd.DataFrame, col: str, days: int = 30) -> pd.Series:
    change = np.ones((1, df.shape[0]))+df[col].pct_change().to_numpy()
    return pd.Series(change[0], index=df.index).rolling(days).apply(lambda s: np.prod(s))

def norm_pairs(df: pd.DataFrame, col_1: str, col_2: str, days: int = 30) -> pd.Series:
    norm_x = rolling_prod_norm(df, col_1, days=days)
    norm_y = rolling_prod_norm(df, col_2, days=days)
    return norm_x/norm_y

def flag_outlier(v: np.float64, s: pd.Series, threshold: int) -> pd.Series:
    if v <= s.mean()-threshold*s.std():
        return -1
    elif v >= s.mean()+threshold*s.std():
        return 1
    return 0