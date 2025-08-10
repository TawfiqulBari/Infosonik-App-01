from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ExpenseBase(BaseModel):
    bill_date: Optional[datetime] = None
    transport_amount: int = 0
    transport_description: Optional[str] = None
    food_amount: int = 0
    food_description: Optional[str] = None
    other_amount: int = 0
    other_description: Optional[str] = None
    fuel_cost: int = 0
    rental_cost: int = 0
    is_billable: bool = True
    general_description: Optional[str] = None
    client_id: Optional[int] = None

class ExpenseCreate(ExpenseBase):
    pass

class Expense(ExpenseBase):
    id: int
    
    class Config:
        from_attributes = True