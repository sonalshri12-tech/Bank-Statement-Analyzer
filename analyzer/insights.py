"""The analysis: summaries, recurring payments and unusual transactions."""
from collections import defaultdict
from statistics import median


def monthly_summary(transactions):
    months = defaultdict(lambda: {"income": 0.0, "spent": 0.0})
    for tx in transactions:
        key = "spent" if tx.is_debit else "income"
        months[tx.month][key] += abs(tx.amount)
    return {m: {**v, "net": v["income"] - v["spent"]} for m, v in sorted(months.items())}


def spending_by_category(transactions):
    totals = defaultdict(float)
    for tx in transactions:
        if tx.is_debit:
            totals[tx.category] += -tx.amount
    grand = sum(totals.values()) or 1
    return [(cat, amt, 100 * amt / grand) for cat, amt in sorted(totals.items(), key=lambda kv: -kv[1])]


def top_merchants(transactions, n=5):
    totals = defaultdict(float)
    for tx in transactions:
        if tx.is_debit:
            totals[tx.merchant] += -tx.amount
    return sorted(totals.items(), key=lambda kv: -kv[1])[:n]


def find_recurring(transactions):
    """Recurring = 3+ payments to one merchant, about a month apart, with nearly the same amount."""
    groups = defaultdict(list)
    for tx in transactions:
        if tx.is_debit:
            groups[tx.merchant].append(tx)
    found = []
    for merchant, items in groups.items():
        if len(items) < 3:
            continue
        items.sort(key=lambda t: t.day)
        gaps = [(b.day - a.day).days for a, b in zip(items, items[1:])]
        amounts = [-t.amount for t in items]
        typical = median(amounts)
        if 25 <= median(gaps) <= 35 and max(amounts) - min(amounts) <= 0.1 * typical:
            found.append({"merchant": merchant, "count": len(items), "amount": typical, "last_paid": items[-1].day})
    return sorted(found, key=lambda r: -r["amount"])


def find_unusual(transactions, factor=3, min_count=5):
    """Flag a payment bigger than `factor` x the median of its category (needs enough history)."""
    by_category = defaultdict(list)
    for tx in transactions:
        if tx.is_debit:
            by_category[tx.category].append(tx)
    flagged = []
    for category, items in by_category.items():
        if len(items) < min_count:
            continue
        typical = median(-t.amount for t in items)
        flagged += [(t, typical) for t in items if -t.amount > factor * typical]
    return sorted(flagged, key=lambda pair: pair[0].amount)
