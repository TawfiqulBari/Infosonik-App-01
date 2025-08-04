#!/usr/bin/env python3
"""
Script to apply RBAC and enhanced reporting migrations
"""

import os
import sys
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

def load_env():
    """Load environment variables"""
    load_dotenv()
    return {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'webapp_db'),
        'username': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'password')
    }

def apply_migrations():
    """Apply all migrations for RBAC and reporting features"""
    db_config = load_env()
    
    try:
        # Connect to database
        conn = psycopg2.connect(
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['database'],
            user=db_config['username'],
            password=db_config['password']
        )
        
        cursor = conn.cursor()
        
        # Apply migration 002 (expense details)
        print("Applying migration: 002_add_expense_details.sql")
        with open('migrations/002_add_expense_details.sql', 'r') as f:
            migration_sql = f.read()
        cursor.execute(migration_sql)
        conn.commit()
        print("✓ Expense details migration applied")
        
        # Apply migration 003 (RBAC and reporting)
        print("Applying migration: 003_rbac_and_reporting.sql")
        with open('migrations/003_rbac_and_reporting.sql', 'r') as f:
            migration_sql = f.read()
        cursor.execute(migration_sql)
        conn.commit()
        print("✓ RBAC and reporting migration applied")
        
        # Verify new tables exist
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('user_permissions', 'group_permissions', 'expense_modifications', 'generated_reports', 'receipt_attachments')
            ORDER BY table_name;
        """)
        
        new_tables = cursor.fetchall()
        print(f"✓ New tables created: {[table[0] for table in new_tables]}")
        
        # Verify new columns in convenience_bills
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'convenience_bills' 
            AND column_name IN ('transport_to', 'transport_from', 'means_of_transportation', 'fuel_cost', 'rental_cost', 'approval_required', 'last_modified_by')
            ORDER BY column_name;
        """)
        
        new_columns = cursor.fetchall()
        print(f"✓ New columns added to convenience_bills: {[col[0] for col in new_columns]}")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 All migrations applied successfully!")
        print("\nNext steps:")
        print("1. Restart your application server")
        print("2. Test the new admin features")
        print("3. Verify expense modification functionality")
        print("4. Test report generation and sharing")
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"❌ Migration file not found: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    apply_migrations()
