from app.ingestion.imap_poller import fetch_unread_emails


tickets = fetch_unread_emails()
for t in tickets:
    print(t)