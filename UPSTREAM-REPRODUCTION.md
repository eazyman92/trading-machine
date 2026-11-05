# London Breakout upstream reproduction and EC2 acceptance test

Selected reference: je-suis-tm/quant-trading, `London Breakout backtest.py`, revision `611b73f2c3f577ac5b28aaa19ac8c43d3236c7a5`, Apache-2.0. Exact source, original license, SHA-256 and attribution are retained under vendor/quant_trading/. See its PROVENANCE.md. Vendored source bytes are protected from Git line-ending conversion.

## What is implemented

`src/tradinglab/upstream_london.py` reproduces the complete upstream `signal_generation` routine with independent Python-list operations. The verifier evaluates the original reviewed functions on identical data and compares **every signal, upper threshold, lower threshold and cumsum row**. This replaces neither the custom breakout nor its tick execution results; it is a distinct reproducible upstream reference.

The upstream script is not imported wholesale: hash-check then AST-select exactly the two reviewed functions. Its `os.chdir('d:/')`, file reads, plotting and main routine never run. Local fixtures prove long/short entries, excessive-breakout rejection, flat/no-entry behavior and mandatory legacy closing-hour exits. Gold observations are also compared against the original functions.

Preserved semantics: 02:00 pre-open prices, threshold setup at 03:00, entry attempts at 03:01–03:29, fixed absolute `0.01` overshoot tolerance, fixed `0.005` exit interval, exits in the source's later branches, and its cumsum quirks. Source timestamps use fixed UTC−5, not corrected London/NY daylight saving. No gold-specific threshold changes are silently introduced. The original repository provides this signal routine, not a reproducible broker portfolio, sizing/cost model or a certified performance result.

## Local Git Bash test

```bash
cd /c/Users/tijan/OneDrive/Documents/ChatGPT/trading-machine
python scripts/verify_upstream_strategy.py \
  --ticks output/market-data/xauusd-2024-01-15/ticks.csv
```

Uses the **actual 15 January 2024, 07:00–16:59 UTC tick sample** already acquired locally. The adapter supplies the last observed minute midpoint, interpreted in the source's fixed UTC−5 clock; this is an explicitly declared input adaptation, not the original FX dataset. Expected: `upstream_signal_parity_passed`; long fixture **2** signal events, short **2**, overshoot **0**, actual_gold **600 rows / 0 signals**. Zero gold signals are an upstream outcome, not a failed engine. The actual sample lacks 17:00 UTC (legacy 12:00 close), and that limitation is recorded in the report; fixtures exercise forced closing separately.

Output: `output/upstream-reproduction/report.json`. Inspect source hash/commit, all cases and `actual_gold` input hash. Every output is a signal parity check, not P&L or evidence of trading edge. No dashboard upload is needed; the UI has not been changed to label this routine as validated/live.

Local verification uses installed pandas 1.5.3. Container requirements pin pandas 2.2.3/numpy 2.2.6; their EC2 build/parity check must also pass. The pure-Python production reproduction module has no pandas dependency; pandas runs only the upstream reference checks. Verification is bounded to 5,000 rows because the source loop is quadratic. Longer evaluation requires an optimized version proven equivalent against this reference.

## Push the complete backend milestone

Check the staged summary before committing. Data under output/ remains ignored; it does NOT arrive through git pull.

```bash
git add .
git diff --cached --stat
git commit -m "Add real-data tick replay and verified upstream London Breakout reproduction"
git push
```

## EC2 acceptance: no market-file transfer needed

```bash
cd ~/trading-machine
git pull --ff-only
docker compose up --build -d --wait
docker compose run --rm --no-deps api \
  python scripts/verify_upstream_strategy.py --output /tmp/upstream-parity.json
python3 scripts/smoke_research.py --base-url http://127.0.0.1:4174
```

Retain your modified EC2 port mapping; if `git pull` reports a compose.yaml conflict, preserve the local 4174 mapping rather than discarding it. The container command should print `upstream_signal_parity_passed` for long/short/overshoot fixtures; it does not submit trades or write a real-data profitability report. The HTTP smoke test should print PASS. No browser change should be expected from this backend release.

## EC2 actual-data parity (optional additional check)

Acquire the ignored sample on the instance separately; network availability may require resuming cached files:

```bash
docker compose exec api python scripts/acquire_xau_sample.py \
  --start 2024-01-15T07:00:00+00:00 --hours 10 --price-scale 1000 \
  --reference-price 2054.33 \
  --reference-source https://goldprice.org/gold-price-today/2024-01-15 \
  --output /data/datasets/technical-xau-sample
docker compose exec api python scripts/verify_upstream_strategy.py \
  --ticks /data/datasets/technical-xau-sample/ticks.csv \
  --output /tmp/upstream-actual.json
```

Expected actual_gold **600 rows / 0 signals**, all columns matching. Data lives inside a subdirectory of the mounted dataset volume; no passwords, paid S3 requests or live orders are involved. Source commercial qualification limits remain in MARKET-DATA-ADAPTER.md. If the provider cannot deliver every hour, stop this actual-data test and report the missing file—do not switch to synthetic data while calling the result real.

## Not finished by reproduction

Gold adaptation, longer representative history, realistic broker specifications, optimized-engine equivalence, chronological development/validation/holdout results, full account risk and paper-forward trading remain outstanding. Faithfully reproducing an upstream signal routine does not reproduce a profitable gold strategy. No LLM, broker order route or live release is authorized by these checks.
