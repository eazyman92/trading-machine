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

Saved research history increment: added bounded history API and dashboard paging/reopen controls, with newest-run restoration on reload. Fourteen Python tests pass. The persistence-check CLI saved and matched a completed result across a local API/worker process restart using SQLite. EC2/PostgreSQL container-recreation verification remains owner-run using EC2-TEST.md; browser interaction testing of the new history controls is still pending.

4 November 2026 — F04 partial: added GitHub Actions jobs for Python regression tests, Rust shared vectors and a Compose/PostgreSQL HTTP smoke test; added scripts/smoke_research.py and Git Bash/EC2 instructions in EC2-TEST.md. Local regression remains 13 passing tests. Workflow YAML parses, but GitHub execution, container builds and Rust compilation are still pending; no repository remote exists yet.

4 November 2026 — W02/W03 partial: added versioned research API, durable SQL queue, separate worker and connected Research lab screen. Thirteen Python tests pass in SQLite mode, including idempotent creation, concurrent claiming, cancellation precedence, expired leases and failures. Compose definitions added for web/API/worker/PostgreSQL/schema initialization; Docker is unavailable, so the PostgreSQL/container path remains unverified. Web still uses the existing buildless prototype; TypeScript scaffold, identity and account isolation remain open. See DEVELOPMENT.md.

Append task ID, date, changed files/artifacts, check results and remaining limits when closing work. Do not mark tasks complete from code presence alone. The next implementation session starts at F01–F05; if download access still blocks F01, proceed with independent F03–F05 and Q01–Q03 rather than repeating stalled installs indefinitely.
