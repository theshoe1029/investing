import logging
import pandas as pd
import dolt
import yfinance as yf
import numpy_financial as npf
import numpy as np

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class FinancialData:
    def __init__(self, ticker: str):
        yf_ticker = yf.Ticker(ticker)
        self.price_history = yf_ticker.history().Close
        self.sector = yf_ticker.info["sector"]
        self.beta = yf_ticker.info["beta"]
        self.free_cash_flow = yf_ticker.cash_flow.loc["Free Cash Flow"].iloc[0]

        self.income_statement = dolt.annual_ticker_data(
            ticker, dolt.StatementType.INCOME_STATEMENT
        )
        self.balance_sheet = dolt.annual_ticker_data(
            ticker, dolt.StatementType.BALANCE_SHEET_EQUITY
        )
        self.balance_sheet_assets = dolt.annual_ticker_data(
            ticker, dolt.StatementType.BALANCE_SHEET_ASSETS
        )
        self.balance_sheet_liabilities = dolt.annual_ticker_data(
            ticker, dolt.StatementType.BALANCE_SHEET_LIABILITIES
        )

    @property
    def shares(self) -> np.float64:
        return self.balance_sheet["shares_outstanding"].astype(np.float64).iloc[-1]

    @property
    def total_equity(self) -> np.float64:
        return self.balance_sheet["total_equity"].astype(np.float64).iloc[-1]

    @property
    def market_cap(self) -> float:
        return self.price_history.iloc[-1] * self.shares

    @property
    def cash(self) -> np.float64:
        return (
            self.balance_sheet_assets["cash_and_equivalents"]
            .astype(np.float64)
            .iloc[-1]
        )

    @property
    def total_assets(self) -> np.float64:
        return self.balance_sheet_assets["total_assets"].astype(np.float64).iloc[-1]

    @property
    def lt_debt(self) -> np.float64:
        return (
            self.balance_sheet_liabilities["long_term_debt"].astype(np.float64).iloc[-1]
        )

    @property
    def minority_interest(self) -> np.float64:
        return (
            self.balance_sheet_liabilities["minority_interest"]
            .astype(np.float64)
            .iloc[-1]
        )

    @property
    def total_liabilities(self) -> np.float64:
        return (
            self.balance_sheet_liabilities["total_liabilities"]
            .astype(np.float64)
            .iloc[-1]
        )

    @property
    def net_income(self) -> float:
        return self.income_statement["net_income"].astype(np.float64)

    @property
    def income_taxes(self) -> pd.Series:
        return self.income_statement["income_taxes"].astype(np.float64)

    @property
    def income_before_tax(self) -> pd.Series:
        return self.income_statement["pretax_income"].astype(np.float64)

    @property
    def interest_expense(self) -> np.float64:
        return self.income_statement["interest_expense"].astype(np.float64).iloc[-1]


def value_score(
    ticker: str, prediction: pd.Series, benchmark_close: pd.Series, rf_rate: np.float64
) -> float:
    logger.info("Scoring %s", ticker)
    financial_data = FinancialData(ticker)
    wacc = calculate_wacc(financial_data, benchmark_close, rf_rate)
    price = financial_data.price_history.iloc[-1]
    est_price = calculate_npv(financial_data, prediction, wacc) / financial_data.shares
    return {
        "ticker": ticker,
        "sector": financial_data.sector,
        "wacc": wacc,
        "est_price": est_price,
        "price": price,
        "diff": est_price - price,
        "score": (est_price - price) / price,
    }


def calculate_npv(
    financial_data: FinancialData, prediction: pd.Series, wacc: float
) -> float:
    cash_flows = prediction.groupby(prediction.index // 4).sum()
    # cash_flows.iloc[-1] += (financial_data.free_cash_flow * 1.05) / (wacc - 0.05)
    maturity = ((cash_flows.iloc[-1] * (1 + 0.05)) / (wacc - 0.05)) / np.pow(
        (1 + wacc), 4
    )
    return (
        npf.npv(wacc, np.append(0, cash_flows))
        + maturity
        + financial_data.cash
        - financial_data.lt_debt
        - financial_data.minority_interest
    )


def calculate_wacc(
    financial_data: FinancialData, benchmark_close: pd.Series, rf_rate: np.float64
) -> float:
    benchmark_return = (
        benchmark_close.groupby(benchmark_close.index // 12).sum().pct_change().mean()
    )

    # beta = financial_data.beta
    beta = 1
    cost_of_equity = rf_rate + beta * (benchmark_return - rf_rate)
    weight_of_equity = (
        financial_data.total_assets - financial_data.lt_debt
    ) / financial_data.total_assets
    # cost_of_debt = (
    #     financial_data.interest_expense / financial_data.total_liabilities
    #     if financial_data.total_liabilities != 0
    #     else 0
    # )
    cost_of_debt = 0.055
    weight_of_debt = financial_data.lt_debt / financial_data.total_assets
    tax_rate = 0.2
    wacc = (weight_of_equity * cost_of_equity) - (weight_of_debt * cost_of_debt) * (
        1 - tax_rate
    )

    return wacc
