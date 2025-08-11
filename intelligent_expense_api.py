"""
Intelligent Expense Management API Endpoints
Comprehensive expense system with approval workflows, reporting, and analytics
"""

from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Date, DECIMAL, ForeignKey, JSON as JSONB
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel, Field
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
import json
import uuid

# Database Models
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
    conditions = Column(JSONB)
    approval_levels = Column(JSONB, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class IntelligentExpense(Base):
    __tablename__ = "intelligent_expenses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    expense_number = Column(String(20), unique=True)
    category_id = Column(Integer, ForeignKey('expense_categories.id'))
    
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
    travel_distance = Column(Integer)
    
    # Project and Client
    project_id = Column(String(100))
    client_name = Column(String(200))
    is_billable = Column(Boolean, default=False)
    
    # Receipts and Attachments
    receipt_uploaded = Column(Boolean, default=False)
    receipt_files = Column(JSONB)
    ocr_extracted_data = Column(JSONB)
    
    # Approval and Status
    workflow_id = Column(Integer, ForeignKey('expense_approval_workflows.id'))
    status = Column(String(20), default='draft')
    current_approver_id = Column(Integer)
    submitted_at = Column(DateTime)
    
    # Automation and Intelligence
    auto_categorized = Column(Boolean, default=False)
    confidence_score = Column(DECIMAL(3,2))
    duplicate_check_passed = Column(Boolean, default=True)
    policy_compliance = Column(JSONB)
    
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
    expense_id = Column(Integer, ForeignKey('intelligent_expenses.id'), nullable=False)
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
    filters = Column(JSONB)
    
    total_expenses = Column(Integer)
    total_approved = Column(Integer)
    total_pending = Column(Integer)
    total_rejected = Column(Integer)
    expense_count = Column(Integer)
    
    summary_data = Column(JSONB)
    detailed_data = Column(JSONB)
    
    is_scheduled = Column(Boolean, default=False)
    schedule_frequency = Column(String(20))
    next_generation = Column(Date)
    
    status = Column(String(20), default='generated')
    generated_at = Column(DateTime, default=datetime.utcnow)
    generated_by = Column(Integer)
    file_path = Column(String(500))
    
    created_at = Column(DateTime, default=datetime.utcnow)

class ExpenseBudget(Base):
    __tablename__ = "expense_budgets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    department_id = Column(Integer)
    category_id = Column(Integer, ForeignKey('expense_categories.id'))
    user_id = Column(Integer)
    
    period_type = Column(String(20), nullable=False)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    
    allocated_amount = Column(Integer, nullable=False)
    spent_amount = Column(Integer, default=0)
    committed_amount = Column(Integer, default=0)
    available_amount = Column(Integer)
    
    alert_threshold = Column(DECIMAL(3,2), default=0.80)
    warning_threshold = Column(DECIMAL(3,2), default=0.90)
    alert_sent = Column(Boolean, default=False)
    warning_sent = Column(Boolean, default=False)
    
    is_active = Column(Boolean, default=True)
    auto_rollover = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

# Pydantic Models
class ExpenseCategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    icon: Optional[str]
    color: Optional[str]
    requires_receipt: bool
    receipt_threshold: int

    class Config:
        from_attributes = True

class ExpenseCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    amount: float = Field(..., gt=0)
    category_id: Optional[int] = None
    expense_date: date
    vendor_name: Optional[str] = None
    vendor_contact: Optional[str] = None
    location_from: Optional[str] = None
    location_to: Optional[str] = None
    project_id: Optional[str] = None
    client_name: Optional[str] = None
    is_billable: bool = False
    reimbursable: bool = True

class ExpenseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[float] = None
    category_id: Optional[int] = None
    expense_date: Optional[date] = None
    vendor_name: Optional[str] = None
    location_from: Optional[str] = None
    location_to: Optional[str] = None
    is_billable: Optional[bool] = None

class ExpenseResponse(BaseModel):
    id: int
    expense_number: Optional[str]
    title: str
    description: Optional[str]
    amount: int
    amount_bdt: float
    category_id: Optional[int]
    category_name: Optional[str]
    category_color: Optional[str]
    expense_date: date
    vendor_name: Optional[str]
    client_name: Optional[str]
    is_billable: bool
    status: str
    submitted_at: Optional[datetime]
    receipt_uploaded: bool
    auto_categorized: bool
    confidence_score: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True

class ApprovalRequest(BaseModel):
    expense_id: int
    action: str  # 'approve' or 'reject'
    comments: Optional[str] = None

class BulkApprovalRequest(BaseModel):
    expense_ids: List[int]
    action: str  # 'approve' or 'reject'
    comments: Optional[str] = None

class ReportRequest(BaseModel):
    report_type: str  # 'weekly', 'monthly', 'yearly', 'custom'
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    category_ids: Optional[List[int]] = None
    status_filter: Optional[List[str]] = None

# Utility Functions
def generate_expense_number():
    """Generate unique expense number"""
    timestamp = datetime.now().strftime("%Y%m")
    random_part = str(uuid.uuid4())[:8].upper()
    return f"EXP-{timestamp}-{random_part}"

def determine_workflow(expense_data: dict, db: Session):
    """Determine appropriate approval workflow based on expense data"""
    workflows = db.query(ExpenseApprovalWorkflow).filter(
        ExpenseApprovalWorkflow.is_active == True
    ).all()
    
    for workflow in workflows:
        conditions = json.loads(workflow.conditions) if workflow.conditions else {}
        
        # Check amount conditions
        if 'amount_min' in conditions and expense_data['amount'] < conditions['amount_min']:
            continue
        if 'amount_max' in conditions and expense_data['amount'] > conditions['amount_max']:
            continue
            
        # Check category conditions
        if 'category' in conditions:
            category = db.query(ExpenseCategory).filter(
                ExpenseCategory.id == expense_data.get('category_id')
            ).first()
            if category and category.name != conditions['category']:
                continue
        
        return workflow
    
    # Default workflow
    return db.query(ExpenseApprovalWorkflow).filter(
        ExpenseApprovalWorkflow.name == 'Standard Workflow'
    ).first()

def auto_categorize_expense(title: str, description: str, amount: int, db: Session):
    """Auto-categorize expense using simple keyword matching"""
    categories = db.query(ExpenseCategory).filter(ExpenseCategory.is_active == True).all()
    
    text = f"{title} {description}".lower()
    
    # Simple keyword matching
    category_keywords = {
        'Transportation': ['transport', 'taxi', 'uber', 'bus', 'train', 'fuel', 'parking'],
        'Meals & Entertainment': ['meal', 'lunch', 'dinner', 'restaurant', 'food', 'coffee'],
        'Office Supplies': ['office', 'supplies', 'stationery', 'paper', 'pen'],
        'Travel & Accommodation': ['hotel', 'accommodation', 'flight', 'travel', 'booking'],
        'Communication': ['phone', 'internet', 'mobile', 'communication'],
        'Training & Development': ['training', 'course', 'seminar', 'workshop'],
        'Equipment & Technology': ['computer', 'laptop', 'software', 'equipment']
    }
    
    best_match = None
    confidence = 0.0
    
    for category in categories:
        if category.name in category_keywords:
            keywords = category_keywords[category.name]
            matches = sum(1 for keyword in keywords if keyword in text)
            category_confidence = matches / len(keywords)
            
            if category_confidence > confidence:
                confidence = category_confidence
                best_match = category
    
    return best_match, min(confidence * 100, 99.0)

# API Endpoint Functions
async def get_expense_categories(db: Session = Depends(get_db)):
    """Get all active expense categories"""
    categories = db.query(ExpenseCategory).filter(ExpenseCategory.is_active == True).all()
    return [ExpenseCategoryResponse.from_orm(cat) for cat in categories]

async def create_expense(expense: ExpenseCreate, current_user: dict, db: Session = Depends(get_db)):
    """Create new expense with intelligent categorization"""
    
    # Convert amount to paisa
    amount_paisa = int(expense.amount * 100)
    
    # Auto-categorize if no category provided
    category_id = expense.category_id
    auto_categorized = False
    confidence_score = None
    
    if not category_id:
        category, confidence = auto_categorize_expense(
            expense.title, expense.description or "", amount_paisa, db
        )
        if category:
            category_id = category.id
            auto_categorized = True
            confidence_score = confidence
    
    # Generate expense number
    expense_number = generate_expense_number()
    
    # Determine workflow
    workflow = determine_workflow({
        'amount': amount_paisa,
        'category_id': category_id
    }, db)
    
    # Calculate net amount (after deductions)
    net_amount = amount_paisa
    
    # Create expense record
    db_expense = IntelligentExpense(
        user_id=current_user.id,
        expense_number=expense_number,
        category_id=category_id,
        title=expense.title,
        description=expense.description,
        amount=amount_paisa,
        expense_date=expense.expense_date,
        vendor_name=expense.vendor_name,
        vendor_contact=expense.vendor_contact,
        location_from=expense.location_from,
        location_to=expense.location_to,
        project_id=expense.project_id,
        client_name=expense.client_name,
        is_billable=expense.is_billable,
        reimbursable=expense.reimbursable,
        workflow_id=workflow.id if workflow else None,
        status='draft',
        auto_categorized=auto_categorized,
        confidence_score=confidence_score,
        net_amount=net_amount,
        created_by=current_user.id
    )
    
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    
    return {
        "message": "Expense created successfully",
        "expense_id": db_expense.id,
        "expense_number": expense_number,
        "auto_categorized": auto_categorized,
        "confidence_score": confidence_score
    }

async def submit_expense(expense_id: int, current_user: dict, db: Session = Depends(get_db)):
    """Submit expense for approval"""
    
    expense = db.query(IntelligentExpense).filter(
        IntelligentExpense.id == expense_id,
        IntelligentExpense.user_id == current_user.id,
        IntelligentExpense.status == 'draft'
    ).first()
    
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found or already submitted")
    
    # Update status and submission time
    expense.status = 'submitted'
    expense.submitted_at = datetime.utcnow()
    
    # Create approval entries based on workflow
    if expense.workflow_id:
        workflow = db.query(ExpenseApprovalWorkflow).filter(
            ExpenseApprovalWorkflow.id == expense.workflow_id
        ).first()
        
        if workflow and workflow.approval_levels:
            approval_levels = json.loads(workflow.approval_levels)
            for level in approval_levels:
                approval = ExpenseApproval(
                    expense_id=expense.id,
                    approver_id=1,  # TODO: Determine actual approver based on role
                    approval_level=level['level'],
                    status='pending'
                )
                db.add(approval)
    
    db.commit()
    
    return {"message": "Expense submitted for approval", "status": "submitted"}

async def get_my_expenses(
    current_user: dict,
    status: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Get user's expenses with filters"""
    
    query = db.query(IntelligentExpense).filter(
        IntelligentExpense.user_id == current_user.id
    )
    
    if status:
        query = query.filter(IntelligentExpense.status == status)
    
    if date_from:
        query = query.filter(IntelligentExpense.expense_date >= date_from)
    
    if date_to:
        query = query.filter(IntelligentExpense.expense_date <= date_to)
    
    expenses = query.order_by(IntelligentExpense.created_at.desc()).all()
    
    result = []
    for expense in expenses:
        category = db.query(ExpenseCategory).filter(
            ExpenseCategory.id == expense.category_id
        ).first()
        
        result.append({
            "id": expense.id,
            "expense_number": expense.expense_number,
            "title": expense.title,
            "description": expense.description,
            "amount": expense.amount,
            "amount_bdt": expense.amount / 100,
            "category_id": expense.category_id,
            "category_name": category.name if category else None,
            "category_color": category.color if category else None,
            "expense_date": expense.expense_date,
            "vendor_name": expense.vendor_name,
            "client_name": expense.client_name,
            "is_billable": expense.is_billable,
            "status": expense.status,
            "submitted_at": expense.submitted_at,
            "receipt_uploaded": expense.receipt_uploaded,
            "auto_categorized": expense.auto_categorized,
            "confidence_score": float(expense.confidence_score) if expense.confidence_score else None,
            "created_at": expense.created_at
        })
    
    return result

async def get_pending_approvals(current_user: dict, db: Session = Depends(get_db)):
    """Get expenses pending approval for current user"""
    
    pending_approvals = db.query(ExpenseApproval).filter(
        ExpenseApproval.approver_id == current_user.id,
        ExpenseApproval.status == 'pending'
    ).all()
    
    result = []
    for approval in pending_approvals:
        expense = db.query(IntelligentExpense).filter(
            IntelligentExpense.id == approval.expense_id
        ).first()
        
        if expense:
            category = db.query(ExpenseCategory).filter(
                ExpenseCategory.id == expense.category_id
            ).first()
            
            submitter = db.query(User).filter(User.id == expense.user_id).first()
            
            result.append({
                "approval_id": approval.id,
                "expense_id": expense.id,
                "expense_number": expense.expense_number,
                "title": expense.title,
                "amount": expense.amount,
                "amount_bdt": expense.amount / 100,
                "category_name": category.name if category else None,
                "submitter_name": submitter.name if submitter else None,
                "submitted_at": expense.submitted_at,
                "approval_level": approval.approval_level
            })
    
    return result

async def process_approval(request: ApprovalRequest, current_user: dict, db: Session = Depends(get_db)):
    """Process expense approval/rejection"""
    
    expense = db.query(IntelligentExpense).filter(
        IntelligentExpense.id == request.expense_id
    ).first()
    
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    approval = db.query(ExpenseApproval).filter(
        ExpenseApproval.expense_id == request.expense_id,
        ExpenseApproval.approver_id == current_user.id,
        ExpenseApproval.status == 'pending'
    ).first()
    
    if not approval:
        raise HTTPException(status_code=404, detail="Approval record not found")
    
    # Update approval record
    approval.status = request.action
    approval.comments = request.comments
    approval.approved_at = datetime.utcnow()
    
    # Update expense status if needed
    if request.action == 'rejected':
        expense.status = 'rejected'
    elif request.action == 'approved':
        # Check if this was the final approval
        remaining_approvals = db.query(ExpenseApproval).filter(
            ExpenseApproval.expense_id == request.expense_id,
            ExpenseApproval.status == 'pending'
        ).count()
        
        if remaining_approvals == 0:
            expense.status = 'approved'
    
    db.commit()
    
    return {
        "message": f"Expense {request.action} successfully",
        "expense_status": expense.status
    }

async def generate_expense_report(
    request: ReportRequest,
    current_user: dict,
    db: Session = Depends(get_db)
):
    """Generate comprehensive expense report"""
    
    # Set date range based on report type
    today = date.today()
    if request.report_type == 'weekly':
        date_from = today - timedelta(days=7)
        date_to = today
    elif request.report_type == 'monthly':
        date_from = today.replace(day=1)
        date_to = today
    elif request.report_type == 'yearly':
        date_from = today.replace(month=1, day=1)
        date_to = today
    else:
        date_from = request.date_from or (today - timedelta(days=30))
        date_to = request.date_to or today
    
    # Build query
    query = db.query(IntelligentExpense).filter(
        IntelligentExpense.expense_date >= date_from,
        IntelligentExpense.expense_date <= date_to
    )
    
    # Add user filter (users can only see their own expenses unless admin)
    if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
        query = query.filter(IntelligentExpense.user_id == current_user.id)
    
    # Add category filter
    if request.category_ids:
        query = query.filter(IntelligentExpense.category_id.in_(request.category_ids))
    
    # Add status filter
    if request.status_filter:
        query = query.filter(IntelligentExpense.status.in_(request.status_filter))
    
    expenses = query.all()
    
    # Calculate summary
    total_expenses = sum(exp.amount for exp in expenses)
    total_approved = sum(exp.amount for exp in expenses if exp.status == 'approved')
    total_pending = sum(exp.amount for exp in expenses if exp.status in ['submitted', 'pending'])
    total_rejected = sum(exp.amount for exp in expenses if exp.status == 'rejected')
    
    # Category breakdown
    category_breakdown = {}
    for expense in expenses:
        if expense.category_id:
            category = db.query(ExpenseCategory).filter(
                ExpenseCategory.id == expense.category_id
            ).first()
            category_name = category.name if category else 'Uncategorized'
            
            if category_name not in category_breakdown:
                category_breakdown[category_name] = {
                    'amount': 0,
                    'count': 0,
                    'color': category.color if category else '#9E9E9E'
                }
            
            category_breakdown[category_name]['amount'] += expense.amount
            category_breakdown[category_name]['count'] += 1
    
    # Create report record
    report = ExpenseReport(
        report_type=request.report_type,
        title=f"{request.report_type.title()} Expense Report",
        user_id=current_user.id,
        date_from=date_from,
        date_to=date_to,
        total_expenses=total_expenses,
        total_approved=total_approved,
        total_pending=total_pending,
        total_rejected=total_rejected,
        expense_count=len(expenses),
        summary_data=json.dumps({
            'category_breakdown': category_breakdown,
            'status_breakdown': {
                'approved': len([e for e in expenses if e.status == 'approved']),
                'pending': len([e for e in expenses if e.status in ['submitted', 'pending']]),
                'rejected': len([e for e in expenses if e.status == 'rejected']),
                'draft': len([e for e in expenses if e.status == 'draft'])
            }
        }),
        generated_by=current_user.id
    )
    
    db.add(report)
    db.commit()
    
    return {
        "report_id": report.id,
        "report_type": request.report_type,
        "date_from": date_from,
        "date_to": date_to,
        "summary": {
            "total_expenses": total_expenses,
            "total_expenses_bdt": total_expenses / 100,
            "total_approved": total_approved,
            "total_approved_bdt": total_approved / 100,
            "total_pending": total_pending,
            "total_pending_bdt": total_pending / 100,
            "total_rejected": total_rejected,
            "total_rejected_bdt": total_rejected / 100,
            "expense_count": len(expenses)
        },
        "category_breakdown": {
            cat: {
                "amount_bdt": data["amount"] / 100,
                "count": data["count"],
                "color": data["color"]
            } for cat, data in category_breakdown.items()
        },
        "expenses": [
            {
                "id": exp.id,
                "expense_number": exp.expense_number,
                "title": exp.title,
                "amount_bdt": exp.amount / 100,
                "expense_date": exp.expense_date,
                "status": exp.status,
                "category_name": next(
                    (cat.name for cat in db.query(ExpenseCategory).filter(
                        ExpenseCategory.id == exp.category_id
                    ) if cat), 'Uncategorized'
                )
            } for exp in expenses
        ]
    }

