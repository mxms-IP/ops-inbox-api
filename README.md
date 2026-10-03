# OpsInboxAPI

A FastAPI service that ingests support tickets (via webhook or a real Gmail
inbox), classifies them, generates draft replies, and routes them through a
human-approval step before sending. 

## Running locally

```bash
git clone <repo-url>
cd ops-inbox-api
python -m venv venv
source venv/bin/activate   # venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env       # fill in real values
uvicorn app.main:app --reload
```

## Running via Docker

```bash
docker build -t opsinboxapi .
docker run -p 8000:8000 --env-file .env opsinboxapi
```

## Environment variables

See `.env.example`. Required: `OPS_INBOX_API_KEY` (auth), `GMAIL_ADDRESS` +
`GMAIL_APP_PASSWORD` (IMAP ingestion + SMTP sending, via a Google App
Password, not the account password). Optional: `GEMINI_API_KEY` +
`CLASSIFIER_BACKEND=llm` (defaults to `rule` — the system works fully
without any LLM key set).

## API

All endpoints except `/health` require an `X-API-Key` header.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | liveness check |
| POST | `/api/v1/inbox/webhook` | submit a ticket for triage (rate-limited, 5/min) |
| POST | `/api/v1/ingest/poll-now` | manually trigger an IMAP poll of a real Gmail inbox |
| GET | `/api/v1/tickets` | debug: list all stored tickets |
| GET | `/api/v1/drafts/pending` | tickets awaiting approval, each with its stored draft |
| POST | `/api/v1/drafts/{ticket_id}/approve` | send the draft to the original sender and mark it sent |

### Example

```bash
curl -X POST http://127.0.0.1:8000/api/v1/inbox/webhook \
  -H "Content-Type: application/json" \
  -H "X-API-Key: devkey" \
  -d '{"sender":"a@b.com","subject":"Site is down","body":"critical, ASAP"}'
```

## Architecture

```
inbound ticket (webhook JSON, or a real email via IMAP poll)
        -> validate (Pydantic)
        -> classify (rule-based, or LLM with automatic fallback)
        -> extract entities (company, ticket reference)
        -> generate draft reply (Jinja2 template, stored once at creation)
        -> save (SQLite via SQLAlchemy)
        -> surface to a human via GET /drafts/pending
        -> human approves -> POST /approve
        -> send real email via SMTP -> only then mark status "sent"
```

## Design notes

**Instant-ack + background processing.** The webhook returns `202` in
milliseconds via `BackgroundTasks`, regardless of how long classification
and storage take. A blocking call placed directly in the route body (instead
of the background task) would freeze request handling for every caller, not
just its own — verified directly during development with a controlled
concurrency test (plain `def` routes run in a threadpool; a blocking call
inside `async def` has no such cushion and serializes every request on the
single event loop).

**Two swappable-backend seams, same pattern applied twice.** Storage started
as flat CSV (`app/storage/csv_store.py`) and was swapped for SQLite/SQLAlchemy
(`app/storage/db.py`) with zero changes to any caller — the swap is a single
import line in `app/storage/__init__.py`. `csv_store.py` is kept in the repo,
unused, as evidence the seam actually works. Classification follows the same
shape: `classify()` is a dispatcher that calls an LLM-backed classifier and
falls back to deterministic keyword matching on *any* failure (network error,
timeout, malformed JSON from the model, out-of-range confidence value) —
chosen specifically so the service never goes down because a third-party API
did.

**Why rule-based classification by default, not LLM-only.** Keyword matching
is free, instant, and fully deterministic, appropriate as the default for a
service that shouldn't have a hard external dependency to function at all.
The LLM path is an enhancement, not a requirement, and is demonstrably more
accurate on nuanced/real-world text (see the Gemini vs. rule-based comparison
below). But it costs latency, money, and introduces a failure mode the
system has to actively guard against, which is why the fallback exists rather
than letting a classification request simply fail.

**Real email ingestion via IMAP polling, not Gmail API push (Pub/Sub).** A
deliberate scope decision: push notifications require a verified domain,
Google Cloud Pub/Sub setup, and a publicly reachable HTTPS endpoint, real
infrastructure unrelated to the FastAPI/automation skills this project is
meant to demonstrate. IMAP polling still authenticates against a live mail
server and parses genuinely messy real-world MIME (multipart text/HTML,
encoded headers, malformed senders) rather than synthetic JSON. Verified
against real inbound email, including a deliberately malformed `From` header
injected via IMAP `APPEND` to confirm one bad message doesn't take down a
batch poll.

**Rate limiting on the webhook specifically, keyed by IP.** Capped at
5/minute to stay well under Gemini's free-tier ceiling (~15 req/min) and to
protect against retry storms. IP-based keying was chosen for simplicity;
an API-key-based key function would be more correct for an authenticated
API (two legitimate callers behind the same IP shouldn't throttle each
other) and is a natural next improvement.

**No DB migrations (Alembic).** `init_db()` uses SQLAlchemy's `create_all`,
which creates missing tables but never alters existing ones — adding the
`draft` column during development required dropping the dev database
entirely. Acceptable for a project at this stage; a real production system
would use Alembic so schema changes don't require data loss.

## Known limitations

- `approve_draft` is not atomic across the send + persist steps (see above)
- Background task failures in the webhook path are logged, not recovered
- No DB migration tooling — schema changes currently require recreating the database
- Rate limiting is IP-keyed, not API-key-keyed
- `test_drafts.py` and full auth-edge-case coverage are not yet complete — see Tests

## Tests

```bash
pytest -v
```

Classifier and webhook tests (status codes, response shape, the <1s instant-ack
timing property, and auth rejection) are complete and passing. Draft/approval
endpoint tests are not yet written.

