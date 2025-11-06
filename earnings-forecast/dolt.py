from enum import Enum
import os
import pandas as pd
import mysql.connector


class StatementType(Enum):
    INCOME_STATEMENT = "income_statement"
    BALANCE_SHEET_ASSETS = "balance_sheet_assets"
    BALANCE_SHEET_EQUITY = "balance_sheet_equity"
    BALANCE_SHEET_LIABILITIES = "balance_sheet_liabilities"


earnings_db = mysql.connector.connect(
    host=os.environ["DOLT_HOST"], username="root", database="earnings"
)


def quarterly_ticker_data(
    ticker: str, statement_type: StatementType, limit: int = 0
) -> pd.DataFrame:
    return _query_ticker(ticker, statement_type.value, "Quarter", limit)


def annual_ticker_data(
    ticker: str, statement_type: StatementType, limit: int = 0
) -> pd.DataFrame:
    return _query_ticker(ticker, statement_type.value, "Year", limit)


def _query_ticker(ticker: str, table: str, period: str, limit: int = 0) -> pd.DataFrame:
    cursor = earnings_db.cursor()
    query = f"SELECT * from {table} WHERE act_symbol='{ticker}' and period='{period}'"
    if limit > 0:
        query += f" LIMIT {limit}"
    cursor.execute(query)
    return (
        pd.DataFrame(cursor.fetchall(), columns=[d[0] for d in cursor.description])
        .set_index("date")
        .sort_index()
    )
