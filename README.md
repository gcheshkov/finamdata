= Загрузка и склейка данных фьючерсных контрактов из finam

```
Usage: finamdata [OPTIONS] OUTFILE [MARGIN_OUTFILE]

  Download continous data for selected time period

Arguments:
  OUTFILE           [required]
  [MARGIN_OUTFILE]

Options:
  --ticker [RI|SR|SI]      [required]
  --start-date [%Y-%m-%d]  [required]
  --end-date [%Y-%m-%d]    [default: (dynamic)]
  --data-dir DIRECTORY     [default: data]
  --format [SIMPLE|TSLAB]  [default: DataFormat.SIMPLE]
  --install-completion     Install completion for the current shell.
  --show-completion        Show completion for the current shell, to copy it
                           or customize the installation.

  --help                   Show this message and exit.

```