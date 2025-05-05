from decimal import Decimal, ROUND_UP

def round_up_decimal(value: Decimal, decimal_places: int = 3, rounding_mode: str = ROUND_UP) -> Decimal:
    quantize_format = Decimal(f"0.{"0" * decimal_places}")
    return value.quantize(quantize_format, rounding=rounding_mode)
