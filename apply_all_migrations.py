#!/usr/bin/env python3
"""
Script to apply all migrations in sequence
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

def apply_all_migrations():
    """Apply all migrations in sequence"""
    db_config = load_env()
    
    migrations = [
        ('002_add_expense_details.sql', 'Enhanced expense fields'),
        ('003_rbac_and_reporting.sql', 'RBAC and reporting features'),
        ('004_add_client_information.sql', 'Client information tracking')
    ]
    
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
        
        print("🚀 Starting migration process...")
        print("=" * 50)
        
        for migration_file, description in migrations:
            print(f"\n📝 Applying: {migration_file}")
            print(f"   Description: {description}")
            
            try:
                with open(f'migrations/{migration_file}', 'r') as f:
                    migration_sql = f.read()
                cursor.execute(migration_sql)
                conn.commit()
                print(f"   ✅ SUCCESS: {migration_file} applied")
            except FileNotFoundError:
                print(f"   ⚠️  WARNING: {migration_file} not found, skipping...")
                continue
            except psycopg2.Error as e:
                print(f"   ❌ ERROR: Failed to apply {migration_file}")
                print(f"   Error details: {e}")
                continue
        
        print("\n" + "=" * 50)
        print("🔍 Verifying database structure...")
        
        # Verify key tables exist
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('clients', 'user_permissions', 'group_permissions', 'expense_modifications', 'generated_reports')
            ORDER BY table_name;
        """)
        
        new_tables = cursor.fetchall()
        if new_tables:
            print(f"✅ New tables created: {[table[0] for table in new_tables]}")
        
        # Verify enhanced convenience_bills columns
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'convenience_bills' 
            AND column_name IN ('transport_to', 'fuel_cost', 'client_id', 'expense_purpose', 'is_billable')
            ORDER BY column_name;
        """)
        
        enhanced_columns = cursor.fetchall()
        if enhanced_columns:
            print(f"✅ Enhanced expense columns: {[col[0] for col in enhanced_columns]}")
        
        # Check default data
        cursor.execute("SELECT COUNT(*) FROM clients WHERE is_active = TRUE;")
        client_count = cursor.fetchone()[0]
        print(f"✅ Active clients in database: {client_count}")
        
        cursor.close()
        conn.close()
        
        print("\n" + "🎉" * 20)
        print("ALL MIGRATIONS COMPLETED SUCCESSFULLY!")
        print("🎉" * 20)
        
        print("\n📋 SUMMARY OF NEW FEATURES:")
        print("=" * 50)
        print("✅ Enhanced Expense Tracking:")
        print("   • Transportation details (To/From, means)")
        print("   • Fuel and rental cost breakdown")
        print("   • Receipt image uploads")
        print("   • Expense modification capabilities")
        
        print("\n✅ Client Management:")
        print("   • Client/Company information tracking")
        print("   • Contact number storage")
        print("   • Expense purpose documentation")
        print("   • Billable expense flagging")
        print("   • Project reference codes")
        
        print("\n✅ Role-Based Access Control:")
        print("   • User permission management")
        print("   • Group-based permissions")
        print("   • Module access control")
        print("   • Admin approval workflows")
        
        print("\n✅ Advanced Reporting:")
        print("   • Multi-format report generation")
        print("   • Sharing via email, WhatsApp, Drive")
        print("   • User monthly reports")
        print("   • Admin expense dashboards")
        
        print("\n🚀 NEXT STEPS:")
        print("=" * 50)
        print("1. Restart your application server")
        print("2. Login as admin to test new features")
        print("3. Create user groups and permissions")
        print("4. Add clients through the interface")
        print("5. Test expense submission with client info")
        print("6. Generate and share reports")
        
        print("\n💡 TIP: Check the application logs for any startup issues")
        
    except psycopg2.Error as e:
        print(f"❌ Database connection error: {e}")
        print("Please check your database configuration in .env file")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🔧 Database Migration Tool - Enhanced Expense Management")
    print("This will apply all pending migrations to your database.")
    
    confirmation = input("\nDo you want to proceed? (y/N): ")
    if confirmation.lower() in ['y', 'yes']:
        apply_all_migrations()
    else:
        print("Migration cancelled.")
        sys.exit(0)
