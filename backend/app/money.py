"""
Exact peso amounts.
Amounts are stored, hashed, and sent to the contract as integer centavos.
The API accepts and returns pesos with at most two decimal places.
"""

from decimal import Decimal, InvalidOperation
from typing import Union

Pesos = Union[Decimal, int, str]


def to_centavos(pesos: Pesos) -> int:
    """Convert a peso amount to integer centavos, rejecting fractions of a centavo."""
    try:
        value = Decimal(str(pesos))
    except InvalidOperation:
        raise ValueError(f"Invalid amount: {pesos!r}")
    centavos = value * 100
    if centavos != centavos.to_integral_value():
        raise ValueError(f"Amount has more than two decimal places: {pesos}")
    return int(centavos)


def centavos_to_pesos(centavos: int) -> float:
    """Peso value for JSON responses. Exact for display at two decimal places."""
    return centavos / 100


def centavos_to_str(centavos: int) -> str:
    """Canonical two-decimal string, e.g. 500000 -> '5000.00'."""
    sign = "-" if centavos < 0 else ""
    whole, cents = divmod(abs(centavos), 100)
    return f"{sign}{whole}.{cents:02d}"


def format_peso(centavos: int) -> str:
    """Display string, e.g. 500000 -> '₱5,000.00'."""
    sign = "-" if centavos < 0 else ""
    whole, cents = divmod(abs(centavos), 100)
    return f"{sign}₱{whole:,}.{cents:02d}"
