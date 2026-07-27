def format_currency(value, symbol='£', decimals=2):
    """Format a number as currency with a space as the thousands separator,
    e.g. 1000 -> '£1 000.00', -20000 -> '-£20 000.00'."""
    negative = value < 0
    grouped = f"{abs(value):,.{decimals}f}".replace(',', ' ')
    return f"{'-' if negative else ''}{symbol}{grouped}"
