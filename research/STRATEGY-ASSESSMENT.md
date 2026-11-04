# Strategy and open-source assessment

Research date: 3 November 2026. Evidence: original project documentation and pinned source snapshots. No upstream source was executed and no backtest has been run in this pass. There is no verified performance, trade-frequency estimate, or selected production strategy yet.

Priority update: see [non-crypto and AI direction](NON-CRYPTO-AND-AI-DIRECTION.md). NFI is retained as historical research and is no longer the primary adaptation candidate. Research now prioritizes pysystemtrade trend rules and a distinct FX session-breakout candidate, with equity-specific baselines. The earlier NFI discussion below records findings, not a current selection.

## What the earlier notes refer to

The strongest match is **Freqtrade**, a Python crypto bot framework, with **NostalgiaForInfinity (NFI)** as a specific strategy. The framework and a strategy are different selection decisions. Freqtrade supplies exchange integration, backtesting, optimization, and dry-run facilities. Its strategies repository describes its contents as educational starting points. Neither repository establishes that a strategy transfers profitably to forex, equities, gold, or oil. [Freqtrade](https://github.com/freqtrade/freqtrade), [strategy collection](https://github.com/freqtrade/freqtrade-strategies).

The notes also name je-suis-tm/quant-trading and Opening Range/London Breakout. Their profitability claims in the pasted discussion have not been reproduced. GitHub stars are evidence of repository attention, not a count of profitable bots or verified users.

## Source provenance

The collection script records exact commit IDs, file hashes, licenses, and retrieval time in [sources/manifest.json](sources/manifest.json). Downloaded files are research evidence, not application imports. The source branches below were inspected at the recorded revisions; they are not necessarily stable release choices. Dependencies and full environments have not been installed.

| Project | Pinned commit prefix | Declared repository license | Role / suitability |
| --- | --- | --- | --- |
| freqtrade/freqtrade | 7d9717cdf865 | GPL-3.0 | Crypto research/bot reference; not an existing universal forex/stock broker adapter |
| freqtrade/freqtrade-strategies | f3340ce11f5b | GPL-3.0 | Candidate ideas; no production strategy selected |
| iterativv/NostalgiaForInfinity | e018685b427c | GPL-3.0 | Complex crypto strategy candidate requiring careful reproduction |
| nautechsystems/nautilus_trader | 8dfef4b7725f | LGPL-3.0 | Rust/Python multi-asset engine candidate; evaluate reuse before building the engine from scratch |
| je-suis-tm/quant-trading | 611b73f2c3f5 | Apache-2.0 | Transparent research examples, including London Breakout; needs realistic execution modeling |

License labels are from source/metadata, not a conclusion about the proposed commercial distribution. Preserve notices and determine applicable obligations before adapting, linking, or distributing source. Porting a file to Rust must not be treated as eliminating its original license obligations.

## NFI: initial findings

The README specifies a 5-minute base timeframe, recommends 6–12 open trades and a broad crypto pair universe, and favors stablecoin pairs. Open-trade capacity is not daily trade frequency. [README](https://github.com/iterativv/NostalgiaForInfinity/blob/e018685b427cc17e6738098c536876c3fa0b981a/README.md).

Static inspection of X8 finds version v18.0.198, higher-timeframe inputs, new-candle indicator processing, position adjustment enabled, and custom exit/stake/position methods. It declares stoploss=-0.99 and stoploss_on_exchange=False while also defining other exit/stop logic. These values alone do not establish actual account risk. The file has multiple long/short mode families; describing it as a single EMA/RSI rule would be misleading. Configuration can change behavior. [Pinned code](https://github.com/iterativv/NostalgiaForInfinity/blob/e018685b427cc17e6738098c536876c3fa0b981a/NostalgiaForInfinityX8.py), [static inventory](nfi-static-review.json).

This is a partial structural review, not a full derivation of every entry/exit mode. The next source review must trace enabled conditions, exposure changes, stop behavior, and configuration overrides end to end. Replacing NFI's risk rules produces a different variant; comparisons must show that change explicitly.

## Alternative references

**London Breakout:** the repository's README states frictionless-trading assumptions. Its script builds a pre-session range, allows breakout entries in an opening window, and uses fixed price offsets and fixed clock-hour checks. Those assumptions need instrument scaling, explicit timezone/daylight-saving treatment, missing-data handling, and broker costs. It is an understandable baseline candidate, not evidence of a profitable ten-year system. [Project](https://github.com/je-suis-tm/quant-trading), [pinned script](https://github.com/je-suis-tm/quant-trading/blob/611b73f2c3f577ac5b28aaa19ac8c43d3236c7a5/London%20Breakout%20backtest.py).

**NautilusTrader:** its architecture combines a Rust-native multi-asset engine, Python strategy/orchestration, and deterministic simulation. Its integration table includes IBKR; this review does not establish ready-made cTrader, OANDA, or Exness adapters. It is an engine candidate, not a strategy or guaranteed performance improvement. Check adapter suitability, licensing, persistence, reconciliation, and Python/Rust strategy parity before adoption. [Pinned project documentation](https://github.com/nautechsystems/nautilus_trader/blob/8dfef4b7725f8371d96c56cc0c7cdec5525a398d/README.md).

**LEAN:** another event-driven engine with Python/C# support and an Apache-2.0 repository license. It is a useful comparison but adds a different core language to the Rust direction, so it is secondary in this review. [Project](https://github.com/QuantConnect/Lean).

## How we choose the timeframe and trade count

These must be measured after the rules and target instrument are understood. Do not ask the owner to guess them before strategy discovery.

| Term | Definition / how to determine it |
| --- | --- |
| Base signal timeframe | Candle or event interval used by the rules. Start with the upstream convention when reproducing; test proposed variants separately. |
| Informative timeframe | Additional market context used by rules; synchronize to only information available at the decision time. |
| Holding period | Time from actual fill to exit; a 5-minute signal interval does not imply a 5-minute holding period. |
| Entry frequency | Filled entries per day/session/week, including zero-trade periods; report by instrument and portfolio. |
| Concurrent positions | Maximum simultaneously open positions; constrained by account risk and margin as well as strategy settings. |
| Order traffic | Entries, exits, adjustments, replacements, and cancellations create separate API traffic. API rate limits are not expected trade counts. |
| Evaluation capacity | How many symbols/signals the service can process; benchmark separately from profitable trading opportunities. |

Do not target a fixed number of trades just to appear active. The app should surface trade opportunities, rejections, and measured activity distributions alongside losses and costs.

## Proposed reproducible evaluation sequence

1. **Rules and provenance:** freeze strategy/config/dependency versions. Document original entry/exit/sizing logic, warm-up, data inputs, and execution timing. Identify original-market assumptions before translating.
2. **Native reproduction:** reproduce the selected upstream strategy in its intended environment using versioned data. Do not silently substitute forex for crypto and label the result upstream NFI.
3. **Target-market baselines:** implement a small, explicit session-breakout baseline and a separate candidate adaptation. Compare against a transparent benchmark appropriate to the product and exposure; do not promise that the more complex candidate wins.
4. **Data qualification:** acquire permitted target-instrument data with documented bid/ask or spread conventions, sessions, missingness, financing, corporate actions/futures rolls where relevant, and account-currency conversion. No paid purchase is authorized by this plan.
5. **Time-separated evaluation:** development, validation, and untouched holdout periods; walk-forward checks and parameter-sensitivity tests. Include different market conditions, realistic fees/spread/slippage/funding, and a record of all material searches. Lock acceptance criteria before examining holdout results.
6. **Bias and execution checks:** use Freqtrade lookahead/recursive analysis where applicable, plus signal fixtures and timing inspection. Passing one analyzer does not prove absence of all bias. For stop/target collisions within one candle, use finer data or conservative explicit assumptions. [Lookahead tooling](https://www.freqtrade.io/en/stable/lookahead-analysis/), [backtest assumptions](https://www.freqtrade.io/en/stable/backtesting/).
7. **Variant comparison:** test each change separately and retain the unmodified baseline. Compare net expectancy, drawdown, exposure, trade count, loss concentration, and uncertainty. Repeatedly tuning to holdout data invalidates its role as untouched evidence.
8. **Rust parity and paper-forward testing:** if live rules are ported to Rust, compare indicator warm-up, timestamps, signals, sizing/rounding, and exit decisions against Python fixtures. Run the approved variant through the execution risk gate and broker demo reconciliation before considering live use.

The first report should include trades/day/session distributions (including zeros), median and upper-percentile holding periods, maximum concurrent positions, rejected opportunities, net performance, drawdown, capital required, costs, and sensitivity to less favorable fills. No numerical forecast belongs in that report until an actual reproducible run exists.

## Decision

Retain the NFI inspection as research history; prioritize the non-crypto candidates in NON-CRYPTO-AND-AI-DIRECTION.md. Evaluate NautilusTrader as an engine reuse option for the accepted Rust direction. Keep strategy timeframe and trade-frequency choices open until rule review and target-market testing supply evidence. The immediate next work is the complete rule specification and licensed data selection, not a request for the owner to choose a timeframe.
