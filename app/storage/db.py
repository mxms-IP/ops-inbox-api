from sqlalchemy import create_engine, Column, String, Float, DateTime, JSON, select
from sqlalchemy.orm import declarative_base, sessionmaker
from app.models.schema import TicketOut

engine = create_engine("sqlite:///data/tickets.db")
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class TicketORM(Base):
    __tablename__ = "tickets"
    ticket_id = Column(String, primary_key=True)
    sender = Column(String)
    subject = Column(String)
    category = Column(String)
    confidence = Column(Float)
    entities = Column(JSON)
    status = Column(String)
    received_at = Column(DateTime)

def init_db() -> None:
    """Create all tables if they don't exist yet."""
    Base.metadata.create_all(engine)
    pass

def save_ticket(ticket: TicketOut) -> None:
    """
    Open a session, convert the TicketOut into a TicketORM,
    add it, commit, close.
    """
    
    with SessionLocal() as session:

        row= TicketORM(**ticket.model_dump())

        session.add(row)

        session.commit()


    pass

def get_all_tickets() -> list[TicketOut]:
    """
    Open a session, query all TicketORM rows,
    convert each back into a TicketOut, return the list.
    """
    stmt= select(TicketORM)
    with SessionLocal() as session:

        db_tickets = session.scalars(stmt).all()

    return [TicketOut.model_validate(ticket) for ticket in db_tickets ]

def get_ticket(ticket_id: str) -> TicketOut | None:
    """
    Query a single row by primary key.
    Return None if it doesn't exist.
    """

    stmt = select(TicketORM).where(TicketORM.ticket_id == ticket_id)

    with SessionLocal() as session:
        row = session.scalars(stmt).first()

        return TicketOut.model_validate(row) if row else None