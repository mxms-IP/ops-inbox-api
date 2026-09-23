from fastapi import FastAPI
from app.api.webhook import router as webhook_router
from app.storage import init_db,get_all_tickets
from contextlib import asynccontextmanager
from app.api.tickets import router as tickets_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing database")
    init_db()
    
    yield  
    
  
    print("Shutting down application...")

app = FastAPI(lifespan=lifespan)
app.include_router(webhook_router)
app.include_router(tickets_router)


@app.get("/health")
def health():
    return {"status": "ok"}
