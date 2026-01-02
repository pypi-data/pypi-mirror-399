import sqlite3
from contextlib import contextmanager
from typing import Generator, List, Dict, Any, Optional
from datetime import date, datetime
from pathlib import Path
import json
from sqlalchemy import create_engine, Column, String, Float, Date, Text, func, extract
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

Base = declarative_base()


class ExpenseDB(Base):
    """SQLAlchemy model for expenses table."""
    __tablename__ = 'expenses'

    id = Column(String, primary_key=True)
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    date = Column(Date, nullable=False)
    created_at = Column(Date, default=datetime.now)
    updated_at = Column(Date, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'amount': float(self.amount) if self.amount else 0.0,
            'category': self.category,
            'description': self.description,
            'date': self.date.isoformat() if self.date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class CategoryDB(Base):
    """SQLAlchemy model for categories table."""
    __tablename__ = 'categories'

    name = Column(String, primary_key=True)
    description = Column(Text, nullable=True)
    budget_limit = Column(Float, default=0.0)
    monthly_budget = Column(Float, default=0.0)

    def to_dict(self):
        return {
            'name': self.name,
            'description': self.description,
            'budget_limit': float(self.budget_limit) if self.budget_limit else 0.0,
            'monthly_budget': float(self.monthly_budget) if self.monthly_budget else 0.0
        }


class Database:
    """Database manager with SQLAlchemy ORM."""
    
    def __init__(self, db_path: str = "data/expenses.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.engine = create_engine(
            f'sqlite:///{db_path}',
            echo=False,
            pool_pre_ping=True
        )
        self.SessionLocal = sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=False
        )
        self._create_tables()

    def _create_tables(self):
        """Create database tables if they don't exist."""
        Base.metadata.create_all(bind=self.engine)

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Context manager for database sessions."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def add_expense(self, expense_data: Dict[str, Any]) -> str:
        """Add a new expense to the database."""
        with self.get_session() as session:
            if 'id' not in expense_data:
                expense_data['id'] = f"EXP_{datetime.now().timestamp()}"
            if 'date' not in expense_data:
                expense_data['date'] = date.today()
            
            expense = ExpenseDB(**expense_data)
            session.add(expense)
            session.flush()
            return expense.id

    def get_expense(self, expense_id: str) -> Optional[Dict[str, Any]]:
        """Get an expense by ID."""
        with self.get_session() as session:
            expense = session.query(ExpenseDB).filter(ExpenseDB.id == expense_id).first()
            return expense.to_dict() if expense else None

    def get_all_expenses(self, limit: int = None) -> List[Dict[str, Any]]:
        """Get all expenses, optionally limited."""
        with self.get_session() as session:
            query = session.query(ExpenseDB).order_by(ExpenseDB.date.desc())
            if limit:
                query = query.limit(limit)
            expenses = query.all()
            return [exp.to_dict() for exp in expenses]

    def update_expense(self, expense_id: str, updates: Dict[str, Any]) -> bool:
        """Update an expense."""
        with self.get_session() as session:
            expense = session.query(ExpenseDB).filter(ExpenseDB.id == expense_id).first()
            if expense:
                updates.pop('id', None)
                updates.pop('created_at', None)
                
                for key, value in updates.items():
                    if hasattr(expense, key):
                        setattr(expense, key, value)
                expense.updated_at = datetime.now()
                return True
            return False

    def delete_expense(self, expense_id: str) -> bool:
        """Delete an expense."""
        with self.get_session() as session:
            expense = session.query(ExpenseDB).filter(ExpenseDB.id == expense_id).first()
            if expense:
                session.delete(expense)
                return True
            return False

    def filter_expenses(self, **filters) -> List[Dict[str, Any]]:
        """Filter expenses based on criteria."""
        with self.get_session() as session:
            query = session.query(ExpenseDB)
            
            if 'start_date' in filters and filters['start_date']:
                start_date = filters['start_date']
                if isinstance(start_date, str):
                    start_date = date.fromisoformat(start_date)
                query = query.filter(ExpenseDB.date >= start_date)
            
            if 'end_date' in filters and filters['end_date']:
                end_date = filters['end_date']
                if isinstance(end_date, str):
                    end_date = date.fromisoformat(end_date)
                query = query.filter(ExpenseDB.date <= end_date)
            
            if 'category' in filters and filters['category']:
                query = query.filter(ExpenseDB.category == filters['category'])
            
            if 'min_amount' in filters and filters['min_amount'] is not None:
                query = query.filter(ExpenseDB.amount >= filters['min_amount'])
            
            if 'max_amount' in filters and filters['max_amount'] is not None:
                query = query.filter(ExpenseDB.amount <= filters['max_amount'])
            
            if 'text' in filters and filters['text']:
                search_text = f"%{filters['text']}%"
                query = query.filter(
                    (ExpenseDB.description.like(search_text)) |
                    (ExpenseDB.category.like(search_text))
                )
            
            expenses = query.order_by(ExpenseDB.date.desc(), ExpenseDB.created_at.desc()).all()
            return [exp.to_dict() for exp in expenses]

    def add_category(self, category_data: Dict[str, Any]) -> str:
        """Add a new category."""
        with self.get_session() as session:
            category = CategoryDB(**category_data)
            session.add(category)
            session.flush()
            return category.name

    def get_all_categories(self) -> List[Dict[str, Any]]:
        """Get all categories."""
        with self.get_session() as session:
            categories = session.query(CategoryDB).all()
            return [cat.to_dict() for cat in categories]

    def get_category(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a category by name."""
        with self.get_session() as session:
            category = session.query(CategoryDB).filter(CategoryDB.name == name).first()
            return category.to_dict() if category else None

    def get_statistics(self) -> Dict[str, Any]:
        """Get expense statistics."""
        with self.get_session() as session:
            
            total_result = session.query(func.sum(ExpenseDB.amount)).scalar()
            total = float(total_result) if total_result else 0.0
            
            
            count = session.query(func.count(ExpenseDB.id)).scalar() or 0
            
            
            avg = total / count if count > 0 else 0.0
            
           
            category_totals = {}
            category_result = session.query(
                ExpenseDB.category,
                func.sum(ExpenseDB.amount).label('total')
            ).group_by(ExpenseDB.category).all()
            
            for category, total_amount in category_result:
                cat_name = category or "Uncategorized"
                category_totals[cat_name] = float(total_amount) if total_amount else 0.0
            
            
            monthly = {}
            monthly_result = session.query(
                func.strftime('%Y-%m', ExpenseDB.date).label('month'),
                func.sum(ExpenseDB.amount).label('total')
            ).group_by('month').order_by('month').all()
            
            for month, total_amount in monthly_result:
                monthly[month] = float(total_amount) if total_amount else 0.0

            return {
                'total_expenses': total,
                'expense_count': count,
                'average_expense': avg,
                'by_category': category_totals,
                'monthly_breakdown': monthly
            }

    def bulk_insert_expenses(self, expenses_data: List[Dict[str, Any]]) -> int:
        """Insert multiple expenses at once (optimized)."""
        with self.get_session() as session:
           
            for expense in expenses_data:
                if 'id' not in expense:
                    expense['id'] = f"BULK_{datetime.now().timestamp()}_{hash(str(expense))}"
            
            session.bulk_insert_mappings(ExpenseDB, expenses_data)
            return len(expenses_data)

    def export_to_json(self, filepath: str):
        """Export all data to JSON file."""
        data = {
            'expenses': self.get_all_expenses(),
            'categories': self.get_all_categories(),
            'statistics': self.get_statistics(),
            'exported_at': datetime.now().isoformat()
        }
        
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)

    def import_from_json(self, filepath: str) -> Dict[str, int]:
        """Import data from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        counts = {'expenses': 0, 'categories': 0}
        
        with self.get_session() as session:
            
            if 'categories' in data:
                for cat_data in data['categories']:
                    # Check if category exists
                    existing = session.query(CategoryDB).filter(
                        CategoryDB.name == cat_data['name']
                    ).first()
                    if not existing:
                        category = CategoryDB(**cat_data)
                        session.add(category)
                        counts['categories'] += 1
            
            
            if 'expenses' in data:
                for exp_data in data['expenses']:
                
                    if 'date' in exp_data and isinstance(exp_data['date'], str):
                        exp_data['date'] = date.fromisoformat(exp_data['date'])
                    
                    existing = session.query(ExpenseDB).filter(
                        ExpenseDB.id == exp_data.get('id')
                    ).first()
                    if not existing:
                        expense = ExpenseDB(**exp_data)
                        session.add(expense)
                        counts['expenses'] += 1
        
        return counts       