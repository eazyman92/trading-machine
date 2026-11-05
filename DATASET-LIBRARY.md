# Persistent historical research datasets

Implemented 5 November 2026. Private development use only; the app remains unauthenticated. Real data must be supplied under verified permission. Registration validates format and records claims; it does not validate the market itself.

## Register and run

1. Choose a permitted normalized CSV in the XAU/USD form. Large files may contain up to 200,000 candles and 20 MB of UTF-8 text.
2. Enter the actual source/period/product in provenance, permission/terms reference in the library section, and confirm permission. Contract/cost settings must be evidenced for the intended product.
3. Click **Register selected CSV**. The server validates data and stores it by SHA-256; registration does not run a backtest. If the same bytes are registered again, the first recorded source declaration remains.
4. The **Saved dataset** dropdown selects the registered file. Use **Refresh dataset library** after returning to the page. The library lists the 100 most recently registered manifests.
5. Choose optional London-session dates and use **Preview dataset quality**, then **Run XAU/USD replay**. Jobs store a dataset reference, not the full CSV. Direct unregistered uploads retain the earlier 3,000-row / 500 KB restriction.
6. Progress shows validation/replay phase and session count. A completed run replaces progress with the report. The worker renews its lease every 10 seconds and on session callbacks; cancellation prevents publishing a late result. Parsing/calculation between callbacks is not immediately interruptible.

For at least ten complete weekday sessions, **Create chronological split plan** calculates development/validation/holdout periods in chronological 60/20/20 proportions. It displays boundaries and a deterministic plan hash. Save these before evaluating variants. This is a reproducible plan, not an automatic optimization service, locked holdout or proof of statistical adequacy. Ten sessions are a software minimum, not enough evidence for deploying a strategy.

## Persistence and deployment

Compose mounts `research-datasets` at `/data/datasets` in API and worker. The image creates the directory for UID 10001. PostgreSQL still holds job records. Dataset files use temporary writes and content hashes; reads reject corrupted contents. Back up BOTH dataset volume and database; a database backup alone cannot restore referenced history. Do not delete either volume.

Local Python uses `output/datasets` unless `DATASET_DIR` is set. Dataset contents are excluded from Git by the existing output ignore. No Postgres schema migration is required for this increment; progress is transient job-result JSON while the job is running.

```bash
# EC2, after local commit/push:
git pull --ff-only
docker compose up --build -d --wait
docker compose restart web
```

Retain the existing EC2 loopback port mapping and tunnel. There is a new dataset volume, so rebuilding/recreating API and worker is necessary. Web restart loads the 24 MB nginx request limit. Hard-refresh for frontend asset version `dataset-library-7`.

## Verification and limitations

Thirty Python tests pass, including a 5,410-candle stored dataset through API/worker, integrity tampering, stable provenance, chronological periods, and cancellation/expired-lease heartbeat rejection. JavaScript syntax and shared-volume YAML checks pass. Container runtime/PostgreSQL, large maximum-bound stress and new browser-library interactions remain unverified locally.

Bounded in-memory CSV parsing is still used within workers; 200,000 candles is a safety bound, not a measured performance guarantee. No full tick replay, qualified historical sample, margin/financing model, provider downloader, automatic strategy promotion or live execution is added. See research/DATA-QUALIFICATION.md for the external data dependency.
