# AI-assisted strategy design

Status: agreed product direction, 3 November 2026. AI should contribute to strategy research, improvement, and explanations. Provider/model, live decision permissions, datasets, evaluation thresholds, and production integration are not finalized. No model is connected and no strategy is approved for live execution.

## What AI contributes

Use AI to turn a market hypothesis into an explicit, testable strategy specification; propose changes to existing rules; interpret timestamped news and market context; analyze backend-computed test results; and explain the resulting decisions. Treat a proposed improvement as a hypothesis until independent evaluation supports it.

The first AI-enabled release adds research and explanation tools. AI-driven live trade proposals are a later capability requiring separate evaluation and explicit account-level permission. The existing manual/automatic trading modes remain: an approved deterministic strategy can trade automatically through the same risk checks without waiting for an LLM call.

## Research loop

1. Provide a versioned baseline strategy, allowed instruments, available data, execution assumptions, and configurable risk constraints. Include the timestamp at which each input became available.
2. Ask the model for a structured change proposal: precise rule differences, rationale linked to inputs, expected mechanism, failure conditions, and a bounded parameter-search plan. A statement such as "buy because sentiment is bullish" is not a complete executable rule.
3. Validate the proposal against a schema and allowed operations. Reject ambiguous units, undefined indicators, unavailable data, unsupported instruments, conflicting rules, or missing exits/sizing constraints. Do not execute arbitrary generated code in production.
4. Implement reviewed research variants in an isolated environment with no production broker credentials. Compare each variant with the unchanged baseline using the same data and realistic costs.
5. Use chronological development/validation/holdout periods. Give the AI development and permitted validation results; keep final holdout data and results out of the improvement loop. If holdout feedback is used for another revision, retire that holdout as independent evidence.
6. Evaluate net returns alongside drawdown, exposure, trade count, costs, concentration, sensitivity, and uncertainty. Do not select solely on maximum historical return or a model's confidence score. Record failed variants and the number of searches.
7. Promote only a version that meets predeclared acceptance criteria and paper-forward checks. Promotion creates an immutable approved strategy/configuration version with rollback information; it does not silently modify deployed rules.

## Optional runtime AI context

Once separately evaluated, AI may provide an expiring, structured market-context assessment or trade proposal. The proposal must identify:

- Account scope, instrument identifier and product type.
- Approved strategy/configuration version and input-data snapshot references.
- Observation time, source publication times, expiry, and evidence links.
- An allowed action: abstain, propose entry, propose exit, or propose cancellation; no unrestricted broker command.
- For an order proposal: side, order type, quantity or an approved deterministic sizing-rule reference, units/currency, entry constraints, protection/exit rules, and invalidation conditions.
- Missing information and uncertainty. Model-generated confidence is not a calibrated probability of profit.

The backend checks source freshness, authorization, instrument specifications, schema, strategy compatibility, exposure, margin, duplicate intent, approval requirements, and order constraints. Rust decides whether an intent is eligible to be submitted and records a machine-readable rejection reason where applicable. The broker determines actual order acceptance and fills.

Free-text explanations never serve as executable instructions. Retrieved news and documents are untrusted inputs, not authority to invoke tools or change permissions. Generated proposals cannot override existing protective orders, risk limits, account ownership, or user approval rules.

## Failure behavior

Define failure behavior per strategy mode. For an approved deterministic strategy, execution and existing risk protection continue independently of model availability. For a mode that requires fresh AI context, missing/expired/invalid context prevents new entries; existing exits and protective orders continue under the approved deterministic rules. Do not have an LLM failure trigger unapproved liquidation or silently fall back to a different strategy/model.

## Explainability and evidence

Record proposal ID, model/configuration version, redacted input references, structured output, evidence, validation results, strategy version, risk decision, user approval where required, submission identifiers, and reconciled broker outcome. Store a concise decision rationale, not hidden model reasoning. Show the user what rule triggered, what evidence was available, what risk was estimated, and what actually happened.

An explanation demonstrates traceability, not that a trade is correct or profitable. Model accuracy, strategy effectiveness, and execution reliability require separate tests.

## Next implementation artifact

Prepare a provider-independent proposal schema and deterministic validator using fixtures before connecting an API. Add a research variant registry and baseline-comparison report format. Connect the selected model only after provider access, data handling, and evaluation configuration are established. Initial model candidate remains GPT-6.1 Sol; no paid model usage or data transmission is authorized merely by this design document.
