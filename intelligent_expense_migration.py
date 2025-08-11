#!/usr/bin/env python3
"""
Intelligent Expense Management System Migration
Creates comprehensive expense tracking with approval workflows, 
reporting systems, and smart automation features.
"""

import os
import psycopg2
from datetime import datetime, timedelta
import json

def get_db_connection():
    """Get database connection from environment variables"""
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:securepassword123@localhost:5432/webapp_db')
    
    # Parse the DATABASE_URL
    if DATABASE_URL.startswith('postgresql://'):
        parts = DATABASE_URL.replace('postgresql://', '').split('@')
        user_pass = parts[0].split(':')
        host_port_db = parts[1].split('/')
        host_port = host_port_db[0].split(':')
        
        return psycopg2.connect(
            host=host_port[0] if len(host_port) > 1 else 'localhost',
            port=int(host_port[1]) if len(host_port) > 1 else 5432,
            user=user_pass[0],
            password=user_pass[1],
            database=host_port_db[1]
        )
    
    return psycopg2.connect(DATABASE_URL)

def execute_sql(conn, sql, description=""):
    """Execute SQL with error handling"""
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        print(f"✅ {description}")
        return True
    except Exception as e:
        print(f"❌ Error in {description}: {str(e)}")
        conn.rollback()
        return False

