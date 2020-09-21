import datetime
from pathlib import Path
from typing import Optional

import pandas as pd
from dateutil.relativedelta import relativedelta
from finam.export import Exporter, Market, Timeframe, LookupComparator

from .contract import ContractName, ContractSpec

DEFAULT_DATADIR = Path("./data")


def download_contract_data(
    contract: ContractSpec, timeframe: Timeframe
) -> pd.DataFrame:
    exporter = Exporter()
    lookup_df = exporter.lookup(
        name=f"{contract.full_code}({contract.short_code})",
        name_comparator=LookupComparator.EQUALS,
    )
    if len(lookup_df.index) != 1:
        raise ValueError(
            f"Contract lookup failed. Returned {len(lookup_df.index)} rows. "
            f"Names: {', '.join(lookup_df['name'])}"
        )

    today = datetime.date.today()
    start_date = contract.expiration - relativedelta(months=3, day=1)
    end_date = contract.expiration + relativedelta(months=1, day=1)

    if end_date > today:
        end_date = today

    df = exporter.download(
        lookup_df.index[0],
        Market(lookup_df["market"].iloc[0]),
        timeframe=timeframe,
        start_date=start_date,
        end_date=end_date,
    )
    df = df.rename(
        columns={
            "<OPEN>": "open",
            "<HIGH>": "high",
            "<LOW>": "low",
            "<CLOSE>": "close",
            "<VOL>": "volume",
        }
    )
    df.insert(0, "contract", contract.full_code)

    return df


def get_contract_data(
    contract: ContractSpec, data_dir=DEFAULT_DATADIR, timeframe=Timeframe.MINUTES1
) -> pd.DataFrame:
    cache_fname = data_dir / contract.cache_filename()

    if cache_fname.exists() and not contract.is_active():
        return pd.read_csv(cache_fname, index_col=0, parse_dates=True)
    else:
        df = download_contract_data(contract, timeframe)

        if not cache_fname.parent.exists():
            cache_fname.parent.mkdir(parents=True)
        df.to_csv(cache_fname)

        return df


def get_market_data(
    contract_name: ContractName,
    start_date: datetime.date,
    end_date: Optional[datetime.date] = None,
    data_dir=DEFAULT_DATADIR,
    timeframe=Timeframe.MINUTES1,
):
    if end_date is None:
        end_date = datetime.date.today()

    assert start_date <= end_date

    contracts = ContractSpec.contracts_for_interval(
        contract_name,
        start_month=start_date.replace(day=1),
        end_month=end_date.replace(day=1),
    )
    contracts_data = {
        c: get_contract_data(c, data_dir=data_dir, timeframe=timeframe)
        for c in contracts
    }

    chunks = (
        _daily_chunk(contract_name, date, contracts_data)
        for date in pd.date_range(start_date, end_date, freq="D")
    )
    result = pd.concat((c for c in chunks if len(c) != 0))

    result["contract"] = result["contract"].astype("category")

    return result


def _daily_chunk(contract_name, date, contracts_data):
    contracts = ContractSpec.contracts_for_date(contract_name, date)
    if len(contracts) == 1:
        return contracts_data[contracts[0]][date.date().isoformat()]
    else:
        per_contract_chunks = []

        for c in contracts:
            try:
                per_contract_chunks.append(contracts_data[c][date.date().isoformat()])
            except KeyError:
                pass

        volumes = [df["volume"].sum() for df in per_contract_chunks]
        chunk = max(zip(per_contract_chunks, volumes), key=lambda t: t[1])[0]
        return chunk.dropna()
