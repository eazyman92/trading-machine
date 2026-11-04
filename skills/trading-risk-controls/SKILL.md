---
name: trading-risk-controls
description: Design and test pre-trade and runtime risk controls for this multi-user trading platform, including sizing, margin, loss limits, approval binding, and order reconciliation. Use when changing risk gates or automated order execution.
---
# Trading risk controls

Read ENGINEERING-REQUIREMENTS.md in the project when present. Preserve paper/live separation and existing authorization boundaries.

- Establish instrument type, account currency, equity definition, executable bid/ask, fee model, quantity increments, contract multiplier, and broker margin rules before sizing. Reject missing or stale inputs with a recorded reason.
- Calculate estimated stop loss in account currency, including conversion and modeled costs. Round quantity down to the valid increment, then recompute loss and margin. Reject a result below the minimum size; do not round it up. A stop is not a guaranteed maximum loss.
- Define configurable per-trade, account, strategy, concentration, gross exposure, and pending-order limits. Do not invent an optimal risk percentage. Specify equity baseline, realized/unrealized treatment, reset timezone, deposits/withdrawals, and restart behavior for daily-loss and drawdown limits.
- Reserve risk atomically for concurrent order intents. Include open positions, pending orders, partial fills, and outstanding reservations. Release reservations only after a confirmed lifecycle transition; reconcile unknown states.
- Bind user approval to account, instrument, side, quantity, order type, price constraints, protection, strategy version, and expiry. Recheck authorization and risk at submission, not just at proposal creation.
- Deduplicate submissions using stable intent IDs and supported broker identifiers. A timeout can follow broker acceptance; reconcile before retrying. Define cancel/replace races and restart recovery.
- Specify separately what stopping new orders, cancelling pending orders, and closing positions do. An emergency control must not silently imply all three.

Deliver explicit decision rules, units, rejection reasons, and meaningful tests for boundary rounding, cross-currency sizing, stale data, concurrent submissions, partial fills, unknown acknowledgements, restart, and changed approvals. Treat numerical examples as fixtures, not financial advice.
