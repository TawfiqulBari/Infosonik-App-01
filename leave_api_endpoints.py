# Bangladesh Leave Management System - API Endpoints
# Add these to main.py after importing the new models

from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
import calendar
import json

# Pydantic models for API
class LeaveBalanceResponse(BaseModel):
    leave_type: str
    total_entitled: float
    used: float
    pending: float
    available: float
    carried_forward: float
    encashed: float

class LeaveApplicationCreate(BaseModel):
    leave_type: str
    start_date: date
    end_date: date
    is_half_day: bool = False
    half_day_period: Optional[str] = None
    reason: str
    emergency_contact: Optional[str] = None
    handover_notes: Optional[str] = None

class LeaveApplicationResponse(BaseModel):
    id: int
    leave_type: str
    start_date: date
    end_date: date
    days_requested: float
    is_half_day: bool
    reason: str
    status: str
    applied_date: datetime
    approval_date: Optional[datetime] = None
    approval_comments: Optional[str] = None
    rejection_reason: Optional[str] = None
    approver_name: Optional[str] = None

class LeaveApprovalRequest(BaseModel):
    action: str  # approve, reject
    comments: Optional[str] = None

class LeaveTeamCalendarResponse(BaseModel):
    date: date
    employees_on_leave: List[Dict[str, Any]]
    team_strength: int
    leave_percentage: float

