import sqlite3
import pandas as pd

class FinancialAccountingSystem:
    def __init__(self, db_name='financial_accounting.db'):
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        """Initialize the database with all required tables"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Chart of Accounts
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS chart_of_accounts (
            account_id INTEGER PRIMARY KEY,
            account_number TEXT UNIQUE,
            account_name TEXT NOT NULL,
            account_type TEXT CHECK(account_type IN ('Asset', 'Liability', 'Equity', 'Revenue', 'Expense')),
            normal_balance TEXT CHECK(normal_balance IN ('Debit', 'Credit')),
            description TEXT,
            is_active BOOLEAN DEFAULT TRUE
        )
        ''')
        
        # Journal Entries
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS journal_entries (
            entry_id INTEGER PRIMARY KEY,
            entry_date DATE NOT NULL,
            description TEXT,
            reference TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Journal Entry Lines
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS journal_entry_lines (
            line_id INTEGER PRIMARY KEY,
            entry_id INTEGER,
            account_id INTEGER,
            amount DECIMAL(15,2) NOT NULL,
            side TEXT CHECK(side IN ('Debit', 'Credit')),
            description TEXT,
            FOREIGN KEY (entry_id) REFERENCES journal_entries (entry_id),
            FOREIGN KEY (account_id) REFERENCES chart_of_accounts (account_id)
        )
        ''')
        
        # Customers
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            contact_info TEXT,
            credit_limit DECIMAL(15,2),
            balance DECIMAL(15,2) DEFAULT 0
        )
        ''')
        
        # Vendors
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS vendors (
            vendor_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            contact_info TEXT,
            payment_terms TEXT
        )
        ''')
        
        # Inventory Items
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            item_id INTEGER PRIMARY KEY,
            item_code TEXT UNIQUE,
            description TEXT,
            unit_cost DECIMAL(15,2),
            quantity_on_hand INTEGER DEFAULT 0,
            reorder_level INTEGER DEFAULT 0
        )
        ''')
        
        conn.commit()
        conn.close()
        
        # Initialize default accounts if not exists
        self.initialize_default_accounts()
    
    def initialize_default_accounts(self):
        """Create default chart of accounts"""
        default_accounts = [
            # Assets
            ('1010', 'Cash', 'Asset', 'Debit', 'Main operating cash account'),
            ('1200', 'Accounts Receivable', 'Asset', 'Debit', 'Amounts owed by customers'),
            ('1400', 'Inventory', 'Asset', 'Debit', 'Goods available for sale'),
            ('1500', 'Equipment', 'Asset', 'Debit', 'Office equipment and furniture'),
            
            # Liabilities
            ('2000', 'Accounts Payable', 'Liability', 'Credit', 'Amounts owed to vendors'),
            ('2500', 'Loans Payable', 'Liability', 'Credit', 'Outstanding loans'),
            
            # Equity
            ('3000', 'Owner\'s Capital', 'Equity', 'Credit', 'Owner investment'),
            ('3500', 'Retained Earnings', 'Equity', 'Credit', 'Accumulated profits'),
            
            # Revenue
            ('4000', 'Sales Revenue', 'Revenue', 'Credit', 'Revenue from product sales'),
            ('4100', 'Service Revenue', 'Revenue', 'Credit', 'Revenue from services'),
            
            # Expenses
            ('5000', 'Cost of Goods Sold', 'Expense', 'Debit', 'Cost of inventory sold'),
            ('5100', 'Salaries Expense', 'Expense', 'Debit', 'Employee salaries'),
            ('5200', 'Rent Expense', 'Expense', 'Debit', 'Office rent'),
            ('5300', 'Utilities Expense', 'Expense', 'Debit', 'Electricity, water, etc.'),
            ('5400', 'Advertising Expense', 'Expense', 'Debit', 'Marketing and advertising')
        ]
        
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        for account in default_accounts:
            cursor.execute('''
            INSERT OR IGNORE INTO chart_of_accounts 
            (account_number, account_name, account_type, normal_balance, description)
            VALUES (?, ?, ?, ?, ?)
            ''', account)
        
        conn.commit()
        conn.close()
    
    def create_journal_entry(self, entry_date, description, reference, entries):
        """
        Create a journal entry with debit and credit entries
        entries: list of tuples (account_number, amount, side, line_description)
        """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        try:
            # Verify accounting equation
            total_debits = sum(entry[1] for entry in entries if entry[2].lower() == 'debit')
            total_credits = sum(entry[1] for entry in entries if entry[2].lower() == 'credit')
            
            if abs(total_debits - total_credits) > 0.01:
                raise ValueError("Debits and credits must be equal")
            
            # Create journal entry
            cursor.execute('''
            INSERT INTO journal_entries (entry_date, description, reference)
            VALUES (?, ?, ?)
            ''', (entry_date, description, reference))
            
            entry_id = cursor.lastrowid
            
            # Add journal entry lines
            for account_number, amount, side, line_desc in entries:
                # Get account_id from account_number
                cursor.execute('SELECT account_id FROM chart_of_accounts WHERE account_number = ?', (account_number,))
                result = cursor.fetchone()
                if not result:
                    raise ValueError(f"Account number {account_number} not found")
                
                account_id = result[0]
                
                cursor.execute('''
                INSERT INTO journal_entry_lines (entry_id, account_id, amount, side, description)
                VALUES (?, ?, ?, ?, ?)
                ''', (entry_id, account_id, amount, side, line_desc))
            
            conn.commit()
            print(f"Journal entry created successfully. Entry ID: {entry_id}")
            
        except Exception as e:
            conn.rollback()
            print(f"Error creating journal entry: {e}")
            raise
        
        finally:
            conn.close()
    
    def get_account_balance(self, account_number, as_of_date=None):
        """Get the balance of a specific account"""
        conn = sqlite3.connect(self.db_name)
        
        query = '''
        SELECT 
            coa.account_number,
            coa.account_name,
            coa.account_type,
            coa.normal_balance,
            SUM(CASE WHEN jel.side = 'Debit' THEN jel.amount ELSE 0 END) as total_debits,
            SUM(CASE WHEN jel.side = 'Credit' THEN jel.amount ELSE 0 END) as total_credits
        FROM chart_of_accounts coa
        LEFT JOIN journal_entry_lines jel ON coa.account_id = jel.account_id
        LEFT JOIN journal_entries je ON jel.entry_id = je.entry_id
        WHERE coa.account_number = ?
        '''
        
        params = [account_number]
        
        if as_of_date:
            query += ' AND je.entry_date <= ?'
            params.append(as_of_date)
        
        query += ' GROUP BY coa.account_id'
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        if not df.empty:
            row = df.iloc[0]
            if row['normal_balance'] == 'Debit':
                balance = row['total_debits'] - row['total_credits']
            else:
                balance = row['total_credits'] - row['total_debits']
            
            return float(balance) if balance else 0.0
        
        return 0.0
    
    def generate_trial_balance(self, as_of_date=None):
        """Generate a trial balance"""
        conn = sqlite3.connect(self.db_name)
        
        query = '''
        SELECT 
            coa.account_number,
            coa.account_name,
            coa.account_type,
            coa.normal_balance,
            SUM(CASE WHEN jel.side = 'Debit' THEN jel.amount ELSE 0 END) as total_debits,
            SUM(CASE WHEN jel.side = 'Credit' THEN jel.amount ELSE 0 END) as total_credits
        FROM chart_of_accounts coa
        LEFT JOIN journal_entry_lines jel ON coa.account_id = jel.account_id
        LEFT JOIN journal_entries je ON jel.entry_id = je.entry_id
        WHERE coa.is_active = TRUE
        '''
        
        params = []
        if as_of_date:
            query += ' AND je.entry_date <= ?'
            params.append(as_of_date)
        
        query += '''
        GROUP BY coa.account_id
        ORDER BY coa.account_number
        '''
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        # Calculate balances
        def calculate_balance(row):
            if row['normal_balance'] == 'Debit':
                return row['total_debits'] - row['total_credits']
            else:
                return row['total_credits'] - row['total_debits']
        
        df['balance'] = df.apply(calculate_balance, axis=1)
        
        return df
    
    def generate_income_statement(self, start_date, end_date):
        """Generate income statement for a period"""
        conn = sqlite3.connect(self.db_name)
        
        # Get revenue and expense accounts
        query = '''
        SELECT 
            coa.account_number,
            coa.account_name,
            coa.account_type,
            SUM(CASE WHEN jel.side = 'Debit' THEN jel.amount ELSE 0 END) as debits,
            SUM(CASE WHEN jel.side = 'Credit' THEN jel.amount ELSE 0 END) as credits
        FROM chart_of_accounts coa
        JOIN journal_entry_lines jel ON coa.account_id = jel.account_id
        JOIN journal_entries je ON jel.entry_id = je.entry_id
        WHERE coa.account_type IN ('Revenue', 'Expense')
        AND je.entry_date BETWEEN ? AND ?
        GROUP BY coa.account_id
        ORDER BY coa.account_type, coa.account_number
        '''
        
        df = pd.read_sql_query(query, conn, params=(start_date, end_date))
        conn.close()
        
        # Calculate net amounts
        revenue_df = df[df['account_type'] == 'Revenue']
        expense_df = df[df['account_type'] == 'Expense']
        
        total_revenue = (revenue_df['credits'] - revenue_df['debits']).sum()
        total_expenses = (expense_df['debits'] - expense_df['credits']).sum()
        net_income = total_revenue - total_expenses
        
        return {
            'revenue': revenue_df,
            'expenses': expense_df,
            'total_revenue': total_revenue,
            'total_expenses': total_expenses,
            'net_income': net_income
        }
    
    def generate_balance_sheet(self, as_of_date):
        """Generate balance sheet as of specific date"""
        trial_balance = self.generate_trial_balance(as_of_date)
        
        assets = trial_balance[trial_balance['account_type'] == 'Asset']
        liabilities = trial_balance[trial_balance['account_type'] == 'Liability']
        equity = trial_balance[trial_balance['account_type'] == 'Equity']
        
        total_assets = assets['balance'].sum()
        total_liabilities = liabilities['balance'].sum()
        total_equity = equity['balance'].sum()
        
        # Get current period net income for equity
        current_year_start = f"{as_of_date[:4]}-01-01"
        income_stmt = self.generate_income_statement(current_year_start, as_of_date)
        retained_earnings = total_equity + income_stmt['net_income']
        
        return {
            'assets': assets,
            'liabilities': liabilities,
            'equity': equity,
            'total_assets': total_assets,
            'total_liabilities': total_liabilities,
            'retained_earnings': retained_earnings,
            'accounting_equation': abs(total_assets - (total_liabilities + retained_earnings)) < 0.01
        }
    
    def generate_cash_flow_statement(self, start_date, end_date):
        """Generate cash flow statement"""
        # This is a simplified version - real implementation would be more complex
        conn = sqlite3.connect(self.db_name)
        
        # Cash from operating activities
        operating_query = '''
        SELECT 
            coa.account_number,
            coa.account_name,
            SUM(CASE WHEN jel.side = 'Debit' THEN jel.amount ELSE 0 END) as cash_in,
            SUM(CASE WHEN jel.side = 'Credit' THEN jel.amount ELSE 0 END) as cash_out
        FROM chart_of_accounts coa
        JOIN journal_entry_lines jel ON coa.account_id = jel.account_id
        JOIN journal_entries je ON jel.entry_id = je.entry_id
        WHERE coa.account_number IN ('1010', '1200', '2000')
        AND je.entry_date BETWEEN ? AND ?
        GROUP BY coa.account_id
        '''
        
        operating_df = pd.read_sql_query(operating_query, conn, params=(start_date, end_date))
        
        net_cash_operating = operating_df['cash_in'].sum() - operating_df['cash_out'].sum()
        
        conn.close()
        
        return {
            'operating_activities': operating_df,
            'net_cash_operating': net_cash_operating,
            'net_cash_investing': 0,  # Simplified
            'net_cash_financing': 0,  # Simplified
            'net_change_cash': net_cash_operating
        }

# Example usage and demonstration
def main():
    # Initialize the accounting system
    accounting_system = FinancialAccountingSystem()
    
    # Example: Record a sales transaction
    try:
        accounting_system.create_journal_entry(
            entry_date='2024-01-15',
            description='Sale of product to customer',
            reference='INV-001',
            entries=[
                ('1200', 1000.00, 'Debit', 'Accounts Receivable - Sale INV-001'),  # Debit AR
                ('4000', 1000.00, 'Credit', 'Sales Revenue - INV-001')             # Credit Revenue
            ]
        )
    except Exception as e:
        print(f"Error: {e}")
    
    # Example: Record an expense
    try:
        accounting_system.create_journal_entry(
            entry_date='2024-01-16',
            description='Office rent payment',
            reference='CHK-001',
            entries=[
                ('5200', 500.00, 'Debit', 'Rent Expense - January'),      # Debit Rent Expense
                ('1010', 500.00, 'Credit', 'Cash payment - CHK-001')      # Credit Cash
            ]
        )
    except Exception as e:
        print(f"Error: {e}")
    
    # Generate financial statements
    print("=== TRIAL BALANCE ===")
    trial_balance = accounting_system.generate_trial_balance()
    print(trial_balance[['account_number', 'account_name', 'balance']])
    
    print("\n=== INCOME STATEMENT (Jan 2024) ===")
    income_stmt = accounting_system.generate_income_statement('2024-01-01', '2024-01-31')
    print(f"Total Revenue: ${income_stmt['total_revenue']:.2f}")
    print(f"Total Expenses: ${income_stmt['total_expenses']:.2f}")
    print(f"Net Income: ${income_stmt['net_income']:.2f}")
    
    print("\n=== BALANCE SHEET (Jan 15, 2024) ===")
    balance_sheet = accounting_system.generate_balance_sheet('2024-01-15')
    print(f"Total Assets: ${balance_sheet['total_assets']:.2f}")
    print(f"Total Liabilities: ${balance_sheet['total_liabilities']:.2f}")
    print(f"Retained Earnings: ${balance_sheet['retained_earnings']:.2f}")
    print(f"Accounting Equation Balanced: {balance_sheet['accounting_equation']}")
    
    print("\n=== CASH FLOW STATEMENT (Jan 2024) ===")
    cash_flow = accounting_system.generate_cash_flow_statement('2024-01-01', '2024-01-31')
    print(f"Net Cash from Operations: ${cash_flow['net_cash_operating']:.2f}")

if __name__ == "__main__":
    main()