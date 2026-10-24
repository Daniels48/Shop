from decimal import Decimal, ROUND_HALF_UP, ROUND_DOWN
from re import findall
from app.utils.decorators import debug_decorator

sign_currency = "₽"

@debug_decorator
def format_decimal_to_str(value: Decimal, decimal_places: int = 2) -> str:
    quantize_str = f"1.{'0' * decimal_places}"
    if not isinstance(value, Decimal):
        value = Decimal("0.00")
    rounded = value.quantize(Decimal(quantize_str), rounding=ROUND_DOWN)
    value = format(rounded.normalize(), 'f')
    return separate_value(value)

@debug_decorator
def decimal_to_str_trimmed_for_quantity(value: Decimal) -> str:
    quantity = format_decimal_to_str(value, 3)
    return quantity

@debug_decorator
def decimal_to_str_trimmed_for_amount(value: Decimal) -> str:
    if type(value) == str:
        return value
    elif isinstance(value, type(None)):
        return "-"
    else:
        sum_value = format_decimal_to_str(value)
        return f"{sum_value} {sign_currency}"

@debug_decorator
def separate_value(number_str: str) -> str:
    if '.' in number_str:
        int_part, frac_part = number_str.split('.', 1)
    else:
        int_part, frac_part = number_str, None

    frac_part = f".{frac_part}" if frac_part else ""

    reversed_int = int_part[::-1]
    grouped = [reversed_int[i:i+3] for i in range(0, len(reversed_int), 3)]
    int_part_with_spaces = ' '.join(grouped)[::-1]

    return f"{int_part_with_spaces}{frac_part}"


def get_numer_in_string(string: str) -> float:
    value = 0
    if isinstance(string, str):
        matches = findall(r'\d+[.,]\d+', string)
        if matches:
            value = float(matches[0])
    return value

def get_formatting_number(number):
    if isinstance(number, float| int| Decimal):
        value = round(float(number), 2)
    else:
        value = get_numer_in_string(number)
