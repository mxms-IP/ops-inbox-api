from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime
from typing import Literal, Optional


class TicketIn(BaseModel):
    sender: EmailStr
    subject: str
    body: str

class TicketOut(BaseModel):
    model_config = ConfigDict(from_attributes=True) 
    ticket_id: str
    sender: str
    subject: str
    category: str
    confidence: float
    entities: dict
    status: Literal["pending", "sent"]
    draft: Optional[str] = None
    received_at: datetime

class WebhookAck(BaseModel):
    ticket_id: str
    status: Literal["queued"]