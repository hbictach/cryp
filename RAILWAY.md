# Railway deployment notes

This repository has two long-running processes. On Railway, run them as two
separate services from the same GitHub repository so each service has its own
start command.

## 1. PostgreSQL

Add a Railway PostgreSQL service and set this variable on both app services:

```text
DATABASE_URL=${{Postgres.DATABASE_URL}}
```

## 2. Web service

Use this start command:

```bash
gunicorn wsgi:app --bind 0.0.0.0:$PORT
```

Set the Railway healthcheck path to:

```text
/health
```

Railway injects `PORT`, and the command above makes Gunicorn listen on that
port.

## 3. Worker service

Create a second Railway service from the same repository with this start
command:

```bash
python worker.py
```

Do not enable public networking or an HTTP healthcheck for the worker service.
The worker retries when the database is not ready and uses `WORKER_SLEEP_SECONDS`
for the polling interval. The default is `60`; values below `10` are clamped to
`10`.

## 4. Optional Telegram alerts

Set these variables only if Telegram alerts are enabled:

```text
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```
