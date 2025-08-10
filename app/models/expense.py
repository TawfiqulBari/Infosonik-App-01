from sqlalchemy import Column, Integer, Text, DateTime, Boolean, ForeignKey
from datetime import datetime
from sqlalchemy.orm import relationship
from .base import Base

class Expense(Base):
    __tablename__ = 'expenses'
    
    id = Column(Integer, primary_key=True)
    bill_date = Column(DateTime)
    transport_amount = Column(Integer, default=0)
    transport_description = Column(Text)
    food_amount = Column(Integer, default=0)
    food_description = Column(Text)
    other_amount = Column(Integer, default=0)
    other_description = Column(Text)
    fuel_cost = Column(Integer, default=0)
    rental_cost = Column(Integer, default=0)
    is_billable = Column(Boolean, default=True)
    general_description = Column(Text)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=True)
    client = relationship("Client", back_populates="expenses")
    
    @property
    def total_amount(self):
        return sum([
            self.transport_amount or 0,
            self.food_amount or 0,
            self.other_amount or 0,
            self.fuel_cost or 0,
            self.rental_cost or 0
        ])