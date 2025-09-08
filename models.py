from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, LargeBinary, Date, DECIMAL, ForeignKey, JSON, func, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

# User Management Models
class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)  # Admin, HR, Accounts, Sales, Technical
    description = Column(Text)
    permissions = Column(Text)  # JSON string for permissions
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    google_id = Column(String, unique=True)
    profile_picture = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    role_id = Column(Integer, nullable=True)  # Foreign key to Role
    preferences = Column(Text)  # JSON string for user preferences
    created_at = Column(DateTime, default=datetime.utcnow)

# Notes and Calendar Models
class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    language = Column(String)
    theme = Column(String, default="light")
    attachments = Column(Text)  # JSON string for file attachments
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    google_event_id = Column(String)
    attachments = Column(Text)  # JSON string for file attachments
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# File Management Models
class FileAttachment(Base):
    __tablename__ = "file_attachments"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    filename = Column(String)
    original_filename = Column(String)
    file_type = Column(String)
    file_size = Column(Integer)
    file_path = Column(String)
    google_drive_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class UserSession(Base):
    __tablename__ = "user_sessions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    access_token = Column(Text)
    refresh_token = Column(Text)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

# Leave Management Models
class LeaveApplication(Base):
    __tablename__ = "leave_applications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    leave_type = Column(String)  # annual, sick, emergency, etc.
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    days_requested = Column(Integer)
    reason = Column(Text)
    status = Column(String, default="pending")  # pending, approved, rejected
    approved_by = Column(Integer, nullable=True)
    approval_date = Column(DateTime, nullable=True)
    approval_comments = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Expense Management Models
class ConvenienceBill(Base):
    __tablename__ = "convenience_bills"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    bill_date = Column(DateTime, nullable=False)

    # Detailed expense breakdown in BDT paisa (1 BDT = 100 paisa)
    transport_amount = Column(Integer, default=0)  # Transportation costs
    transport_description = Column(Text)

    food_amount = Column(Integer, default=0)  # Food costs
    food_description = Column(Text)

    other_amount = Column(Integer, default=0)  # Other costs
    other_description = Column(Text)

    # Enhanced transportation details
    transport_to = Column(String(255))
    transport_from = Column(String(255))
    means_of_transportation = Column(String(255))

    # Additional cost breakdown in BDT paisa
    fuel_cost = Column(Integer, default=0)
    rental_cost = Column(Integer, default=0)

    # Client information fields
    client_id = Column(Integer, nullable=True)
    client_company_name = Column(String(255))
    client_contact_number = Column(String(50))
    expense_purpose = Column(Text)
    project_reference = Column(String(255))
    is_billable = Column(Boolean, default=False)

    # General description and metadata
    general_description = Column(Text)
    receipt_file_id = Column(Integer, nullable=True)
    status = Column(String, default="pending")
    approved_by = Column(Integer, nullable=True)
    approval_date = Column(DateTime, nullable=True)
    approval_comments = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def total_amount(self):
        return ((self.transport_amount or 0) + (self.food_amount or 0) +
                (self.other_amount or 0) + (self.fuel_cost or 0) + (self.rental_cost or 0))

# Intelligent Expense Models
class ExpenseCategory(Base):
    __tablename__ = "expense_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    icon = Column(String(50))
    color = Column(String(20))
    is_active = Column(Boolean, default=True)
    requires_receipt = Column(Boolean, default=False)
    receipt_threshold = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class ExpenseApprovalWorkflow(Base):
    __tablename__ = "expense_approval_workflows"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    conditions = Column(Text)  # JSON as Text for compatibility
    approval_levels = Column(Text, nullable=False)  # JSON as Text
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class IntelligentExpense(Base):
    __tablename__ = "intelligent_expenses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    expense_number = Column(String(20), unique=True)
    category_id = Column(Integer)

    # Basic Information
    title = Column(String(200), nullable=False)
    description = Column(Text)
    amount = Column(Integer, nullable=False)
    currency = Column(String(3), default='BDT')
    expense_date = Column(Date, nullable=False)
    vendor_name = Column(String(200))
    vendor_contact = Column(String(50))

    # Location and Travel
    location_from = Column(String(200))
    location_to = Column(String(200))
    transport_mode = Column(String(50))
    travel_distance = Column(Integer)

    # Project and Client
    project_id = Column(String(100))
    client_name = Column(String(200))
    is_billable = Column(Boolean, default=False)

    # Receipts and Attachments
    receipt_uploaded = Column(Boolean, default=False)
    receipt_files = Column(Text)  # JSON as Text
    ocr_extracted_data = Column(Text)  # JSON as Text

    # Approval and Status
    workflow_id = Column(Integer)
    status = Column(String(20), default='draft')
    current_approver_id = Column(Integer)
    submitted_at = Column(DateTime)

    # Automation and Intelligence
    auto_categorized = Column(Boolean, default=False)
    confidence_score = Column(DECIMAL(5,2))
    duplicate_check_passed = Column(Boolean, default=True)
    policy_compliance = Column(Text)  # JSON as Text

    # Financial
    reimbursable = Column(Boolean, default=True)
    advance_deduction = Column(Integer, default=0)
    net_amount = Column(Integer)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer)

