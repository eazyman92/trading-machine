# XAU/USD research import

Status: first bounded CSV import and gold-specific sizing implementation, 5 November 2026. No historical data provider, broker product or live gold contract has been selected or qualified. User-declared settings are research assumptions, not verified broker specifications. Never replace EUR/USD symbol text and reuse its unit sizing for gold.

## Use the dashboard

Research lab now includes **XAU/USD historical CSV research**. Choose a CSV, describe the source/period/rights and gold product, confirm permission to use it, and enter all contract/cost settings. No default contract values are silently assumed. Submit to the background worker; results are saved and reopenable through history.

Required header (exact order):

```csv
time,bid_open,bid_high,bid_low,bid_close,spread
2026-03-27T07:00:00+00:00,2000.00,2000.01,1999.99,2000.00,0.20
```

The row above is an artificial formatting example, not sufficient data for a backtest. Each timestamp is a UTC minute **open**. `spread` is a declared constant ask-minus-bid USD/oz offset throughout that candle, not an observed separate ask OHLC stream. Do not import bid-only/midpoint data and invent a spread without labeling the assumption. Real spread variation within a candle is not captured.

The importer rejects duplicate/unordered times, naive/non-UTC or non-minute timestamps, nonfinite/nonpositive values and invalid OHLC. Maximum 3,000 rows / 500 KB per run. Missing minutes cause the affected London session to be excluded, never silently forward-filled. The baseline needs every minute from 07:00 through the 16:00 bar open, groups by Europe/London with DST, and skips weekends. This is an offline completeness filter, not a live decision rule. Inputs outside those session windows do not generate signals. No exchange/broker holiday calendar is modeled.

## Explicit contract model

- USD account and USD per troy-ounce prices; linear gold spot/CFD-style research model only, not futures or ETFs.
- Troy ounces per lot, lot increment and minimum lots must be supplied for the exact intended product. The minimum must be a multiple of the increment.
- Round lots down to both the estimated stop-risk budget and notional cap. Include one adverse exit tick plus both sides of commission in the loss estimate. Do not round up to minimum size.
- Entry is next candle's ask for a buy or bid for a sell, plus one adverse tick. Stop/target triggers use the appropriate executable quote side. Ambiguous candles use stop-first; gaps can exceed the risk budget.
- Midpoint range 07:00–08:00 London; five-tick breakout buffer; two-times entry-to-stop price distance target; one trade/session; close at 16:00. These are unoptimized baseline rules, not a gold recommendation.
- Fees are USD/lot/side. Spread is included in executable prices; it is not charged again as a separate fee. No broker margin, minimum commission, financing, intratrade equity drawdown or cross-currency conversion model.

Results show quantity in lots and ounces, after-cost net USD, total commission, trade count, win rate and **closed-trade** drawdown in USD. The latter understates intratrade risk and must not be labeled full equity drawdown. The report retains the CSV SHA-256, source declaration, complete contract settings and caveats. Reports remain `user_supplied_unverified` even if declared provenance sounds authoritative.

## Try the importer without purchasing data

```bash
python scripts/generate_gold_sample.py
```

Upload `output/gold-synthetic-import.csv`. State “Generated synthetic gold import fixture; not historical market data” in provenance. Illustrative test settings only: tick `0.01`, ounces/lot `100`, lot step `0.01`, minimum `0.01`, commission `7`, risk budget `25`, notional cap `10000`. These invented settings do not describe or recommend any broker. Replace all of them with evidenced product terms before meaningful market research.

## Deploy to EC2

## Dataset preview, selected periods and comparison

Use **Preview dataset quality** after selecting a file. The report shows total/selected rows, UTC coverage, spread bounds and complete/incomplete London sessions. Invalid duplicate, unordered, malformed or non-UTC input is rejected rather than repaired. Dates are inclusive Europe/London session dates, not UTC calendar boundaries; start/end fields are optional. A date range without candles is rejected. Date selection does not make an incomplete session eligible.

New results retain `data_quality` and `closed_trade_curve`. Charts show cumulative realized net P&L and drawdown at trade closes, starting at zero; the horizontal axis is trade index. They are not full equity curves or mark-to-market risk measurements. Older reports remain unchanged; rerun them to obtain chart/quality metadata.

**Compare saved gold runs** uses completed jobs from the current history page. It requires the exact same uploaded CSV hash and selected date range, exposes strategy versions and all changed contract/cost/risk inputs, and reports the candidate-minus-baseline net result. Changed sizing/cost settings confound any strategy comparison. Only the current breakout strategy is implemented; comparing two configurations does not create another strategy or constitute walk-forward/holdout validation.

New API routes: `POST /api/v1/research/gold/validate` and `GET /api/v1/research/comparison?left=UUID&right=UUID`. Preview requires CSV text plus optional ISO start/end dates. No changes to existing database schema are needed; configuration and quality metadata are stored with each new job.

The 3,000-row / 500 KB limit remains. File-backed long-history storage, worker heartbeats/progress and licensed feed qualification are separate outstanding work; this release does not claim large historical research is ready. Validation cannot establish source authenticity, licensing or market accuracy. Browser interaction verification remains pending; 22 local Python tests and frontend syntax checks pass.

After committing/pushing locally:

```bash
git pull --ff-only
docker compose up --build -d --wait
docker compose restart web
```

The web restart reloads the increased nginx request limit. Retain your EC2 port mapping and SSH tunnel; hard-refresh the browser for the new script. Existing EUR/USD synthetic jobs and smoke tests stay supported. Historical dataset licensing/qualification and a real gold strategy evaluation remain outstanding.
