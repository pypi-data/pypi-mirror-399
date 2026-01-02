# expense_tracker/__init__.py
"""
Expense Tracker System
"""

__version__ = "1.0.0"
__all__ = [
    "Expense",
    "Category", 
    "StatisticsManager",
    "ExpenseTracker",
    "Database",
    "DataSeeder",
    "app"
]

def __getattr__(name):
    if name == "Expense":
        from .models import Expense
        return Expense
    elif name == "Category":
        from .models import Category
        return Category
    elif name == "StatisticsManager":
        from .models import StatisticsManager
        return StatisticsManager
    elif name == "ExpenseTracker":
        from .tracker import ExpenseTracker
        return ExpenseTracker
    elif name == "Database":
        from .database import Database
        return Database
    elif name == "DataSeeder":
        from .seed import DataSeeder
        return DataSeeder
    elif name == "app":
        from .api import app
        return app
    else:
        raise AttributeError(f"module 'expense_tracker' has no attribute '{name}'")