# Trading application: agreed direction

General implementation diagram and build-versus-buy/cost inventory: SYSTEM-BLUEPRINT.md.

Full delivery roadmap and milestone acceptance gates: ROADMAP.md. Current actionable tasks, blockers and completion evidence: WORK-QUEUE.md. These are the primary planning references as of 4 November 2026.

Research integration added 4 November: the Research lab screen connects to a Python API and separate worker with durable synthetic replay jobs. Compose configuration targets PostgreSQL; local verification uses SQLite because Docker is unavailable. Setup and verification limits: DEVELOPMENT.md. Other dashboard screens remain sample-data prototypes.

Updated: 3 November 2026. Status: local design prototype plus first paper-only research implementation. See IMPLEMENTATION.md for replay rules, commands, shared Python/Rust risk fixtures and remaining integration gates. No production trading application exists yet.

## Confirmed requirements

- Build and test from Nigeria; design for users across Africa, USA, Canada, UK, Europe, and Asia.
- Web application first; mobile application later, sharing backend services.
- Serve both beginners and experienced traders. Default visual direction: dark professional terminal with a light option. A buildless local interaction prototype lives under prototype/; Axiom is only a provisional name.
- Support automatic trading and user approval of proposed trades.
- Cover individual stocks including NASDAQ-listed equities, forex including EURUSD and GBPUSD, gold, and US oil. Exact oil and gold instruments remain to be selected: futures, CFDs, ETFs, and spot products are not interchangeable.
- Keep analysis, charts, broker connection, orders, positions, and performance tracking within the application where supported.
- Research brokers rather than assume a broker has already been selected.
- Reuse suitable open-source components after checking licenses and integration suitability.
- Profitability and execution latency must be measured; neither is guaranteed by a strategy, programming language, or skill.
- Rust is accepted as the execution-language direction, with Python for strategy research and TypeScript for the web interface. Engine/framework reuse remains under evaluation.
- Broker discovery is our responsibility: assess global coverage country by country, with Nigeria tested explicitly. No broker has been selected or passed live-readiness qualification.
- Derive strategy timeframe, holding period, and expected trade frequency from source review and reproducible tests. Do not require the owner to choose these before understanding the strategy.
- Prioritize non-crypto-native strategy research: pysystemtrade trend rules and FX session breakout; NFI is no longer the primary candidate. An LLM assistant is proposed for explanations/research/account summaries, with GPT-6.1 Sol as the initial model candidate subject to evaluations. No LLM integration exists yet. See research/NON-CRYPTO-AND-AI-DIRECTION.md.
- AI-assisted strategy improvement is an explicit product requirement. AI proposes precise, versioned research changes; reproducible testing determines whether they improve the baseline. Future runtime AI proposals require structured validation and permission; Rust enforces execution/risk rules. See AI-STRATEGY-DESIGN.md. Clear explanations and confident language are not evidence of profitability.

## Initial broker research

These are integration candidates, not endorsements or a completed reliability assessment. Availability must be checked per residence, broker legal entity, product, and account type. No continent-wide eligibility is assumed.

| Candidate | Evidence and potential role | Unresolved constraints |
| --- | --- | --- |
| Interactive Brokers | Broad country list includes Canada, USA, UK, South Africa, and several Asian countries. Web API supports authorized third-party access. Candidate for multi-asset coverage. | Nigeria is absent from the country list reviewed. Third-party integration requires compliance approval and agreements. Automated trading offerings have additional regional registration/legal-opinion expectations. |
| Saxo | OpenAPI explicitly supports individual clients, institutions, and third parties. Candidate for further multi-asset research. | Country eligibility is determined through the account-opening form. Nigerian eligibility, regional products, commercial terms, and third-party production approval remain unverified. |
| OANDA | v20 supports prices, orders, positions, and transaction history. Candidate for forex and eligible regional products. | v20 is explicitly unavailable for OANDA Global Markets and OANDA TMS BROKERS S.A. Nigerian eligibility and relevant entity/API combination remain unverified. |
| Alpaca | Candidate for US-stock integration. Official guidance supports many non-US residents. | Current retail guidance excludes Canadian residents; its Canada site says services depend on pending approvals. Nigerian eligibility requires confirmation. Trading API and Broker API are different integration arrangements. |
| IG | REST and streaming APIs support prices, account updates, and order execution. Candidate for further regional forex/CFD research. | Exact entity, residence eligibility, third-party use, and product/API coverage remain unverified. |

Sources reviewed:

- https://portal.interactivebrokers.com/en/accounts/open-account-country-list.php
- https://www.interactivebrokers.com/campus/ibkr-api-page/webapi-doc/
- https://openapi.help.saxo/hc/en-us/articles/4488515250717-What-is-Saxo-OpenAPI
- https://www.help.saxo/hc/en-us/articles/360001268286-How-do-I-open-an-account
- https://developer.oanda.com/rest-live-v20/introduction/
- https://alpaca.markets/learn/live-trading-account-non-us
- https://alpaca.markets/ca
- https://www.ig.com/en/trading-platforms/trading-apis/how-to-use-ig-api

## Development preparation

Initial skill selection: OpenAI playwright, security-best-practices, security-threat-model; Vercel React performance and web interface guidelines. Installation status is reported separately in chat. Existing available Data skills already cover notebooks, data quality, and analysis validation.

Database and strategy engineering preparation has been expanded: PostgreSQL best practices, strategy backtesting, Python testing, asynchronous Python, and cross-language API design skills are installed. See ENGINEERING-REQUIREMENTS.md for sources and project-specific requirements. Mobile-specific additions remain deferred until the mobile stack is selected. Skills provide workflows and references, not evidence of profitable trading or an absence of vulnerabilities.

Trading preparation now includes installed risk metrics plus four custom skills covering risk controls, forex execution rules, strategy adaptation, and portfolio exposure. Sources are under skills/. Broker qualification remains outstanding. The first product and technology proposal is in PRODUCT-AND-ARCHITECTURE.md; its visual/audience assumptions and vendor choices remain open for discussion.

## Next decisions and evidence

The first expanded desk assessments are in research/BROKER-ASSESSMENT.md and research/STRATEGY-ASSESSMENT.md. Pinned public source snapshots, licenses, and hashes are in research/sources/manifest.json. Static review is not a backtest; no performance or trades/day estimate has been measured. The research identifies Freqtrade/NostalgiaForInfinity as the probable reference from the original notes and NautilusTrader as an additional Rust/Python engine candidate.

1. Complete a Nigeria-first broker qualification matrix: resident acceptance, legal entity and regulator register, authorized third-party API, demo availability, stock/forex/gold/oil products, funding/withdrawals, data rights/costs, fees, limits, and incident history.
2. Select one demonstrable broker path for the first integration, while retaining an adapter boundary for more brokers.
3. Select the web/backend/data stack and define the paper-trading milestone.
4. Validate strategy candidates with reproducible evidence before enabling live automation.

Global architecture is a design objective; availability will expand country by country after eligibility and integration verification.
