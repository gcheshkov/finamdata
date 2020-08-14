import datetime
import enum
import functools
import operator
from pathlib import Path
from typing import List, Optional, Set

import pandas as pd
from dateutil.relativedelta import relativedelta

EXPIRATION_MONTHS = [3, 6, 9, 12]
EXPIRATION_MONTH_CODES = [
    "F",
    "G",
    "H",
    "J",
    "K",
    "M",
    "N",
    "Q",
    "U",
    "V",
    "X",
    "Z",
]


class ContractName(enum.Enum):
    RTS = "RI"
    SBRF = "SR"
    SI = "SI"


class ContractSpec:
    def __init__(self, name: ContractName, expiration: datetime.date):
        self.name = name
        self.expiration = expiration

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.full_code}>"

    def __str__(self):
        return self.full_code

    def __hash__(self):
        return hash((self.name, self.expiration))

    def __eq__(self, other):
        return (
            self.__class__ == other.__class__
            and self.name == other.name
            and self.expiration == other.expiration
        )

    def __lt__(self, other):
        return self.expiration < other.expiration

    @property
    def full_code(self):
        return (
            f"{self.name.name}-{self.expiration.month}.{self.expiration.year % 100:02}"
        )

    @property
    def short_code(self):
        return (
            f"{self.name.value}"
            f"{EXPIRATION_MONTH_CODES[self.expiration.month - 1]}"
            f"{self.expiration.year % 10}"
        )

    def cache_filename(self):
        return Path("finam") / self.name.name / f"{self.full_code}.csv"

    def is_active(self):
        return datetime.date.today() < self.expiration + relativedelta(months=1, day=1)

    def next_contract(self):
        return ContractSpec(self.name, self.expiration + relativedelta(months=3))

    @staticmethod
    def contracts_for_date(
        name: ContractName, date: datetime.date
    ) -> List["ContractSpec"]:
        # если в текущем месяце есть экспирация, нужен текущй контракт и предыдущий,
        # если экспирации нет - только текущий
        current_exp_month = (((date.month - 1) // 3) + 1) * 3  # 3, 6, 9, 12
        current_contract = ContractSpec(
            name, datetime.date(date.year, current_exp_month, 1)
        )

        if date.month in EXPIRATION_MONTHS:
            return [current_contract, current_contract.next_contract()]
        else:
            return [current_contract]

    @staticmethod
    def contracts_for_interval(
        name: ContractName,
        start_month: datetime.date,
        end_month: Optional[datetime.date] = None,
    ) -> List["ContractSpec"]:
        """
        Возвращает список контрактов, которые нужны для получения данных
        за зданный интервал.
        Последний месяц включен в интервал.
        """

        if end_month is None:
            end_month = datetime.date.today().replace(day=1)

        contracts: Set["ContractSpec"] = functools.reduce(
            operator.or_,
            (
                set(ContractSpec.contracts_for_date(name, month))
                for month in pd.date_range(start_month, end_month, freq="MS")
            ),
            set(),
        )

        return list(sorted(contracts))
