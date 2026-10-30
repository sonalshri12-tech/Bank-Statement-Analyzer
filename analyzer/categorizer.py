"""Rule-based categorizer: a description containing a keyword gets that keyword's category."""
import json

from .models import ParseError

DEFAULT_RULES = {
    "Rent": ["rent payment", "house rent"],
    "Bills & Utilities": ["electricity", "bses", "jio", "airtel", "broadband"],
    "Groceries": ["bigbasket", "dmart", "blinkit", "grocery"],
    "Food & Dining": ["zomato", "swiggy", "restaurant", "cafe", "dominos"],
    "Transport": ["uber", "ola", "metro", "irctc", "petrol"],
    "Entertainment": ["netflix", "spotify", "bookmyshow", "hotstar"],
    "Shopping": ["amazon", "flipkart", "myntra", "croma"],
    "Health & Fitness": ["pharmeasy", "apollo", "fitlife", "gym"],
}


class Categorizer:
    def __init__(self, rules=None):
        self.rules = {cat: [k.lower() for k in words] for cat, words in (rules or DEFAULT_RULES).items()}

    @classmethod
    def from_json(cls, path):
        """Add or override rules from a JSON file, e.g. {"Food & Dining": ["chaayos"]}."""
        try:
            with open(path, encoding="utf-8") as f:
                custom = json.load(f)
        except FileNotFoundError:
            raise ParseError(f"Rules file not found: {path}") from None
        except json.JSONDecodeError as err:
            raise ParseError(f"Rules file is not valid JSON: {err}") from None
        return cls({**DEFAULT_RULES, **custom})

    def categorize(self, tx):
        if not tx.is_debit:
            return "Income"
        text = tx.description.lower()
        for category, keywords in self.rules.items():
            if any(word in text for word in keywords):
                return category
        return "Other"

    def apply(self, transactions):
        for tx in transactions:
            tx.category = self.categorize(tx)
