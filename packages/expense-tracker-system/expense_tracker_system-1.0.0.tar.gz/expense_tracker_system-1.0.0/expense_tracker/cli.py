import sys
import os
from datetime import date, datetime
from typing import Optional


from expense_tracker.database import Database
from expense_tracker.statistics import StatisticsManager

db = Database("data/expenses.db")
stats = StatisticsManager(db)


try:
    from .tracker import ExpenseTracker
except ImportError:
    class ExpenseTracker:
        def __init__(self, db_path=None, auto_load=False):
            print("⚠️  ExpenseTracker not fully implemented - using minimal version")
            from .database import Database
            self.db = Database(db_path) if db_path else None
            self.is_dirty = False
            
        def add_expense(self, amount, category=None, description=None, date_value=None):
            from .database import Database
            import uuid
            
            if self.db is None:
                print("❌ Database not initialized")
                return None
                
            try:
                amount = float(amount)
                if amount <= 0:
                    print("❌ Amount must be positive")
                    return None
                    
                # Process date
                if date_value is None:
                    date_value = date.today()
                elif isinstance(date_value, str):
                    date_value = date.fromisoformat(date_value)
                
                # Create expense data
                expense_data = {
                    'id': f"EXP_{uuid.uuid4().hex[:8]}",
                    'amount': amount,
                    'category': category or 'Uncategorized',
                    'description': description or '',
                    'date': date_value
                }
                
                expense_id = self.db.add_expense(expense_data)
                self.is_dirty = True
                print(f"✅ Expense added (ID: {expense_id})")
                return expense_data
            except ValueError as e:
                print(f"❌ Invalid input: {e}")
                return None
                
        def view_all(self, formatted=True):
            if self.db is None:
                return "No database connection"
            
            expenses = self.db.get_all_expenses()
            if not expenses:
                return "No expenses found"
            
            if formatted:
                output = []
                output.append("=" * 60)
                output.append(f"{'Date':<12} {'Category':<15} {'Amount':<10} {'Description'}")
                output.append("-" * 60)
                for exp in expenses:
                    exp_date = exp.get('date', '')[:10] if exp.get('date') else 'N/A'
                    category = exp.get('category', 'N/A')[:14]
                    amount = f"${exp.get('amount', 0):.2f}"
                    description = exp.get('description', '')[:30]
                    output.append(f"{exp_date:<12} {category:<15} {amount:<10} {description}")
                output.append("=" * 60)
                return "\n".join(output)
            else:
                return str(expenses)
                
        def view_statistics(self):
            if self.db is None:
                return {"error": "Database not initialized"}
            return self.db.get_statistics()
            
        def get_db_statistics(self):
            return self.view_statistics()
            
        def filter(self, **filters):
            if self.db is None:
                return []
            return self.db.filter_expenses(**filters)
            
        def save_to_db(self):
            self.is_dirty = False
            return True
            
        def get_all(self):
            if self.db is None:
                return []
            return self.db.filter_expenses()
        def show_statistics():
            db = Database("data/expenses.db")
            stats = StatisticsManager(db)

            print("\n📊 STATISTICS")
            for name in stats.list_statistics():
                print(f"- {name}: {stats.get(name)}")


try:
    from .database import Database
except ImportError:
    Database = None


def prompt_input(prompt_text: str, default: str = "") -> str:
    """Get user input with error handling."""
    try:
        if default:
            user_input = input(f"{prompt_text} [{default}]: ").strip()
            return user_input if user_input else default
        else:
            return input(prompt_text).strip()
    except (EOFError, KeyboardInterrupt):
        print("\n👋 Goodbye!")
        sys.exit(0)


def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(title: str):
    """Print a formatted header."""
    clear_screen()
    print("=" * 60)
    print(f"💰 {title.center(56)} 💰")
    print("=" * 60)


