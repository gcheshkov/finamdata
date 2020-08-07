import datetime
import enum
from pathlib import Path
from typing import Optional

import typer

from finamdata.finam import DEFAULT_DATADIR, get_market_data
from finamdata.moex import get_initial_margin, align_margin_to_marketdata
from finamdata.utils import format_for_tslab

from .contract import ContractName

app = typer.Typer()


class DataFormat(enum.Enum):
    SIMPLE = "SIMPLE"
    TSLAB = "TSLAB"


def _default_end_date():
    return datetime.datetime.now()


@app.command()
def main(
    outfile: typer.FileTextWrite,
    margin_outfile: Optional[typer.FileTextWrite] = typer.Argument(None),
    ticker: ContractName = typer.Option(...),
    start_date: datetime.datetime = typer.Option(..., formats=["%Y-%m-%d"]),
    end_date: datetime.datetime = typer.Option(_default_end_date, formats=["%Y-%m-%d"]),
    data_dir: Path = typer.Option(
        DEFAULT_DATADIR,
        exists=True,
        file_okay=False,
        dir_okay=True,
        writable=True,
        readable=True,
    ),
    format: DataFormat = typer.Option(DataFormat.SIMPLE),
):
    """
    Download continous data for selected time period
    """
    df = get_market_data(ticker, start_date, end_date, data_dir)

    if margin_outfile is not None:
        margin_df = get_initial_margin(ticker, start_date, end_date)
        aligned_margin_df = align_margin_to_marketdata(df, margin_df)

    if format == DataFormat.SIMPLE:
        df.to_csv(outfile)
        if margin_outfile is not None:
            # noinspection PyUnboundLocalVariable
            aligned_margin_df.to_csv(margin_outfile)
    elif format == DataFormat.TSLAB:
        df = format_for_tslab(df)
        df.to_csv(outfile, index=False)
        if margin_outfile is not None:
            # noinspection PyUnboundLocalVariable
            aligned_margin_df = format_for_tslab(aligned_margin_df)
            aligned_margin_df.to_csv(margin_outfile, index=False)


if __name__ == "__main__":
    app()
