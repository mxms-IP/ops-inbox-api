from fastapi import APIRouter
from app.storage import get_all_tickets

router = APIRouter()

@router.get("/api/v1/tickets")
def list_tickets():
    return get_all_tickets()