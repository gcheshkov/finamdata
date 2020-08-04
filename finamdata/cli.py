import datetime
import enum
from pathlib import Path

import typer

from finamdata.finam import DEFAULT_DATADIR, get_market_data
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

    if format == DataFormat.SIMPLE:
        df.to_csv(outfile)
    elif format == DataFormat.TSLAB:
        df = format_for_tslab(df)
        df.to_csv(outfile, index=False)


if __name__ == "__main__":
    app()
