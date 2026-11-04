---
name: forex-execution-rules
description: Implement and verify broker-specific forex pricing, pip values, sizing, financing, sessions, and order restrictions. Use when adding FX instruments or broker adapters; gold, oil, equities, and derivatives require their own contract specifications.
---
# Forex execution rules

- Fetch current official specifications for the selected broker entity and account. Record source and retrieval time. Confirm units versus lots, base/quote/account currencies, price tick, quantity step, contract size, minimum/maximum size, margin, supported order/fill types, protection distances, and trading hours. Never infer these solely from a symbol string.
- For a simple spot-FX convention, quote-currency pip value is base units times pip size. Convert quote-currency amounts to account currency using documented direction and appropriate executable conversion rates. Check the formula against broker examples and supported profit/margin calculators. Broker CFD or derivative conventions can differ.
- Distinguish pip size, tick size, and display precision. Do not hard-code four decimal places or assume a lot convention applies to every instrument. Treat XAUUSD, oil CFDs, and futures using explicit contract metadata.
- Model execution against bid/ask and correct side; test spread widening, stale/crossed quotes, minimum distances, quantity rounding, unavailable conversion quotes, and broker rejection. Do not assume a candle close is an executable fill.
- Use timezone-aware calendars for sessions, holidays, daylight saving, and broker maintenance. Model financing/rollover from entity-specific terms, including multi-day charges. Do not hard-code a universal triple-swap weekday.
- Keep macro/news rules configurable. Timestamp economic releases and data revisions as available at decision time; do not assume a calendar filter improves profitability.

Deliver a normalized instrument mapping, calculation conventions, source links, unresolved metadata, and fixtures including a JPY pair and an account currency different from both pair currencies. Missing specifications block order submission for the affected instrument.

Example specification source, not a selected broker: https://developer.oanda.com/rest-live-v20/primitives-df/