def run_cli(db_path: str = "data/expenses.db"):
    """Run the command line interface."""

    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    print_header("EXPENSE TRACKER SYSTEM")
    print(f"📁 Database: {db_path}")
    

    try:
        if Database:
            db = Database(db_path)
            print("✅ Database initialized successfully")
        else:
            print("⚠️  Database module not available")
            db = None
    except Exception as e:
        print(f"❌ Database error: {e}")
        db = None

    try:
        tracker = ExpenseTracker(db_path=db_path, auto_load=True)
        print("✅ Expense tracker initialized")
    except Exception as e:
        print(f"❌ Tracker error: {e}")
        print("⚠️  Using fallback tracker")
        tracker = ExpenseTracker(db_path=db_path, auto_load=False)
        if db:
            tracker.db = db
    
    print("\n" + "=" * 60)
    
    while True:
        print("\n📋 MAIN MENU")
        print("-" * 30)
        print("1) ➕ Add Expense")
        print("2) 📋 View All Expenses")
        print("3) 📊 View Statistics")
        print("4) 🔍 Filter Expenses")
        print("5) 💾 Export Data")
        print("6) 📥 Import Data")
        print("7) 🚪 Save and Exit")
        print("8) ❌ Exit Without Saving")
        print("-" * 30)
        
        choice = prompt_input("Choose option (1-8): ").strip()
        
        if choice == "1":
            print_header("ADD EXPENSE")
            try:
                
                while True:
                    amt_str = prompt_input("Amount ($): ")
                    try:
                        amount = float(amt_str)
                        if amount <= 0:
                            print("❌ Amount must be positive")
                            continue
                        break
                    except ValueError:
                        print("❌ Please enter a valid number")
                
               
                category = prompt_input("Category (e.g., Food, Transport): ", "Miscellaneous")
                
                
                description = prompt_input("Description: ", "")
                
                
                today = date.today().isoformat()
                date_str = prompt_input("Date (YYYY-MM-DD): ", today)
                try:
                    expense_date = date.fromisoformat(date_str) if date_str else date.today()
                except ValueError:
                    print("⚠️  Invalid date format, using today")
                    expense_date = date.today()
                
                
                exp = tracker.add_expense(
                    amount=amount,
                    category=category,
                    description=description,
                    date_value=expense_date
                )
                
                if exp:
                    print(f"\n✅ Expense added successfully!")
                    if isinstance(exp, dict):
                        print(f"   Amount: ${amount:.2f}")
                        print(f"   Category: {category}")
                        print(f"   Date: {expense_date}")
                        if description:
                            print(f"   Description: {description}")
                else:
                    print("❌ Failed to add expense")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
            
            input("\nPress Enter to continue...")
        
        elif choice == "2":
            print_header("ALL EXPENSES")
            
           
            format_choice = prompt_input("Format (1=Formatted, 2=JSON): ", "1")
            formatted = format_choice != "2"
            
           
            limit_str = prompt_input("Maximum number to show (0 for all): ", "0")
            try:
                limit = int(limit_str) if limit_str and int(limit_str) > 0 else None
            except:
                limit = None
            
            try:
                if hasattr(tracker, 'view_all'):
                    output = tracker.view_all(formatted=formatted)
                    print(output)
                elif hasattr(tracker, 'get_all'):
                    expenses = tracker.get_all()
                    if limit:
                        expenses = expenses[:limit]
                    
                    if formatted:
                        print("=" * 80)
                        print(f"{'ID':<10} {'Date':<12} {'Category':<15} {'Amount':<10} {'Description'}")
                        print("-" * 80)
                        for exp in expenses:
                            if isinstance(exp, dict):
                                exp_id = exp.get('id', 'N/A')[:8]
                                exp_date = exp.get('date', '')[:10] if exp.get('date') else 'N/A'
                                category = exp.get('category', 'N/A')[:14]
                                amount = f"${exp.get('amount', 0):.2f}"
                                description = exp.get('description', '')[:40]
                                print(f"{exp_id:<10} {exp_date:<12} {category:<15} {amount:<10} {description}")
                    else:
                        import json
                        print(json.dumps(expenses, indent=2, default=str))
                else:
                    print("❌ View method not available")
            except Exception as e:
                print(f"❌ Error: {e}")
            
            input("\nPress Enter to continue...")
        
        elif choice == "3":
            print_header("STATISTICS")
            
            try:
               
                if hasattr(tracker, 'get_db_statistics'):
                    db_stats = tracker.get_db_statistics()
                    print("📊 DATABASE STATISTICS:")
                    print("-" * 40)
                    if isinstance(db_stats, dict):
                        print(f"💰 Total Expenses: ${db_stats.get('total_expenses', 0):.2f}")
                        print(f"📈 Expense Count: {db_stats.get('expense_count', 0)}")
                        print(f"📊 Average Expense: ${db_stats.get('average_expense', 0):.2f}")
                        
                        # Category breakdown
                        print(f"\n📁 BY CATEGORY:")
                        for cat, amount in db_stats.get('by_category', {}).items():
                            print(f"  {cat}: ${amount:.2f}")
                    else:
                        print(db_stats)
                
                
                print(f"\n🎯 CUSTOM STATISTICS:")
                print("-" * 40)
                if hasattr(tracker, 'view_statistics'):
                    custom_stats = tracker.view_statistics()
                    if isinstance(custom_stats, dict):
                        for k, v in custom_stats.items():
                            print(f"  {k}: {v}")
                    else:
                        print(custom_stats)
                else:
                    print("No custom statistics available")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
            
            input("\nPress Enter to continue...")
        
        elif choice == "4":
            print_header("FILTER EXPENSES")
            print("Leave fields empty to skip filters")
            print("-" * 50)
            
            try:
                start_date = prompt_input("Start date (YYYY-MM-DD): ")
                end_date = prompt_input("End date (YYYY-MM-DD): ")
                category = prompt_input("Category: ")
                
                min_amount = None
                max_amount = None
                min_str = prompt_input("Minimum amount: ")
                if min_str:
                    try:
                        min_amount = float(min_str)
                    except:
                        print("⚠️  Invalid minimum amount, ignoring")
                
                max_str = prompt_input("Maximum amount: ")
                if max_str:
                    try:
                        max_amount = float(max_str)
                    except:
                        print("⚠️  Invalid maximum amount, ignoring")
                
                search_text = prompt_input("Search in description: ")
                
                
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
                if search_text:
                    filters['text'] = search_text
                
               
                if hasattr(tracker, 'filter'):
                    results = tracker.filter(**filters)
                elif hasattr(tracker.db, 'filter_expenses'):
                    results = tracker.db.filter_expenses(**filters)
                else:
                    results = []
                
                print(f"\n🔍 Found {len(results)} expenses:")
                print("-" * 70)
                
                if results:
                    print(f"{'#':<3} {'Date':<12} {'Category':<15} {'Amount':<10} {'Description'}")
                    print("-" * 70)
                    for i, exp in enumerate(results, 1):
                        if isinstance(exp, dict):
                            exp_date = exp.get('date', '')[:10] if exp.get('date') else 'N/A'
                            exp_cat = exp.get('category', 'N/A')[:14]
                            exp_amt = f"${exp.get('amount', 0):.2f}"
                            exp_desc = exp.get('description', '')[:40]
                            print(f"{i:<3} {exp_date:<12} {exp_cat:<15} {exp_amt:<10} {exp_desc}")
                        else:
                            print(f"{i}: {str(exp)[:60]}...")
                else:
                    print("No expenses found matching your criteria")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
            
            input("\nPress Enter to continue...")
        
        elif choice == "5":
            print_header("EXPORT DATA")
            try:
                if db:
                    default_file = f"expense_export_{date.today().isoformat()}.json"
                    export_file = prompt_input("Export filename: ", default_file)
                    
                    db.export_to_json(export_file)
                    print(f"✅ Data exported to {export_file}")
                    print(f"📁 Location: {os.path.abspath(export_file)}")
                else:
                    print("❌ Database not available for export")
            except Exception as e:
                print(f"❌ Export error: {e}")
            
            input("\nPress Enter to continue...")
        
        elif choice == "6":
            print_header("IMPORT DATA")
            try:
                if db:
                    import_file = prompt_input("Import filename: ")
                    if os.path.exists(import_file):
                        counts = db.import_from_json(import_file)
                        print(f"✅ Data imported successfully!")
                        print(f"   Categories: {counts.get('categories', 0)}")
                        print(f"   Expenses: {counts.get('expenses', 0)}")
                    else:
                        print(f"❌ File not found: {import_file}")
                else:
                    print("❌ Database not available for import")
            except Exception as e:
                print(f"❌ Import error: {e}")
            
            input("\nPress Enter to continue...")
        
        elif choice == "7":
            print_header("SAVE AND EXIT")
            try:
                if hasattr(tracker, 'save_to_db'):
                    if tracker.save_to_db():
                        print("✅ Expenses saved successfully")
                    else:
                        print("⚠️  No changes to save")
                elif hasattr(tracker, 'is_dirty') and tracker.is_dirty:
                    print("⚠️  You have unsaved changes, but no save method available")
                else:
                    print("✅ Database is up to date")
                
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error saving: {e}")
                retry = prompt_input("Exit anyway? (y/N): ").lower()
                if retry == 'y':
                    break
        
        elif choice == "8":
            print_header("EXIT WITHOUT SAVING")
            if hasattr(tracker, 'is_dirty') and tracker.is_dirty:
                confirm = prompt_input("⚠️  You have unsaved changes. Exit anyway? (y/N): ").lower()
                if confirm != 'y':
                    continue
            print("\n👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid option. Please choose 1-8.")


def main():
    """Main CLI entry point."""
    try:
        if len(sys.argv) > 1:
            db_path = sys.argv[1]
        else:
            db_path = "data/expenses.db"
        
        run_cli(db_path)
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()