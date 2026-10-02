from fastapi import APIRouter
from app.ingestion.imap_poller import fetch_unread_emails
from app.api.webhook import process_ticket
import uuid

router = APIRouter()

@router.post("/api/v1/ingest/poll-now")
def poll_now():
    ticket_list, skipped_parsing = fetch_unread_emails()
    succeeded = 0
    failed = 0

    for ticket_obj in ticket_list:
        ticket_id = str(uuid.uuid4())
        try:
            process_ticket(ticket_id, ticket_obj)
            succeeded += 1
        except Exception as e:
            print(f"There was an error processing this ticket: {e}")
            failed += 1

    return {"fetched": len(ticket_list), "succeeded": succeeded, "failed": failed, "skipped_parsing": skipped_parsing}