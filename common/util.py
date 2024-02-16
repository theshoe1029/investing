import numpy as np
import pandas as pd

def norm_pairs(df: pd.DataFrame, col_1: str, col_2: str, days: int = 30) -> pd.Series:
    change_x = np.ones((1, df.shape[0]))+df[col_1].pct_change().to_numpy()
    norm_x = pd.Series(change_x[0], index=df.index).rolling(days).apply(lambda s: np.prod(s))
    change_y = np.ones((1, df.shape[0]))+df[col_2].pct_change().to_numpy()
    norm_y = pd.Series(change_y[0], index=df.index).rolling(days).apply(lambda s: np.prod(s))
    return norm_x/norm_y

def flag_outliers(df: pd.DataFrame, col: str, threshold: int) -> pd.Series:
    return ~df[col].between(df[col].mean()-threshold*df[col].std(),
                            df[col].mean()+threshold*df[col].std())