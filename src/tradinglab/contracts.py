"""Fixture policy, not a production account risk service. Integer units only."""
FIELDS = {"schema_version", "environment", "symbol", "side", "quantity_units", "entry_ticks", "stop_ticks", "target_ticks", "quote_at_ms", "expires_at_ms"}
NUMBERS = FIELDS - {"environment", "symbol", "side"}

def validate(order, now_ms):
    if set(order) != FIELDS or any(type(order[k]) is not int or not 0 < order[k] <= 10**15 for k in NUMBERS):
        return False
    if order["schema_version"] != 1 or order["environment"] != "paper" or order["symbol"] not in ("EUR_USD", "GBP_USD") or order["side"] not in ("buy", "sell"):
        return False
    q, e, s, t = (order[k] for k in ("quantity_units", "entry_ticks", "stop_ticks", "target_ticks"))
    if q > 10000 or not 0 <= now_ms-order["quote_at_ms"] <= 2000 or not 0 < order["expires_at_ms"]-now_ms <= 60000:
        return False
    if not (s < e < t if order["side"] == "buy" else t < e < s):
        return False
    # Tick=1e-5 USD; USD amounts use 1e-6 scaling. Fee=35 microUSD/unit/side.
    loss = q*((abs(e-s)+1)*10+70)
    notional = q*e*10
    return loss <= 25_000_000 and notional <= 10_000_000_000