class ExpenseApproval(Base):
    __tablename__ = "expense_approvals"

    id = Column(Integer, primary_key=True, index=True)
    expense_id = Column(Integer, nullable=False)
    approver_id = Column(Integer, nullable=False)
    approval_level = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False)
    comments = Column(Text)
    approved_at = Column(DateTime)
    delegated_to = Column(Integer)
    escalated = Column(Boolean, default=False)
    escalated_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

class ExpenseReport(Base):
    __tablename__ = "expense_reports"

    id = Column(Integer, primary_key=True, index=True)
    report_type = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    user_id = Column(Integer)
    department_id = Column(Integer)

    date_from = Column(Date, nullable=False)
    date_to = Column(Date, nullable=False)
    filters = Column(Text)  # JSON as Text

    total_expenses = Column(Integer)
    total_approved = Column(Integer)
    total_pending = Column(Integer)
    total_rejected = Column(Integer)
    expense_count = Column(Integer)

    summary_data = Column(Text)  # JSON as Text
    detailed_data = Column(Text)  # JSON as Text

    is_scheduled = Column(Boolean, default=False)
    schedule_frequency = Column(String(20))
    next_generation = Column(Date)

    status = Column(String(20), default='generated')
    generated_at = Column(DateTime, default=datetime.utcnow)
    generated_by = Column(Integer)
    file_path = Column(String(500))

    created_at = Column(DateTime, default=datetime.utcnow)

# RBAC Models
class UserPermission(Base):
    __tablename__ = "user_permissions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    module = Column(String)
    permission = Column(String)
    granted_by = Column(Integer, index=True)
    granted_at = Column(DateTime, default=datetime.utcnow)

class GroupPermission(Base):
    __tablename__ = "group_permissions"
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, index=True)
    module = Column(String)
    permission = Column(String)
    granted_by = Column(Integer, index=True)
    granted_at = Column(DateTime, default=datetime.utcnow)

class ExpenseModification(Base):
    __tablename__ = "expense_modifications"
    id = Column(Integer, primary_key=True, index=True)
    expense_id = Column(Integer, index=True)
    modified_by = Column(Integer, index=True)
    modification_type = Column(String)
    old_values = Column(Text)  # JSON string
    new_values = Column(Text)  # JSON string
    modification_reason = Column(Text)
    modified_at = Column(DateTime, default=datetime.utcnow)

class GeneratedReport(Base):
    __tablename__ = "generated_reports"
    id = Column(Integer, primary_key=True, index=True)
    report_type = Column(String)
    report_period = Column(String)
    start_date = Column(Date)
    end_date = Column(Date)
    user_id = Column(Integer, nullable=True, index=True)
    group_id = Column(Integer, nullable=True, index=True)
    generated_by = Column(Integer, index=True)
    file_path = Column(String)
    file_format = Column(String)
    share_link = Column(String, nullable=True)
    drive_file_id = Column(String, nullable=True)
    generated_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)

class ReceiptAttachment(Base):
    __tablename__ = "receipt_attachments"
    id = Column(Integer, primary_key=True, index=True)
    expense_id = Column(Integer, index=True)
    file_attachment_id = Column(Integer, index=True)
    receipt_type = Column(String)
    uploaded_by = Column(Integer, index=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

# Client Management Model
class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, nullable=False, index=True)
    contact_person = Column(String)
    contact_number = Column(String)
    email = Column(String)
    address = Column(Text)
    created_by = Column(Integer, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

# Sales Funnel Models
class MEDDPICC(Base):
    __tablename__ = "meddpicc"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    client_name = Column(String)
    opportunity_name = Column(String)
    metrics = Column(Text)
    economic_buyer = Column(Text)
    decision_criteria = Column(Text)
    decision_process = Column(Text)
    paper_process = Column(Text)
    identify_pain = Column(Text)
    champion = Column(Text)
    competition = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class SalesFunnel(Base):
    __tablename__ = "sales_funnel"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    opportunity_name = Column(String)
    client_name = Column(String)
    stage = Column(String)  # Lead, Qualified, Proposal, Negotiation, Closed Won, Closed Lost
    probability = Column(Integer)  # 0-100
    amount = Column(Integer)  # Amount in cents
    closing_date = Column(DateTime)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Group Management Models
class UserGroup(Base):
    __tablename__ = "user_groups"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text)
    created_by = Column(Integer, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class GroupMembership(Base):
    __tablename__ = "group_memberships"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    group_id = Column(Integer, index=True)
    role = Column(String, default="member")  # member, admin
    added_by = Column(Integer, index=True)
    added_at = Column(DateTime, default=datetime.utcnow)