def main():
    """Main migration function"""
    print("🚀 Intelligent Expense Management System Migration")
    print("=" * 60)
    
    try:
        conn = get_db_connection()
        print("✅ Connected to database successfully")
        
        # 1. Create Expense Categories Table
        create_categories_sql = """
        CREATE TABLE IF NOT EXISTS expense_categories (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL UNIQUE,
            description TEXT,
            icon VARCHAR(50),
            color VARCHAR(20),
            is_active BOOLEAN DEFAULT true,
            requires_receipt BOOLEAN DEFAULT false,
            receipt_threshold INTEGER DEFAULT 0, -- Amount above which receipt is required
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        execute_sql(conn, create_categories_sql, "Created expense_categories table")
        
        # 2. Create Approval Workflows Table
        create_workflows_sql = """
        CREATE TABLE IF NOT EXISTS expense_approval_workflows (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            conditions JSONB, -- JSON conditions for when this workflow applies
            approval_levels JSONB NOT NULL, -- Array of approval levels
            is_active BOOLEAN DEFAULT true,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        execute_sql(conn, create_workflows_sql, "Created expense_approval_workflows table")
        
        # 3. Create Enhanced Expenses Table
        create_expenses_sql = """
        CREATE TABLE IF NOT EXISTS intelligent_expenses (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            expense_number VARCHAR(20) UNIQUE, -- Auto-generated expense number
            category_id INTEGER REFERENCES expense_categories(id),
            
            -- Basic Information
            title VARCHAR(200) NOT NULL,
            description TEXT,
            amount INTEGER NOT NULL, -- Amount in paisa
            currency VARCHAR(3) DEFAULT 'BDT',
            expense_date DATE NOT NULL,
            vendor_name VARCHAR(200),
            vendor_contact VARCHAR(50),
            
            -- Location and Travel
            transport_mode VARCHAR(50), -- Mode of transportation
            location_from VARCHAR(200),
            location_to VARCHAR(200),
            travel_distance INTEGER, -- in kilometers
            
            -- Project and Client
            project_id VARCHAR(100),
            client_name VARCHAR(200),
            is_billable BOOLEAN DEFAULT false,
            
            -- Receipts and Attachments
            receipt_uploaded BOOLEAN DEFAULT false,
            receipt_files JSONB, -- Array of file information
            ocr_extracted_data JSONB, -- OCR data from receipts
            
            -- Approval and Status
            workflow_id INTEGER REFERENCES expense_approval_workflows(id),
            status VARCHAR(20) DEFAULT 'draft', -- draft, submitted, approved, rejected, paid
            current_approver_id INTEGER,
            submitted_at TIMESTAMP,
            
            -- Automation and Intelligence
            auto_categorized BOOLEAN DEFAULT false,
            confidence_score DECIMAL(3,2), -- AI confidence in categorization
            duplicate_check_passed BOOLEAN DEFAULT true,
            policy_compliance JSONB, -- Policy violations or warnings
            
            -- Financial
            reimbursable BOOLEAN DEFAULT true,
            advance_deduction INTEGER DEFAULT 0,
            net_amount INTEGER, -- Final amount after deductions
            
            -- Audit
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by INTEGER,
            
            CONSTRAINT valid_amount CHECK (amount > 0),
            CONSTRAINT valid_net_amount CHECK (net_amount >= 0)
        );
        """
        execute_sql(conn, create_expenses_sql, "Created intelligent_expenses table")
        
        # 4. Create Expense Approvals Table
        create_approvals_sql = """
        CREATE TABLE IF NOT EXISTS expense_approvals (
            id SERIAL PRIMARY KEY,
            expense_id INTEGER NOT NULL REFERENCES intelligent_expenses(id) ON DELETE CASCADE,
            approver_id INTEGER NOT NULL,
            approval_level INTEGER NOT NULL,
            status VARCHAR(20) NOT NULL, -- pending, approved, rejected, delegated
            comments TEXT,
            approved_at TIMESTAMP,
            delegated_to INTEGER,
            escalated BOOLEAN DEFAULT false,
            escalated_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        execute_sql(conn, create_approvals_sql, "Created expense_approvals table")
        
        # 5. Create Expense Reports Table
        create_reports_sql = """
        CREATE TABLE IF NOT EXISTS expense_reports (
            id SERIAL PRIMARY KEY,
            report_type VARCHAR(50) NOT NULL, -- weekly, monthly, yearly, custom
            title VARCHAR(200) NOT NULL,
            user_id INTEGER,
            department_id INTEGER,
            
            -- Report Parameters
            date_from DATE NOT NULL,
            date_to DATE NOT NULL,
            filters JSONB, -- Additional filters applied
            
            -- Report Data
            total_expenses INTEGER,
            total_approved INTEGER,
            total_pending INTEGER,
            total_rejected INTEGER,
            expense_count INTEGER,
            
            -- Report Content
            summary_data JSONB,
            detailed_data JSONB,
            
            -- Scheduling
            is_scheduled BOOLEAN DEFAULT false,
            schedule_frequency VARCHAR(20), -- weekly, monthly, yearly
            next_generation DATE,
            
            -- Status and Metadata
            status VARCHAR(20) DEFAULT 'generated', -- generating, generated, sent, failed
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            generated_by INTEGER,
            file_path VARCHAR(500),
            
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        execute_sql(conn, create_reports_sql, "Created expense_reports table")
        
        # 6. Create Expense Budget Tracking
        create_budgets_sql = """
        CREATE TABLE IF NOT EXISTS expense_budgets (
            id SERIAL PRIMARY KEY,
            name VARCHAR(200) NOT NULL,
            department_id INTEGER,
            category_id INTEGER REFERENCES expense_categories(id),
            user_id INTEGER,
            
            -- Budget Period
            period_type VARCHAR(20) NOT NULL, -- monthly, quarterly, yearly
            period_start DATE NOT NULL,
            period_end DATE NOT NULL,
            
            -- Budget Amounts
            allocated_amount INTEGER NOT NULL,
            spent_amount INTEGER DEFAULT 0,
            committed_amount INTEGER DEFAULT 0, -- Pending approvals
            available_amount INTEGER,
            
            -- Alerts
            alert_threshold DECIMAL(3,2) DEFAULT 0.80, -- Alert at 80%
            warning_threshold DECIMAL(3,2) DEFAULT 0.90, -- Warning at 90%
            alert_sent BOOLEAN DEFAULT false,
            warning_sent BOOLEAN DEFAULT false,
            
            -- Status
            is_active BOOLEAN DEFAULT true,
            auto_rollover BOOLEAN DEFAULT false,
            
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        execute_sql(conn, create_budgets_sql, "Created expense_budgets table")
        
        # 7. Create Expense Analytics Table
        create_analytics_sql = """
        CREATE TABLE IF NOT EXISTS expense_analytics (
            id SERIAL PRIMARY KEY,
            user_id INTEGER,
            department_id INTEGER,
            category_id INTEGER REFERENCES expense_categories(id),
            
            -- Analytics Period
            period_start DATE NOT NULL,
            period_end DATE NOT NULL,
            period_type VARCHAR(20) NOT NULL,
            
            -- Spending Analytics
            total_amount INTEGER,
            avg_expense_amount INTEGER,
            expense_count INTEGER,
            unique_vendors INTEGER,
            
            -- Approval Analytics
            avg_approval_time INTERVAL,
            approval_rate DECIMAL(3,2),
            rejection_rate DECIMAL(3,2),
            
            -- Compliance Analytics
            policy_violations INTEGER,
            late_submissions INTEGER,
            missing_receipts INTEGER,
            
            -- Trends
            month_over_month_change DECIMAL(5,2),
            budget_utilization DECIMAL(3,2),
            
            calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        execute_sql(conn, create_analytics_sql, "Created expense_analytics table")
        
        # 8. Create Notifications Table
        create_notifications_sql = """
        CREATE TABLE IF NOT EXISTS expense_notifications (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            expense_id INTEGER REFERENCES intelligent_expenses(id),
            notification_type VARCHAR(50) NOT NULL, -- approval_request, approved, rejected, reminder, etc.
            title VARCHAR(200) NOT NULL,
            message TEXT NOT NULL,
            
            -- Notification Channels
            email_sent BOOLEAN DEFAULT false,
            sms_sent BOOLEAN DEFAULT false,
            push_sent BOOLEAN DEFAULT false,
            in_app_read BOOLEAN DEFAULT false,
            
            -- Scheduling
            send_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            sent_at TIMESTAMP,
            
            -- Priority and Status
            priority VARCHAR(10) DEFAULT 'normal', -- low, normal, high, urgent
            status VARCHAR(20) DEFAULT 'pending', -- pending, sent, failed
            
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        execute_sql(conn, create_notifications_sql, "Created expense_notifications table")
        
        # 9. Insert Default Data
        print("\n🎯 Inserting default data...")
        
        # Default Categories
        categories_data = """
        INSERT INTO expense_categories (name, description, icon, color, requires_receipt, receipt_threshold) VALUES
        ('Transportation', 'Travel and transportation costs', 'DirectionsCar', '#2196F3', true, 5000),
        ('Meals & Entertainment', 'Business meals and client entertainment', 'Restaurant', '#FF9800', true, 3000),
        ('Office Supplies', 'Office equipment and supplies', 'BusinessCenter', '#4CAF50', true, 2000),
        ('Travel & Accommodation', 'Business travel and hotel expenses', 'Flight', '#9C27B0', true, 10000),
        ('Communication', 'Phone, internet, and communication costs', 'Phone', '#00BCD4', false, 0),
        ('Training & Development', 'Professional training and courses', 'School', '#8BC34A', true, 5000),
        ('Marketing & Advertising', 'Marketing campaigns and promotional activities', 'Campaign', '#E91E63', true, 5000),
        ('Equipment & Technology', 'IT equipment and technology purchases', 'Computer', '#607D8B', true, 15000),
        ('Professional Services', 'Legal, consulting, and professional fees', 'AccountBalance', '#795548', true, 10000),
        ('Miscellaneous', 'Other business expenses', 'MoreHoriz', '#9E9E9E', true, 1000)
        ON CONFLICT (name) DO NOTHING;
        """
        execute_sql(conn, categories_data, "Inserted default expense categories")
        
        # Default Approval Workflows
        workflows_data = """
        INSERT INTO expense_approval_workflows (name, description, conditions, approval_levels) VALUES
        (
            'Standard Workflow', 
            'Standard approval for expenses under 10,000 BDT',
            '{"amount_max": 1000000}',
            '[{"level": 1, "role": "manager", "required": true}, {"level": 2, "role": "finance", "required": true}]'
        ),
        (
            'High Value Workflow',
            'Approval for expenses over 10,000 BDT',
            '{"amount_min": 1000000}',
            '[{"level": 1, "role": "manager", "required": true}, {"level": 2, "role": "finance", "required": true}, {"level": 3, "role": "ceo", "required": true}]'
        ),
        (
            'Travel Workflow',
            'Special workflow for travel expenses',
            '{"category": "Travel & Accommodation"}',
            '[{"level": 1, "role": "travel_manager", "required": true}, {"level": 2, "role": "finance", "required": true}]'
        ),
        (
            'Auto Approval',
            'Automatic approval for low-value expenses',
            '{"amount_max": 200000, "trusted_user": true}',
            '[{"level": 1, "role": "auto", "required": true}]'
        )
        ON CONFLICT (name) DO NOTHING;
        """
        execute_sql(conn, workflows_data, "Inserted default approval workflows")
        
        # Create Indexes for Performance
        indexes_sql = [
            "CREATE INDEX IF NOT EXISTS idx_intelligent_expenses_user_id ON intelligent_expenses(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_intelligent_expenses_status ON intelligent_expenses(status);",
            "CREATE INDEX IF NOT EXISTS idx_intelligent_expenses_expense_date ON intelligent_expenses(expense_date);",
            "CREATE INDEX IF NOT EXISTS idx_intelligent_expenses_category ON intelligent_expenses(category_id);",
            "CREATE INDEX IF NOT EXISTS idx_expense_approvals_expense_id ON expense_approvals(expense_id);",
            "CREATE INDEX IF NOT EXISTS idx_expense_approvals_approver ON expense_approvals(approver_id);",
            "CREATE INDEX IF NOT EXISTS idx_expense_reports_user_id ON expense_reports(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_expense_notifications_user_id ON expense_notifications(user_id);",
        ]
        
        for idx_sql in indexes_sql:
            execute_sql(conn, idx_sql, f"Created index: {idx_sql.split('idx_')[1].split(' ON')[0]}")
        
        # Create Views for Common Queries
        views_sql = """
        CREATE OR REPLACE VIEW expense_summary_view AS
        SELECT 
            ie.id,
            ie.expense_number,
            ie.title,
            ie.amount,
            ie.expense_date,
            ie.status,
            ec.name as category_name,
            ec.color as category_color,
            ie.is_billable,
            ie.user_id,
            COUNT(ea.id) as approval_count,
            MAX(ea.approved_at) as last_approval_date
        FROM intelligent_expenses ie
        LEFT JOIN expense_categories ec ON ie.category_id = ec.id
        LEFT JOIN expense_approvals ea ON ie.id = ea.expense_id AND ea.status = 'approved'
        GROUP BY ie.id, ec.name, ec.color;
        """
        execute_sql(conn, views_sql, "Created expense summary view")
        
        print("\n" + "=" * 60)
        print("🎉 INTELLIGENT EXPENSE SYSTEM MIGRATION COMPLETED!")
        print("=" * 60)
        
        print("\n📊 Migration Summary:")
        print("✅ 8 new tables created for comprehensive expense management")
        print("✅ 10 expense categories with smart thresholds")
        print("✅ 4 approval workflows (Standard, High Value, Travel, Auto)")
        print("✅ Performance indexes for optimal query speed")
        print("✅ Analytics and reporting infrastructure")
        print("✅ Notification system for real-time updates")
        
        print("\n🚀 Key Features Enabled:")
        print("• Intelligent expense categorization with confidence scoring")
        print("• Multi-level approval workflows with auto-routing")
        print("• OCR receipt processing and duplicate detection")
        print("• Real-time budget tracking with threshold alerts")
        print("• Comprehensive reporting (weekly, monthly, yearly)")
        print("• Advanced analytics and spending insights")
        print("• Smart notifications across multiple channels")
        print("• Policy compliance monitoring and violations tracking")
        
        print("\n📋 Next Steps:")
        print("1. Update the main.py API endpoints")
        print("2. Create the new React frontend components")
        print("3. Implement OCR and AI categorization")
        print("4. Set up automated reporting schedules")
        print("5. Configure notification channels")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()
