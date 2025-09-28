
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, date

class GetMenuPayload(BaseModel):
    tags: Optional[List[str]] = None

class CheckItemAvailabilityPayload(BaseModel):
    item_id: str
    qty: int

class CreateOrderItem(BaseModel):
    item_id: str
    qty: int
    notes: Optional[str] = None

class CreateOrderCustomer(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None

class CreateOrderPayload(BaseModel):
    items: List[CreateOrderItem]
    customer: CreateOrderCustomer

class GetTimeslotsPayload(BaseModel):
    date: date
    party_size: int

class CreateReservationPayload(BaseModel):
    datetime: datetime
    party_size: int
    name: str
    phone: str

class CreateReminderPayload(BaseModel):
    assignee: str = Field(..., pattern="^chef$") # Only 'chef' is allowed
    due_at: datetime
    payload: dict

class HandoverHumanPayload(BaseModel):
    reason: str


