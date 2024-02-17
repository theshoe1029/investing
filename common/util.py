import numpy as np
import pandas as pd

def rolling_prod_norm(df: pd.DataFrame, col: str, days: int = 30) -> pd.Series:
    change = np.ones((1, df.shape[0]))+df[col].pct_change().to_numpy()
    return pd.Series(change[0], index=df.index).rolling(days).apply(lambda s: np.prod(s))

def norm_pairs(df: pd.DataFrame, col_1: str, col_2: str, days: int = 30) -> pd.Series:
    norm_x = rolling_prod_norm(df, col_1, days=days)
    norm_y = rolling_prod_norm(df, col_2, days=days)
    return norm_x/norm_y

def flag_outliers(df: pd.DataFrame, col: str, threshold: int) -> pd.Series:
    outliers = []
    for val in df[col]:
        if val <= df[col].mean()-threshold*df[col].std():
            outliers.append(-1)
        elif val >= df[col].mean()+threshold*df[col].std():
            outliers.append(1)
        else:
            outliers.append(0)
    return pd.Series(outliers, index=df.index)