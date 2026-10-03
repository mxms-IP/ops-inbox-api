# OpsInboxAPI

An inbox that reads itself, figures out what each message needs, writes the first draft of a reply, and waits for a person to say go.

A FastAPI service that triages support tickets (webhook or a real Gmail inbox), classifies them, drafts a reply, and routes everything through a human approval step before anything gets sent. No AI/LLM dependency required, rule-based classification is the default and the system runs fully without it. An LLM backend (Gemini) is available as a swap-in upgrade with automatic fallback if it fails.

## Quickstart

```bash
git clone <repo-url> && cd ops-inbox-api
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in real values
uvicorn app.main:app --reload
```

Docker image is written but not build-tested locally (no disk space for Docker on the dev machine) — validate via CI or another machine before trusting it.

## API

All routes but `/health` need an `X-API-Key` header.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | liveness check |
| POST | `/api/v1/inbox/webhook` | submit a ticket (rate-limited, 5/min) |
| POST | `/api/v1/ingest/poll-now` | pull unread email from a real Gmail inbox |
| GET | `/api/v1/tickets` | debug: list everything stored |
| GET | `/api/v1/drafts/pending` | tickets waiting on a human, with their draft |
| POST | `/api/v1/drafts/{ticket_id}/approve` | send the draft, mark it sent |

```bash
curl -X POST http://127.0.0.1:8000/api/v1/inbox/webhook \
  -H "X-API-Key: devkey" -H "Content-Type: application/json" \
  -d '{"sender":"a@b.com","subject":"Site is down","body":"critical, ASAP"}'
```

## Flow

webhook JSON **or** a real inbound email → validate → classify → extract entities → draft a reply → store → human reviews → approve → real email sent, *then* marked sent.

## Decisions worth knowing about

**Webhook responds in milliseconds, work happens after.** `BackgroundTasks` does the classifying/storing/drafting *after* the `202` goes out. Proved this matters with a real concurrency test — a blocking call left inside the route body freezes every other request, not just its own.

**Two things are swappable by design.** Storage went CSV → SQLite with a one-line import change and zero edits anywhere else. Classification works the same way: an LLM call with a hard-coded fallback to keyword matching on any failure — bad JSON, timeout, network error, doesn't matter. `csv_store.py` is still in the repo, unused, as proof the seam actually works.

**Rules by default, LLM as upgrade.** Free, instant, zero external dependency to function at all. The LLM path is demonstrably better on messy real text, but it's a bonus, not a requirement — see the comparison below.

**Real inbox via IMAP polling, not Gmail Pub/Sub push.** Push notifications need a verified domain and a public HTTPS endpoint — real infra, not really a FastAPI lesson. Polling still means real auth against a live mail server and real MIME parsing (multipart, encoded headers, a deliberately malformed sender injected via IMAP `APPEND` to prove one bad email doesn't kill a batch).

**Send before marking sent, not after.** If it marked "sent" first and the email failed, the ticket would lie. Trade-off: a DB write failing *after* a successful send leaves it stuck "pending" — a human could resend it by accident. Flagged as a distinct `500` with a do-not-retry warning rather than hidden. A real fix needs an outbox pattern; out of scope here, but named instead of ignored.

**Background task failures are logged, not recovered.** Once the `202` ships there's no response left to carry a later failure back — it's caught and printed, and the ticket is lost. Production version: a retry queue, not a print statement.

**No DB migrations.** `create_all()` only makes new tables, never alters old ones — adding the `draft` column meant wiping the dev DB. Alembic is the real answer; skipped here deliberately.

## Known gaps, named on purpose

- Approve-and-send isn't fully atomic (see above)
- Lost background-task failures aren't recoverable, just logged
- No migration tooling
- Rate limit is per-IP, not per-API-key
- `test_drafts.py` isn't written yet

## Tests

```bash
pytest -v
```

