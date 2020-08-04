import pandas as pd


def format_for_tslab(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(
        {
            "contract": "<TICKER>",
            "open": "<OPEN>",
            "high": "<HIGH>",
            "low": "<LOW>",
            "close": "<CLOSE>",
            "volume": "<VOL>",
        },
        axis=1,
    )
    dates = df.index.to_series().apply(lambda v: v.strftime("%Y%m%d"))
    times = df.index.to_series().apply(lambda v: v.strftime("%H%M%S"))
    df.insert(1, "<PER>", 1)
    df.insert(2, "<DATE>", dates)
    df.insert(3, "<TIME>", times)
    return df
