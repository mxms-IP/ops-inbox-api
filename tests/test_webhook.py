import time
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.environ.get("OPS_INBOX_API_KEY", "@key@123")

HEADERS = {"x-api-key": API_KEY}   

@pytest.mark.asyncio
async def test_webhook_returns_202_instantly():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        start = time.time()
        response = await client.post(
            "/api/v1/inbox/webhook",
            json={"sender": "a@b.com", "subject": "test", "body": "test"},
            headers=HEADERS,
        )
        elapsed = time.time() - start

        assert response.status_code == 202
        assert "ticket_id" in response.json()
        assert elapsed < 1.0   # background stub sleeps ~1s; the request itself must not

@pytest.mark.asyncio
async def test_webhook_rejects_missing_api_key():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/inbox/webhook",
            json={"sender": "a@b.com", "subject": "test", "body": "test"},
        )
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_webhook_rejects_wrong_api_key():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/inbox/webhook",
            json={"sender": "a@b.com", "subject": "test", "body": "test"},
            headers={"x-api-key": "wrong_key"},
        )
        assert response.status_code == 401