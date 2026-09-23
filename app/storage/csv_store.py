import pandas as pd
from pathlib import Path
from app.models.schema import TicketOut
import os

FILENAME   = "tickets.csv"
DATA_PATH = Path("data") / FILENAME 


def append_ticket(ticket: TicketOut) -> None:
    """
    Append one row to data/tickets.csv via pandas.
    If the file doesn't exist yet, create it with headers first.
    """

    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)

    write_header = not DATA_PATH.exists()

    new_data = pd.DataFrame([ticket.model_dump()])
    new_data.to_csv(DATA_PATH, mode="a", index=False, header=write_header)

    pass

def read_all_tickets() -> list[TicketOut]:
    """
    Read data/tickets.csv back into a list of TicketOut objects.
    If the file doesn't exist, return an empty list.
    """
    
    if not DATA_PATH.exists():
        return []
        
    df = pd.read_csv(DATA_PATH)
    
    
    return [TicketOut(**row) for row in df.to_dict(orient="records")]

