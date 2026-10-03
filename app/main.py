from fastapi import Depends, FastAPI
from app.api.webhook import router as webhook_router
from app.storage import init_db
from contextlib import asynccontextmanager
from app.auth import verify_api_key

# Router imports
from app.api.tickets import router as tickets_router
from app.api.drafts import router as drafts_router
from app.api.ingestion import router as poll_router

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded



@asynccontextmanager
async def lifespan(app: FastAPI):
    
    init_db()
    
    yield  
  
    print("Shutting down application...")

app = FastAPI(lifespan=lifespan)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(poll_router,dependencies=[Depends(verify_api_key)])
app.include_router(tickets_router, dependencies=[Depends(verify_api_key)])
app.include_router(webhook_router, dependencies=[Depends(verify_api_key)])
app.include_router(drafts_router, dependencies=[Depends(verify_api_key)])



@app.get("/health")
def health():
    return {"status": "ok"}
