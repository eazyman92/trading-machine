# Containerized research development

This is a local, unauthenticated research stack. It runs synthetic fixtures only. No broker, LLM, live trading or historical feed is connected. Other dashboard screens remain sample-data prototypes. Only Research lab is backend-connected.

## Docker Compose

Install/start Docker with Compose v2, copy `.env.example` to `.env`, and set `POSTGRES_PASSWORD` to a random URL-safe development password. Do not commit `.env`.

```bash
docker compose config --quiet
docker compose up --build
```

Open http://127.0.0.1:4173/#research and select **Run synthetic backtest**. The API creates a durable queued job; the separate worker claims it and writes a reproducible report. The browser polls for status and renders worker trades, costs, exclusions and dataset hash.

Services: nginx web/reverse proxy, Python API, Python research worker, one-shot schema initializer and PostgreSQL. Only the web port is published, on loopback. The database lives in the named `research-db` volume. `docker compose down` stops services without deleting that volume; do not use `down -v` unless deliberately discarding the research database. The password must remain consistent with an existing initialized volume.

Static web changes are visible on refresh; API code uses a read-only source mount and reload. Restart the worker after Python changes (`docker compose restart worker`). Dependency changes require a rebuild. Schema changes must use a new explicit migration; the current initializer only establishes schema 001 and is idempotent for that schema, not a general migration framework.

Health checks gate startup on database/schema/API readiness. The worker polls the database queue; `docker compose logs -f api worker` shows service activity. No extra Redis service is necessary for this bounded first slice.

## Local fallback and checks

Without Docker, use Python 3.10+:

```bash
python -m pip install --target .local-deps -r requirements-dev.txt
python dev.py
```

If the PostgreSQL binary wheel is unavailable for your local Windows Python, install only `fastapi`, `pydantic`, `uvicorn`, `httpx` and `tzdata` at the versions in the requirements files for SQLite development. PostgreSQL remains mandatory in Compose.

This starts the same API and worker using SQLite at `output/research.db` and serves the same web files on port 4173. Stop with Ctrl+C. In Git Bash, use `PORT=4174 python dev.py` if 4173 is occupied. SQLite checks do not establish PostgreSQL correctness or container readiness.

Verification on 4 November 2026: 13 Python tests passed using SQLite and the installed FastAPI 0.128.8/Pydantic 2.12.5 environment, with local Uvicorn 0.34.2. The pinned container dependency set has not been installed/tested end to end. JavaScript syntax checks pass. Docker/Compose is absent on this machine, so image builds, PostgreSQL queue concurrency and container startup remain unverified. Windows sandbox restrictions required permission to run event-loop socket tests and the loopback server outside the sandbox.

```bash
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
python -m pytest -q
node --check prototype/dist/app.js
node --check prototype/dist/research.js
```

## API contract

The schema is available at `/api/v1/openapi.json` and interactive documentation at `/api/v1/docs`. The browser uses these versioned routes:

- `GET /api/v1/health`: database readiness, 503 if unavailable.
- `POST /api/v1/research/jobs`: JSON configuration, UUID `Idempotency-Key` header, 202 response with job ID/status. Same key/config returns the same job; a conflicting config returns 409.
- `GET /api/v1/research/jobs/{uuid}`: status, configuration and completed result; 404 if absent.
- `GET /api/v1/research/jobs?limit=20&offset=0`: newest-first saved summaries, up to 100 per page, with `next_offset`; full results are fetched separately. History uses offset pagination for this small development workspace and can shift if new jobs arrive between pages.
- `POST /api/v1/research/jobs/{uuid}/cancel`: cancels queued/running work logically. Completed/failed/cancelled states remain unchanged. It does not stop a currently executing CPU calculation; its result is discarded if cancellation wins the state transition.

Only `synthetic-london-dst-v1`, `session-breakout-v0.1` and `EUR_USD` are accepted. Extra fields are rejected. Terminal states are completed, failed and cancelled. A claimed job has a 60-second lease; another worker poll marks an expired run failed. This bounded fixture finishes well inside that lease. Longer research needs heartbeat/lease ownership and workload isolation before support is enabled.

Gold import uses the separate `POST /api/v1/research/gold/jobs` endpoint, with a UUID idempotency key, CSV text, provenance, rights confirmation and explicit gold contract settings. Its bounded reports share the same history/status endpoints. See GOLD-RESEARCH.md for supported assumptions and limits. Verification updated 5 November: 17 Python tests pass locally; interactive browser verification of the new gold form is pending.

## Before production or Kubernetes

This Compose file is for development: reload and source mounts are intentional. It is not a production deployment. Add identity/account authorization, access controls, job quotas, request limits, migration version tracking, complete dependency locking/image digests, dependency vulnerability checks, production image delivery, encrypted secret injection, backups/restoration, monitoring and PostgreSQL integration/soak checks. The bootstrap PostgreSQL role is not the final least-privilege application role. Public hosting must wait for those controls.

Service boundaries and environment-driven database configuration allow later deployment changes. Kubernetes would require manifests, probes, secret/storage provisioning and operational ownership; it is not an automatic conversion from Compose. Rust remains outside this stack until its compilation and paper execution workstream is ready.
