#!/usr/bin/env python3
"""
Script to apply database migrations for enhanced expense tracking
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

def apply_migration():
    """Apply the migration to add enhanced expense fields"""
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
        
        # Read and execute migration
        with open('migrations/002_add_expense_details.sql', 'r') as f:
            migration_sql = f.read()
        
        print("Applying migration: 002_add_expense_details.sql")
        cursor.execute(migration_sql)
        conn.commit()
        
        print("Migration applied successfully!")
        
        # Verify the new columns exist
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'convenience_bills' 
            AND column_name IN ('transport_to', 'transport_from', 'means_of_transportation', 'fuel_cost', 'rental_cost')
            ORDER BY column_name;
        """)
        
        new_columns = cursor.fetchall()
        print(f"New columns added: {[col[0] for col in new_columns]}")
        
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("Migration file not found: migrations/002_add_expense_details.sql")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    apply_migration()
