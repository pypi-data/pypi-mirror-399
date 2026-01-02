from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator, field_validator
from typing import List, Optional, Dict, Any
from datetime import date
import uuid
import os
import uvicorn
from .tracker import ExpenseTracker
from .database import Database




app = FastAPI(title="Expense Tracker API", version="1.0.0")
DB_PATH = os.getenv("EXPENSE_DB_PATH", "data/expenses.db")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ExpenseCreate(BaseModel):
    amount: float
    category: Optional[str] = None
    description: Optional[str] = None
    date: Optional[date] = None

    @field_validator('amount')
    @classmethod
    def amount_must_be_positive(cls, v):
        if v < 0:
            raise ValueError('amount must be non-negative')
        return v

class ExpenseUpdate(BaseModel):
    amount: Optional[float] = None
    category: Optional[str] = None
    description: Optional[str] = None
    date: Optional[date] = None

class ExpenseResponse(BaseModel):
    id: str
    amount: float
    category: Optional[str]
    description: Optional[str]
    date: date

class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    budget_limit: Optional[float] = 0.0
    monthly_budget: Optional[float] = 0.0

class StatisticsResponse(BaseModel):
    total_expenses: float
    expense_count: int
    average_expense: float
    by_category: Dict[str, float]
    monthly_breakdown: Dict[str, float]


def get_database():
    return Database(DB_PATH)

def get_tracker(db: Database = Depends(get_database)):
    return ExpenseTracker(db)


@app.get("/")
def root():
    return {"message": "Expense Tracker API"}

@app.get("/expenses", response_model=List[ExpenseResponse])
def get_all_expenses(tracker: ExpenseTracker = Depends(get_tracker)):
    """Get all expenses."""
    return [exp.to_serializable() for exp in tracker.get_all()]

@app.get("/expenses/{expense_id}", response_model=ExpenseResponse)
def get_expense(expense_id: str, db: Database = Depends(get_database)):
    """Get expense by ID."""
    expense = db.get_expense(expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense

@app.post("/expenses", response_model=ExpenseResponse)
def create_expense(expense_data: ExpenseCreate, tracker: ExpenseTracker = Depends(get_tracker)):
    """Create a new expense."""
    expense = tracker.add_expense(
        amount=expense_data.amount,
        category=expense_data.category,
        description=expense_data.description,
        date_value=expense_data.date
    )
    return expense.to_serializable()

@app.post("/expenses")
def create(amount: float, category: str, description: str = "", date: date = None):
    return {"id": "1", "amount": amount, "category": category, "description": description}



@app.put("/expenses/{expense_id}", response_model=ExpenseResponse)
def update_expense(expense_id: str, updates: ExpenseUpdate, db: Database = Depends(get_database)):
    """Update an expense."""
    update_dict = {k: v for k, v in updates.dict().items() if v is not None}
    
    if not update_dict:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    success = db.update_expense(expense_id, update_dict)
    if not success:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    return db.get_expense(expense_id)

@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: str, db: Database = Depends(get_database)):
    """Delete an expense."""
    success = db.delete_expense(expense_id)
    if not success:
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"message": "Expense deleted successfully"}


@app.get("/categories")
def get_categories(db: Database = Depends(get_database)):
    """Get all categories."""
    return db.get_all_categories()

@app.post("/categories")
def create_category(category_data: CategoryCreate, db: Database = Depends(get_database)):
    """Create a new category."""
    category_dict = category_data.dict()
    category_name = db.add_category(category_dict)
    return {"message": f"Category '{category_name}' created"}

@app.get("/statistics", response_model=StatisticsResponse)
def get_statistics(db: Database = Depends(get_database)):
    """Get expense statistics."""
    return db.get_statistics()

@app.get("/statistics/custom")
def get_custom_statistics(tracker: ExpenseTracker = Depends(get_tracker)):
    """Get custom statistics."""
    return tracker.view_statistics()

@app.get("/expenses/filter")
def filter_expenses(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    category: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    db: Database = Depends(get_database)
):
    """Filter expenses."""
    filters = {}
    if start_date:
        filters['start_date'] = start_date
    if end_date:
        filters['end_date'] = end_date
    if category:
        filters['category'] = category
    if min_amount is not None:
        filters['min_amount'] = min_amount
    if max_amount is not None:
        filters['max_amount'] = max_amount
    
    return db.filter_expenses(**filters)

@app.get("/")
def root():
    """Root endpoint with API information."""
    return {
        "message": "Expense Tracker API",
        "version": "1.0.0",
        "endpoints": {
            "expenses": "/expenses",
            "statistics": "/statistics",
            "categories": "/categories"
        }
    }

def run():
    """Run the API server."""

    uvicorn.run("expense_tracker.api:app", host="0.0.0.0", port=8000, reload=True, log_level="info")