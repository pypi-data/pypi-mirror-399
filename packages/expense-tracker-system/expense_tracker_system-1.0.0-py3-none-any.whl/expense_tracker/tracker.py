import os
import tempfile
from datetime import datetime, date
from typing import Callable, Dict, List, Optional, Any, Iterator
import traceback

from .models import Expense, Category, StatisticsManager
from .database import Database
from .utils import log_action, mark_dirty, handle_errors
from expense_tracker.statistics import StatisticsManager



from expense_tracker.database import Database
from expense_tracker.statistics import StatisticsManager

db = Database("data/expenses.db")
stats = StatisticsManager(db)  # ✅ correct

class ExpenseTracker:
    """Main expense tracker class with database integration."""
    
    def __init__(self, db_path: str = "data/expenses.db", auto_load: bool = False):
        self._database = Database(db_path)
        self._expenses: List[Expense] = []
        self._statistics = StatisticsManager(db_path)
        self._dirty: bool = False
        self._auto_load = bool(auto_load)

        self._register_builtins()

        if self._auto_load:
            try:
                self.load_from_db()
            except Exception:
                pass

    def _register_builtins(self):
        """Register built-in statistics for the tracker."""
        try:
            self._statistics.register("count", lambda exs: len(exs))
        except ValueError:
            pass
        
        try:
            self._statistics.register("total", lambda exs: sum(exp.amount for exp in exs))
        except ValueError:
            pass
        
        try:
            self._statistics.register("average", lambda exs: sum(exp.amount for exp in exs) / len(exs) if exs else 0)
        except ValueError:
            pass
        
        def maximum(exs):
            return max((e.amount for e in exs), default=0.0)
        self._statistics.register("max", maximum)
        
        def totals_by_category(exs):
            totals = {}
            for e in exs:
                k = e.category or "<uncategorized>"
                totals[k] = totals.get(k, 0.0) + e.amount
            return totals
        self._statistics.register("totals_by_category", totals_by_category)

    @handle_errors
    @mark_dirty
    @log_action
    def add_expense(self, amount, category, description, date_value=None) -> Expense:
        """Add a new expense."""
        exp = Expense(
            amount=amount,
            category=category,
            description=description,
            date_value=date_value
        )
        
        self._database.add_expense(exp.to_serializable())
        
        self._expenses.append(exp)
        return exp

    @handle_errors
    @mark_dirty
    @log_action
    def remove_expense(self, expense_or_index_or_id) -> bool:
        """Remove an expense by ID, index, or Expense object."""
        
        if isinstance(expense_or_index_or_id, int):
            idx = expense_or_index_or_id
            if 0 <= idx < len(self._expenses):
                expense = self._expenses[idx]
                self._database.delete_expense(expense.id)
                self._expenses.pop(idx)
                return True
            return False

        if isinstance(expense_or_index_or_id, Expense):
            expense = expense_or_index_or_id
            success = self._database.delete_expense(expense.id)
            if success:
                try:
                    self._expenses.remove(expense)
                except ValueError:
                    pass
            return success

        ident = str(expense_or_index_or_id)
        success = self._database.delete_expense(ident)
        if success:
            self._expenses = [e for e in self._expenses if e.id != ident]
        return success

    def get_all(self) -> List[Expense]:
        """Get all expenses."""
        return list(self._expenses)

    def view_all(self, formatted: bool = False):
        """View all expenses, optionally formatted."""
        exs = self.get_all()
        if formatted:
            lines = []
            for i, e in enumerate(exs):
                lines.append(f"{i}: {e.amount:.2f} | {e.category or '-'} | {e.date.isoformat()} | {e.description}")
            return "\n".join(lines) if lines else "(no expenses)"
        return exs

    def filter(self, start_date=None, end_date=None, category=None, 
               min_amount=None, max_amount=None, text=None) -> List[Expense]:
        """Filter expenses based on criteria."""
        
        def to_date(v):
            if v is None:
                return None
            if isinstance(v, date):
                return v
            if isinstance(v, datetime):
                return v.date()
            if isinstance(v, str):
                try:
                    return date.fromisoformat(v)
                except ValueError:
                    try:
                        return datetime.fromisoformat(v).date()
                    except ValueError:
                        raise ValueError("date filter must be YYYY-MM-DD or ISO datetime string")
            raise ValueError("invalid date value")

        sd = to_date(start_date)
        ed = to_date(end_date)
        cat_norm = category.strip() if category else None
        tx = text.lower().strip() if text else None

        results: List[Expense] = []
        for e in self._expenses:
            if sd and e.date < sd:
                continue
            if ed and e.date > ed:
                continue
            if cat_norm and e.category != cat_norm:
                continue
            if min_amount is not None and e.amount < float(min_amount):
                continue
            if max_amount is not None and e.amount > float(max_amount):
                continue
            if tx:
                if tx not in e.description.lower() and tx not in (e.category or "").lower():
                    continue
            results.append(e)
        return results

    def register_stat(self, name, callable_stat):
        """Register a custom statistic function."""
        self._statistics.register(name, callable_stat)

    def unregister_stat(self, name):
        """Unregister a statistic function."""
        self._statistics.unregister(name)

    def view_statistics(self):
        """Compute and view all registered statistics."""
        return self._statistics.compute_all(self.get_all())

    def get_stat_names(self):
        """Get names of all registered statistics."""
        return self._statistics.names()

    def load_from_db(self):
        """Load expenses from database."""
        db_expenses = self._database.get_all_expenses()
        self._expenses = [
            Expense.from_serializable(exp) for exp in db_expenses
        ]
        self._dirty = False

    def save_to_db(self):
        """Save expenses to database."""
        for expense in self._expenses:
            self._database.add_expense(expense.to_serializable())
        self._dirty = False

    def get_db_statistics(self) -> Dict[str, Any]:
        """Get statistics directly from database."""
        return self._database.get_statistics()

    def clear(self, confirm: bool = False):
        """Clear all expenses."""
        if not confirm:
            raise ValueError("confirm=True required to clear all expenses")
        self._expenses.clear()
        self._dirty = True

    def merge_from(self, other, deduplicate: bool = True):
        """Merge expenses from another ExpenseTracker."""
        if not isinstance(other, ExpenseTracker):
            raise ValueError("other must be ExpenseTracker")
        
        before = len(self._expenses)
        existing_ids = {e.id for e in self._expenses}
        
        for e in other.get_all():
            if deduplicate and e.id in existing_ids:
                continue
            self._expenses.append(e)
            self._database.add_expense(e.to_serializable())
        
        self._dirty = True
        return len(self._expenses) - before

    @property
    def is_dirty(self):
        return bool(self._dirty)

    @property
    def categories(self):
        cats = sorted({(e.category or "").strip() for e in self._expenses if e.category is not None})
        return cats

    def __len__(self):
        return len(self._expenses)

    def __iter__(self):
        return iter(self._expenses)

    def __contains__(self, item):
        if isinstance(item, Expense):
            return item in self._expenses
        sid = str(item)
        return any(e.id == sid for e in self._expenses)

    def __getitem__(self, index):
        return self._expenses[index]

    def __repr__(self):
        return f"ExpenseTracker({len(self._expenses)} expenses, dirty={self._dirty})"

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self._dirty:
            self.save_to_db()
        return False