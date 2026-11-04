# Trading platform engineering requirements

Agreed preparation: 3 November 2026. These requirements guide implementation; they do not assert that controls already exist or that any system can be free of every vulnerability.

## Skills installed

| Skill | Source | Purpose |
| --- | --- | --- |
| supabase-postgres-best-practices | supabase/agent-skills | PostgreSQL schema, indexing, migrations, connections, locking, and row-level security; usable without Supabase hosting |
| backtesting-frameworks | wshobson/agents | Bias-aware strategy backtesting and walk-forward evaluation |
| python-testing-patterns | wshobson/agents | Tests of strategy calculations, adapters, persistence, and failures |
| async-python-patterns | wshobson/agents | Concurrent network I/O, cancellation, and timeouts |
| api-design-principles | wshobson/agents | API schemas, boundaries, versioning, and errors across languages |

Previously installed: playwright, vercel-react-best-practices, web-design-guidelines, security-best-practices, security-threat-model. Community guidance and sample code must be checked against current official documentation and our requirements before reuse.

Additional installed trading skills: risk-metrics-calculation (wshobson/agents), trading-risk-controls, forex-execution-rules, strategy-research-adaptation, and portfolio-exposure-management. The latter four are custom project skills with maintained source under skills/ in this repository and installed copies in the user's Codex skills directory. They passed structural validation; their guidance is not itself a validated trading system. Update and revalidate installed copies when maintained source changes.

## Data and language boundaries

- Rust is the accepted execution-language direction; Python supports research/application services and TypeScript the web interface. Evaluate existing Rust/Python engine components against integration, licensing, correctness, and operational needs. Additional languages require a concrete dependency or measured benefit. Do not infer an end-to-end execution latency from a language choice.
- Distinguish transactional account/order records from large historical price datasets and research workloads. Benchmark storage and processing needs before selecting extra databases or services.
- Define versioned API/event contracts with explicit units, currencies, instrument IDs, UTC timestamps, precision, nullability, and error semantics. Generate client types where practical and test compatibility between services.
- Use decimal or integer-scaled monetary values at persistence and execution boundaries; specify rounding and broker quantity/price increments. Research numeric representations may differ but must convert explicitly.
- Keep CPU-heavy research off request and execution event loops. Async I/O does not itself accelerate Python CPU computation or guarantee execution latency.
- Design migration safety, uniqueness constraints, atomic state transitions, retention, and restore verification. Enforce account ownership in application authorization and database policies where appropriate.

## Reusing open-source strategies

- Record repository URL, exact revision, license, notices, dependencies, upstream strategy rules, and local modifications. Public availability alone does not grant unrestricted reuse.
- Inspect strategy code and dependencies before running them. Run research without production broker credentials and with appropriately restricted access.
- Preserve reference behavior with representative fixtures before changing strategy logic or porting languages. Compare signal timestamps, entries/exits, position sizes, and monetary rounding.
- Test with time-separated development/validation/holdout periods, point-in-time data, appropriate delisted-symbol coverage, realistic commissions, spread, slippage, financing, and instrument/session calendars. Report parameter searches and unsuccessful trials.
- Confirm that signals use only information available at the decision time. Include latency and fill assumptions and distinguish paper results from actual broker fills.
- Keep signals separate from authorization, risk controls, and order submission. Strategy code must not bypass account limits or directly access production secrets.

## Account and application safety

- Prefer broker-authorized OAuth/delegated access where supported. Request the minimum permissions; exclude withdrawal permissions where the broker allows. Store any required credentials server-side under managed encryption with separated key access and rotation/revocation support.
- Do not put broker tokens, passwords, or secrets in frontend bundles, URLs, source control, telemetry, exception messages, or chat. Redact sensitive fields in logs and diagnostic artifacts.
- Use a maintained identity system, MFA/passkeys where supported, secure session handling, and server-side authorization for each account operation. Test that one user cannot read or trade another user's account, including through WebSocket subscriptions and background jobs.
- Record explicit user consent for automatic trading and enforce configured account/strategy/risk limits server-side. Bind an approval to the precise order terms and expire it; changes require renewed approval.
- Track order intents with stable identifiers. A timeout after submission means the outcome may be unknown: reconcile with the broker before retrying. Verify duplicate delivery, partial fills, reconnects, cancellation races, and stale prices.
- Provide controls to stop new automated orders and separately define handling of existing positions. Do not assume a stop button closes positions or that a stop-loss guarantees an exact loss cap.
- Use dependency and secret scanning, static security checks, targeted authorization tests, rate limits, and deployment hardening. Review third-party code and license obligations before integration.
- Separate development, paper, and production credentials and resources. Production order submission requires a deliberate environment configuration and user authorization.
- Before public live trading, verify critical flows with a scoped independent security assessment, resolve release-blocking findings, and establish alerting, incident response, credential revocation, and tested backup recovery.

## Evidence required before live automation

Demonstrate isolation between accounts, protected credential handling, risk-limit enforcement, duplicate-order prevention under failure, broker reconciliation, strategy/data correctness, and recovery from process or connection loss. Report remaining findings and limitations explicitly. No skill installation substitutes for these checks.
