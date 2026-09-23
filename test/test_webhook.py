import time
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_webhook_returns_202_instantly():
    # 1. Initialize the app inside the ASGITransport
    transport = ASGITransport(app=app)
    
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Record start time
        start = time.time()
        
        # 2. Await the POST request using relative path
        response = await client.post(
            "/api/v1/inbox/webhook",
            json={"sender": "test@gmail.com", "subject": "test", "body": "test"}
        )
        
        # Record end time
        end = time.time()
        duration = end - start
        
        # 4. Assert status code is 202 (Accepted for background processing)
        assert response.status_code == 202
        
        # 5. Extract JSON data and assert key exists
        data = response.json()
        assert "ticket_id" in data
        
        # 6. Assert it returned instantly (e.g., in under 50 milliseconds)
        # Change 0.05 to match whatever your background task's sleep duration is
        assert duration < 0.05, f"Webhook took too long: {duration} seconds"
