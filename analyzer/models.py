"""Data model: one bank transaction (credit > 0, debit < 0) and a custom error."""
import re
from dataclasses import dataclass
from datetime import date

NOISE_WORDS = {"UPI", "POS", "NEFT", "IMPS", "ACH", "ATM", "DR", "CR"}


class ParseError(Exception):
    """Raised when a file or its columns cannot be understood."""


@dataclass
class Transaction:
    day: date
    description: str
    amount: float
    category: str = "Other"

    @property
    def is_debit(self) -> bool:
        return self.amount < 0

    @property
    def month(self) -> str:
        return self.day.strftime("%Y-%m")

    @property
    def merchant(self) -> str:
        """'UPI-ZOMATO-4821' -> 'ZOMATO': keep letters, drop payment-type words and numbers."""
        words = [w for w in re.sub(r"[^A-Z ]", " ", self.description.upper()).split() if w not in NOISE_WORDS]
        return " ".join(words[:2]) or "UNKNOWN"
