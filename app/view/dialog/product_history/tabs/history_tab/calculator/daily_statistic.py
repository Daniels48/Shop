from dataclasses import dataclass, field, fields
from datetime import date

from app.view.dialog.product_history.tabs.history_tab.calculator.statistic_value import StatisticValue


@dataclass
class DailyStatistic:
    day: date = field(metadata={"label": "Дата", "order": 0})

    sold: StatisticValue = field(default_factory=StatisticValue,metadata={"label": "Продано", "order": 1})

    card_sold: StatisticValue = field(default_factory=StatisticValue,metadata={"label": "Картой (Общее)", "order": 2})

    cash_sold: StatisticValue = field(default_factory=StatisticValue,metadata={"label": "Наличными (Общее)", "order": 3})

    lunch: StatisticValue = field(default_factory=StatisticValue,metadata={"label": "Обеды (Общее)", "order": 4})

    added: StatisticValue = field(default_factory=StatisticValue,metadata={"label": "Добавлено товаров", "order": 5})

    cleared: StatisticValue = field(default_factory=StatisticValue,metadata={"label": "Списано товаров", "order": 6})

    created: StatisticValue = field(default_factory=StatisticValue, metadata={"label": "Создано товаров", "order": 7})



def get_statistic_fields():
    return sorted(
        (item for item in fields(DailyStatistic) if item.name != "day"),
        key=lambda item: item.metadata["order"],
    )