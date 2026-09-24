import os
from typing import Optional
from fastapi import Header, HTTPException, status
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.environ.get("OPS_INBOX_API_KEY", "@key@123")

def verify_api_key(x_api_key: Optional[str] = Header(...)):
    """
    Read the X-API-Key request header (FastAPI auto-converts the
    hyphenated header name to the x_api_key parameter name).
    Compare it against the OPS_INBOX_API_KEY environment variable.
    Raise HTTPException(401) if they don't match.
    """
    if not (API_KEY == x_api_key):
        raise HTTPException(status_code=401, detail="Not Allowed")

    pass