# Paired bid/ask tick replay

Backend-only research feature. No API, UI, broker or live order path is added. This engine is separate from the dashboard's approximate candle replay.

## Local Git Bash test

Input: actual downloaded provider ticks at `output/market-data/xauusd-2024-01-15/ticks.csv`, covering **15 January 2024, 07:00–16:59 UTC**. This file is ignored by Git. If missing, follow MARKET-DATA-ADAPTER.md to acquire it first; do not substitute the synthetic candle CSV.

Configuration: `contracts/gold-tick-replay.example.json`. Its lot size, commission, risk and notional limits are invented engineering test inputs, not confirmed broker terms. Review this file before running another product/dataset.

```bash
cd /c/Users/tijan/OneDrive/Documents/ChatGPT/trading-machine
python scripts/replay_xau_ticks.py --config contracts/gold-tick-replay.example.json
```

Expected CLI output: `reproduced_identically`, **47580** ticks, **1** trade. The command executes the engine twice and checks full report equality before saving:

```text
output/tick-replay/report.json
```

Open that JSON in an editor. Inspect `ledger` for signal, fill, rejection and exit events, `trades` for prices/fees/risk, and `input_sha256` against the acquisition manifest's `tick_sha256`. No upload or EC2 update is needed for this local check. No dashboard result is expected from this CLI-only feature.

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q
```

Regression cases exercise candle completion, next executable quote, long bid/short ask exits, fees and sizing, quote gaps exceeding the risk estimate, spread rejection, equal-time source ordering, minimum size, missing session data, invalid UTC/quotes, already-crossed protection and session closure.

## Exact modeled behavior

- Group quotes into Europe/London research sessions. Offline eligibility requires every minute from 07:00 through 16:00 to contain a quote, with weekends excluded. This future coverage filter is a research-quality rule, not a live trading decision. Long intra-minute gaps remain possible.
- Form the range from observed midpoint ticks during 07:00–08:00 London. Signal on the last observed midpoint of a completed minute during 08:00–10:00. Evaluate once on the first quote in the immediately following minute. If spread exceeds the limit, reject that signal; do not wait within the minute for a better quote.
- Fill buys at actual ask plus adverse slippage; sells at actual bid minus slippage. Round lots down to risk/notional constraints; reject below minimum. Prices use USD/oz and explicit ounces/lot. Stop prices round outward to the configured tick; targets round outward as well. Already-crossed stop levels at entry are rejected.
- Exit a long against observed bid, a short against observed ask, with adverse slippage. Stops/targets use the first observed quote reaching the trigger, including gap prices. A target is market-on-touch, not a guaranteed limit fill. Protection triggers take precedence over session closing at the same quote. Otherwise use the first quote at/after 16:00.
- At most one accepted entry per instrument/session. Equal timestamps preserve file sequence; no invented within-timestamp ordering or same-candle high/low path. Exits follow entry in source sequence, never precede it. Same-timestamp sequence can affect results, and no latency is modeled.
- Ledger fees are round-trip commission; spread is reflected in executable bid/ask, not charged again. Drawdown is realized at trade closes only. Stop estimates are not guaranteed loss caps.

No market depth, volume-based fills, latency, margin, partial fills, financing, portfolio exposure or broker order restrictions are modeled. One session cannot establish statistical effectiveness. Source scale and rights remain subject to MARKET-DATA-ADAPTER.md qualification limits. The acquisition sample is provider data; the execution settings are still fixtures.
