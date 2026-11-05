# Historical gold data qualification

Official routes reviewed 5 November 2026:

- Dukascopy historical export: https://www.dukascopy.com/swiss/english/marketwatch/historical/
- Official historical-price export documentation: https://www.dukascopy.com/wiki/en/development/data-export/

These establish an official export route, not our commercial license, redistribution rights, broker eligibility or data accuracy. No commercial data agreement or dataset has been obtained. Do not publish/repackage the provider's files without confirmed permission. Keep downloaded files under ignored `output/`.

## New real-export preparation tool

Use a bid/ask tick export you have permission to use. Normalize a COPY to the exact header `time,bid,ask` and ISO UTC timestamps such as `2025-01-02T07:00:00.123+00:00`. Map the original provider's documented columns and timezone explicitly; do not rename local timestamps as UTC or substitute bid-only prices. The utility deliberately does not guess vendor column names/timezones or scrape undocumented download endpoints.

```bash
python scripts/prepare_gold_ticks.py output/xau-ticks-utc.csv \
  --output output/xau-research.csv \
  --source "Provider, XAU/USD product, export period and UTC settings" \
  --rights-reference "Your actual permission or applicable research-use terms reference"
```

The script produces a dashboard CSV and sidecar source/output SHA-256 manifest. It rejects unordered timestamps, invalid quotes and oversized dashboard output; it never silently fills gaps or truncates a long history. Identical-timestamp ticks retain source order. Review large tick gaps even when every minute contains at least one tick.

The current candle model uses bid OHLC plus the **first observed spread per minute**, held constant for that minute. This preserves a measured spread input without using the minute's future maximum at entry. It is still an approximation: the first quote may arrive after minute open, and actual ask extrema differ. It is not tick-accurate execution, not a validated profitability test, and must be replaced with paired executable quotes/tick replay before relying on fine-grained spread-sensitive findings.

Upload the prepared CSV, put the source/rights reference in provenance, use evidenced product contract/cost settings and preview session completeness. The existing 3000-candle/500 KB bound remains; begin with a short permitted sample. Large dataset storage, full tick execution, licensing qualification and chronological development/holdout evaluation are outstanding. No verified real market file is bundled with this change.
