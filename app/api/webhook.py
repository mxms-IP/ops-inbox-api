from datetime import datetime
from uuid import uuid4
from fastapi import APIRouter, BackgroundTasks, status
from app.models.schema import TicketIn, WebhookAck, TicketOut
from app.classification import classifier
from app.storage import save_ticket
from app.drafts.generator import generate_draft

router = APIRouter()

def process_ticket(ticket_id: str, ticket: TicketIn):
    try:
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
            status="pending", 
            received_at=received_at
        )
        draft = generate_draft(ticket_data)
        ticket_data.draft=draft

        save_ticket(ticket_data)
    except Exception as e:
        print(f"CRITICAL: failed to process ticket {ticket_id}: {e}")
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