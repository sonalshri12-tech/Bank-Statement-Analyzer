"""Turn the analysis into a readable Markdown report."""
from . import insights


def money(value):
    return f"Rs. {value:,.0f}"


def build_report(transactions, errors):
    if not transactions:
        return "No valid transactions found."
    income = sum(t.amount for t in transactions if not t.is_debit)
    spent = -sum(t.amount for t in transactions if t.is_debit)
    saved = income - spent
    days = [t.day for t in transactions]
    lines = ["# Bank Statement Report", "",
             f"Period: {min(days)} to {max(days)}  |  Transactions: {len(transactions)}"
             + (f"  |  Skipped rows: {len(errors)}" if errors else ""), "",
             "## Overview",
             f"- Income: {money(income)}", f"- Spent: {money(spent)}",
             f"- Saved: {money(saved)} ({100 * saved / income:.0f}% of income)" if income else f"- Saved: {money(saved)}",
             "", "## Monthly summary", "| Month | Income | Spent | Net |", "|---|---|---|---|"]
    for month, v in insights.monthly_summary(transactions).items():
        lines.append(f"| {month} | {money(v['income'])} | {money(v['spent'])} | {money(v['net'])} |")
    lines += ["", "## Spending by category"]
    for cat, amount, pct in insights.spending_by_category(transactions):
        lines.append(f"- {cat:<18} {money(amount):>12}  {pct:4.1f}%  {'#' * int(pct / 2)}")
    lines += ["", "## Top merchants"]
    lines += [f"- {name}: {money(amount)}" for name, amount in insights.top_merchants(transactions)]
    recurring = insights.find_recurring(transactions)
    lines += ["", "## Recurring payments"]
    lines += [f"- {r['merchant']}: {money(r['amount'])} per month ({r['count']} payments, last on {r['last_paid']})"
              for r in recurring] or ["- None found"]
    if recurring:
        lines.append(f"- Total fixed monthly commitments: {money(sum(r['amount'] for r in recurring))}")
    lines += ["", "## Unusual transactions (over 3x the category's typical amount)"]
    lines += [f"- {t.day}: {t.description} - {money(-t.amount)} (typical {t.category}: {money(typ)})"
              for t, typ in insights.find_unusual(transactions)] or ["- None found"]
    if errors:
        lines += ["", "## Rows skipped"] + [f"- Line {n}: {msg}" for n, msg in errors]
    return "\n".join(lines)
