from dataclasses import replace
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP

from app.view.dialog.product_history.tabs.history_tab.calculator.enums import PaymentMethod, ActionType, InventoryChangeStatistic
from app.view.dialog.product_history.tabs.history_tab.calculator.daily_statistic import DailyStatistic
from app.view.dialog.product_history.tabs.history_tab.calculator.statistic_value import StatisticValue


class Statistic:
    def __init__(self):
        self._data: dict[date, DailyStatistic] = {}

        self._methods = {
            ActionType.SALE: self.sale,
            ActionType.NEW_ITEM: self.new_item,
            ActionType.CLEAR: self.clear,
            ActionType.ADD: self.add_item,
        }

        self._sale_methods = {
            PaymentMethod.CASH: self.cash_sale,
            PaymentMethod.CARD: self.card_sale,
            PaymentMethod.COMBINED: self.combined_sale,
            PaymentMethod.CARD_NOBARCODE: self.card_nobarcode,
            PaymentMethod.CASH_NOBARCODE: self.cash_nobarcode,
        }

    def get_daily_summary(self, day: datetime) -> DailyStatistic:
        day = day.date()
        return self._data.get(day, DailyStatistic(day=day))

    def add_statistic(self, raw:InventoryChangeStatistic) -> None:
        day = raw.change_date.date()
        daily = self._data.setdefault(day, DailyStatistic(day=day))

        self.calculate(daily, raw)

    def calculate(self, daily: DailyStatistic, raw:InventoryChangeStatistic) -> None:
        method = self._methods.get(raw.type_action)

        if method is not None:
            method(daily, raw)

    def sale(self, daily: DailyStatistic, raw:InventoryChangeStatistic) -> None:
        method = self._sale_methods.get(raw.payment_method)

        if method is not None:
            method(daily, raw)

    @staticmethod
    def get_decimal(value) -> Decimal:
        return Decimal(str(value or 0))

    @staticmethod
    def update_statistic(statistic: StatisticValue, raw: InventoryChangeStatistic) -> None:
        statistic.sum += raw.amount
        statistic.quantity += raw.quantity

    @staticmethod
    def get_raw_combine(raw: InventoryChangeStatistic) -> dict[str, InventoryChangeStatistic]:
        total = raw.card_amount_combine + raw.cash_amount_combine

        card_ratio = (raw.card_amount_combine / total).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        cash_ratio = Decimal("1.00") - card_ratio

        return  {
            "card": replace(raw, amount=raw.card_amount_combine, quantity=raw.quantity * card_ratio),
            "cash": replace(raw, amount=raw.cash_amount_combine, quantity=raw.quantity * cash_ratio),
        }

    @staticmethod
    def get_raw_lunch(raw: InventoryChangeStatistic) -> InventoryChangeStatistic:
        return replace(raw,amount=Statistic.get_decimal(raw.lunch_amount),quantity=Decimal("1"))

    def get_lunch(self,daily: DailyStatistic,raw: InventoryChangeStatistic) -> None:
        raw_lunch = self.get_raw_lunch(raw)

        if raw_lunch.amount == 0:
            return

        self.update_statistic(daily.lunch, raw_lunch)

    def cash_sale(self, daily: DailyStatistic, raw) -> None:
        self.update_statistic(daily.sold, raw)
        self.update_statistic(daily.cash_sold, raw)
        self.get_lunch(daily, raw)

    def card_sale(self, daily: DailyStatistic, raw) -> None:
        self.update_statistic(daily.sold, raw)
        self.update_statistic(daily.card_sold, raw)
        self.get_lunch(daily, raw)

    def cash_nobarcode(self, daily: DailyStatistic, raw) -> None:
        self.cash_sale(daily, raw)

    def card_nobarcode(self, daily: DailyStatistic, raw) -> None:
        self.card_sale(daily, raw)

    def combined_sale(self, daily: DailyStatistic, raw:InventoryChangeStatistic) -> None:
        self.update_statistic(daily.sold, raw)
        self.get_lunch(daily, raw)

        raw_combine = self.get_raw_combine(raw)

        self.update_statistic(daily.card_sold, raw_combine.get("card"))
        self.update_statistic(daily.cash_sold, raw_combine.get("cash"))

    def new_item(self, daily: DailyStatistic, raw) -> None:
        self.update_statistic(daily.created, raw)

    def clear(self, daily: DailyStatistic, raw) -> None:
        self.update_statistic(daily.cleared, raw)

    def add_item(self, daily: DailyStatistic, raw) -> None:
        self.update_statistic(daily.added, raw)