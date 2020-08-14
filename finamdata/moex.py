import datetime

import pandas as pd

from finamdata.contract import ContractName


def get_initial_margin(
    contract: ContractName, start_date: datetime.date, end_date: datetime.date
) -> pd.DataFrame:
    url = (
        f"https://www.moex.com/ru/forts/contractbaseresults-exp.aspx?"
        f"day1={start_date.strftime('%Y%m%d')}&"
        f"day2={end_date.strftime('%Y%m%d')}&"
        f"base={contract.value}"
    )
    df = pd.read_csv(
        url,
        encoding="cp1251",
        usecols=[0, 15],
        names=["date", "initial_margin"],
        header=0,
        parse_dates=[0],
        dayfirst=True,
    )
    return df


def align_margin_to_marketdata(
    data_df: pd.DataFrame, margin_df: pd.DataFrame
) -> pd.DataFrame:
    data_df = data_df.copy()
    data_df["date"] = data_df.index.to_series().dt.normalize()
    data_df["index"] = data_df.index.to_series()

    result = data_df.merge(margin_df, on="date", how="left")

    result["initial_margin"] = result["initial_margin"].ffill()

    result = result.set_index("index")
    result["contract"] = "MARGIN"
    result["open"] = result["initial_margin"]
    result["high"] = result["initial_margin"]
    result["low"] = result["initial_margin"]
    result["close"] = result["initial_margin"]
    result["volume"] = 0
    result = result.drop(["date", "initial_margin"], axis=1)
    return result
