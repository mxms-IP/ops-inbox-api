KEYWORD_RULES = {
    "urgent": ["asap", "down", "not working", "emergency", "critical"],
    "billing": ["invoice", "refund", "charge", "payment", "subscription"],
    "support": ["how do i", "help", "issue", "problem", "question"],
}

COMPANY_DOMAIN_MAP = {
    "acme.com": "Acme Corp",
}

import re
TICKET_ID_PATTERN = re.compile(r"#\d+|TICKET-\d+")