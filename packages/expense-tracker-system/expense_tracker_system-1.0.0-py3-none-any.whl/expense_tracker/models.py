import json
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, List, Dict, Any, Union
from uuid import uuid4
import re


class Expense:
    """Represents one expense record with database integration."""

    def __init__(self, amount: Union[float, int, str], 
                 category: Optional[str] = None,
                 description: Optional[str] = None,
                 date_value: Union[date, datetime, str, None] = None,
                 uid: Optional[str] = None):
        """
        Initialize an expense.
        
        Args:
            amount: Expense amount (must be positive)
            category: Optional category name
            description: Optional description
            date_value: Date of expense (date, datetime, or ISO string)
            uid: Optional unique ID (auto-generated if not provided)
        """
        self._id = uid or f"EXP_{uuid4().hex[:8]}"
        self._amount = 0.0
        self._category = ""
        self._description = ""
        self._date = None

        self.amount = amount
        self.category = category
        self.description = description
        self.date = date_value if date_value is not None else date.today()

    @property
    def id(self) -> str:
        """Get expense ID (read-only)."""
        return self._id

    @property
    def amount(self) -> float:
        """Get expense amount."""
        return self._amount

    @amount.setter
    def amount(self, value: Union[float, int, str]) -> None:
        """Set expense amount with validation."""
        if value is None:
            raise ValueError("Amount is required")
        
        try:
            val = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Amount must be a number, got {type(value).__name__}") from exc
        
        if val < 0:
            raise ValueError("Amount must be non-negative")
        
        self._amount = round(val, 2)

    @property
    def category(self) -> str:
        """Get expense category."""
        return self._category

    @category.setter
    def category(self, value: Optional[str]) -> None:
        """Set expense category with validation."""
        if value is None:
            self._category = "Uncategorized"
        elif not isinstance(value, str):
            raise ValueError("Category must be a string")
        else:
            val = value.strip()
            self._category = val if val else "Uncategorized"

    @property
    def description(self) -> str:
        """Get expense description."""
        return self._description

    @description.setter
    def description(self, value: Optional[str]) -> None:
        """Set expense description."""
        if value is None:
            self._description = ""
        elif not isinstance(value, str):
            raise ValueError("Description must be a string")
        else:
            self._description = value.strip()

    @property
    def date(self) -> date:
        """Get expense date."""
        return self._date

    @date.setter
    def date(self, value: Union[date, datetime, str]) -> None:
        """Set expense date with flexible parsing."""
        if value is None:
            self._date = date.today()
            return
        
        if isinstance(value, date):
            self._date = value
            return
        
        if isinstance(value, datetime):
            self._date = value.date()
            return
        
        if isinstance(value, str):
            value = value.strip()
            
            try:
                if 'T' in value or ' ' in value:
                    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                    self._date = dt.date()
                    return
                else:
                    # Try date-only format
                    d = date.fromisoformat(value)
                    self._date = d
                    return
            except ValueError:
                # Try other common formats
                formats = [
                    '%Y-%m-%d',
                    '%d/%m/%Y',
                    '%m/%d/%Y',
                    '%d-%m-%Y',
                    '%m-%d-%Y',
                ]
                
                for fmt in formats:
                    try:
                        dt = datetime.strptime(value, fmt)
                        self._date = dt.date()
                        return
                    except ValueError:
                        continue
                
                raise ValueError(f"Unable to parse date string: '{value}'. "
                               f"Use YYYY-MM-DD format.")
        
        raise ValueError(f"Date must be a date, datetime, or string, got {type(value).__name__}")

    def as_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with Python objects."""
        return {
            "id": self.id,
            "amount": self.amount,
            "category": self.category,
            "description": self.description,
            "date": self.date,
        }

    def to_serializable(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return {
            "id": self.id,
            "amount": self.amount,
            "category": self.category,
            "description": self.description,
            "date": self.date.isoformat() if self.date else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Expense':
        """Create Expense from dictionary."""
        return cls(
            amount=data.get("amount", 0),
            category=data.get("category"),
            description=data.get("description"),
            date_value=data.get("date"),
            uid=data.get("id")
        )

    @classmethod
    def from_serializable(cls, data: Dict[str, Any]) -> 'Expense':
        """Create Expense from serializable dictionary."""
        return cls.from_dict(data)

    def __repr__(self) -> str:
        """String representation for debugging."""
        date_str = self.date.isoformat() if self.date else "None"
        return (f"Expense(id={self.id[:8]}..., "
                f"amount=${self.amount:.2f}, "
                f"category='{self.category}', "
                f"date={date_str})")

    def __str__(self) -> str:
        """User-friendly string representation."""
        date_str = self.date.strftime("%Y-%m-%d") if self.date else "Unknown"
        return (f"${self.amount:.2f} for {self.category} "
                f"on {date_str} - {self.description[:30]}...")

    def __eq__(self, other: object) -> bool:
        """Equality comparison (ignores ID)."""
        if not isinstance(other, Expense):
            return False
        return (
            self.id == other.id and
            self.amount == other.amount
            and self.category == other.category
            and self.description == other.description
            and self.date == other.date
        )

    def __hash__(self) -> int:
        """Hash based on ID."""
        return hash(self.id)


class Category:
    """Category model for expense categorization."""
    
    def __init__(self, name: str, description: str = "",
                 budget_limit: float = 0.0, monthly_budget: float = 0.0):
        """
        Initialize a category.
        
        Args:
            name: Category name (required)
            description: Optional description
            budget_limit: Maximum budget for this category
            monthly_budget: Monthly budget limit
        """
        if not isinstance(name, str) or name.strip() == "":
            raise ValueError("Category name must be non-empty string")
        
        self._name = name.strip()
        self.description = description.strip()
        self.budget_limit = budget_limit
        self.monthly_budget = monthly_budget

    @property
    def name(self) -> str:
        """Get category name (read-only)."""
        return self._name

    @property
    def budget_limit(self) -> float:
        """Get budget limit."""
        return self._budget_limit

    @budget_limit.setter
    def budget_limit(self, value: float) -> None:
        """Set budget limit with validation."""
        try:
            val = float(value)
        except (TypeError, ValueError):
            raise ValueError("Budget limit must be a number")
        
        if val < 0:
            raise ValueError("Budget limit cannot be negative")
        
        self._budget_limit = round(val, 2)

    @property
    def monthly_budget(self) -> float:
        """Get monthly budget."""
        return self._monthly_budget

    @monthly_budget.setter
    def monthly_budget(self, value: float) -> None:
        """Set monthly budget with validation."""
        try:
            val = float(value)
        except (TypeError, ValueError):
            raise ValueError("Monthly budget must be a number")
        
        if val < 0:
            raise ValueError("Monthly budget cannot be negative")
        
        self._monthly_budget = round(val, 2)

    def set_budget(self, limit: float, monthly: Optional[float] = None) -> None:
        """Set budget limits."""
        self.budget_limit = limit
        if monthly is not None:
            self.monthly_budget = monthly

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'description': self.description,
            'budget_limit': self.budget_limit,
            'monthly_budget': self.monthly_budget
        }

    def to_serializable(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return self.to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Category':
        """Create Category from dictionary."""
        return cls(
            name=data['name'],
            description=data.get('description', ''),
            budget_limit=data.get('budget_limit', 0.0),
            monthly_budget=data.get('monthly_budget', 0.0)
        )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (f"Category(name='{self.name}', "
                f"budget_limit=${self.budget_limit:.2f}, "
                f"monthly_budget=${self.monthly_budget:.2f})")

    def __str__(self) -> str:
        """User-friendly string representation."""
        return self.name

    def __eq__(self, other: object) -> bool:
        """Equality comparison by name."""
        if not isinstance(other, Category):
            return False
        return self.name == other.name

    def __hash__(self) -> int:
        """Hash based on name."""
        return hash(self.name)


class StatisticsManager:
    """Manager for computing various statistics on expenses."""
    _instance = None 
    
    def __new__(cls):
        # Reset for testing
        cls._instance = None
        return super().__new__(cls)
    
    def __init__(self):
       
        if hasattr(self, '_stats'):
            return
        self._stats = {}
        self._register_builtins()
    def _register_builtins(self):
        """Register built-in statistics functions."""
        self.register("total", lambda expenses: sum(exp.amount for exp in expenses))
        self.register("average", lambda expenses: sum(exp.amount for exp in expenses) / len(expenses) if expenses else 0)
        self.register("count", lambda expenses: len(expenses))
    def clear(self):
        """Clear all registered statistics."""
        self._stats = {}

    def _register_default_statistics(self) -> None:
        """Register default statistics functions."""
        self.register("total", self._compute_total)
        self.register("average", self._compute_average)
        self.register("count", self._compute_count)
        self.register("by_category", self._compute_by_category)
        self.register("monthly_total", self._compute_monthly_total)



        def by_category_func(expenses):
            result = {}
            for exp in expenses:
                result[exp.category] = result.get(exp.category, 0) + exp.amount
            return result
        self.register("by_category", by_category_func)
        
        # Register monthly_total statistic
        def monthly_total_func(expenses):
            result = {}
            for exp in expenses:
                if hasattr(exp.date, 'strftime'):
                    month_key = exp.date.strftime('%Y-%m')
                else:
                    month_key = str(exp.date)[:7] if exp.date else "unknown"
                result[month_key] = result.get(month_key, 0) + exp.amount
            return result
        self.register("monthly_total", monthly_total_func)
        
        # Register total_sum (alias for total)
        self.register("total_sum", lambda expenses: sum(exp.amount for exp in expenses))

    def _compute_total(self, expenses: List[Expense]) -> float:
        """Compute total of all expenses."""
        return sum(exp.amount for exp in expenses)

    def _compute_average(self, expenses: List[Expense]) -> float:
        """Compute average expense amount."""
        if not expenses:
            return 0.0
        return self._compute_total(expenses) / len(expenses)

    def _compute_count(self, expenses: List[Expense]) -> int:
        """Count number of expenses."""
        return len(expenses)

    def _compute_by_category(self, expenses: List[Expense]) -> Dict[str, float]:
        """Compute total by category."""
        result = {}
        for exp in expenses:
            category = exp.category or "Uncategorized"
            result[category] = result.get(category, 0.0) + exp.amount
        return result

    def _compute_monthly_total(self, expenses: List[Expense]) -> Dict[str, float]:
        """Compute total by month (YYYY-MM)."""
        result = {}
        for exp in expenses:
            if exp.date:
                month_key = exp.date.strftime("%Y-%m")
                result[month_key] = result.get(month_key, 0.0) + exp.amount
        return result

    def register(self, name: str, func: callable) -> None:
        """Register a new statistic function."""
        if name in self._stats:
            raise ValueError(f"Statistic with name '{name}' already registered")
        if not callable(func):
            raise ValueError("Function must be callable")
        self._stats[name] = func

    def unregister(self, name: str) -> None:
        """Unregister a statistic function."""
        if name not in self._stats:
            raise KeyError(f"No statistic named '{name}'")
        del self._stats[name]

    def compute(self, name: str, expenses: List[Expense]) -> Any:
        """Compute a specific statistic."""
        if name not in self._stats:
            raise KeyError(f"No statistic named '{name}'")
        return self._stats[name](expenses)

    def compute_all(self, expenses: List[Expense]) -> Dict[str, Any]:
        """Compute all registered statistics."""
        results = {}
        for name, func in self._stats.items():
            try:
                results[name] = func(expenses)
            except Exception as e:
                results[name] = f"Error: {str(e)}"
        return results

    def names(self) -> List[str]:
        """Get names of all registered statistics."""
        return list(self._stats.keys())

    def clear(self) -> None:
        """Clear all statistics (except defaults)."""
        self._stats.clear()
        self._register_default_statistics()

    def __len__(self) -> int:
        """Number of registered statistics."""
        return len(self._stats)

    def __repr__(self) -> str:
        """String representation."""
        return f"StatisticsManager(statistics={list(self._stats.keys())})"


def validate_expense_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and normalize expense data."""
    validated = data.copy()
    
    if 'amount' in validated:
        try:
            validated['amount'] = float(validated['amount'])
            if validated['amount'] < 0:
                raise ValueError("Amount cannot be negative")
        except (TypeError, ValueError) as e:
            raise ValueError(f"Invalid amount: {e}")
    
    if 'date' in validated and validated['date']:
        if isinstance(validated['date'], str):
            try:
                if 'T' in validated['date']:
                    dt = datetime.fromisoformat(validated['date'].replace('Z', '+00:00'))
                    validated['date'] = dt.date()
                else:
                    validated['date'] = date.fromisoformat(validated['date'])
            except ValueError:
                raise ValueError(f"Invalid date format: {validated['date']}")
    
    return validated


def create_expense_from_input(amount: Union[float, str], 
                             category: Optional[str] = None,
                             description: Optional[str] = None,
                             date_str: Optional[str] = None) -> Expense:
    """Create an expense from user input."""
    date_value = None
    if date_str:
        try:
            if 'T' in date_str:
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                date_value = dt.date()
            else:
                date_value = date.fromisoformat(date_str)
        except ValueError:
            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y']:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    date_value = dt.date()
                    break
                except ValueError:
                    continue
    
    return Expense(
        amount=amount,
        category=category,
        description=description,
        date_value=date_value or date.today()
    )