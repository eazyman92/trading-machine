"""Generate shared Python/Rust boundary fixtures, not market observations."""
import json
from pathlib import Path

base = dict(schema_version=1, environment="paper", symbol="EUR_USD", side="buy",
            quantity_units=1000, entry_ticks=110051, stop_ticks=110004,
            target_ticks=110145, quote_at_ms=100000, expires_at_ms=110000)
cases = []
def add(name, accepted, **changes):
    cases.append(dict(name=name, accepted=accepted, now_ms=101000, order=base | changes))
add("valid paper", True)
add("live blocked", False, environment="live")
add("stale quote", False, quote_at_ms=98000)
add("future quote", False, quote_at_ms=102000)
add("expired", False, expires_at_ms=101000)
add("long expiry", False, expires_at_ms=162000)
add("unsupported instrument", False, symbol="USD_JPY")
add("fractional units", False, quantity_units=1.5)
add("boolean units", False, quantity_units=True)
add("negative units", False, quantity_units=-1)
add("excess quantity", False, quantity_units=10001)
add("stop geometry", False, stop_ticks=110060)
add("risk exceeded", False, stop_ticks=100000)
add("notional exceeded", False, quantity_units=10000)
add("unknown field", False, broker_token="fixture")
add("valid sell", True, side="sell", stop_ticks=110098, target_ticks=109957)
add("overflow attempt", False, quantity_units=10**18)
Path(__file__).with_name("vectors.json").write_text(json.dumps(cases, indent=2)+"\n", encoding="utf-8")
