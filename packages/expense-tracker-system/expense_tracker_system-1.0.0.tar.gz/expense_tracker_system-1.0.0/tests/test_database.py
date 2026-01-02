# tests/test_database.py - FIXED
import pytest
from datetime import date, datetime
from sqlalchemy.exc import IntegrityError
from expense_tracker.database import Database  # ADDED IMPORT


class TestDatabase:
    """Test Database class."""
    
    def test_database_initialization(self, database):
        """Test database initialization."""
        # Verify tables were created
        with database.get_session() as session:
            # Check if ExpenseDB table exists
            from sqlalchemy import inspect
            inspector = inspect(database.engine)
            tables = inspector.get_table_names()
            
            assert 'expenses' in tables
            assert 'categories' in tables
    
    def test_add_expense(self, database, sample_expense_data):
        """Test adding an expense to database."""
        expense_id = database.add_expense(sample_expense_data)
        
        assert expense_id == 'test_exp_001'
        
        # Verify the expense was added
        expense = database.get_expense(expense_id)
        assert expense is not None
        assert expense['amount'] == 100.50
        assert expense['category'] == 'Food'
        assert expense['description'] == 'Lunch at restaurant'
    
    def test_get_expense(self, database, sample_expense_data):
        """Test retrieving an expense by ID."""
        # Add expense first
        expense_id = database.add_expense(sample_expense_data)
        
        # Get expense
        expense = database.get_expense(expense_id)
        
        assert expense['id'] == expense_id
        assert expense['amount'] == 100.50
        assert expense['category'] == 'Food'
        assert expense['description'] == 'Lunch at restaurant'
        assert expense['date'] == '2024-01-15'
    
    def test_get_expense_not_found(self, database):
        """Test getting non-existent expense."""
        expense = database.get_expense('non_existent_id')
        assert expense is None
    
    def test_get_all_expenses(self, database):
        """Test getting all expenses."""
        # Add multiple expenses
        expenses_data = [
            {'id': 'exp1', 'amount': 100, 'category': 'Food', 'description': 'Test1', 'date': date(2024, 1, 1)},
            {'id': 'exp2', 'amount': 200, 'category': 'Transport', 'description': 'Test2', 'date': date(2024, 1, 2)},
            {'id': 'exp3', 'amount': 300, 'category': 'Food', 'description': 'Test3', 'date': date(2024, 1, 3)},
        ]
        
        for data in expenses_data:
            database.add_expense(data)
        
        # Get all expenses
        all_expenses = database.get_all_expenses()
        
        assert len(all_expenses) == 3
        # Should be ordered by date descending (newest first)
        assert all_expenses[0]['id'] == 'exp3'
        assert all_expenses[1]['id'] == 'exp2'
        assert all_expenses[2]['id'] == 'exp1'
    
    def test_update_expense(self, database, sample_expense_data):
        """Test updating an expense."""
        # Add expense first
        expense_id = database.add_expense(sample_expense_data)
        
        # Update expense
        updates = {'amount': 150.75, 'description': 'Updated lunch'}
        success = database.update_expense(expense_id, updates)
        
        assert success is True
        
        # Verify update
        expense = database.get_expense(expense_id)
        assert expense['amount'] == 150.75
        assert expense['description'] == 'Updated lunch'
        # Other fields should remain unchanged
        assert expense['category'] == 'Food'
        assert expense['date'] == '2024-01-15'
    
    def test_update_expense_not_found(self, database):
        """Test updating non-existent expense."""
        success = database.update_expense('non_existent', {'amount': 100})
        assert success is False
    
    def test_delete_expense(self, database, sample_expense_data):
        """Test deleting an expense."""
        # Add expense first
        expense_id = database.add_expense(sample_expense_data)
        
        # Verify it exists
        assert database.get_expense(expense_id) is not None
        
        # Delete expense
        success = database.delete_expense(expense_id)
        
        assert success is True
        
        # Verify deletion
        assert database.get_expense(expense_id) is None
    
    def test_delete_expense_not_found(self, database):
        """Test deleting non-existent expense."""
        success = database.delete_expense('non_existent')
        assert success is False
    
    def test_filter_expenses(self, database):
        """Test filtering expenses."""
        # Add test expenses
        test_expenses = [
            {'id': 'exp1', 'amount': 100, 'category': 'Food', 'description': 'Lunch', 'date': date(2024, 1, 15)},
            {'id': 'exp2', 'amount': 200, 'category': 'Transport', 'description': 'Taxi', 'date': date(2024, 1, 20)},
            {'id': 'exp3', 'amount': 150, 'category': 'Food', 'description': 'Dinner', 'date': date(2024, 2, 1)},
            {'id': 'exp4', 'amount': 300, 'category': 'Entertainment', 'description': 'Movie', 'date': date(2024, 2, 15)},
            {'id': 'exp5', 'amount': 50, 'category': 'Food', 'description': 'Coffee', 'date': date(2024, 3, 1)},
        ]
        
        for exp in test_expenses:
            database.add_expense(exp)
        
        # Test filter by category
        food_expenses = database.filter_expenses(category='Food')
        assert len(food_expenses) == 3
        assert all(exp['category'] == 'Food' for exp in food_expenses)
        
        # Test filter by date range
        jan_expenses = database.filter_expenses(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31)
        )
        assert len(jan_expenses) == 2
        
        # Test filter by amount range - FIXED EXPECTATION
        cheap_expenses = database.filter_expenses(
            min_amount=0,
            max_amount=100
        )
        assert len(cheap_expenses) == 2  # 50 and 100 are both <= 100
        amounts = [exp['amount'] for exp in cheap_expenses]
        assert 50 in amounts
        assert 100 in amounts
        
        # Test multiple filters
        filtered = database.filter_expenses(
            category='Food',
            start_date=date(2024, 2, 1),
            min_amount=100
        )
        assert len(filtered) == 1
        assert filtered[0]['id'] == 'exp3'
    
    def test_add_category(self, database, sample_category_data):
        """Test adding a category."""
        category_name = database.add_category(sample_category_data)
        
        assert category_name == 'Test Category'
        
        # Verify category was added
        categories = database.get_all_categories()
        test_category = next((c for c in categories if c['name'] == 'Test Category'), None)
        assert test_category is not None
        assert test_category['description'] == 'Test description'
        assert test_category['budget_limit'] == 1000.00
        assert test_category['monthly_budget'] == 500.00
    
    def test_get_all_categories(self, database):
        """Test getting all categories."""
        # Add multiple categories
        categories_data = [
            {'name': 'Food', 'description': 'Food expenses', 'budget_limit': 1000, 'monthly_budget': 500},
            {'name': 'Transport', 'description': 'Transportation', 'budget_limit': 500, 'monthly_budget': 300},
            {'name': 'Entertainment', 'description': 'Fun activities', 'budget_limit': 300, 'monthly_budget': 200},
        ]
        
        for data in categories_data:
            database.add_category(data)
        
        categories = database.get_all_categories()
        
        assert len(categories) == 3
        category_names = [c['name'] for c in categories]
        assert 'Food' in category_names
        assert 'Transport' in category_names
        assert 'Entertainment' in category_names
    
    def test_get_statistics(self, database):
        """Test getting expense statistics."""
        # Add test expenses
        test_expenses = [
            {'id': 'exp1', 'amount': 100, 'category': 'Food', 'description': 'Lunch', 'date': date(2024, 1, 15)},
            {'id': 'exp2', 'amount': 200, 'category': 'Transport', 'description': 'Taxi', 'date': date(2024, 1, 20)},
            {'id': 'exp3', 'amount': 150, 'category': 'Food', 'description': 'Dinner', 'date': date(2024, 2, 1)},
            {'id': 'exp4', 'amount': 300, 'category': 'Entertainment', 'description': 'Movie', 'date': date(2024, 2, 15)},
        ]
        
        for exp in test_expenses:
            database.add_expense(exp)
        
        stats = database.get_statistics()
        
        assert stats['total_expenses'] == 750.0
        assert stats['expense_count'] == 4
        assert stats['average_expense'] == 187.5
        
        # Check category breakdown
        assert stats['by_category']['Food'] == 250.0
        assert stats['by_category']['Transport'] == 200.0
        assert stats['by_category']['Entertainment'] == 300.0
        
        # Check monthly breakdown
        assert '2024-01' in stats['monthly_breakdown']
        assert '2024-02' in stats['monthly_breakdown']
        assert stats['monthly_breakdown']['2024-01'] == 300.0
        assert stats['monthly_breakdown']['2024-02'] == 450.0
    
    def test_empty_database_statistics(self, database):
        """Test statistics on empty database."""
        stats = database.get_statistics()
        
        assert stats['total_expenses'] == 0.0
        assert stats['expense_count'] == 0
        assert stats['average_expense'] == 0.0
        assert stats['by_category'] == {}
        assert stats['monthly_breakdown'] == {}
    
    def test_bulk_insert_expenses(self, database):
        """Test bulk insertion of expenses."""
        expenses_data = [
            {'id': f'exp{i}', 'amount': i * 10, 'category': 'Test', 'description': f'Test {i}', 'date': date(2024, 1, i)}
            for i in range(1, 6)
        ]
        
        inserted_count = database.bulk_insert_expenses(expenses_data)
        
        assert inserted_count == 5
        
        # Verify all were inserted
        all_expenses = database.get_all_expenses()
        assert len(all_expenses) == 5
        
        # Verify data integrity
        for i, expense in enumerate(sorted(all_expenses, key=lambda x: x['amount']), 1):
            assert expense['amount'] == i * 10
            assert expense['category'] == 'Test'
            assert expense['description'] == f'Test {i}'
    
    def test_export_import_json(self, database, tmp_path):
        """Test JSON export and import."""
        # Add test data
        test_expenses = [
            {'id': 'exp1', 'amount': 100, 'category': 'Food', 'description': 'Test1', 'date': date(2024, 1, 1)},
            {'id': 'exp2', 'amount': 200, 'category': 'Transport', 'description': 'Test2', 'date': date(2024, 1, 2)},
        ]
        
        for exp in test_expenses:
            database.add_expense(exp)
        
        # Add test category
        database.add_category({'name': 'TestCat', 'description': 'Test', 'budget_limit': 1000})
        
        # Export to JSON
        export_path = tmp_path / 'export.json'
        database.export_to_json(str(export_path))
        
        assert export_path.exists()
        
        # Create new database and import
        new_db_path = tmp_path / 'new.db'
        new_db = Database(str(new_db_path))  # FIXED: Database is imported
        
        # Import data
        counts = new_db.import_from_json(str(export_path))
        
        assert counts['expenses'] == 2
        assert counts['categories'] == 1
        
        # Verify imported data
        imported_expenses = new_db.get_all_expenses()
        assert len(imported_expenses) == 2
        
        imported_categories = new_db.get_all_categories()
        assert len(imported_categories) == 1