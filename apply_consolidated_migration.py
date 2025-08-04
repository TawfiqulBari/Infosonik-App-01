#!/usr/bin/env python3
"""
Consolidated Database Migration Script for Infosonik App
This script applies all database migrations in the correct order.
"""

import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migration.log'),
        logging.StreamHandler()
    ]
)

def get_db_connection():
    """Get database connection from environment variables"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is required")
    
    conn = psycopg2.connect(database_url)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    return conn

def create_migration_table(conn):
    """Create migration tracking table if it doesn't exist"""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            id SERIAL PRIMARY KEY,
            migration_name VARCHAR(255) UNIQUE NOT NULL,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            checksum VARCHAR(64)
        );
    """)
    logging.info("Migration tracking table created/verified")

def is_migration_applied(conn, migration_name):
    """Check if a migration has already been applied"""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM schema_migrations WHERE migration_name = %s",
        (migration_name,)
    )
    return cursor.fetchone()[0] > 0

def apply_migration(conn, migration_name, sql_content):
    """Apply a single migration"""
    if is_migration_applied(conn, migration_name):
        logging.info(f"Migration {migration_name} already applied, skipping")
        return
    
    cursor = conn.cursor()
    try:
        # Execute the migration SQL
        cursor.execute(sql_content)
        
        # Record the migration as applied
        cursor.execute(
            "INSERT INTO schema_migrations (migration_name) VALUES (%s)",
            (migration_name,)
        )
        
        logging.info(f"Successfully applied migration: {migration_name}")
    except Exception as e:
        logging.error(f"Failed to apply migration {migration_name}: {e}")
        raise

def read_migration_file(filepath):
    """Read migration file content"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def main():
    """Main migration function"""
    try:
        conn = get_db_connection()
        create_migration_table(conn)
        
        # Define migrations in order
        migrations = [
            ('001_initial.sql', 'migrations/001_initial.sql'),
            ('002_add_expense_details.sql', 'migrations/002_add_expense_details.sql'),
            ('003_rbac_and_reporting.sql', 'migrations/003_rbac_and_reporting.sql'),
            ('004_add_client_information.sql', 'migrations/004_add_client_information.sql')
        ]
        
        logging.info("Starting database migration process...")
        
        for migration_name, filepath in migrations:
            if os.path.exists(filepath):
                sql_content = read_migration_file(filepath)
                apply_migration(conn, migration_name, sql_content)
            else:
                logging.warning(f"Migration file not found: {filepath}")
        
        logging.info("All migrations completed successfully!")
        
    except Exception as e:
        logging.error(f"Migration failed: {e}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()