---
name: portfolio-exposure-management
description: Design and verify portfolio exposure aggregation and limits across accounts, currencies, instruments, and strategies. Use when building concentration checks, shared-currency exposure, stress scenarios, or portfolio risk reporting.
---
# Portfolio exposure management

- Define scope and permissions: risk must be enforced per actual trading account; cross-account reporting does not imply transferable margin or capital. Keep one user's information isolated from other users.
- Normalize marks and timestamps, currencies, contract multipliers, side, quantity, and instrument type. Convert to a declared reporting currency with timestamped rates. Surface stale/missing prices and conversion gaps rather than silently excluding positions.
- Include pending orders, partial fills, and reserved intents without double counting. Calculate gross and net exposure separately. Represent FX positions as both currency legs; explain shared USD exposure across pairs. Do not treat unlike derivatives as interchangeable notional exposure.
- Aggregate concentration by instrument, underlying, currency, sector where available, strategy, and account. Opposing strategies in a netted account can still create turnover and execution risk; net notional is not a complete risk measure.
- Use aligned returns and explicit frequency, lookback, financing, and missing-data conventions for correlation and risk metrics. Handle zero variance, short histories, and nonstationarity. Historical correlation is not a guarantee of diversification.
- Define stress scenarios for currency moves, underlying moves, spread widening, price gaps, and unavailable markets. Use instrument-appropriate repricing for nonlinear derivatives; do not assume all P&L is linear. Document model limitations.
- Express limits as configurable constraints and enforce them atomically with order reservations. Show rejected proposals and responsible exposures. Do not automatically liquidate or rebalance without the relevant user authorization.

Deliver exposure definitions, freshness/coverage indicators, limits, explainable examples, and tests for shared currencies, offsetting positions, pending orders, conversions, and stressed correlations. Use risk-metrics-calculation for metric implementation only after checking its assumptions.
