# Non-crypto strategy direction and proposed AI assistant

Date: 3 November 2026. Status: research recommendation. No candidate has been backtested here; no LLM is integrated or called by the prototype.

## Strategy priority correction

NFI should no longer be the primary strategy-adaptation candidate for a product centered on forex, equities, gold, and oil. Keep its prior inspection as research history. Prefer implementations and market conventions closer to the intended products. No open-source implementation can be declared the best fit on reputation alone.

### Primary multi-asset research candidate: pysystemtrade rules

[pst-group/pysystemtrade](https://github.com/pst-group/pysystemtrade) is Rob Carver's systematic futures backtesting/trading project with IBKR connectivity. Its repository dates the original open sourcing to 2015. That history is not an independently verified return record. Source/licensing reviewed at commit bbf5cf823e16be1cca27493a94099eb8cf33f6e7; file hashes are in sources/manifest.json.

Two concrete rules inspected:

- **EWMAC:** a fast/slow exponentially weighted price-average difference normalized by price-unit volatility; the supplied functions assume daily data. Scaling, forecast caps, portfolio sizing, and execution live outside the raw rule. [Source](https://github.com/pst-group/pysystemtrade/blob/bbf5cf823e16be1cca27493a94099eb8cf33f6e7/systems/provided/rules/ewmac.py).
- **Breakout:** a forecast based on price relative to the midpoint of a rolling high/low range, normalized by range width and smoothed. It is not a complete entry/exit strategy by itself. Flat ranges, warm-up, sizing, and execution need explicit handling. [Source](https://github.com/pst-group/pysystemtrade/blob/bbf5cf823e16be1cca27493a94099eb8cf33f6e7/systems/provided/rules/breakout.py).

This makes a stronger starting point for a diversified futures trend system than a crypto-specific strategy. Gold, oil, currencies, and stock-index exposure still require supported instrument data and complete portfolio rules. Futures, spot FX, CFDs, and individual shares differ in sizing, trading sessions, carry/financing, and rolls. Do not apply a futures result directly to a CFD or equate a stock-index future with NASDAQ-listed shares. This is not inherently a high-turnover intraday strategy. GPL obligations require assessment before code reuse/distribution.

### Intraday forex candidate: session breakout

The already pinned [je-suis-tm London Breakout script](https://github.com/je-suis-tm/quant-trading/blob/611b73f2c3f577ac5b28aaa19ac8c43d3236c7a5/London%20Breakout%20backtest.py) provides an inspectable FX starting point. Prior review identifies fixed clock-hour and fixed-price-offset assumptions; replace them explicitly for the tested instrument/session and document the new variant. Model bid/ask, DST, spread widening, stops, financing, and order timing. Do not presume these corrections improve returns.

### Individual-stock baseline and further research

[Backtesting.py's own quick-start example](https://kernc.github.io/backtesting.py/doc/examples/Quick%20Start%20User%20Guide.html) provides a simple moving-average crossover example on stock data. It is a transparent educational benchmark, not a production recommendation or a portfolio engine. Compare against an appropriate passive benchmark after fees and exposure differences.

Equity Opening Range Breakout is a further candidate, but the QuantConnect research page did not expose the complete implementation through the fetched page in this pass. Do not label search excerpts as a reviewed, licensed source file or accept its published performance. Locate the original code and license before copying. LEAN is an engine/reference ecosystem, not evidence that any particular strategy is profitable.

### Proposed evaluation choice

Prioritize a complete volatility-scaled trend system informed by pysystemtrade and a separate intraday FX session-breakout candidate. Use a simple equity crossover as an implementation/benchmark reference while locating a suitable original equity intraday implementation. Keep different strategy families separate initially. Determine timeframes and frequency from rules and target-market tests; do not force one strategy or a daily trade quota across every asset.

## Proposed LLM integration

An LLM is useful for the product experience, but systematic execution can operate without one. Initial recommendation: **GPT-6.1 Sol (`gpt-6.1-sol`) through the OpenAI Responses API**, behind a server-side provider interface. This is a proposal, not a final procurement or a claim of superior trading returns. Official documentation supports structured outputs, function calls, and retrieval/search tools. [Model documentation](https://developers.openai.com/api/docs/models/gpt-6.1-sol).

Candidate alternatives for comparative evaluations: **Claude Sonnet 5.5** and **Gemini 3.8 Flash**. They appear in their respective current vendor catalogs; their performance on this app has not been measured. [Claude catalog](https://platform.claude.com/docs/en/models/overview), [Gemini catalog](https://aistudio.google.com/docs/models).

Start with one model rather than a multi-model voting system. Consider GPT-6 Luna later for bounded high-volume extraction/classification only if evals justify its quality and cost. [OpenAI model catalog](https://developers.openai.com/api/docs/models).

Initial useful tasks:

- Explain selected strategy rules and research results in language suitable to the user's experience.
- Summarize permitted news/calendar material with source links and publication/event timestamps.
- Answer portfolio questions using authorized account summaries and backend-computed figures.
- Explain an order rejection or risk-limit decision from authoritative recorded events.
- Turn a natural-language strategy preference into a structured draft for review, validation, and backtesting.

The model receives scoped, minimized context. Backend services compute monetary/risk metrics; a model must not manufacture balances, latest prices, backtest results, or probability-of-profit claims. Source gaps must remain visible. Market news is untrusted input and cannot grant tool permissions or override policies.

For the first version the assistant has read-only tools. It receives no broker secrets or unrestricted SQL access. Any later ability to propose orders or settings must use validated schemas and the same user-authorization and risk gates as other orders, with explicit change tracking. The Rust execution service remains outside the LLM request path; exits and risk protection must work through model outages, slow calls, invalid output, and provider errors.

## Evaluation and privacy requirements

Compare models on a fixed set of representative prompts: correct explanations from rules; numerical fidelity to supplied calculations; source citations and freshness; missing-data abstention; account isolation; malicious-news/prompt-injection resistance; schema compliance; latency; and cost per successful task. No proprietary or real-user data needs to leave the system to run the initial tests. Model changes require repeat evaluation and a recorded model/configuration version.

Never transmit broker keys, passwords, full unnecessary identifiers, or unrelated user data to an LLM provider. Verify contracts, residency requirements, retention settings, and disclosure/consent for any actual account data before integration. OpenAI states API data is not used for training by default, but this does not mean zero retention; default abuse-monitoring retention and feature-specific state must be considered. [Official data controls](https://developers.openai.com/api/docs/guides/your-data).

No API credentials were created, no model calls were run, and no paid services were activated during this research.
