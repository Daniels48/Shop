from enum import Enum

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from app.view.dialog.product_history.utils import decimal_to_str_trimmed_for_amount


class ActionType(str, Enum):
    SALE = "sale"
    ADD = "add"
    NEW_ITEM = "new_item"
    CLEAR = "clear"
    UNION = "union"

    @property
    def label(self) -> str:
        return {
            self.SALE: "Продажа",
            self.ADD: "Добавление товара",
            self.NEW_ITEM: "Создание нового товара",
            self.CLEAR: "Списание товара",
            self.UNION: "Объединение товара",
        }[self]

    @classmethod
    def get_label(cls, value: str) -> str:
        try:
            return cls(value).label
        except ValueError:
            return ""

    @classmethod
    def get_value(cls, label: str) -> "ActionType | None":
        for action in cls:
            if action.label == label:
                return action
        return None

class PaymentMethod(str, Enum):
    CASH = "cash"
    CARD = "card"
    CARD_NOBARCODE = "card_nobarcode"
    CASH_NOBARCODE = "cash_nobarcode"
    COMBINED = "combined"

    @property
    def label(self) -> str:
        return {
            self.CASH: "Наличные",
            self.CARD: "По карте",
            self.CARD_NOBARCODE: "Без штрих-кода (К)",
            self.CASH_NOBARCODE: "Без штрих-кода (Н)",
            self.COMBINED: "Комбинированная оплата",
        }[self]

    @classmethod
    def get_label(cls, value: str, card_amount: Decimal | None = None, cash_amount: Decimal | None = None) -> str:
        try:
            method = cls(value)
        except (ValueError, TypeError):
            return "-"

        if method == cls.COMBINED:
            format_amount = decimal_to_str_trimmed_for_amount

            card_amount_str = f"{format_amount(card_amount)} 💳"
            cash_amount_str = f"{format_amount(cash_amount)} 💰"

            return f"Комб. {cash_amount_str} {card_amount_str}"

        return method.label


@dataclass(slots=True)
class InventoryChangeStatistic:
    type_action: str
    payment_method: str | None
    amount: Decimal
    quantity: Decimal
    change_date: datetime
    change_id: int
    sale_id: int | None
    cash_amount_combine: Decimal | None
    card_amount_combine: Decimal | None
    lunch_amount: Decimal