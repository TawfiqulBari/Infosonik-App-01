from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from ..models.expense import Expense as ExpenseModel
from ..models.schemas import Expense, ExpenseCreate
from ..models.base import get_db

router = APIRouter()

@router.post("/expenses/", response_model=Expense)
async def create_expense(expense: ExpenseCreate, db: Session = Depends(get_db)):
    db_expense = ExpenseModel(**expense.dict())
    db.add(db_expense)
    db.commit()
    db.refresh(expense)
    return expense

@router.get("/expenses/", response_model=List[Expense])
async def read_expenses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(ExpenseModel).offset(skip).limit(limit).all()

@router.get("/expenses/{expense_id}", response_model=Expense)
async def read_expense(expense_id: int, db: Session = Depends(get_db)):
    expense = db.query(ExpenseModel).filter(ExpenseModel.id == expense_id).first()
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense