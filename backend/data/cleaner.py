import pandas as pd

def clean_price_history(ph_df):
    df = ph_df.copy()
    df.index = pd.to_datetime(df.index)
    df.columns = df.columns.get_level_values(0)
    df.columns = df.columns.str.lower()
    df = df.sort_index()
    df = df.ffill()
    df = df.dropna()
    return df


def is_float(string):
    try:
        float(string)
        return True
    except (ValueError, TypeError):
        return False


def clean_fundamentals(f_dict):
    keys_selected = ["marketCap", "bookValue", "priceToBook", "returnOnEquity", "profitMargins", "operatingMargins", "revenueGrowth", "earningsGrowth", "shortName", "longName", "sector", "industry", "country", "currency"]
    clean_dict = {key: f_dict[key] for key in keys_selected if key in f_dict}
    for key in clean_dict:
        if isinstance(clean_dict[key], (int, float)):
            continue
        if clean_dict[key] in ["N/A", "None", "", None]:
            clean_dict[key] = None
            continue
        if is_float(clean_dict[key]):
            clean_dict[key] = float(clean_dict[key])
    return clean_dict
    

def clean_balance_sheet(bs_df):
    important_rows = ["stockholders_equity", "common_stock_equity", "total_assets", "total_liabilities_net_minority_interest", "total_debt", "net_debt", "cash_and_cash_equivalents", "cash_cash_equivalents_and_short_term_investments", "ordinary_shares_number", "treasury_shares_number", "share_issued"]
    df = bs_df.copy()
    df.index = df.index.str.lower().str.replace(" ", "_")
    df = df.reindex(important_rows)
    df = df.apply(pd.to_numeric, errors="coerce")
    return df


def clean_quarterly_balance_sheet(qbs_df):
    important_rows = ["totalassets", "totalliabilitiesnetminorityinterest", "commonstockequity", "stockholdersequity","totaldebt", "netdebt", "cashandcashequivalents", "cashcashequivalentsandshortterminvestments", "inventory", "accountsreceivable", "accountspayable", "othercurrentassets", "othercurrentliabilities", "ordinarysharesnumber", "treasurysharesnumber", "shareissued"]
    row_map = {"totalassets": "total_assets", "totalliabilitiesnetminorityinterest": "total_liabilities", "commonstockequity": "common_stock_equity", "stockholdersequity": "stockholders_equity", "totaldebt": "total_debt", "netdebt": "net_debt", "cashandcashequivalents": "cash_and_cash_equivalents", "cashcashequivalentsandshortterminvestments": "cash_cash_equivalents_and_short_term_investments", "inventory": "inventory", "accountsreceivable": "accounts_receivable", "accountspayable": "accounts_payable", "othercurrentassets": "other_current_assets", "othercurrentliabilities": "other_current_liabilities", "ordinarysharesnumber": "ordinary_shares_number", "treasurysharesnumber": "treasury_shares_number", "shareissued": "share_issued"}
    df = qbs_df.copy()
    df.index = df.index.str.lower()
    df = df.reindex(important_rows)
    df = df.apply(pd.to_numeric, errors="coerce")
    df.index = df.index.map(row_map)
    return df
    

def clean_income_statement(is_df):
    important_rows=["total_revenue", "cost_of_revenue", "gross_profit", "operating_income", "ebit", "ebitda", "pretax_income", "net_income", "operating_expense", "research_and_development"]
    df = is_df.copy()
    df.index = df.index.str.lower().str.replace(" ", "_")
    df= df.reindex(important_rows)
    df = df.apply(pd.to_numeric, errors="coerce")
    return df

def clean_quarterly_income_statement(qis_df):
    important_rows = ["total_revenue", "cost_of_revenue", "gross_profit", "operating_income", "operating_expense", "ebit", "ebitda",  "pretax_income", "net_income", "research_and_development", "selling_general_and_administration"]
    df = qis_df.copy()
    df.index = df.index.str.lower().str.replace(" ", "_")
    df= df.reindex(important_rows)
    df = df.apply(pd.to_numeric, errors="coerce")
    return df


def clean_ttm_income_statement(ttmis_df):
    important_rows = ["total_revenue", "cost_of_revenue", "gross_profit", "operating_income", "operating_expense", "ebit", "ebitda", "normalized_ebitda", "pretax_income", "net_income", "research_and_development", "selling_general_and_administration", "reconciled_depreciation"]
    df = ttmis_df.copy()
    df.index = df.index.str.lower().str.replace(" ", "_")
    df= df.reindex(important_rows)
    df = df.apply(pd.to_numeric, errors="coerce")
    return df

def clean_cashflow(cf_df):
    important_rows = ["operating_cash_flow", "free_cash_flow", "capital_expenditure", "repurchase_of_capital_stock", "issuance_of_debt", "repayment_of_debt", "stock_based_compensation", "net_income_from_continuing_operations", "change_in_working_capital"]
    df = cf_df.copy()
    df.index = df.index.str.lower().str.replace(" ", "_")
    df= df.reindex(important_rows)
    df = df.apply(pd.to_numeric, errors="coerce")
    return df


def clean_quarterly_cashflow(qcf_df):
    important_rows = ["operating_cash_flow", "free_cash_flow", "capital_expenditure", "repurchase_of_capital_stock", "stock_based_compensation", "net_income_from_continuing_operations", "change_in_working_capital"]
    df = qcf_df.copy()
    df.index = df.index.str.lower().str.replace(" ", "_")
    df= df.reindex(important_rows)
    df = df.apply(pd.to_numeric, errors="coerce")
    return df


def clean_ttm_cashflow(ttmcf_df):
    important_rows = ["operating_cash_flow", "free_cash_flow", "capital_expenditure", "repurchase_of_capital_stock", "cash_dividends_paid", "common_stock_dividend_paid", "stock_based_compensation", "net_income_from_continuing_operations", "change_in_working_capital"]
    df = ttmcf_df.copy()
    df.index = df.index.str.lower().str.replace(" ", "_")
    df= df.reindex(important_rows)
    df = df.apply(pd.to_numeric, errors="coerce")
    return df


def clean_metadata(m_dict):
    keys_selected = ["symbol", "longName", "currency", "exchangeName", "fullExchangeName", "fiftyTwoWeekHigh", "fiftyTwoWeekLow", "previousClose", "regularMarketTime"]
    clean_dict = {key: m_dict[key] for key in keys_selected if key in m_dict}
    for key in clean_dict:
        if isinstance(clean_dict[key], (int, float)):
            continue
        if clean_dict[key] in ["N/A", "None", "", None]:
            clean_dict[key] = None
            continue
        if is_float(clean_dict[key]):
            clean_dict[key] = float(clean_dict[key])
    return clean_dict





