# Bank Statement Analyzer
A Python command-line tool that reads a bank statement CSV and produces a spending report:
income vs. expenses, monthly summary, spending by category, top merchants, **recurring payments**
and **unusual transactions**.

## Features
- Reads CSVs with different column names (Date / Description / Debit / Credit **or** a single Amount column)
  and several date formats; bad rows are skipped and listed instead of crashing the program
- Rule-based categorization (food, rent, transport...) that can be extended with your own JSON rules
- Detects recurring payments (3+ payments, about a month apart, same amount)
- Flags unusual spending (a payment more than 3x the typical amount of its category)
- Saves the report as Markdown and the categorized transactions as CSV

## Project structure
```
main.py               command-line interface
analyzer/models.py    Transaction class, custom ParseError
analyzer/parser.py    CSV reading and validation
analyzer/categorizer.py  Categorizer class (rules)
analyzer/insights.py  summaries, recurring and unusual detection
analyzer/report.py    report builder
tests/                unit tests
sample_data/          synthetic sample statement (not real data)
```

## Run
```
python main.py sample_data/statement.csv
python main.py sample_data/statement.csv --out report.md --export categorized.csv
python main.py my_statement.csv --rules my_rules.json     # {"Food & Dining": ["chaayos"]}
python -m unittest -v
```
No external libraries are needed (Python 3.9+).

**Concepts used:** OOP (dataclass, classes), modules/packages, file handling (CSV, JSON), exception handling
and custom exceptions, dictionaries/sorting/grouping, the `statistics` module, regular expressions, unit testing.
