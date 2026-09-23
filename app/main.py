from fastapi import FastAPI
from app.api.webhook import router as webhook_router
from app.storage.csv_store import append_ticket

app = FastAPI()
app.include_router(webhook_router)

@app.get("/health")
def health():
    return {"status": "ok"}