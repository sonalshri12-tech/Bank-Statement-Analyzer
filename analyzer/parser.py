"""File handling: read a bank-statement CSV, tolerate different column names and date styles."""
import csv
from datetime import datetime

from .models import ParseError, Transaction

DATE_FORMATS = ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%d %b %Y")
COLUMN_ALIASES = {
    "date": {"date", "txn date", "transaction date"},
    "description": {"description", "narration", "details", "particulars"},
    "debit": {"debit", "withdrawal", "withdrawals", "dr"},
    "credit": {"credit", "deposit", "deposits", "cr"},
    "amount": {"amount"},  # single signed column: negative = money out
}


def parse_date(text):
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(text.strip(), fmt).date()
        except ValueError:
            continue
    raise ValueError(f"unrecognized date '{text}'")


def parse_amount(text):
    cleaned = (text or "").replace(",", "").replace("\u20b9", "").replace("Rs.", "").strip()
    return float(cleaned) if cleaned else 0.0


def map_columns(header):
    """Match the file's column names to the fields we need."""
    found = {}
    for name in header:
        for field, aliases in COLUMN_ALIASES.items():
            if name.strip().lower() in aliases:
                found[field] = name
    if "date" not in found or "description" not in found:
        raise ParseError("The file needs a date column and a description column.")
    if "amount" not in found and not ({"debit", "credit"} & found.keys()):
        raise ParseError("The file needs an amount column, or debit/credit columns.")
    return found


def load_transactions(path):
    """Return (transactions, errors). Bad rows are skipped and reported, not fatal."""
    try:
        file = open(path, newline="", encoding="utf-8-sig")
    except FileNotFoundError:
        raise ParseError(f"File not found: {path}") from None
    transactions, errors = [], []
    with file:
        reader = csv.DictReader(file)
        if not reader.fieldnames:
            raise ParseError("The file is empty.")
        cols = map_columns(reader.fieldnames)
        for row in reader:
            try:
                day = parse_date(row[cols["date"]])
                if "amount" in cols:
                    amount = parse_amount(row[cols["amount"]])
                else:
                    amount = parse_amount(row.get(cols.get("credit"))) - parse_amount(row.get(cols.get("debit")))
                if amount == 0:
                    raise ValueError("missing or zero amount")
                transactions.append(Transaction(day, row[cols["description"]].strip(), amount))
            except ValueError as err:
                errors.append((reader.line_num, str(err)))
    return transactions, errors
