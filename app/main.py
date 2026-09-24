from fastapi import Depends, FastAPI
from app.api.webhook import router as webhook_router
from app.storage import init_db
from contextlib import asynccontextmanager
from app.api.tickets import router as tickets_router
from app.api.drafts import router as drafts_router
from app.auth import verify_api_key

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    
    yield  
  
    print("Shutting down application...")

app = FastAPI(lifespan=lifespan)
app.include_router(webhook_router, dependencies=[Depends(verify_api_key)])
app.include_router(tickets_router, dependencies=[Depends(verify_api_key)])
app.include_router(drafts_router, dependencies=[Depends(verify_api_key)])


@app.get("/health")
def health():
    return {"status": "ok"}
