from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Literal


class TicketIn(BaseModel):
    sender: EmailStr
    subject: str
    body: str

class TicketOut(BaseModel): 
    ticket_id: str
    sender: str
    subject: str
    category: str
    confidence: float
    entities: dict
    status: Literal["pending", "sent"]
    received_at: datetime

class WebhookAck(BaseModel):
    ticket_id: str
    status: Literal["queued"]