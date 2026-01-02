# tests/test_tracker.py - FIXED
import pytest
from datetime import date
from unittest.mock import Mock, patch
from expense_tracker.tracker import ExpenseTracker  # ADDED IMPORT


class TestExpenseTracker:
    """Test ExpenseTracker class."""
    
    def test_tracker_initialization(self, expense_tracker):
        """Test ExpenseTracker initialization."""
        assert expense_tracker.db_path is not None
        assert hasattr(expense_tracker, 'db')
        assert expense_tracker.is_dirty == False
    
    def test_add_expense(self, expense_tracker):
        """Test adding an expense through tracker."""
        expense = expense_tracker.add_expense(
            amount=100.50,
            category='Food',
            description='Lunch',
            date_value=date(2024, 1, 15)
        )
        
        assert expense is not None
        assert expense.amount == 100.50
        assert expense.category == 'Food'
        assert expense.description == 'Lunch'
        assert expense.date == date(2024, 1, 15)
        assert expense_tracker.is_dirty == True
    
    def test_add_expense_with_string_date(self, expense_tracker):
        """Test adding expense with date as string."""
        expense = expense_tracker.add_expense(
            amount=100,
            category='Food',
            description='Test',
            date_value='2024-01-15'
        )
        
        assert expense.date == date(2024, 1, 15)
    
    def test_add_expense_without_date(self, expense_tracker):
        """Test adding expense without date (should use today)."""
        expense = expense_tracker.add_expense(
            amount=100,
            category='Food',
            description='Test'
        )
        
        assert expense.date == date.today()
    
    def test_add_expense_invalid_amount(self, expense_tracker):
        """Test adding expense with invalid amount."""
        with pytest.raises(ValueError):
            expense_tracker.add_expense(
                amount='invalid',
                category='Food',
                description='Test'
            )
    
    def test_view_all_expenses(self, expense_tracker):
        """Test viewing all expenses."""
        # Add some expenses
        expense_tracker.add_expense(100, 'Food', 'Lunch', date(2024, 1, 1))
        expense_tracker.add_expense(200, 'Transport', 'Taxi', date(2024, 1, 2))
        
        # Test formatted view
        formatted = expense_tracker.view_all(formatted=True)
        assert isinstance(formatted, str)
        assert 'Food' in formatted
        assert 'Transport' in formatted
        assert '100.00' in formatted
        assert '200.00' in formatted
        
        # Test unformatted view
        unformatted = expense_tracker.view_all(formatted=False)
        assert isinstance(unformatted, str)
        # Should contain expense representations
    
    def test_view_all_empty(self, expense_tracker):
        """Test viewing all expenses when database is empty."""
        result = expense_tracker.view_all()
        assert 'No expenses' in result or 'No data' in result or result == ''
    
    def test_get_all_expenses(self, expense_tracker):
        """Test getting all expenses as objects."""
        # Add expenses
        expense_tracker.add_expense(100, 'Food', 'Lunch')
        expense_tracker.add_expense(200, 'Transport', 'Taxi')
        
        expenses = expense_tracker.get_all()
        
        assert len(expenses) == 2
        assert all(hasattr(exp, 'amount') for exp in expenses)
        assert all(hasattr(exp, 'category') for exp in expenses)
        assert all(hasattr(exp, 'description') for exp in expenses)
        assert all(hasattr(exp, 'date') for exp in expenses)
    
    def test_view_statistics(self, expense_tracker):
        """Test viewing statistics."""
        # Add expenses
        expense_tracker.add_expense(100, 'Food', 'Lunch', date(2024, 1, 15))
        expense_tracker.add_expense(200, 'Transport', 'Taxi', date(2024, 1, 16))
        expense_tracker.add_expense(50, 'Food', 'Coffee', date(2024, 2, 1))
        
        stats = expense_tracker.view_statistics()
        
        assert isinstance(stats, dict)
        assert 'total' in stats
        assert 'average' in stats
        assert 'count' in stats
        assert 'by_category' in stats
        
        assert stats['count'] == 3
        assert stats['total'] == 350.0
        assert stats['average'] == pytest.approx(116.67, 0.01)
        assert stats['by_category']['Food'] == 150.0
        assert stats['by_category']['Transport'] == 200.0
    
    def test_get_db_statistics(self, expense_tracker):
        """Test getting database statistics."""
        # Add expenses
        expense_tracker.add_expense(100, 'Food', 'Lunch')
        expense_tracker.add_expense(200, 'Transport', 'Taxi')
        
        stats = expense_tracker.get_db_statistics()
        
        assert isinstance(stats, dict)
        assert 'total_expenses' in stats
        assert 'expense_count' in stats
        assert 'average_expense' in stats
        assert 'by_category' in stats
        assert 'monthly_breakdown' in stats
    
    def test_filter_expenses(self, expense_tracker):
        """Test filtering expenses."""
        # Add test expenses
        expense_tracker.add_expense(100, 'Food', 'Lunch', date(2024, 1, 15))
        expense_tracker.add_expense(200, 'Transport', 'Taxi', date(2024, 1, 20))
        expense_tracker.add_expense(150, 'Food', 'Dinner', date(2024, 2, 1))
        expense_tracker.add_expense(300, 'Entertainment', 'Movie', date(2024, 2, 15))
        
        # Filter by category
        food_expenses = expense_tracker.filter(category='Food')
        assert len(food_expenses) == 2
        assert all(exp.category == 'Food' for exp in food_expenses)
        
        # Filter by date range
        jan_expenses = expense_tracker.filter(
            start_date='2024-01-01',
            end_date='2024-01-31'
        )
        assert len(jan_expenses) == 2
        
        # Filter by amount
        expensive_expenses = expense_tracker.filter(min_amount=200)
        assert len(expensive_expenses) == 2
        assert all(exp.amount >= 200 for exp in expensive_expenses)
        
        # Multiple filters
        filtered = expense_tracker.filter(
            category='Food',
            start_date='2024-01-01',
            min_amount=100
        )
        assert len(filtered) == 1
        assert filtered[0].description == 'Lunch'
    
    def test_save_to_db(self, expense_tracker):
        """Test saving to database."""
        # Mock the database save method
        with patch.object(expense_tracker.db, 'bulk_insert_expenses') as mock_save:
            expense_tracker.add_expense(100, 'Food', 'Lunch')
            expense_tracker.save_to_db()
            
            # Should call save method
            mock_save.assert_called_once()
            expense_tracker.is_dirty = False
    
    def test_save_to_db_no_changes(self, expense_tracker):
        """Test saving when no changes were made."""
        # Initially not dirty
        assert expense_tracker.is_dirty == False
        
        # Save should not do anything significant
        result = expense_tracker.save_to_db()
        assert result is True
    
    def test_auto_load_on_initialization(self, database):
        """Test auto-load on tracker initialization."""
        # Add some expenses to database
        with database.get_session() as session:
            from expense_tracker.database import ExpenseDB
            session.add(ExpenseDB(
                id='test1',
                amount=100,
                category='Food',
                description='Test',
                date=date(2024, 1, 1)
            ))
            session.commit()
        
        # Create tracker with auto_load=True
        tracker = ExpenseTracker(db_path=database.db_path, auto_load=True)  # FIXED: ExpenseTracker imported
        
        # Should have loaded existing expenses
        expenses = tracker.get_all()
        assert len(expenses) >= 1
    
    @patch('builtins.print')
    def test_expense_string_representation(self, mock_print, expense_tracker):
        """Test expense string representation."""
        expense = expense_tracker.add_expense(100, 'Food', 'Lunch')
        
        # Test __str__ method
        str_repr = str(expense)
        assert 'Food' in str_repr
        assert '100.00' in str_repr
        
        # Test __repr__ method
        repr_str = repr(expense)
        assert 'Expense' in repr_str
        assert expense.id in repr_str