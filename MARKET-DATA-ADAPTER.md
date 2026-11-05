# XAU/USD history adapter: verified technical sample

Verified 5 November 2026. This increment adds backend acquisition/ingestion only, not interface changes or live trading.

## Actual sample

Source: Dukascopy's own public HTTPS hourly feed, `https://datafeed.dukascopy.com/datafeed/XAUUSD/`. Acquired 15 January 2024, 07:00–16:59 UTC: **ten raw files, 47,580 paired bid/ask ticks, 600 projected minute candles, one complete London research session**. Largest observed inter-tick gap: 19.743 seconds. Decoded minimum bid / maximum ask: 2049.290 / 2058.835 USD/oz.

The raw compressed files, true paired-tick CSV, projected candle CSV, manifest and isolated ingestion receipt are in ignored `output/market-data/xauusd-2024-01-15/`. They are actual downloaded prices, not generated fixtures. They are not committed to Git.

- Paired-tick SHA-256: `2643ecb57dc7804f45d003d7d0234272517bee935a0f38636be39c5098b57d34`
- Candle-projection SHA-256: `4238fe31d2c79fd5caf9dfe613e827916e4a8c26cd325d79c3c2aaa8d5d563ff`

Divisor **1000** is explicit configuration. Decoded prices passed a broad 5% scale sanity check against GoldPrice.org's published 2054.33 daily close for the same date. That catches gross decimal mistakes, but is NOT an exact same-timestamp provider quote comparison or verified broker contract specification.

Primary/source references:

- https://www.dukascopy.com/swiss/english/marketwatch/historical/
- https://www.dukascopy.com/wiki/en/development/data-export/
- https://goldprice.org/gold-price-today/2024-01-15

## Reproduce in Git Bash

```bash
python scripts/acquire_xau_sample.py \
  --start 2024-01-15T07:00:00+00:00 --hours 10 --price-scale 1000 \
  --reference-price 2054.33 \
  --reference-source https://goldprice.org/gold-price-today/2024-01-15 \
  --output output/market-data/xauusd-2024-01-15
```

No account, credentials or paid S3 request is used. The adapter permits at most 24 hours per invocation, uses three bounded retries/backoff, retains completed raw files and fails on missing hours. Provider 503/timeouts occurred during verification; resuming eventually obtained all ten. There is no synthetic fallback or gap fill.

Repeat the same command with `--offline` appended. It must use only cached files, detect modified bytes and reproduce the tick/candle hashes above. Preserve a separate output directory for each requested sample window; derived files are regenerated for that window.

```bash
python scripts/verify_xau_ingestion.py
```

This registers the actual projected CSV in an isolated local dataset directory/SQLite database, submits it through the existing queue/worker, and checks the completed result's dataset hash, 600 bars and zero excluded sessions. Contract/commission settings in this technical check are invented engineering fixtures, so its trading performance is NOT a strategy finding. Windows sandbox hard-link restrictions required running this check outside the sandbox.

## Checks completed

- Strict UTC hour alignment, zero-indexed URL month and hourly millisecond bounds.
- Complete 20-byte big-endian records; ordered time, positive uncrossed quotes, finite nonnegative volumes.
- Compression/response bounds and rejection of malformed/trailing streams.
- Offline cache completeness, previous raw-hash validation and deterministic normalized output.
- Wrong-scale daily-reference rejection and bounded transient-error retries.
- Actual full sample through dataset registry → queued job → worker → persisted result.
- **39 Python tests pass**, with artificial binary unit fixtures plus separate actual-download/offline checks.

## Outstanding qualification

Commercial use and redistribution permission remains unconfirmed. Public access is not a commercial data license. Exact same-timestamp provider decimal comparison, execution-broker specifications, longer representative history and independent strategy validation are still outstanding.

The paired-tick CSV retains real simultaneous bid and ask. Dashboard candles use the first observed spread held constant per minute; they are not true ask OHLC or tick-accurate fills, and first quotes may occur after minute open. Do not claim a precise trading edge from that approximation. This is a verified technical acquisition path and sample, not a production-qualified market-data service.
