"""
Utility functions and decorators for Expense Tracker
"""

import traceback
import functools
import re
import os
import json
import csv
from typing import Callable, Any, TypeVar, cast
from datetime import datetime, date
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


F = TypeVar('F', bound=Callable[..., Any])


def log_action(fn: F) -> F:
    """Decorator to log function calls."""
    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        print(f"[LOG] Calling {fn.__name__} with args={args} kwargs={kwargs}")
        result = fn(*args, **kwargs)
        print(f"[LOG] {fn.__name__} finished")
        return result
    return cast(F, wrapper)


def mark_dirty(fn: F) -> F:
    """Decorator to mark object as dirty after method call."""
    @functools.wraps(fn)
    def wrapper(self, *args: Any, **kwargs: Any) -> Any:
        result = fn(self, *args, **kwargs)
        try:
            if hasattr(self, "_dirty"):
                self._dirty = True
        except Exception:
            pass
        return result
    return cast(F, wrapper)


def handle_errors(fn: F) -> F:
    """Decorator to handle and format errors."""
    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return fn(*args, **kwargs)
        except ValueError as e:
            raise ValueError(f"{fn.__name__}: {e}") from e
        except (OSError, IOError) as e:
            raise e
        except Exception as e:
            tb = traceback.format_exc()
            raise RuntimeError(f"{fn.__name__} unexpected error: {e}\n{tb}") from e
    return cast(F, wrapper)


def retry(max_attempts: int = 3, delay: float = 1.0):
    """Decorator to retry function on failure."""
    def decorator(fn: F) -> F:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return fn(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        print(f"Retry {attempt + 1}/{max_attempts} for {fn.__name__}: {e}")
                        import time
                        time.sleep(delay)
            raise last_exception
        return cast(F, wrapper)
    return decorator


# ========== VALIDATION FUNCTIONS ==========
def validate_amount(amount: Any) -> float:
    """Validate and convert amount to float."""
    try:
        val = float(amount)
        if val < 0:
            raise ValueError("Amount must be non-negative")
        return round_currency(val)
    except (TypeError, ValueError):
        raise ValueError("Amount must be a valid number")


def validate_date(date_str: str) -> date:
    """Validate and parse date string."""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        raise ValueError("Date must be in YYYY-MM-DD format")


def is_valid_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


# ========== FORMATTING FUNCTIONS ==========
def format_currency(amount: float, currency_symbol: str = "$", include_symbol: bool = True) -> str:
    """Format amount as currency string."""
    rounded = round_currency(amount)
    if include_symbol:
        return f"{currency_symbol}{rounded:,.2f}"
    return f"{rounded:,.2f}"


def round_currency(value: float) -> float:
    """Round currency values properly to 2 decimal places."""
    return float(Decimal(str(value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))


def format_date(dt: Any, fmt: str = "%Y-%m-%d") -> str:
    """Format date/datetime object to string."""
    if isinstance(dt, str):
        return dt
    elif isinstance(dt, datetime):
        return dt.strftime(fmt)
    elif isinstance(dt, date):
        return dt.strftime(fmt)
    else:
        raise ValueError(f"Cannot format type: {type(dt)}")


def calculate_monthly_summary(expenses: list, sort_by: str = 'date') -> dict:
    """Calculate monthly expense summary."""
    monthly = {}
    
    for expense in expenses:
        month_key = None
        if hasattr(expense, 'date'):
            exp_date = expense.date
            if isinstance(exp_date, str):
                month_key = exp_date[:7] 
            elif hasattr(exp_date, 'strftime'):
                month_key = exp_date.strftime("%Y-%m")
        
        if not month_key:
            continue
        
       
        amount = getattr(expense, 'amount', 0)
        

        if month_key not in monthly:
            monthly[month_key] = {
                'total': 0.0,
                'count': 0,
                'average': 0.0,
                'categories': {}
            }
        
        monthly[month_key]['total'] += amount
        monthly[month_key]['count'] += 1
        

        category = getattr(expense, 'category', 'Uncategorized')
        if category not in monthly[month_key]['categories']:
            monthly[month_key]['categories'][category] = 0.0
        monthly[month_key]['categories'][category] += amount

    for data in monthly.values():
        if data['count'] > 0:
            data['average'] = data['total'] / data['count']
    

    if sort_by == 'date':
        monthly = dict(sorted(monthly.items()))
    elif sort_by == 'total':
        monthly = dict(sorted(monthly.items(), key=lambda x: x[1]['total'], reverse=True))
    
    return monthly


def calculate_percentages(values: dict) -> dict:
    """Calculate percentages for a dictionary of values."""
    total = sum(values.values())
    if total == 0:
        return {k: 0.0 for k in values.keys()}
    
    return {k: (v / total) * 100 for k, v in values.items()}


def read_json_file(filepath: str, default: Any = None) -> Any:
    """Read and parse JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return default if default is not None else {}
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {filepath}: {e}")


def write_json_file(filepath: str, data: Any) -> None:
    """Write data to JSON file."""
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)


def export_to_csv(data: list, filepath: str) -> bool:
    """Export data to CSV file."""
    if not data:
        return False
    
    try:
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        # Get fieldnames from first item
        fieldnames = list(data[0].keys()) if data else []
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        
        return True
    except Exception as e:
        print(f"Error exporting to CSV: {e}")
        return False


def load_config() -> dict:
    """Load configuration from environment variables."""
    config = {
        'db_path': os.getenv('EXPENSE_DB_PATH', 'data/expenses.db'),
        'api_host': os.getenv('API_HOST', '0.0.0.0'),
        'api_port': int(os.getenv('API_PORT', '8000')),
        'debug': os.getenv('DEBUG', 'False').lower() == 'true',
        'log_level': os.getenv('LOG_LEVEL', 'INFO'),
        'max_expenses_per_page': int(os.getenv('MAX_EXPENSES_PER_PAGE', '100'))
    }
    
    return config


def get_timestamp() -> str:
    """Get current timestamp string."""
    return datetime.now().isoformat()


def human_readable_size(size_bytes: int) -> str:
    """Convert bytes to human readable size."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"