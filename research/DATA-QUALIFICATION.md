# Historical XAU/USD source qualification receipt

Update 5 November 2026: the earlier desk-review table below is superseded for **technical sample acquisition** by MARKET-DATA-ADAPTER.md. Ten actual hourly files (47,580 paired ticks / 600 minute projections) were downloaded, offline hashes reproduced, and isolated dataset/worker ingestion verified. Daily-reference scale sanity passed; exact provider quote confirmation and commercial rights remain unresolved. The table is retained as the initial qualification record, not current proof that no sample exists.

Reviewed: 5 November 2026. No data account opened, agreement accepted, paid request made or real market dataset obtained during this increment.

| Gate | Evidence | Status |
| --- | --- | --- |
| Official export route | Dukascopy historical export page and historical-price documentation | Route identified, not selected as execution broker |
| Bulk access | Official guide describes AWS requester-pays S3 access | May incur charges; no AWS requester credentials/budget used |
| Raw format | Official decoder uses 20-byte records with millisecond timestamps, bid/ask integers and volumes | Current daily versus legacy hourly layout needs explicit selection |
| Gold scale | Official guide comments XAUUSD in a non-FX mapping but warns non-FX scale must be confirmed | Blocked: commented example is not a verified instrument specification |
| Research/commercial rights | Public export availability alone does not establish app redistribution or commercial usage rights | Unresolved: exact permission/terms reference needed |
| Actual sample | None acquired or decoded here | Outstanding; no source-versus-chart sanity check performed |
| Statistical evaluation | Baseline and split-plan tooling implemented | No actual real-price baseline/validation/holdout result yet |

Primary references:

- https://www.dukascopy.com/swiss/english/marketwatch/historical/
- https://www.dukascopy.com/wiki/en/development/data-export/

Next concrete external step is an approved short XAU/USD bid/ask export with documented UTC timestamps and quote scale. Prefer decimal CSV from the official exporter for initial sanity checking instead of assuming a binary divisor. Record provider, product, export configuration, period, retrieval time, permission and source hashes. Compare selected timestamps/prices/spreads with the provider's own display before treating it as a qualified research source.

The normalized tick converter records a first-observed-spread candle approximation. It is not tick-accurate executable history. Provider data also does not establish the eventual execution broker's spreads, fees, margin, financing or contract size. Do not silently route market research through the synthetic fixtures when access is unavailable.
