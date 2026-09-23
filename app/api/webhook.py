from datetime import datetime, date
import time
from uuid import uuid4
from fastapi import APIRouter, BackgroundTasks, status
from app.models.schema import TicketIn, WebhookAck, TicketOut
from app.classification import classifier
from app.storage.csv_store import append_ticket

router = APIRouter()

def process_ticket(ticket_id: str, ticket: TicketIn):

    category= classifier.classify(ticket.subject,ticket.body)
    entities= classifier.extract_entities(ticket.sender,ticket.subject,ticket.body)
    received_at= datetime.now()
    ticket_data = TicketOut(
        ticket_id=ticket_id, 
        sender=ticket.sender, 
        subject=ticket.subject, 
        category=category["category"], 
        confidence=category["confidence"], 
        entities=entities, 
        status="sent", 
        received_at=received_at
    )

    append_ticket(ticket_data)
    pass




@router.post(
    "/api/v1/inbox/webhook",
    response_model=WebhookAck,
    status_code=status.HTTP_202_ACCEPTED,
)
def receive_webhook(ticket: TicketIn, background_tasks: BackgroundTasks):
    ticket_id = str(uuid4())
    background_tasks.add_task(process_ticket,ticket_id,ticket)
    return WebhookAck(ticket_id=ticket_id, status="queued")