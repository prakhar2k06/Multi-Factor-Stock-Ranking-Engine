"""
cleaner.py

Data cleaning and normalization utilities for raw financial data fetched
from Yahoo Finance. This module standardizes column names, selects
relevant rows, coerces numeric values, and handles missing data.
"""

from typing import Any

import pandas as pd

# -------------------------------
# Price History
# -------------------------------


def clean_price_history(ph_df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize yfinance price history into the project's internal schema.

    Expected output columns:
    open, high, low, close, volume
    """
    if ph_df is None or ph_df.empty:
        return pd.DataFrame()

    df = ph_df.copy()

    if isinstance(df.columns, pd.MultiIndex):
        field_names: set[str] = {"open", "high", "low", "close", "adj close", "volume"}

        level_0: list[str] = [str(x).lower() for x in df.columns.get_level_values(0)]
        level_1: list[str] = [str(x).lower() for x in df.columns.get_level_values(1)]

        if any(x in field_names for x in level_0):
            df.columns = df.columns.get_level_values(0)

        elif any(x in field_names for x in level_1):
            df.columns = df.columns.get_level_values(1)

        else:
            raise ValueError(f"Unexpected price history column format: {df.columns}")

    df.columns = df.columns.astype(str).str.lower().str.strip().str.replace(" ", "_")

    if "adj_close" in df.columns:
        df = df.drop(columns=["adj_close"])

    df = df.loc[:, ~df.columns.duplicated()]

    required_cols: list[str] = ["open", "high", "low", "close", "volume"]
    missing: list[str] = [col for col in required_cols if col not in df.columns]

    if missing:
        raise ValueError(f"Missing required price columns: {missing}")

    df = df[required_cols]

    df.index = pd.to_datetime(df.index)
    df = df.sort_index()

    for col in required_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.ffill()
    df = df.dropna(subset=["close"])

    return df


# -------------------------------
# Helpers
# -------------------------------


def is_float(string: str) -> bool:
    """Checks whether a value can safely be converted to float."""
    try:
        float(string)
        return True
    except (ValueError, TypeError):
        return False


# -------------------------------
# Fundamentals
# -------------------------------


def clean_fundamentals(f_dict: dict) -> dict[str, Any]:
    keys_selected: list[str] = [
        "marketCap",
        "bookValue",
        "priceToBook",
        "returnOnEquity",
        "profitMargins",
        "operatingMargins",
        "revenueGrowth",
        "earningsGrowth",
        "shortName",
        "longName",
        "sector",
        "industry",
        "country",
        "currency",
        "sharesOutstanding",
        "beta",
        "currentPrice",
        "grossMargins",
        "ebitdaMargins",
    ]
    clean_dict: dict[str, Any] = {
        key: f_dict[key] for key in keys_selected if key in f_dict
    }
    for key in clean_dict:
        if isinstance(clean_dict[key], (int, float)):
            continue
        if clean_dict[key] in ["N/A", "None", "", None]:
            clean_dict[key] = None
            continue
        if is_float(clean_dict[key]):
            clean_dict[key] = float(clean_dict[key])
    return clean_dict


# -------------------------------
# Balance sheets
# -------------------------------


def clean_balance_sheet(bs_df: pd.DataFrame) -> pd.DataFrame:
    important_rows: list[str] = [
        "stockholders_equity",
        "common_stock_equity",
        "total_assets",
        "total_liabilities_net_minority_interest",
        "total_debt",
        "net_debt",
        "cash_and_cash_equivalents",
        "cash_cash_equivalents_and_short_term_investments",
        "ordinary_shares_number",
        "treasury_shares_number",
        "share_issued",
    ]
    df = bs_df.copy()
    df.index = df.index.str.lower().str.replace(" ", "_")
    df = df.reindex(important_rows)
    df = df.apply(pd.to_numeric, errors="coerce")
    return df


def clean_quarterly_balance_sheet(qbs_df: pd.DataFrame) -> pd.DataFrame:
    important_rows: list[str] = [
        "totalassets",
        "totalliabilitiesnetminorityinterest",
        "commonstockequity",
        "stockholdersequity",
        "totaldebt",
        "netdebt",
        "cashandcashequivalents",
        "cashcashequivalentsandshortterminvestments",
        "inventory",
        "accountsreceivable",
        "accountspayable",
        "othercurrentassets",
        "othercurrentliabilities",
        "ordinarysharesnumber",
        "treasurysharesnumber",
        "shareissued",
    ]
    row_map: dict[str, str] = {
        "totalassets": "total_assets",
        "totalliabilitiesnetminorityinterest": "total_liabilities",
        "commonstockequity": "common_stock_equity",
        "stockholdersequity": "stockholders_equity",
        "totaldebt": "total_debt",
        "netdebt": "net_debt",
        "cashandcashequivalents": "cash_and_cash_equivalents",
        "cashcashequivalentsandshortterminvestments": "cash_cash_equivalents_and_short_term_investments",
        "inventory": "inventory",
        "accountsreceivable": "accounts_receivable",
        "accountspayable": "accounts_payable",
        "othercurrentassets": "other_current_assets",
        "othercurrentliabilities": "other_current_liabilities",
        "ordinarysharesnumber": "ordinary_shares_number",
        "treasurysharesnumber": "treasury_shares_number",
        "shareissued": "share_issued",
    }
    df = qbs_df.copy()
    df.index = df.index.str.lower()
    df = df.reindex(important_rows)
    df = df.apply(pd.to_numeric, errors="coerce")
    df.index = df.index.map(row_map)
    return df


# -------------------------------
# Income statements
# -------------------------------


def clean_income_statement(is_df: pd.DataFrame) -> pd.DataFrame:
    important_rows: list[str] = [
        "total_revenue",
        "cost_of_revenue",
        "gross_profit",
        "operating_income",
        "ebit",
        "ebitda",
        "pretax_income",
        "net_income",
        "operating_expense",
        "research_and_development",
    ]
    df = is_df.copy()
    df.index = df.index.str.lower().str.replace(" ", "_")
    df = df.reindex(important_rows)
    df = df.apply(pd.to_numeric, errors="coerce")
    return df


def clean_quarterly_income_statement(qis_df: pd.DataFrame) -> pd.DataFrame:
    important_rows: list[str] = [
        "total_revenue",
        "cost_of_revenue",
        "gross_profit",
        "operating_income",
        "operating_expense",
        "ebit",
        "ebitda",
        "pretax_income",
        "net_income",
        "research_and_development",
        "selling_general_and_administration",
    ]
    df = qis_df.copy()
    df.index = df.index.str.lower().str.replace(" ", "_")
    df = df.reindex(important_rows)
    df = df.apply(pd.to_numeric, errors="coerce")
    return df


def clean_ttm_income_statement(ttmis_df: pd.DataFrame) -> pd.DataFrame:
    important_rows: list[str] = [
        "total_revenue",
        "cost_of_revenue",
        "gross_profit",
        "operating_income",
        "operating_expense",
        "ebit",
        "ebitda",
        "normalized_ebitda",
        "pretax_income",
        "net_income",
        "research_and_development",
        "selling_general_and_administration",
        "reconciled_depreciation",
    ]
    df = ttmis_df.copy()
    df.index = df.index.str.lower().str.replace(" ", "_")
    df = df.reindex(important_rows)
    df = df.apply(pd.to_numeric, errors="coerce")
    return df


# -------------------------------
# Cash flow statements
# -------------------------------


def clean_cashflow(cf_df: pd.DataFrame) -> pd.DataFrame:
    important_rows: list[str] = [
        "operating_cash_flow",
        "free_cash_flow",
        "capital_expenditure",
        "repurchase_of_capital_stock",
        "issuance_of_debt",
        "repayment_of_debt",
        "stock_based_compensation",
        "net_income_from_continuing_operations",
        "change_in_working_capital",
    ]
    df = cf_df.copy()
    df.index = df.index.str.lower().str.replace(" ", "_")
    df = df.reindex(important_rows)
    df = df.apply(pd.to_numeric, errors="coerce")
    return df


def clean_quarterly_cashflow(qcf_df: pd.DataFrame) -> pd.DataFrame:
    important_rows: list[str] = [
        "operating_cash_flow",
        "free_cash_flow",
        "capital_expenditure",
        "repurchase_of_capital_stock",
        "stock_based_compensation",
        "net_income_from_continuing_operations",
        "change_in_working_capital",
    ]
    df = qcf_df.copy()
    df.index = df.index.str.lower().str.replace(" ", "_")
    df = df.reindex(important_rows)
    df = df.apply(pd.to_numeric, errors="coerce")
    return df


def clean_ttm_cashflow(ttmcf_df: pd.DataFrame) -> pd.DataFrame:
    important_rows: list[str] = [
        "operating_cash_flow",
        "free_cash_flow",
        "capital_expenditure",
        "repurchase_of_capital_stock",
        "cash_dividends_paid",
        "common_stock_dividend_paid",
        "stock_based_compensation",
        "net_income_from_continuing_operations",
        "change_in_working_capital",
    ]
    df = ttmcf_df.copy()
    df.index = df.index.str.lower().str.replace(" ", "_")
    df = df.reindex(important_rows)
    df = df.apply(pd.to_numeric, errors="coerce")
    return df


# -------------------------------
# Metadata
# -------------------------------


def clean_metadata(m_dict: dict) -> dict[str, Any]:
    keys_selected: list[str] = [
        "symbol",
        "longName",
        "currency",
        "exchangeName",
        "fullExchangeName",
        "fiftyTwoWeekHigh",
        "fiftyTwoWeekLow",
        "previousClose",
        "regularMarketTime",
    ]
    clean_dict: dict[str, Any] = {
        key: m_dict[key] for key in keys_selected if key in m_dict
    }
    for key in clean_dict:
        if isinstance(clean_dict[key], (int, float)):
            continue
        if clean_dict[key] in ["N/A", "None", "", None]:
            clean_dict[key] = None
            continue
        if is_float(clean_dict[key]):
            clean_dict[key] = float(clean_dict[key])
    return clean_dict
