# First working research slice

This is a local, paper-only engineering baseline. The existing web prototype still uses sample data; it is not connected to this replay. No broker, production account, LLM, or historical-data feed is connected.

Update 4 November 2026: the new Research lab screen now connects to this replay through a Python API and separate worker. Other web screens still use sample data. Container setup, local fallback and the current 13-test verification record are in DEVELOPMENT.md.

Run with Python 3.10+:

```powershell
python -m pip install --target .local-deps tzdata==2025.2
python run_replay.py
python -m pytest -q
```

If unrelated globally installed pytest plugins slow startup, set `$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'` before the test command. Verification: eight tests pass, covering DST and entry timing, missing/duplicate/out-of-order data, invalid prices, sizing/costs, gap losses, short-side spread, target/session exits and 17 shared contract vectors. This verifies fixture behavior, not strategy profitability.

The replay writes inspectable synthetic candles and a report under `output/replay/`. Its two sessions span the London daylight-saving change. Fixture losses are intentional test scenarios, not historical strategy results.

## Explicit baseline

Independently authored session breakout, not a port of an upstream strategy. One-minute candles have UTC open timestamps and a fixed intra-candle spread. The midpoint range forms from 07:00 inclusive to 08:00 exclusive Europe/London. Completed candles from 08:00 through 09:59 may signal a close more than five ticks outside that range. Execution uses the following candle's bid/ask open plus one adverse tick. One entry per instrument/session; opposite range edge stop and twice the entry-to-stop price distance target. Remaining positions close at the 16:00 open.

When stop and target both occur in a candle, the stop wins. Gaps fill at the executable open with adverse slippage. Target behavior is market-on-touch, not a guaranteed limit fill. Stop gaps can exceed the configured loss budget. A session missing any expected minute from 07:00 to 16:00 is excluded; this completeness check is an offline data-quality gate, not a live decision rule. No future price is used to compute an entry.

Sizing uses Decimal, whole base units rounded down, a $25 fixture budget, $10,000 notional cap and 10,000-unit cap. Both currencies quoted into a USD fixture account only. Fees are invented $35/million base units/side, with no minimum commission. No overnight holdings, financing model, holidays, cross-currency conversion, JPY, oil, gold, futures, partial fills or real broker contract specifications are supported. These inputs must be replaced and qualified before market evaluation.

## Shared paper risk boundary

`src/tradinglab/contracts.py` and `execution/src/main.rs` implement the same restricted fixture policy. Contract version 1 uses positive integer price ticks (1e-5 USD), whole base units and UTC epoch milliseconds. Risk calculations use integer microUSD. Unknown fields, unsupported symbols, live mode, invalid geometry, stale/future quotes, expired intents and limits fail closed. The trusted limits are local constants, not request-controlled inputs. `contracts/vectors.json` supplies shared acceptance/rejection cases.

With Rust installed:

```powershell
cargo test --manifest-path execution/Cargo.toml
```

Local verification limitation (updated 4 November 2026): disk space is available again (approximately 30 GB at verification). Retried the stable MSVC compiler download and the Windows GNU toolchain, since Microsoft linker/SDK prerequisites are absent. Downloads stopped showing progress and were interrupted; neither compiler installation completed. The Rust source is uncompiled and its tests have not run. All eight Python tests pass independently; Rust parity is not established until the shared-vector test passes in both languages.

The Rust CLI reads one intent JSON from standard input and takes the evaluation epoch milliseconds as its only argument. Its output always includes `submitted: false`. It has no network or broker submission capability. It does not provide account authorization, persistent reservations, idempotency, portfolio aggregation, daily loss controls or order reconciliation; those remain required before any actual execution service.

## Next integration gate

Qualify a Nigeria-compatible broker demo and licensed historical bid/ask data. Evaluate the baseline on time-separated real datasets with recorded costs, unsuccessful variants and holdout results. Then connect the web research view to a backend, implement durable account-isolated paper order lifecycles and exercise reconnect/reconciliation failures. AI proposals must pass these same research gates before promotion.
