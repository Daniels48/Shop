from dataclasses import dataclass
from decimal import Decimal


@dataclass
class StatisticValue:
    sum: Decimal = Decimal("0")
    quantity: Decimal = Decimal("0")