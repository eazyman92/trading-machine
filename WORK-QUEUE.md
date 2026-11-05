# Active work queue

Updated: 4 November 2026. Full dependencies and release gates: ROADMAP.md. Statuses: ready, blocked, planned, verified. Only attach “verified” to recorded evidence.

## Current objective: reproducible engineering foundation

| ID | Task | Status | Completion evidence required |
| --- | --- | --- | --- |
| F01 | Finish Rust compiler/linker setup | Blocked: compiler downloads stalled | Record compiler/toolchain versions; cargo test succeeds |
| F02 | Verify Python/Rust contract parity | Blocked by F01 | Both implementations pass the shared vectors; preserve rejection cases |
| F03 | Formalize order intent schema and rejection codes | Ready | Versioned schema, units/limits/expiry documentation and meaningful malformed-input checks |
| F04 | Reproducible setup and automated checks | Ready | Dependency/version approach, clean setup instructions and CI configuration checked locally where possible |
| F05 | Review replay/model scope before adding historical input | Ready | Explicit data ingestion contract, completeness policy, fill/cost assumptions and regression coverage |

Python baseline evidence: eight tests passed on 4 November 2026; synthetic replay runs. Rust tests have not run. No historical profitability claim.

## Next integrated increment: research through the web

| ID | Task | Dependency | Completion evidence required |
| --- | --- | --- | --- |
| W01 | Confirm web/API scaffold decisions | F03/F04 | Short architecture decision and runnable local scaffold |
| W02 | Add replay job API with validation and explicit synthetic labels | W01/F05 | Valid job returns reproducible artifacts; invalid input/failure/cancel paths checked |
| W03 | Connect research screen to actual job results | W02 | Browser-tested job-to-result flow, trade/rejection detail and clear sample-data distinction |
| W04 | Add identity, persistence and account isolation | Schema/identity design, W01 | Migration and ownership checks; separate users cannot access each other's records |

Local synthetic development may precede identity; no public deployment or multi-user exposure until authorization/isolation are implemented.

## Parallel qualification queue

| ID | Task | Status | Completion evidence required |
| --- | --- | --- | --- |
| Q01 | Compare historical FX dataset access/rights and permitted samples | Ready | Dated provider evidence, coverage/cost/rights comparison; no purchase without authorization |
| Q02 | Close Nigeria demo/account/API eligibility questions | Ready for documentation research | Exact entity/platform/products and commercial-permission evidence; account steps remain owner-controlled |
| Q03 | Write statistical evaluation protocol before market backtests | Ready | Splits, benchmarks, costs, search log, sensitivity and acceptance/rejection criteria |
| Q04 | Select/reproduce the first upstream strategy reference or retain explicit custom variant | After Q01/Q03 | Source/license record, reference comparison and justified decision |

## Decisions to resolve when they become actionable

- Product name before branding/public release; it does not block backend work.
- Dataset and demo route after evidence comparison, including any subscription budget.
- Identity/database hosting before multi-user persistence deployment.
- AI provider and capped usage after proposal/evaluation fixtures exist.
- Launch countries and live scope after paper evidence and external permissions.

## Completion record

5 November 2026 — Real-data preparation increment: reviewed official Dukascopy historical export/docs as a qualification candidate (no commercial rights established). Added strict normalized UTC bid/ask tick-to-candle preparation with source/output hashes and gap statistics, no silent filling, and explicit first-observed-spread approximation. Real data remains unverified and must be owner-supplied with permission; no dataset downloaded or bundled. Existing 3000-row bound remains. See REAL-DATA.md.

5 November 2026 — Strategy-engine research increment: gold v0.2 adds configurable breakout buffer, reward multiple and maximum-entry-spread filter, deterministic configuration fingerprint, research-only status and rule-derived per-trade entry/risk evidence. Saved comparisons disclose rule changes. Twenty-three Python tests pass and frontend syntax checks pass. No historical-data qualification, LLM, broker submission or live approval added. Interactive browser verification remains pending.

5 November 2026 — Dataset preview/research charts increment: added strict CSV preview with row/coverage/spread/session completeness, optional inclusive London session date range, stored closed-trade P&L/drawdown series and dashboard charts, and descriptive saved-run comparison enforcing exact CSV/date-range match and exposing changed settings. Twenty-two Python tests pass; JS syntax checks pass. No qualified market dataset or large-history storage added; existing 3,000-row/500 KB bound and unverified data status remain. Browser/EC2 interaction checks are pending.

5 November 2026 — Research result clarity/recovery: added USD metric cards, win-rate N/A for no trades, gold-specific selected-job labels and quantity headers, sizing rejection explanations, and request-key lookup after interrupted gold submission. Nineteen Python tests pass; syntax checks pass. Recovery tests model a lost response by retrieving/retrying the original key and checking exactly one stored job. Browser/network interruption interaction and EC2 deployment remain unverified.

5 November 2026 — XAU/USD research increment: added bounded UTC bid-candle/spread CSV import, explicit user-declared ounce/lot contract and cost inputs, separate gold sizing, saved worker reports and dashboard import form. Seventeen Python tests pass, including existing EUR/USD regression and gold import/API/sizing cases; all three frontend scripts pass syntax checks. Synthetic gold sample generator added. Real historical data, broker specification qualification and browser interaction verification remain outstanding (browser automation timed out during verification). See GOLD-RESEARCH.md. No Rust/live gold support is enabled.

Saved research history increment: added bounded history API and dashboard paging/reopen controls, with newest-run restoration on reload. Fourteen Python tests pass. The persistence-check CLI saved and matched a completed result across a local API/worker process restart using SQLite. EC2/PostgreSQL container-recreation verification remains owner-run using EC2-TEST.md; browser interaction testing of the new history controls is still pending.

4 November 2026 — F04 partial: added GitHub Actions jobs for Python regression tests, Rust shared vectors and a Compose/PostgreSQL HTTP smoke test; added scripts/smoke_research.py and Git Bash/EC2 instructions in EC2-TEST.md. Local regression remains 13 passing tests. Workflow YAML parses, but GitHub execution, container builds and Rust compilation are still pending; no repository remote exists yet.

4 November 2026 — W02/W03 partial: added versioned research API, durable SQL queue, separate worker and connected Research lab screen. Thirteen Python tests pass in SQLite mode, including idempotent creation, concurrent claiming, cancellation precedence, expired leases and failures. Compose definitions added for web/API/worker/PostgreSQL/schema initialization; Docker is unavailable, so the PostgreSQL/container path remains unverified. Web still uses the existing buildless prototype; TypeScript scaffold, identity and account isolation remain open. See DEVELOPMENT.md.

Append task ID, date, changed files/artifacts, check results and remaining limits when closing work. Do not mark tasks complete from code presence alone. The next implementation session starts at F01–F05; if download access still blocks F01, proceed with independent F03–F05 and Q01–Q03 rather than repeating stalled installs indefinitely.
