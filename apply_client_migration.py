#!/usr/bin/env python3
"""
Script to apply client information migration
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

def apply_client_migration():
    """Apply client information migration"""
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
        
        # Apply migration 004 (client information)
        print("Applying migration: 004_add_client_information.sql")
        with open('migrations/004_add_client_information.sql', 'r') as f:
            migration_sql = f.read()
        cursor.execute(migration_sql)
        conn.commit()
        print("✓ Client information migration applied")
        
        # Verify clients table exists
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'clients';
        """)
        
        clients_table = cursor.fetchone()
        if clients_table:
            print("✓ Clients table created successfully")
        else:
            print("❌ Clients table not found")
        
        # Verify new columns in convenience_bills
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'convenience_bills' 
            AND column_name IN ('client_id', 'client_company_name', 'client_contact_number', 'expense_purpose', 'project_reference', 'is_billable')
            ORDER BY column_name;
        """)
        
        new_columns = cursor.fetchall()
        print(f"✓ New client columns added to convenience_bills: {[col[0] for col in new_columns]}")
        
        # Check default clients
        cursor.execute("SELECT COUNT(*) FROM clients;")
        client_count = cursor.fetchone()[0]
        print(f"✓ {client_count} default clients created")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Client information migration applied successfully!")
        print("\nNew Features Available:")
        print("• Client/Company tracking for expenses")
        print("• Expense purpose documentation")
        print("• Billable expense flagging")
        print("• Project reference tracking")
        print("• Client contact information storage")
        
        print("\nNext steps:")
        print("1. Restart your application server")
        print("2. Test expense submission with client information")
        print("3. Add additional clients through the interface")
        
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
    apply_client_migration()
