#!/usr/bin/env python3
"""Build a fictional review fixture. Writes only a new directory you specify."""
import argparse
import subprocess
from pathlib import Path

CASES = {
    "clean": {
        "before": {
            "greeting.py": 'def greet(name: str) -> str:\n    return "Hi, " + name\n',
            "caller.py": 'from greeting import greet\n\nprint(greet("Ada"))\n',
            "test_greeting.py": 'import unittest\nfrom greeting import greet\n\nclass TestGreeting(unittest.TestCase):\n    def test_greeting(self):\n        self.assertEqual(greet("Ada"), "Hi, Ada")\n        self.assertEqual(greet(""), "Hi, ")\n',
        },
        "after": {"greeting.py": 'def greet(name: str) -> str:\n    return f"Hi, {name}"\n'},
    },
    "defect": {
        "before": {
            "limits.py": 'def can_add(current, limit):\n    return current < limit\n',
            "checkout.py": 'from limits import can_add\n\ndef add_item(items, item, limit):\n    if not can_add(len(items), limit):\n        raise ValueError("cart full")\n    items.append(item)\n',
            "test_checkout.py": 'import unittest\nfrom checkout import add_item\n\nclass TestCheckout(unittest.TestCase):\n    def test_below_capacity(self):\n        items = []\n        add_item(items, "book", 2)\n        self.assertEqual(items, ["book"])\n',
            "TEAM-CONTEXT.md": '# Fictional evaluation context\nCart capacity is a hard limit; exceeding it rejects downstream fulfillment.\nCritical path: checkout.py → limits.py.\n',
        },
        "after": {"limits.py": 'def can_add(current, limit):\n    return current <= limit\n'},
    },
    "exception": {
        "before": {
            "legacy/__init__.py": '',
            "legacy/exporter.py": 'def export(conn):\n    return conn.execute("SELECT id FROM reporting").fetchall()\n',
            "test_exporter.py": 'import sqlite3\nimport unittest\nfrom legacy.exporter import export\n\nclass TestExporter(unittest.TestCase):\n    def test_export(self):\n        with sqlite3.connect(":memory:") as conn:\n            conn.execute("CREATE TABLE reporting (id INTEGER, currency TEXT)")\n            conn.execute("INSERT INTO reporting VALUES (1, \'EUR\')")\n            self.assertEqual(export(conn), [(1,)])\n',
            "TEAM-CONTEXT.md": '# Fictional evaluation context\nExport column order is a contract; append new columns.\nAccepted tradeoff: see [reporting access](docs/adr/reporting-access.md).\n',
            "docs/adr/reporting-access.md": '# Reporting access — fictional decision\nDirect reporting reads in legacy/exporter.py are accepted until migration.\nNo writes or access to customer credentials. Revisit at migration completion.\n',
        },
        "after": {"legacy/exporter.py": 'def export(conn):\n    return conn.execute("SELECT id, currency FROM reporting").fetchall()\n'},
    },
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", choices=CASES)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    root = args.destination.resolve()
    root.mkdir(parents=True, exist_ok=False)
    case = CASES[args.case]

    def write(files):
        for name, content in files.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)

    def git(*argv):
        subprocess.run(["git", "-c", "user.name=Fictional Fixture",
                        "-c", "user.email=fixture@example.invalid",
                        "-c", "commit.gpgsign=false", *argv], cwd=root, check=True,
                       stdout=subprocess.DEVNULL)

    write(case["before"])
    git("init", "-q")
    git("add", ".")
    git("commit", "-qm", "Fictional baseline")
    git("branch", "baseline")
    git("checkout", "-qb", "candidate")
    write(case["after"])
    if args.case == "exception":
        path = root / "test_exporter.py"
        path.write_text(path.read_text().replace('[(1,)]', '[(1, "EUR")]'))
    git("add", ".")
    git("commit", "-qm", "Fictional candidate change")
    print(f"Fixture ready: {root}\nReview candidate against baseline.\n"
          "Run tests: python3 -m unittest discover")


if __name__ == "__main__":
    main()
