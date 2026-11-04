---
name: strategy-research-adaptation
description: Inspect, reproduce, adapt, and evaluate open-source trading strategies for this app. Use when selecting upstream strategy code, translating trading rules, porting languages, or comparing strategy modifications.
---
# Strategy research and adaptation

- Record upstream repository, exact commit, license obligations, dependencies, required data, markets, and execution assumptions before reuse. Separate upstream performance claims from independently reproduced results.
- Inspect code and installation hooks before executing. Use an isolated research environment without live credentials. Strategy code emits signals; it does not obtain production tokens or bypass execution risk gates.
- Write precise rules for indicators, warm-up, sessions, long/short entry, exit, stops, sizing, simultaneous signals, and evaluation timing. Specify whether the source uses closing-bar information and when a fill can first occur.
- Reproduce reference signals on representative fixtures before modifications. Compare timestamp alignment, missing bars, indicator initialization, signals, and rounding when porting languages. If semantics cannot be reproduced, label the implementation as a new variant.
- Specify data provenance and point-in-time handling, corporate actions or futures rolls when relevant, spread, commissions, financing, slippage, capacity, and rejected orders. Inspect leakage from resampling, indicator shifts, revised releases, and universe selection.
- Reserve chronological development, validation, and untouched holdout periods; use walk-forward checks where useful. Record all material parameter searches, not just the winner. Reusing holdout results for tuning consumes that holdout.
- Report after-cost returns alongside drawdown, exposure, turnover, trade count, benchmark, parameter sensitivity, and uncertainty across market conditions. Never declare profitability from upstream reputation or an attractive equity curve.
- Require paper-forward evidence and execution reconciliation before proposing live use. Research approval does not authorize real orders.

Deliver a provenance record, rule specification, reproduction comparison, test assumptions, results including failures, and a justified next decision. Use installed backtesting/data-quality skills when their workflows are needed.
