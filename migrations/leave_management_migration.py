#!/usr/bin/env python3
"""
Bangladesh Leave Management System - Database Migration
Add comprehensive leave management tables according to Bangladesh Labour Act
"""

import os
import sys
from datetime import datetime, date
from sqlalchemy import create_engine, text, Column, Integer, String, DateTime, Date, Boolean, Float, Text, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import enum

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/infosonik")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Enums for Leave Management
class LeaveTypeEnum(enum.Enum):
    CASUAL = "casual"
    SICK = "sick"
    EARNED = "earned"
    PRIVILEGE = "privilege"
    MATERNITY = "maternity"
    PATERNITY = "paternity"
    RELIGIOUS = "religious"
    OPTIONAL = "optional"
    COMPENSATORY = "compensatory"
    BEREAVEMENT = "bereavement"
    STUDY = "study"
    UNPAID = "unpaid"
    HALF_DAY = "half_day"
    EMERGENCY = "emergency"

class LeaveStatusEnum(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    WITHDRAWN = "withdrawn"

def run_migration():
    """Execute the migration"""
    print("🚀 Starting Bangladesh Leave Management System Migration...")
    
    db = SessionLocal()
    
    try:
        # Create ENUM types first (PostgreSQL specific)
        print("📝 Creating ENUM types...")
        
        # Create leave_type_enum if it doesn't exist
        db.execute(text("""
            DO $$ BEGIN
                CREATE TYPE leave_type_enum AS ENUM (
                    'casual', 'sick', 'earned', 'privilege', 'maternity', 
                    'paternity', 'religious', 'optional', 'compensatory', 
                    'bereavement', 'study', 'unpaid', 'half_day', 'emergency'
                );
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """))
        
        # Create leave_status_enum if it doesn't exist
        db.execute(text("""
            DO $$ BEGIN
                CREATE TYPE leave_status_enum AS ENUM (
                    'pending', 'approved', 'rejected', 'cancelled', 'withdrawn'
                );
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """))
        
        # Create leave_balances table
        print("📊 Creating leave_balances table...")
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS leave_balances (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id),
                leave_type leave_type_enum NOT NULL,
                year INTEGER NOT NULL,
                total_entitled FLOAT DEFAULT 0,
                used_days FLOAT DEFAULT 0,
                pending FLOAT DEFAULT 0,
                carried_forward FLOAT DEFAULT 0,
                encashed FLOAT DEFAULT 0,
                available FLOAT DEFAULT 0,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW(),
                UNIQUE(user_id, leave_type, year)
            );
        """))
        
        # Create indexes for leave_balances
        db.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_leave_balances_user_year 
            ON leave_balances(user_id, year);
        """))
        
        # Create leave_policies table
        print("📋 Creating leave_policies table...")
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS leave_policies (
                id SERIAL PRIMARY KEY,
                leave_type leave_type_enum NOT NULL UNIQUE,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                days_per_year FLOAT,
                accrual_method VARCHAR(50) DEFAULT 'yearly',
                max_consecutive_days INTEGER,
                min_notice_days INTEGER DEFAULT 0,
                max_carry_forward FLOAT DEFAULT 0,
                applicable_gender VARCHAR(10) DEFAULT 'all',
                requires_medical_certificate BOOLEAN DEFAULT FALSE,
                medical_cert_after_days INTEGER DEFAULT 3,
                requires_approval BOOLEAN DEFAULT TRUE,
                is_mandatory BOOLEAN DEFAULT TRUE,
                labour_act_section VARCHAR(20),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
        """))
        
        # Update existing leave_applications table with new columns
        print("🔄 Updating leave_applications table...")
        
        # Add new columns to leave_applications
        migrations = [
            "ALTER TABLE leave_applications ADD COLUMN IF NOT EXISTS leave_type_new leave_type_enum",
            "ALTER TABLE leave_applications ADD COLUMN IF NOT EXISTS start_date_new DATE",
            "ALTER TABLE leave_applications ADD COLUMN IF NOT EXISTS end_date_new DATE", 
            "ALTER TABLE leave_applications ADD COLUMN IF NOT EXISTS days_requested_new FLOAT",
            "ALTER TABLE leave_applications ADD COLUMN IF NOT EXISTS is_half_day BOOLEAN DEFAULT FALSE",
            "ALTER TABLE leave_applications ADD COLUMN IF NOT EXISTS half_day_period VARCHAR(20)",
            "ALTER TABLE leave_applications ADD COLUMN IF NOT EXISTS emergency_contact VARCHAR(15)",
            "ALTER TABLE leave_applications ADD COLUMN IF NOT EXISTS handover_notes TEXT",
            "ALTER TABLE leave_applications ADD COLUMN IF NOT EXISTS status_new leave_status_enum DEFAULT 'pending'",
            "ALTER TABLE leave_applications ADD COLUMN IF NOT EXISTS primary_approver_id INTEGER REFERENCES users(id)",
            "ALTER TABLE leave_applications ADD COLUMN IF NOT EXISTS secondary_approver_id INTEGER REFERENCES users(id)",
            "ALTER TABLE leave_applications ADD COLUMN IF NOT EXISTS hr_approver_id INTEGER REFERENCES users(id)",
            "ALTER TABLE leave_applications ADD COLUMN IF NOT EXISTS primary_approved_at TIMESTAMP",
            "ALTER TABLE leave_applications ADD COLUMN IF NOT EXISTS secondary_approved_at TIMESTAMP", 
            "ALTER TABLE leave_applications ADD COLUMN IF NOT EXISTS hr_approved_at TIMESTAMP",
            "ALTER TABLE leave_applications ADD COLUMN IF NOT EXISTS final_approved_by INTEGER REFERENCES users(id)",
            "ALTER TABLE leave_applications ADD COLUMN IF NOT EXISTS rejection_reason TEXT",
            "ALTER TABLE leave_applications ADD COLUMN IF NOT EXISTS medical_certificate_url VARCHAR(500)",
            "ALTER TABLE leave_applications ADD COLUMN IF NOT EXISTS supporting_documents TEXT",
            "ALTER TABLE leave_applications ADD COLUMN IF NOT EXISTS applied_date TIMESTAMP DEFAULT NOW()"
        ]
        
        for migration in migrations:
            try:
                db.execute(text(migration))
            except Exception as e:
                print(f"Warning: {migration} failed: {e}")
        
        # Create leave_approval_workflows table
        print("🔄 Creating leave_approval_workflows table...")
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS leave_approval_workflows (
                id SERIAL PRIMARY KEY,
                leave_type leave_type_enum,
                department VARCHAR(100),
                employee_level VARCHAR(50),
                requires_manager_approval BOOLEAN DEFAULT TRUE,
                requires_hr_approval BOOLEAN DEFAULT FALSE,
                requires_ceo_approval BOOLEAN DEFAULT FALSE,
                days_threshold_hr INTEGER DEFAULT 5,
                days_threshold_ceo INTEGER DEFAULT 15,
                auto_approve_limit INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """))
        
        # Create leave_calendar table
        print("📅 Creating leave_calendar table...")
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS leave_calendar (
                id SERIAL PRIMARY KEY,
                application_id INTEGER REFERENCES leave_applications(id),
                user_id INTEGER REFERENCES users(id),
                department VARCHAR(100),
                leave_date DATE NOT NULL,
                leave_type leave_type_enum NOT NULL,
                is_half_day BOOLEAN DEFAULT FALSE,
                team_strength_on_date INTEGER DEFAULT 1,
                leaves_on_date INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """))
        
        # Create indexes for leave_calendar
        db.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_leave_calendar_date 
            ON leave_calendar(leave_date);
            CREATE INDEX IF NOT EXISTS idx_leave_calendar_user_date 
            ON leave_calendar(user_id, leave_date);
        """))
        
        # Create leave_encashments table
        print("💰 Creating leave_encashments table...")
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS leave_encashments (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                year INTEGER NOT NULL,
                leave_type leave_type_enum,
                days_encashed FLOAT NOT NULL,
                daily_rate FLOAT NOT NULL,
                total_amount FLOAT NOT NULL,
                processed_by INTEGER REFERENCES users(id),
                processed_at TIMESTAMP,
                payroll_reference VARCHAR(100),
                created_at TIMESTAMP DEFAULT NOW()
            );
        """))
        
        # Create leave_audit_logs table
        print("📝 Creating leave_audit_logs table...")
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS leave_audit_logs (
                id SERIAL PRIMARY KEY,
                application_id INTEGER REFERENCES leave_applications(id),
                user_id INTEGER REFERENCES users(id),
                action_by INTEGER REFERENCES users(id),
                action VARCHAR(50) NOT NULL,
                old_values TEXT,
                new_values TEXT,
                comments TEXT,
                ip_address VARCHAR(45),
                user_agent VARCHAR(500),
                created_at TIMESTAMP DEFAULT NOW()
            );
        """))
        
        # Insert default leave policies (Bangladesh Labour Act compliant)
        print("📜 Inserting default leave policies...")
        
        policies = [
            {
                'type': 'casual',
                'name': 'Casual Leave',
                'description': 'Short-term personal needs and urgent matters',
                'days': 10,
                'section': 'Section 103',
                'medical': False,
                'mandatory': True
            },
            {
                'type': 'sick',
                'name': 'Sick Leave', 
                'description': 'Medical illness requiring rest',
                'days': 14,
                'section': 'Section 104',
                'medical': True,
                'mandatory': True
            },
            {
                'type': 'earned',
                'name': 'Earned Leave',
                'description': 'Privilege leave earned through service',
                'days': 22,
                'section': 'Section 106', 
                'medical': False,
                'mandatory': True
            },
            {
                'type': 'maternity',
                'name': 'Maternity Leave',
                'description': '16 weeks maternity benefit',
                'days': 112,
                'section': 'Section 107',
                'medical': True,
                'mandatory': True,
                'gender': 'female'
            },
            {
                'type': 'paternity',
                'name': 'Paternity Leave',
                'description': 'Leave for new fathers',
                'days': 5,
                'section': 'Company Policy',
                'medical': False,
                'mandatory': False,
                'gender': 'male'
            },
            {
                'type': 'religious',
                'name': 'Religious Holiday',
                'description': 'Government declared religious holidays',
                'days': 15,
                'section': 'Govt. Declaration',
                'medical': False,
                'mandatory': True
            },
            {
                'type': 'bereavement',
                'name': 'Bereavement Leave',
                'description': 'Death of immediate family member',
                'days': 5,
                'section': 'Company Policy',
                'medical': False,
                'mandatory': False
            },
            {
                'type': 'study',
                'name': 'Study Leave', 
                'description': 'For higher education and professional development',
                'days': 30,
                'section': 'Company Policy',
                'medical': False,
                'mandatory': False
            },
            {
                'type': 'compensatory',
                'name': 'Compensatory Leave',
                'description': 'For overtime and extra work',
                'days': 15,
                'section': 'Company Policy', 
                'medical': False,
                'mandatory': False
            },
            {
                'type': 'unpaid',
                'name': 'Unpaid Leave',
                'description': 'Extended leave without pay',
                'days': 0,
                'section': 'With Approval',
                'medical': False,
                'mandatory': False
            }
        ]
        
        for policy in policies:
            db.execute(text(f"""
                INSERT INTO leave_policies (
                    leave_type, name, description, days_per_year, 
                    labour_act_section, requires_medical_certificate, 
                    is_mandatory, applicable_gender, max_consecutive_days,
                    min_notice_days, max_carry_forward
                )
                VALUES (
                    '{policy["type"]}', '{policy["name"]}', '{policy["description"]}', 
                    {policy["days"]}, '{policy["section"]}', {policy["medical"]}, 
                    {policy["mandatory"]}, '{policy.get("gender", "all")}', 
                    {policy.get("max_days", 30)}, {policy.get("notice", 1)}, 
                    {policy.get("carry_forward", 60 if policy["type"] == "earned" else 0)}
                )
                ON CONFLICT (leave_type) DO NOTHING;
            """))
        
        # Insert default workflow configurations
        print("⚙️ Creating default approval workflows...")
        
        workflows = [
            ('casual', None, None, True, False, False, 3, 10, 2),
            ('sick', None, None, True, False, False, 5, 15, 3),
            ('earned', None, None, True, True, False, 7, 20, 0),
            ('maternity', None, None, True, True, True, 30, 0, 0),
            ('paternity', None, None, True, True, False, 7, 0, 0),
            ('study', None, None, True, True, True, 15, 0, 0)
        ]
        
        for workflow in workflows:
            db.execute(text(f"""
                INSERT INTO leave_approval_workflows (
                    leave_type, department, employee_level, requires_manager_approval,
                    requires_hr_approval, requires_ceo_approval, days_threshold_hr,
                    days_threshold_ceo, auto_approve_limit
                )
                VALUES (
                    '{workflow[0]}', {workflow[1] or 'NULL'}, {workflow[2] or 'NULL'}, 
                    {workflow[3]}, {workflow[4]}, {workflow[5]}, {workflow[6]}, 
                    {workflow[7]}, {workflow[8]}
                );
            """))
        
        # Update existing data to use new enums (if there's existing data)
        print("🔄 Migrating existing leave data...")
        
        # Map old leave_type strings to new enum values
        type_mapping = {
            'annual': 'earned',
            'sick': 'sick', 
            'emergency': 'casual',
            'casual': 'casual',
            'earned': 'earned',
            'maternity': 'maternity',
            'paternity': 'paternity'
        }
        
        for old_type, new_type in type_mapping.items():
            db.execute(text(f"""
                UPDATE leave_applications 
                SET leave_type_new = '{new_type}',
                    start_date_new = start_date::date,
                    end_date_new = end_date::date,
                    days_requested_new = days_requested::float,
                    status_new = CASE 
                        WHEN status = 'approved' THEN 'approved'::leave_status_enum
                        WHEN status = 'rejected' THEN 'rejected'::leave_status_enum
                        ELSE 'pending'::leave_status_enum
                    END,
                    applied_date = COALESCE(created_at, NOW())
                WHERE leave_type = '{old_type}' AND leave_type_new IS NULL;
            """))
        
        # Update any remaining records with default values
        db.execute(text("""
            UPDATE leave_applications 
            SET leave_type_new = 'casual'::leave_type_enum,
                start_date_new = COALESCE(start_date::date, CURRENT_DATE),
                end_date_new = COALESCE(end_date::date, CURRENT_DATE),
                days_requested_new = COALESCE(days_requested::float, 1.0),
                status_new = COALESCE(
                    CASE status 
                        WHEN 'approved' THEN 'approved'::leave_status_enum
                        WHEN 'rejected' THEN 'rejected'::leave_status_enum
                        ELSE 'pending'::leave_status_enum
                    END, 
                    'pending'::leave_status_enum
                ),
                applied_date = COALESCE(applied_date, created_at, NOW())
            WHERE leave_type_new IS NULL;
        """))
        
        db.commit()
        
        print("✅ Migration completed successfully!")
        print("\n📋 Summary of changes:")
        print("  • Created leave_balances table")
        print("  • Created leave_policies table with Bangladesh Labour Act compliance")
        print("  • Enhanced leave_applications table with new fields")
        print("  • Created leave_approval_workflows table")
        print("  • Created leave_calendar table for team planning")
        print("  • Created leave_encashments table")
        print("  • Created leave_audit_logs table for compliance")
        print("  • Added 10 default leave policies")
        print("  • Added default approval workflows")
        print("  • Migrated existing leave data")
        
        print("\n🇧🇩 Bangladesh Labour Act compliance features:")
        print("  • Casual Leave: 10 days/year (Section 103)")
        print("  • Sick Leave: 14 days/year (Section 104)")
        print("  • Earned Leave: 22 days/year (Section 106)")
        print("  • Maternity Leave: 16 weeks (Section 107)")
        print("  • Carry forward up to 60 days for Earned Leave")
        print("  • Medical certificate requirements")
        print("  • Multi-level approval workflows")
        print("  • Complete audit trail")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        db.rollback()
        sys.exit(1)
        
    finally:
        db.close()

if __name__ == "__main__":
    run_migration()
