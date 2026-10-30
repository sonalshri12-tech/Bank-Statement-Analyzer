"""Command-line entry point.
Examples:
    python main.py sample_data/statement.csv
    python main.py my_statement.csv --out report.md --export categorized.csv
    python main.py my_statement.csv --rules my_rules.json
"""
import argparse
import csv

from analyzer.categorizer import Categorizer
from analyzer.models import ParseError
from analyzer.parser import load_transactions
from analyzer.report import build_report


def main(argv=None):
    p = argparse.ArgumentParser(description="Analyze a bank statement CSV")
    p.add_argument("csv_file")
    p.add_argument("--rules", help="JSON file with extra category keywords")
    p.add_argument("--out", help="save the report to this .md file")
    p.add_argument("--export", help="save categorized transactions to this .csv file")
    args = p.parse_args(argv)
    try:
        categorizer = Categorizer.from_json(args.rules) if args.rules else Categorizer()
        transactions, errors = load_transactions(args.csv_file)
        categorizer.apply(transactions)
    except ParseError as err:
        print(f"Error: {err}")
        return 1
    report = build_report(transactions, errors)
    print(report)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(report)
    if args.export:
        with open(args.export, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["date", "description", "amount", "category"])
            writer.writerows([t.day, t.description, t.amount, t.category] for t in transactions)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
