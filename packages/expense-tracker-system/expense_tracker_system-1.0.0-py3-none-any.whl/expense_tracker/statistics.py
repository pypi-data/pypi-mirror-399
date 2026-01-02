"""
Statistics Manager for Expense Tracker
SAFE: no circular imports
"""

from typing import Dict, Callable, Any
import inspect


class StatisticsManager:
    def __init__(self, db):
        self.db = db
        self._statistics = {}

        self._register_builtins()

    def _register_builtins(self):
        self.register("total_expenses", self.total_expenses)
        self.register("average_expense", self.average_expense)
        self.register("count_expenses", self.count_expenses)
        self.register("expenses_by_category", self.expenses_by_category)
        self.register("expenses_by_date", self.expenses_by_date)

    def register(self, name: str, func: Callable):
        self._statistics[name] = func

    def get(self, name: str) -> Any:
        if name not in self._statistics:
            raise KeyError(f"Statistic '{name}' not found")
        return self._statistics[name]()
    
    def list_statistics(self):
        return list(self._statistics.keys())

    def compute_all(self, exs=None, *_, **__):
        """
        Compute all statistics.
        Supports both:
        - DB-based stats: func()
        - Expense-list stats: func(exs)
        """
        results = {}

        for name, func in self._statistics.items():
            try:
                params = inspect.signature(func).parameters
                if len(params) == 0:
                    results[name] = func()
                else:
                    if exs is None:
                        results[name] = "Error: No expenses provided"
                    else:
                        results[name] = func(exs)
            except Exception as e:
                results[name] = f"Error: {e}"

        return results

    def total_expenses(self):
        row = self.db.execute(
            "SELECT SUM(amount) FROM expenses"
        ).fetchone()
        return row[0] or 0.0

    def average_expense(self):
        row = self.db.execute(
            "SELECT AVG(amount) FROM expenses"
        ).fetchone()
        return row[0] or 0.0

    def count_expenses(self):
        row = self.db.execute(
            "SELECT COUNT(*) FROM expenses"
        ).fetchone()
        return row[0] or 0

    def expenses_by_category(self):
        rows = self.db.execute(
            """
            SELECT category, SUM(amount)
            FROM expenses
            GROUP BY category
            """
        ).fetchall()
        return {c or "Uncategorized": v for c, v in rows}

    def expenses_by_date(self):
        rows = self.db.execute(
            """
            SELECT date, SUM(amount)
            FROM expenses
            GROUP BY date
            ORDER BY date
            """
        ).fetchall()
        return {d: v for d, v in rows}
