import csv
import re
import unittest

import rules

CSV_PATH = "test_data/ground_truth.csv"


def parse_range(text):
    # "70 - 99" -> (70, 99); "< 200" -> (None, 200); "> 40" -> (40, None)
    text = text.strip()
    if text.startswith("<"):
        return None, float(text[1:])
    if text.startswith(">"):
        return float(text[1:]), None
    low, high = text.split(" - ")
    return float(low), float(high)


def parse_values(cell, date=""):
    # "Sodium 134 [135 - 145]; ..." -> list of test dicts
    out = []
    for part in cell.split(";"):
        m = re.match(r"\s*(.+?) (-?[\d.]+) \[(.+)\]", part)
        low, high = parse_range(m.group(3))
        out.append({"date": date, "name": m.group(1), "value": float(m.group(2)),
                    "range_low": low, "range_high": high})
    return out


def load_rows():
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


class GroundTruth(unittest.TestCase):
    def test_all_reports(self):
        rows = load_rows()
        self.assertEqual(len(rows), 25)
        # Every reading per patient, used for the trend rule
        history = {}
        for r in rows:
            history.setdefault(r["patient"], []).extend(
                parse_values(r["all_values_and_printed_range"], r["date"]))
        for r in rows:
            with self.subTest(file=r["file"]):
                values = parse_values(r["all_values_and_printed_range"], r["date"])
                res = rules.assess(values, history=history[r["patient"]])
                want = r["expected_tier"].lower()
                if want == "trend":
                    self.assertEqual(res["level"], "watch")
                    self.assertIn("rising", res["flags"])
                else:
                    self.assertEqual(res["level"], want)
                    self.assertNotIn("rising", res["flags"])


class SmallRules(unittest.TestCase):
    def t(self, name, value, low, high):
        return {"name": name, "value": value, "range_low": low, "range_high": high}

    def test_bounds_inclusive(self):
        res = rules.assess([self.t("TSH", 4.0, 0.4, 4.0)])
        self.assertEqual(res["level"], "routine")

    def test_critical_limit_is_strict(self):
        self.assertEqual(rules.assess([self.t("Potassium", 3.0, 3.5, 5.1)])["level"], "watch")
        self.assertEqual(rules.assess([self.t("Potassium", 2.9, 3.5, 5.1)])["level"], "urgent")

    def test_keyword_raises_one_step(self):
        ok = [self.t("TSH", 2.0, 0.4, 4.0)]
        self.assertEqual(rules.assess(ok, "I fainted today")["level"], "watch")
        high = [self.t("TSH", 6.8, 0.4, 4.0)]
        self.assertEqual(rules.assess(high, "chest pain")["level"], "urgent")

    def test_worst_is_reported(self):
        vals = [self.t("TSH", 6.8, 0.4, 4.0), self.t("Sodium", 120, 135, 145)]
        self.assertEqual(rules.assess(vals)["worst"]["name"], "Sodium")

    def test_trend_needs_three_rising_out_of_range(self):
        def h(d, v):
            return {"date": d, "name": "Glucose (Fasting)", "value": v,
                    "range_low": 70, "range_high": 99}
        self.assertEqual(rules.rising_tests([h("1", 110), h("2", 120)]), [])
        self.assertEqual(rules.rising_tests([h("1", 110), h("2", 120), h("3", 130)]),
                         ["Glucose (Fasting)"])
        self.assertEqual(rules.rising_tests([h("1", 110), h("2", 130), h("3", 120)]), [])
        self.assertEqual(rules.rising_tests([h("1", 90), h("2", 120), h("3", 130)]), [])


if __name__ == "__main__":
    unittest.main()
