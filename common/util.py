import pandas as pd

def pair_rebase(df: pd.DataFrame, col_1: str, col_2: str) -> pd.Series:
    df['Norm_x'] = df[col_1]/df.iloc[0].loc[col_1]
    df['Norm_y'] = df[col_2]/df.iloc[0].loc[col_2]

def pair_rolling_avg(df: pd.DataFrame, col_1: str, col_2: str) -> pd.Series:
    avg_1 = df['Close_x'].rolling(30).mean()
    avg_2 = df['Close_y'].rolling(30).mean()
    return avg_1/avg_2

def flag_outliers(df: pd.DataFrame, col: str, threshold: int) -> pd.Series:
    return ~df[col].between(df[col].mean()-threshold*df[col].std(), 
                            df[col].mean()+threshold*df[col].std())