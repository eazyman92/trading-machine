# Local design prototype

This buildless HTML/CSS/JavaScript prototype explores the trading app's navigation and interaction design. It is separate from the proposed React/Python production implementation.

Run from the project root:

```powershell
python -m http.server 4173 --bind 127.0.0.1 --directory prototype/dist
```

Open http://127.0.0.1:4173. Stop the server with Ctrl+C.

Features: six screens, dark/light theme, simple/advanced overview, symbol/timeframe selection, preview order validation and review, simulated fills, activity history, strategy preferences, and preview risk limits. Only the theme is persisted. Other state resets on reload.

All prices, candles, equity, existing positions, and performance values are illustrative. Manually created fills are interaction fixtures and do not update a real accounting ledger. No broker, authentication, production risk engine, market feed, strategy execution, or security service is connected. No credentials are collected or transmitted. The preview uses no third-party runtime assets or libraries.

## Verification

Checked in the browser on 3 November 2026: overview and trading layouts in both themes; small-screen overview and trading views without page-level horizontal overflow; order review and simulated fill; rejection above the preview per-order limit; disabling new orders through the pause control; strategy execution preference and pause interactions; connections screen. No browser console errors were recorded in the checked flows. JavaScript syntax was checked with Node. These checks verify a design prototype, not production financial correctness or security.

Design screenshot: [dark overview](../output/playwright/overview-dark.png).
