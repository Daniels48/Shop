from decimal import Decimal

# from db.models.enums import DailyStatistic


def calculate_init_dict():
    data_calculate = {
        "total_sold": Decimal("0"), "total_amount": Decimal("0"),
        "cash_sold": Decimal("0"), "cash_amount": Decimal("0"),
        "card_sold": Decimal("0"), "card_amount": Decimal("0"),
        "card_no_barcode_sold": Decimal("0"), "card_no_barcode_amount": Decimal("0"),
        "cash_no_barcode_sold": Decimal("0"), "cash_no_barcode_amount": Decimal("0"),
        "created": Decimal("0"), "created_sum": Decimal("0"),
        "cleared": Decimal("0"), "cleared_sum": Decimal("0"),
        "added": Decimal("0"), "added_sum": Decimal("0"),
        "lunch_sum": Decimal("0"), "lunch_count": Decimal("0"),
    }
    return data_calculate

# def calculate_init_dict() -> DailyStatistic:
#     return DailyStatistic()