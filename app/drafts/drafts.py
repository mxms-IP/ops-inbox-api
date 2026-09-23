from fastapi import APIRouter, HTTPException
from app.models.schema import TicketOut
from app.storage import get_all_tickets, get_ticket, save_ticket,update_status
from app.drafts.generator import generate_draft

router = APIRouter()

@router.get("/api/v1/drafts/pending")
def list_pending_drafts():
    """
    Return all tickets with status == "pending",
    each augmented with its rendered draft text.
    Shape of each item: the ticket's fields plus a "draft" key.
    """
    tickets = get_all_tickets()
    pending_tickets = [ticket for ticket in tickets if ticket.status == "pending"]

    list_of_tickets=[]
    
    for ticket in pending_tickets:
        draft= generate_draft(ticket)
        ticket= ticket.model_dump()
        ticket["draft"]= draft
        list_of_tickets.append(ticket)

    return list_of_tickets

@router.post("/api/v1/drafts/{ticket_id}/approve")
def approve_draft(ticket_id: str):
    """
    Look up the ticket by ticket_id.
    If it doesn't exist, raise HTTPException(404).
    Otherwise set status = "sent", persist the change (save_ticket
    with sqlite acts as an upsert on primary key — same ticket_id
    overwrites the existing row), and return a confirmation payload.
    """

    try:
        ticket= get_ticket(ticket_id)
    except None:
        raise HTTPException(404)

    ticket.status= "sent"
    update_status(ticket_id,"sent")

    return ticket
    pass