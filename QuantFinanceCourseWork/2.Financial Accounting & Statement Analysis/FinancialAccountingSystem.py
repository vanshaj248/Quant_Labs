import sqlite3
from datetime import datetime
import os

class AccountingDashboard:
    def __init__(self):
        # Initialize database
        self.init_db()

    def init_db(self):
        """Initialize the database and create table if it doesn't exist"""
        db_path = os.path.join(os.path.dirname(__file__), 'accounting.db')
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        
        # Create table if it doesn't exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                acc_id INTEGER PRIMARY KEY AUTOINCREMENT,
                acc_no TEXT NOT NULL UNIQUE,
                acc_name TEXT NOT NULL,
                acc_type TEXT NOT NULL,
                normal_balance TEXT CHECK(normal_balance IN ('Debit', 'Credit')),
                description TEXT,
                is_active INTEGER DEFAULT 1,
                equity_amount REAL DEFAULT 0,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def load_data(self):
        """Load data from database and print to terminal"""
        # Fetch data from database
        self.cursor.execute("SELECT * FROM accounts ORDER BY acc_no")
        rows = self.cursor.fetchall()
        
        if not rows:
            print("No accounts found.")
            return
        
        print(f"{'ID':<4} {'Account No':<12} {'Account Name':<20} {'Type':<10} {'Normal Balance':<15} {'Active':<7} Description")
        print("-"*80)
        for row in rows:
            is_active = "Yes" if row[6] else "No"
            description = row[5] if row[5] else ""
            print(f"{row[0]:<4} {row[1]:<12} {row[2]:<20} {row[3]:<10} {row[4]:<15} {is_active:<7} {description}")
        print(f"\nLoaded {len(rows)} accounts.\n")

    def add_account(self, acc_no, acc_name, acc_type, normal_balance, description, is_active):
        """Add a new account to the database"""
        # Validate required fields
        if not acc_no or not acc_name or not acc_type or not normal_balance:
            print("Error: Please fill in all required fields.")
            return
        
        try:
            # Insert into database
            self.cursor.execute(
                "INSERT INTO accounts (acc_no, acc_name, acc_type, normal_balance, description, is_active) VALUES (?, ?, ?, ?, ?, ?)",
                (acc_no, acc_name, acc_type, normal_balance, description, 1 if is_active else 0)
            )
            self.conn.commit()
            print(f"Account '{acc_name}' added successfully.\n")
            
        except sqlite3.IntegrityError:
            print("Error: Account number must be unique.\n")

    def update_account(self, acc_id, acc_no, acc_name, acc_type, normal_balance, description, is_active):
        """Update selected account"""
        if not acc_id:
            print("Error: Account ID must be provided.")
            return
        
        # Validate required fields
        if not acc_no or not acc_name or not acc_type or not normal_balance:
            print("Error: Please fill in all required fields.")
            return
        
        try:
            # Update database
            self.cursor.execute(
                "UPDATE accounts SET acc_no=?, acc_name=?, acc_type=?, normal_balance=?, description=?, is_active=?, last_updated=CURRENT_TIMESTAMP WHERE acc_id=?",
                (acc_no, acc_name, acc_type, normal_balance, description, 1 if is_active else 0, acc_id)
            )
            if self.cursor.rowcount == 0:
                print(f"Error: No account found with ID {acc_id}.\n")
                return
            self.conn.commit()
            print(f"Account '{acc_name}' updated successfully.\n")
            
        except sqlite3.IntegrityError:
            print("Error: Account number must be unique.\n")

    def delete_account(self, acc_id):
        """Delete selected account"""
        if not acc_id:
            print("Error: Account ID must be provided.")
            return
        
        # Check if account exists
        self.cursor.execute("SELECT acc_name FROM accounts WHERE acc_id=?", (acc_id,))
        row = self.cursor.fetchone()
        if not row:
            print(f"Error: No account found with ID {acc_id}.\n")
            return
        
        acc_name = row[0]
        confirm = input(f"Are you sure you want to delete account '{acc_name}'? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Deletion cancelled.\n")
            return
        
        # Delete from database
        self.cursor.execute("DELETE FROM accounts WHERE acc_id=?", (acc_id,))
        self.conn.commit()
        print(f"Account '{acc_name}' deleted successfully.\n")

    def search_accounts(self, search_term):
        """Search accounts based on input and print results"""
        search_term = search_term.strip()
        
        if not search_term:
            print("Search term is empty. Listing all accounts.\n")
            self.load_data()
            return
        
        self.cursor.execute(
            "SELECT * FROM accounts WHERE acc_no LIKE ? OR acc_name LIKE ? OR acc_type LIKE ? ORDER BY acc_no",
            (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%')
        )
        
        rows = self.cursor.fetchall()
        
        if not rows:
            print("No accounts found matching the search criteria.\n")
            return
        
        print(f"{'ID':<4} {'Account No':<12} {'Account Name':<20} {'Type':<10} {'Normal Balance':<15} {'Active':<7} Description")
        print("-"*80)
        for row in rows:
            is_active = "Yes" if row[6] else "No"
            description = row[5] if row[5] else ""
            print(f"{row[0]:<4} {row[1]:<12} {row[2]:<20} {row[3]:<10} {row[4]:<15} {is_active:<7} {description}")
        print(f"\nFound {len(rows)} accounts.\n")

    def run_terminal_interface(self):
        while True:
            print("Accounting Dashboard")
            print("1. Add Account")
            print("2. Update Account")
            print("3. Delete Account")
            print("4. List Accounts")
            print("5. Search Accounts")
            print("6. Exit")
            choice = input("Enter your choice (1-6): ").strip()
            
            if choice == '1':
                print("\nAdd Account:")
                acc_no = input("Account No: ").strip()
                acc_name = input("Account Name: ").strip()
                acc_type = input("Account Type (Asset, Liability, Equity, Revenue, Expense): ").strip()
                normal_balance = input("Normal Balance (Debit, Credit): ").strip()
                description = input("Description (optional): ").strip()
                is_active_input = input("Is Active? (y/n, default y): ").strip().lower()
                is_active = True if is_active_input in ('', 'y', 'yes') else False
                self.add_account(acc_no, acc_name, acc_type, normal_balance, description, is_active)

            elif choice == '2':
                print("\nUpdate Account:")
                try:
                    acc_id = int(input("Account ID to update: ").strip())
                except ValueError:
                    print("Invalid ID.\n")
                    continue
                acc_no = input("New Account No: ").strip()
                acc_name = input("New Account Name: ").strip()
                acc_type = input("New Account Type (Asset, Liability, Equity, Revenue, Expense): ").strip()
                normal_balance = input("New Normal Balance (Debit, Credit): ").strip()
                description = input("New Description (optional): ").strip()
                is_active_input = input("Is Active? (y/n, default y): ").strip().lower()
                is_active = True if is_active_input in ('', 'y', 'yes') else False
                self.update_account(acc_id, acc_no, acc_name, acc_type, normal_balance, description, is_active)

            elif choice == '3':
                print("\nDelete Account:")
                try:
                    acc_id = int(input("Account ID to delete: ").strip())
                except ValueError:
                    print("Invalid ID.\n")
                    continue
                self.delete_account(acc_id)

            elif choice == '4':
                print("\nList Accounts:")
                self.load_data()

            elif choice == '5':
                print("\nSearch Accounts:")
                search_term = input("Enter search term: ").strip()
                self.search_accounts(search_term)

            elif choice == '6':
                print("Exiting. Goodbye!")
                break

            else:
                print("Invalid choice. Please enter a number between 1 and 6.\n")

    def __del__(self):
        """Close database connection when object is destroyed"""
        if hasattr(self, 'conn'):
            self.conn.close()

if __name__ == "__main__":
    app = AccountingDashboard()
    app.run_terminal_interface()