# Leave Policy Management Endpoints
@app.get("/leave/policies", response_model=List[Dict])
async def get_leave_policies(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all leave policies with Bangladesh Labour Act compliance"""
    policies = db.query(LeavePolicy).filter(LeavePolicy.is_active == True).all()
    
    return [
        {
            "id": policy.id,
            "leave_type": policy.leave_type.value,
            "name": policy.name,
            "description": policy.description,
            "days_per_year": policy.days_per_year,
            "max_consecutive_days": policy.max_consecutive_days,
            "min_notice_days": policy.min_notice_days,
            "max_carry_forward": policy.max_carry_forward,
            "requires_medical_certificate": policy.requires_medical_certificate,
            "medical_cert_after_days": policy.medical_cert_after_days,
            "is_mandatory": policy.is_mandatory,
            "labour_act_section": policy.labour_act_section,
            "applicable_gender": policy.applicable_gender
        }
        for policy in policies
    ]

@app.get("/leave/balances", response_model=List[LeaveBalanceResponse])
async def get_leave_balances(
    year: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's leave balances"""
    if not year:
        year = datetime.now().year
    
    balances = db.query(LeaveBalance).filter(
        LeaveBalance.user_id == current_user.id,
        LeaveBalance.year == year
    ).all()
    
    # If no balances exist, create them based on policies
    if not balances:
        await create_yearly_leave_balances(current_user.id, year, db)
        balances = db.query(LeaveBalance).filter(
            LeaveBalance.user_id == current_user.id,
            LeaveBalance.year == year
        ).all()
    
    return [
        LeaveBalanceResponse(
            leave_type=balance.leave_type.value,
            total_entitled=balance.total_entitled,
            used=balance.used,
            pending=balance.pending,
            available=balance.available,
            carried_forward=balance.carried_forward,
            encashed=balance.encashed
        )
        for balance in balances
    ]

@app.post("/leave/apply", response_model=LeaveApplicationResponse)
async def apply_for_leave(
    leave_request: LeaveApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Apply for leave with Bangladesh Labour Act validation"""
    
    # Calculate days requested
    if leave_request.is_half_day:
        days_requested = 0.5
        end_date = leave_request.start_date
    else:
        days_requested = calculate_working_days(
            leave_request.start_date, 
            leave_request.end_date
        )
        end_date = leave_request.end_date
    
    # Validate leave application
    validation_result = await validate_leave_application(
        current_user.id, 
        leave_request.leave_type,
        leave_request.start_date,
        end_date,
        days_requested,
        db
    )
    
    if not validation_result["valid"]:
        raise HTTPException(status_code=400, detail=validation_result["message"])
    
    # Get approval workflow
    workflow = await get_approval_workflow(
        leave_request.leave_type,
        current_user,
        days_requested,
        db
    )
    
    # Create leave application
    application = LeaveApplication(
        user_id=current_user.id,
        leave_type=LeaveTypeEnum(leave_request.leave_type),
        start_date=leave_request.start_date,
        end_date=end_date,
        days_requested=days_requested,
        is_half_day=leave_request.is_half_day,
        half_day_period=leave_request.half_day_period,
        reason=leave_request.reason,
        emergency_contact=leave_request.emergency_contact,
        handover_notes=leave_request.handover_notes,
        primary_approver_id=workflow["primary_approver_id"],
        secondary_approver_id=workflow.get("secondary_approver_id"),
        hr_approver_id=workflow.get("hr_approver_id")
    )
    
    db.add(application)
    db.commit()
    db.refresh(application)
    
    # Update pending balance
    await update_leave_balance_pending(
        current_user.id,
        leave_request.leave_type,
        days_requested,
        "add",
        db
    )
    
    # Create calendar entries
    await create_leave_calendar_entries(application, db)
    
    # Send notifications
    await send_leave_application_notifications(application, db)
    
    # Audit log
    await create_leave_audit_log(
        application.id,
        current_user.id,
        current_user.id,
        "applied",
        {},
        leave_request.dict(),
        db
    )
    
    return LeaveApplicationResponse(
        id=application.id,
        leave_type=application.leave_type.value,
        start_date=application.start_date,
        end_date=application.end_date,
        days_requested=application.days_requested,
        is_half_day=application.is_half_day,
        reason=application.reason,
        status=application.status.value,
        applied_date=application.applied_date,
        approval_date=application.approval_date,
        approval_comments=application.approval_comments,
        rejection_reason=application.rejection_reason
    )

@app.get("/leave/my-applications", response_model=List[LeaveApplicationResponse])
async def get_my_leave_applications(
    year: Optional[int] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's leave applications"""
    query = db.query(LeaveApplication).filter(
        LeaveApplication.user_id == current_user.id
    )
    
    if year:
        query = query.filter(
            db.extract('year', LeaveApplication.start_date) == year
        )
    
    if status:
        query = query.filter(LeaveApplication.status == LeaveStatusEnum(status))
    
    applications = query.order_by(LeaveApplication.created_at.desc()).all()
    
    result = []
    for app in applications:
        approver_name = None
        if app.final_approved_by:
            approver = db.query(User).filter(User.id == app.final_approved_by).first()
            approver_name = approver.name if approver else None
        
        result.append(LeaveApplicationResponse(
            id=app.id,
            leave_type=app.leave_type.value,
            start_date=app.start_date,
            end_date=app.end_date,
            days_requested=app.days_requested,
            is_half_day=app.is_half_day,
            reason=app.reason,
            status=app.status.value,
            applied_date=app.applied_date,
            approval_date=app.approval_date,
            approval_comments=app.approval_comments,
            rejection_reason=app.rejection_reason,
            approver_name=approver_name
        ))
    
    return result

@app.get("/leave/pending-approvals", response_model=List[LeaveApplicationResponse])
async def get_pending_approvals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get leave applications pending approval by current user"""
    
    # Check user permissions
    if not has_leave_approval_permission(current_user):
        raise HTTPException(status_code=403, detail="No permission to approve leave")
    
    query = db.query(LeaveApplication).filter(
        LeaveApplication.status == LeaveStatusEnum.PENDING
    )
    
    # Filter based on approval hierarchy
    if current_user.role == "manager":
        query = query.filter(
            LeaveApplication.primary_approver_id == current_user.id
        )
    elif current_user.role == "hr":
        query = query.filter(
            LeaveApplication.hr_approver_id == current_user.id
        )
    elif current_user.role == "admin":
        # Admin can see all pending applications
        pass
    else:
        # Regular employees can only see their subordinates' applications
        subordinates = get_user_subordinates(current_user.id, db)
        subordinate_ids = [sub.id for sub in subordinates]
        query = query.filter(LeaveApplication.user_id.in_(subordinate_ids))
    
    applications = query.order_by(LeaveApplication.applied_date.asc()).all()
    
    result = []
    for app in applications:
        employee = db.query(User).filter(User.id == app.user_id).first()
        
        result.append(LeaveApplicationResponse(
            id=app.id,
            leave_type=app.leave_type.value,
            start_date=app.start_date,
            end_date=app.end_date,
            days_requested=app.days_requested,
            is_half_day=app.is_half_day,
            reason=app.reason,
            status=app.status.value,
            applied_date=app.applied_date,
            employee_name=employee.name if employee else "Unknown",
            employee_department=getattr(employee, 'department', 'N/A')
        ))
    
    return result

@app.post("/leave/{application_id}/approve")
async def process_leave_application(
    application_id: int,
    approval_request: LeaveApprovalRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Approve or reject leave application"""
    
    application = db.query(LeaveApplication).filter(
        LeaveApplication.id == application_id
    ).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="Leave application not found")
    
    # Check approval permissions
    can_approve = await check_approval_permission(application, current_user, db)
    if not can_approve:
        raise HTTPException(status_code=403, detail="No permission to approve this application")
    
    old_values = {
        "status": application.status.value,
        "approval_comments": application.approval_comments
    }
    
    if approval_request.action == "approve":
        application.status = LeaveStatusEnum.APPROVED
        application.final_approved_by = current_user.id
        application.approval_date = datetime.utcnow()
        application.approval_comments = approval_request.comments
        
        # Update leave balance
        await update_leave_balance_used(
            application.user_id,
            application.leave_type.value,
            application.days_requested,
            db
        )
        
        # Remove from pending
        await update_leave_balance_pending(
            application.user_id,
            application.leave_type.value,
            application.days_requested,
            "subtract",
            db
        )
        
        message = "Leave application approved successfully"
        
    elif approval_request.action == "reject":
        application.status = LeaveStatusEnum.REJECTED
        application.final_approved_by = current_user.id
        application.approval_date = datetime.utcnow()
        application.rejection_reason = approval_request.comments
        
        # Remove from pending balance
        await update_leave_balance_pending(
            application.user_id,
            application.leave_type.value,
            application.days_requested,
            "subtract",
            db
        )
        
        message = "Leave application rejected"
    
    else:
        raise HTTPException(status_code=400, detail="Invalid action")
    
    db.commit()
    
    # Audit log
    await create_leave_audit_log(
        application.id,
        application.user_id,
        current_user.id,
        approval_request.action,
        old_values,
        {
            "status": application.status.value,
            "comments": approval_request.comments
        },
        db
    )
    
    # Send notification to employee
    await send_leave_approval_notification(application, approval_request.action, db)
    
    return {"message": message}

@app.get("/leave/team-calendar")
async def get_team_leave_calendar(
    start_date: date,
    end_date: date,
    department: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get team leave calendar for specified period"""
    
    query = db.query(LeaveCalendar).filter(
        LeaveCalendar.leave_date >= start_date,
        LeaveCalendar.leave_date <= end_date
    )
    
    if department:
        query = query.filter(LeaveCalendar.department == department)
    elif hasattr(current_user, 'department'):
        query = query.filter(LeaveCalendar.department == current_user.department)
    
    calendar_entries = query.all()
    
    # Group by date
    calendar_data = {}
    for entry in calendar_entries:
        date_str = entry.leave_date.isoformat()
        if date_str not in calendar_data:
            calendar_data[date_str] = {
                "date": entry.leave_date,
                "employees_on_leave": [],
                "team_strength": entry.team_strength_on_date,
                "total_leaves": 0
            }
        
        user = db.query(User).filter(User.id == entry.user_id).first()
        calendar_data[date_str]["employees_on_leave"].append({
            "name": user.name if user else "Unknown",
            "leave_type": entry.leave_type.value,
            "is_half_day": entry.is_half_day
        })
        
        calendar_data[date_str]["total_leaves"] += 0.5 if entry.is_half_day else 1.0
    
    # Calculate leave percentage
    for date_data in calendar_data.values():
        if date_data["team_strength"] > 0:
            date_data["leave_percentage"] = (date_data["total_leaves"] / date_data["team_strength"]) * 100
        else:
            date_data["leave_percentage"] = 0
    
    return list(calendar_data.values())

@app.get("/leave/reports/summary")
async def get_leave_summary_report(
    year: Optional[int] = None,
    department: Optional[str] = None,
    leave_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate leave summary reports for HR and management"""
    
    if not has_hr_permission(current_user):
        raise HTTPException(status_code=403, detail="HR permission required")
    
    if not year:
        year = datetime.now().year
    
    # Base query for applications in the specified year
    query = db.query(LeaveApplication).filter(
        db.extract('year', LeaveApplication.start_date) == year
    )
    
    if department:
        # Join with users to filter by department
        query = query.join(User).filter(User.department == department)
    
    if leave_type:
        query = query.filter(LeaveApplication.leave_type == LeaveTypeEnum(leave_type))
    
    applications = query.all()
    
    # Generate summary statistics
    summary = {
        "total_applications": len(applications),
        "approved": len([app for app in applications if app.status == LeaveStatusEnum.APPROVED]),
        "rejected": len([app for app in applications if app.status == LeaveStatusEnum.REJECTED]),
        "pending": len([app for app in applications if app.status == LeaveStatusEnum.PENDING]),
        "total_days_taken": sum([app.days_requested for app in applications if app.status == LeaveStatusEnum.APPROVED]),
        "by_leave_type": {},
        "by_month": {},
        "by_department": {},
        "average_approval_time": 0
    }
    
    # Group by leave type
    for app in applications:
        leave_type_key = app.leave_type.value
        if leave_type_key not in summary["by_leave_type"]:
            summary["by_leave_type"][leave_type_key] = {
                "count": 0,
                "days": 0,
                "approved": 0,
                "rejected": 0,
                "pending": 0
            }
        
        summary["by_leave_type"][leave_type_key]["count"] += 1
        summary["by_leave_type"][leave_type_key]["days"] += app.days_requested
        summary["by_leave_type"][leave_type_key][app.status.value] += 1
    
    # Group by month
    for app in applications:
        month_key = app.start_date.strftime("%B")
        if month_key not in summary["by_month"]:
            summary["by_month"][month_key] = {"count": 0, "days": 0}
        
        summary["by_month"][month_key]["count"] += 1
        if app.status == LeaveStatusEnum.APPROVED:
            summary["by_month"][month_key]["days"] += app.days_requested
    
    # Calculate average approval time
    approved_apps = [app for app in applications if app.approval_date]
    if approved_apps:
        total_approval_time = sum([
            (app.approval_date - app.applied_date).days 
            for app in approved_apps
        ])
        summary["average_approval_time"] = total_approval_time / len(approved_apps)
    
    return summary

@app.post("/leave/initialize-balances/{year}")
async def initialize_yearly_leave_balances(
    year: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Initialize leave balances for all users for a given year (Admin only)"""
    
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin permission required")
    
    users = db.query(User).filter(User.is_active == True).all()
    initialized_count = 0
    
    for user in users:
        await create_yearly_leave_balances(user.id, year, db)
        initialized_count += 1
    
    return {
        "message": f"Leave balances initialized for {initialized_count} users for year {year}"
    }

# Helper functions
async def create_yearly_leave_balances(user_id: int, year: int, db: Session):
    """Create yearly leave balances based on policies"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return
    
    policies = db.query(LeavePolicy).filter(LeavePolicy.is_active == True).all()
    
    for policy in policies:
        # Check if balance already exists
        existing = db.query(LeaveBalance).filter(
            LeaveBalance.user_id == user_id,
            LeaveBalance.leave_type == policy.leave_type,
            LeaveBalance.year == year
        ).first()
        
        if existing:
            continue
        
        # Calculate entitled days based on joining date and policy
        entitled_days = calculate_leave_entitlement(
            user, policy, year
        )
        
        # Get carried forward from previous year
        carried_forward = get_carried_forward_balance(
            user_id, policy.leave_type, year, db
        )
        
        balance = LeaveBalance(
            user_id=user_id,
            leave_type=policy.leave_type,
            year=year,
            total_entitled=entitled_days,
            carried_forward=carried_forward,
            available=entitled_days + carried_forward
        )
        
        db.add(balance)
    
    db.commit()

def calculate_leave_entitlement(user: User, policy: LeavePolicy, year: int) -> float:
    """Calculate leave entitlement based on joining date and policy"""
    
    if not user.created_at:
        return policy.days_per_year
    
    # Get joining date
    joining_date = user.created_at.date()
    year_start = date(year, 1, 1)
    year_end = date(year, 12, 31)
    
    # If joined after year start, calculate pro-rata
    if joining_date > year_start:
        if policy.accrual_method == "monthly":
            months_served = 12 - joining_date.month + 1
            return (policy.days_per_year / 12) * months_served
        elif policy.accrual_method == "per_working_day" and policy.leave_type == LeaveTypeEnum.EARNED:
            # For earned leave: 1 day per 18 working days
            working_days_in_year = calculate_working_days(
                max(joining_date, year_start), 
                year_end
            )
            return working_days_in_year / 18
    
    return policy.days_per_year

def calculate_working_days(start_date: date, end_date: date) -> int:
    """Calculate working days between two dates (excluding weekends)"""
    
    working_days = 0
    current_date = start_date
    
    while current_date <= end_date:
        # In Bangladesh, Friday is typically a weekend day, Saturday is half-day
        if current_date.weekday() != 4:  # Not Friday
            working_days += 1
        current_date += timedelta(days=1)
    
    return working_days

async def validate_leave_application(
    user_id: int,
    leave_type: str,
    start_date: date,
    end_date: date,
    days_requested: float,
    db: Session
) -> Dict[str, Any]:
    """Validate leave application against policies and balances"""
    
    # Get policy
    policy = db.query(LeavePolicy).filter(
        LeavePolicy.leave_type == LeaveTypeEnum(leave_type),
        LeavePolicy.is_active == True
    ).first()
    
    if not policy:
        return {"valid": False, "message": f"Leave type {leave_type} not found"}
    
    # Check minimum notice period
    notice_days = (start_date - date.today()).days
    if notice_days < policy.min_notice_days:
        return {
            "valid": False, 
            "message": f"Minimum {policy.min_notice_days} days notice required"
        }
    
    # Check maximum consecutive days
    if policy.max_consecutive_days and days_requested > policy.max_consecutive_days:
        return {
            "valid": False,
            "message": f"Maximum {policy.max_consecutive_days} consecutive days allowed"
        }
    
    # Check available balance
    current_year = start_date.year
    balance = db.query(LeaveBalance).filter(
        LeaveBalance.user_id == user_id,
        LeaveBalance.leave_type == LeaveTypeEnum(leave_type),
        LeaveBalance.year == current_year
    ).first()
    
    if balance and balance.available < days_requested:
        return {
            "valid": False,
            "message": f"Insufficient balance. Available: {balance.available} days"
        }
    
    # Check for overlapping applications
    overlapping = db.query(LeaveApplication).filter(
        LeaveApplication.user_id == user_id,
        LeaveApplication.status.in_([LeaveStatusEnum.PENDING, LeaveStatusEnum.APPROVED]),
        LeaveApplication.start_date <= end_date,
        LeaveApplication.end_date >= start_date
    ).first()
    
    if overlapping:
        return {
            "valid": False,
            "message": "Overlapping leave application exists"
        }
    
    return {"valid": True, "message": "Valid"}

# Add more helper functions for workflow, notifications, etc.
