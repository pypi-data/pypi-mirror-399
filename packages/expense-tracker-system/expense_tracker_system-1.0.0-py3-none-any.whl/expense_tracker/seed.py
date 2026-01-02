"""
Simple Expense Tracker Seeder
Demonstrates threading for I/O-bound operations
"""
import random
from datetime import datetime, date, timedelta
import threading
import time
from typing import List, Dict
import concurrent.futures
import os
import sqlite3

from .database import Database


class DataSeeder:
    """Simple data seeder for demonstration."""
    
    def __init__(self, db_path: str = "data/expenses.db"):
        self.db_path = db_path
        self.categories = ["Food", "Transport", "Entertainment", "Bills", "Shopping"]
        
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    def generate_expense_data(self, count: int) -> List[Dict]:
        """Generate sample expense data."""
        data = []
        start_date = date(2023, 1, 1)
        
        for i in range(count):
            record = {
                'id': f'EXP{i:06d}',
                'amount': round(random.uniform(5, 500), 2),
                'category': random.choice(self.categories),
                'description': f'Expense {i} - {random.choice(["Lunch", "Gas", "Movie", "Groceries"])}',
                'date': (start_date + timedelta(days=random.randint(0, 365))).isoformat()
            }
            data.append(record)
        
        return data
    
    def save_batch_to_db(self, batch: List[Dict], thread_id: int = 0) -> int:
        """Save a batch of expenses (I/O-bound operation)."""
        print(f"  Thread {thread_id}: Saving {len(batch)} expenses...")
        time.sleep(0.1) 
        
        try:
            db = Database(self.db_path)
            count = 0
            
            for expense in batch:
                try:
                    
                    if 'date' in expense and isinstance(expense['date'], str):
                        expense['date'] = date.fromisoformat(expense['date'])
                    
                    db.add_expense(expense)
                    count += 1
                except Exception:
                    continue
            
            return count
        except Exception as e:
            print(f"  Thread {thread_id}: Error: {e}")
            return 0
    
    def seed_with_threading(self, total_expenses: int = 100):
        """Demonstrate threading for I/O-bound operations."""
        print("=" * 60)
        print("EXPENSE TRACKER - THREADING DEMONSTRATION")
        print("=" * 60)
        print(f"Generating {total_expenses} expenses using threading...")
        
        start_time = time.time()
        
        num_threads = 4
        batch_size = total_expenses // num_threads
        
        print("Generating expense data...")
        all_data = self.generate_expense_data(total_expenses)
        
        batches = []
        for i in range(num_threads):
            start_idx = i * batch_size
            end_idx = start_idx + batch_size if i < num_threads - 1 else total_expenses
            batches.append(all_data[start_idx:end_idx])
        
        print(f"Using {num_threads} threads for database operations...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = []
            for i, batch in enumerate(batches):
                if batch: 
                    future = executor.submit(self.save_batch_to_db, batch, i+1)
                    futures.append(future)
            
            total_saved = 0
            for future in concurrent.futures.as_completed(futures):
                try:
                    saved = future.result()
                    total_saved += saved
                    print(f"  Thread completed: saved {saved} expenses")
                except Exception as e:
                    print(f"Thread error: {e}")
        
        elapsed_time = time.time() - start_time
        
        print("-" * 60)
        print(f"✅ Seeding completed in {elapsed_time:.2f} seconds")
        print(f"📊 Total expenses saved: {total_saved}")
        
        try:
            db = Database(self.db_path)
            stats = db.get_statistics()
            print(f"📈 Database now has {stats['expense_count']} expenses")
            print(f"💰 Total amount: ${stats['total_expenses']:.2f}")
        except Exception as e:
            print(f"Note: {e}")
        
        print("=" * 60)
        return total_saved
    
    def seed_without_threading(self, total_expenses: int = 100):
        """Seed without threading for comparison."""
        print("=" * 60)
        print("EXPENSE TRACKER - SINGLE THREAD")
        print("=" * 60)
        print(f"Generating {total_expenses} expenses (no threading)...")
        
        start_time = time.time()
        
        data = self.generate_expense_data(total_expenses)
        
        saved = self.save_batch_to_db(data, 1)
        
        elapsed_time = time.time() - start_time
        
        print("-" * 60)
        print(f"✅ Seeding completed in {elapsed_time:.2f} seconds")
        print(f"📊 Total expenses saved: {saved}")
        print("=" * 60)
        
        return saved
    
    def run_seeding_pipeline(self):
        """Main seeding pipeline."""
        print("=" * 60)
        print("EXPENSE TRACKER - DATA SEEDING DEMONSTRATION")
        print("=" * 60)
        
        print("\n1️⃣  SINGLE THREAD (Baseline):")
        single_start = time.time()
        single_saved = self.seed_without_threading(100)
        single_time = time.time() - single_start
        
        time.sleep(1)
        
        print("\n2️⃣  WITH THREADING (4 threads):")
        thread_start = time.time()
        thread_saved = self.seed_with_threading(100)
        thread_time = time.time() - thread_start
        
        print("\n" + "=" * 60)
        print("📊 COMPARISON RESULTS")
        print("=" * 60)
        print(f"Single thread time: {single_time:.2f} seconds")
        print(f"Multi-thread time:  {thread_time:.2f} seconds")
        
        if thread_time > 0:
            speedup = single_time / thread_time
            print(f"Speedup factor: {speedup:.2f}x")
            
            if speedup > 1:
                print("✅ Threading improved performance!")
            elif speedup < 1:
                print("⚠️  Threading was slower (SQLite limitation)")
            else:
                print("➖ No significant difference")
        
        print("\n💡 Explanation:")
        print("- Database operations are I/O-bound (waiting for disk)")
        print("- Threading allows overlapping I/O wait times")
        print("- SQLite has some concurrency limitations")
        print("- Real-world databases (PostgreSQL, MySQL) benefit more")
        
        print("=" * 60)


def main():
    """Main entry point."""
    seeder = DataSeeder("data/expenses.db")
    seeder.run_seeding_pipeline()


if __name__ == "__main__":
    main()