# Bangladesh Leave Management System - Database Models
# Add these models to main.py

from datetime import datetime, date
from sqlalchemy import Column, Integer, String, DateTime, Date, Boolean, Float, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

class LeaveTypeEnum(enum.Enum):
    # Bangladesh Labour Act Compliant Leave Types
    CASUAL = "casual"                    # 10 days/year
    SICK = "sick"                       # 14 days/year with medical certificate
    EARNED = "earned"                   # 1 day per 18 days worked (~20-22 days/year)
    PRIVILEGE = "privilege"             # Same as earned leave
    MATERNITY = "maternity"             # 16 weeks (8 pre + 8 post-birth)
    PATERNITY = "paternity"             # 3-5 days (progressive policy)
    RELIGIOUS = "religious"             # Eid/Religious holidays
    OPTIONAL = "optional"               # Optional holidays
    COMPENSATORY = "compensatory"       # For overtime work
    BEREAVEMENT = "bereavement"         # 3-5 days for family death
    STUDY = "study"                     # For higher education
    UNPAID = "unpaid"                   # Unpaid leave with approval
    HALF_DAY = "half_day"              # Half day leave
    EMERGENCY = "emergency"             # Emergency leave

class LeaveStatusEnum(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    WITHDRAWN = "withdrawn"

class LeaveBalance(Base):
    """Employee Leave Balance Tracking"""
    __tablename__ = "leave_balances"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    leave_type = Column(Enum(LeaveTypeEnum))
    year = Column(Integer)  # Fiscal year
    total_entitled = Column(Float, default=0)  # Total days entitled
    used = Column(Float, default=0)            # Days used
    pending = Column(Float, default=0)         # Days in pending applications
    carried_forward = Column(Float, default=0) # Carried from previous year
    encashed = Column(Float, default=0)        # Days encashed
    
    # Auto-calculated fields
    available = Column(Float, default=0)       # Available = total_entitled + carried_forward - used - pending
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User")

class LeavePolicy(Base):
    """Leave Policy Configuration"""
    __tablename__ = "leave_policies"
    
    id = Column(Integer, primary_key=True, index=True)
    leave_type = Column(Enum(LeaveTypeEnum))
    name = Column(String(100))
    description = Column(Text)
    
    # Entitlement rules
    days_per_year = Column(Float)
    accrual_method = Column(String(50))  # yearly, monthly, per_working_day
    max_consecutive_days = Column(Integer)
    min_notice_days = Column(Integer)
    max_carry_forward = Column(Float, default=0)
    
    # Gender specific
    applicable_gender = Column(String(10))  # all, male, female
    
    # Documentation requirements
    requires_medical_certificate = Column(Boolean, default=False)
    medical_cert_after_days = Column(Integer, default=3)
    requires_approval = Column(Boolean, default=True)
    
    # Bangladeshi compliance flags
    is_mandatory = Column(Boolean, default=True)  # As per Labour Act
    labour_act_section = Column(String(20))  # e.g., "Section 103"
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class LeaveApplication(Base):
    """Enhanced Leave Application"""
    __tablename__ = "leave_applications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    leave_type = Column(Enum(LeaveTypeEnum))
    
    # Leave period
    start_date = Column(Date)
    end_date = Column(Date)
    days_requested = Column(Float)  # Support half days (0.5)
    is_half_day = Column(Boolean, default=False)
    half_day_period = Column(String(20))  # morning, afternoon
    
    # Application details
    reason = Column(Text)
    emergency_contact = Column(String(15))
    handover_notes = Column(Text)
    
    # Status and approval
    status = Column(Enum(LeaveStatusEnum), default=LeaveStatusEnum.PENDING)
    
    # Multi-level approval support
    primary_approver_id = Column(Integer, ForeignKey("users.id"))
    secondary_approver_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    hr_approver_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    primary_approved_at = Column(DateTime, nullable=True)
    secondary_approved_at = Column(DateTime, nullable=True)
    hr_approved_at = Column(DateTime, nullable=True)
    
    final_approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approval_date = Column(DateTime, nullable=True)
    approval_comments = Column(Text)
    rejection_reason = Column(Text)
    
    # Documentation
    medical_certificate_url = Column(String(500), nullable=True)
    supporting_documents = Column(Text, nullable=True)  # JSON array of file URLs
    
    # System fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    applied_date = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    primary_approver = relationship("User", foreign_keys=[primary_approver_id])
    secondary_approver = relationship("User", foreign_keys=[secondary_approver_id])
    hr_approver = relationship("User", foreign_keys=[hr_approver_id])
    final_approver = relationship("User", foreign_keys=[final_approved_by])

class LeaveApprovalWorkflow(Base):
    """Approval Workflow Configuration"""
    __tablename__ = "leave_approval_workflows"
    
    id = Column(Integer, primary_key=True, index=True)
    leave_type = Column(Enum(LeaveTypeEnum))
    department = Column(String(100), nullable=True)  # Department specific workflows
    employee_level = Column(String(50), nullable=True)  # junior, senior, manager
    
    # Workflow steps
    requires_manager_approval = Column(Boolean, default=True)
    requires_hr_approval = Column(Boolean, default=False)
    requires_ceo_approval = Column(Boolean, default=False)  # For senior positions
    
    # Conditions
    days_threshold_hr = Column(Integer, default=5)  # HR approval needed if > 5 days
    days_threshold_ceo = Column(Integer, default=15)  # CEO approval needed if > 15 days
    
    auto_approve_limit = Column(Integer, default=0)  # Auto-approve if <= this many days
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class LeaveCalendar(Base):
    """Team/Department Leave Calendar"""
    __tablename__ = "leave_calendar"
    
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("leave_applications.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    department = Column(String(100))
    
    leave_date = Column(Date)
    leave_type = Column(Enum(LeaveTypeEnum))
    is_half_day = Column(Boolean, default=False)
    
    # For conflict detection
    team_strength_on_date = Column(Integer)
    leaves_on_date = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    application = relationship("LeaveApplication")
    user = relationship("User")

class LeaveEncashment(Base):
    """Leave Encashment Records"""
    __tablename__ = "leave_encashments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    year = Column(Integer)
    leave_type = Column(Enum(LeaveTypeEnum))
    
    days_encashed = Column(Float)
    daily_rate = Column(Float)  # Daily salary rate
    total_amount = Column(Float)
    
    # Processing
    processed_by = Column(Integer, ForeignKey("users.id"))
    processed_at = Column(DateTime)
    payroll_reference = Column(String(100))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    processed_by_user = relationship("User", foreign_keys=[processed_by])

class LeaveAuditLog(Base):
    """Audit Trail for Leave Operations"""
    __tablename__ = "leave_audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("leave_applications.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    action_by = Column(Integer, ForeignKey("users.id"))
    
    action = Column(String(50))  # applied, approved, rejected, modified, cancelled
    old_values = Column(Text)    # JSON of previous values
    new_values = Column(Text)    # JSON of new values
    comments = Column(Text)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    application = relationship("LeaveApplication")
    user = relationship("User", foreign_keys=[user_id])
    action_by_user = relationship("User", foreign_keys=[action_by])
