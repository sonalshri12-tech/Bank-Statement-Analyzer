import os
import tempfile
import unittest
from datetime import date

from analyzer.categorizer import Categorizer
from analyzer.insights import find_recurring, find_unusual, monthly_summary
from analyzer.models import ParseError, Transaction
from analyzer.parser import load_transactions, parse_date


def write_csv(text):
    f = tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8")
    f.write(text)
    f.close()
    return f.name


class TestParser(unittest.TestCase):
    def test_date_formats(self):
        self.assertEqual(parse_date("05-03-2026"), date(2026, 3, 5))
        self.assertEqual(parse_date("2026-03-05"), date(2026, 3, 5))
        with self.assertRaises(ValueError):
            parse_date("hello")

    def test_debit_credit_columns_and_bad_rows(self):
        path = write_csv("Date,Narration,Withdrawal,Deposit\n01-01-2026,SALARY,,50000\n02-01-2026,UPI-ZOMATO-1,500,\nxx,BAD,10,\n")
        txs, errors = load_transactions(path)
        os.remove(path)
        self.assertEqual([t.amount for t in txs], [50000, -500])
        self.assertEqual(len(errors), 1)

    def test_single_amount_column(self):
        path = write_csv("Date,Description,Amount\n2026-01-01,Coffee,\"-1,200.50\"\n")
        txs, _ = load_transactions(path)
        os.remove(path)
        self.assertEqual(txs[0].amount, -1200.5)

    def test_missing_columns_and_missing_file(self):
        path = write_csv("Foo,Bar\n1,2\n")
        with self.assertRaises(ParseError):
            load_transactions(path)
        os.remove(path)
        with self.assertRaises(ParseError):
            load_transactions("does_not_exist.csv")


class TestInsights(unittest.TestCase):
    def tx(self, day, desc, amount):
        t = Transaction(date(2026, *day), desc, amount)
        return t

    def test_categorizer(self):
        c = Categorizer()
        self.assertEqual(c.categorize(self.tx((1, 1), "UPI-ZOMATO-12", -300)), "Food & Dining")
        self.assertEqual(c.categorize(self.tx((1, 1), "SALARY", 5000)), "Income")
        self.assertEqual(c.categorize(self.tx((1, 1), "UNKNOWN SHOP", -50)), "Other")

    def test_merchant_name(self):
        self.assertEqual(self.tx((1, 1), "UPI-ZOMATO-4821", -1).merchant, "ZOMATO")

    def test_monthly_summary(self):
        txs = [self.tx((1, 1), "SALARY", 1000), self.tx((1, 5), "X", -400), self.tx((2, 5), "Y", -100)]
        s = monthly_summary(txs)
        self.assertEqual(s["2026-01"]["net"], 600)
        self.assertEqual(s["2026-02"]["spent"], 100)

    def test_recurring_detection(self):
        txs = [self.tx((m, 8), "UPI-NETFLIX-SUB", -649) for m in (1, 2, 3, 4)]
        txs += [self.tx((m, 9), "UPI-SHOP-1", -a) for m, a in ((1, 100), (2, 900), (3, 400))]  # varying: not recurring
        found = find_recurring(txs)
        self.assertEqual([r["merchant"] for r in found], ["NETFLIX SUB"])

    def test_unusual_detection(self):
        txs = [self.tx((1, d), "UPI-ZOMATO-1", -400) for d in range(1, 7)] + [self.tx((1, 20), "UPI-ZOMATO-2", -4000)]
        c = Categorizer()
        c.apply(txs)
        flagged = find_unusual(txs)
        self.assertEqual([t.amount for t, _ in flagged], [-4000])


if __name__ == "__main__":
    unittest.main()
