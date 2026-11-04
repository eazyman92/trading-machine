"""Independently authored session-breakout baseline; synthetic research only."""
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal as D, ROUND_FLOOR
from zoneinfo import ZoneInfo

LONDON = ZoneInfo("Europe/London")
TICK = D("0.00001")
FEE = D("0.000035")  # USD/base unit/side: invented fixture, not broker pricing

@dataclass(frozen=True)
class Bar:
    time: datetime  # UTC minute OPEN time
    bid_open: D
    bid_high: D
    bid_low: D
    bid_close: D
    spread: D = D("0.00010")  # constant within this fixture candle

    def __post_init__(self):
        if self.time.tzinfo is None or self.time.utcoffset() != timedelta(0):
            raise ValueError("UTC timestamp required")
        if self.time.second or self.time.microsecond:
            raise ValueError("minute alignment required")
        values = (self.bid_open, self.bid_high, self.bid_low, self.bid_close, self.spread)
        if any(not isinstance(v, D) or not v.is_finite() or v <= 0 for v in values):
            raise ValueError("finite positive Decimal prices required")
        if not self.bid_low <= min(self.bid_open, self.bid_close) <= max(self.bid_open, self.bid_close) <= self.bid_high:
            raise ValueError("invalid OHLC")

def size(entry, stop, budget=D("25")):
    """USD quote/account fixture; floor units, including both fees and exit slip."""
    if budget <= 0 or entry <= 0 or entry == stop:
        raise ValueError("invalid sizing inputs")
    per_unit = abs(entry - stop) + TICK + 2 * FEE
    return max(0, min(10000, int((budget / per_unit).to_integral_value(rounding=ROUND_FLOOR)),
                      int((D("10000") / entry).to_integral_value(rounding=ROUND_FLOOR))))

def replay(bars):
    if any(a.time >= b.time for a, b in zip(bars, bars[1:])):
        raise ValueError("timestamps must be strictly increasing; duplicates rejected")
    groups = {}
    for bar in bars:
        groups.setdefault(bar.time.astimezone(LONDON).date(), []).append(bar)
    trades, rejected = [], []
    for day, daily in groups.items():
        start = datetime(day.year, day.month, day.day, 7, tzinfo=LONDON).astimezone(timezone.utc)
        expected = [start + timedelta(minutes=i) for i in range(541)]
        by_time = {b.time: b for b in daily}
        if day.weekday() >= 5 or any(t not in by_time for t in expected):
            rejected.append({"session": str(day), "reason": "closed_or_incomplete_session"})
            continue
        seq = [by_time[t] for t in expected]
        high = max(b.bid_high + b.spread / 2 for b in seq[:60])
        low = min(b.bid_low + b.spread / 2 for b in seq[:60])
        position = None
        for i in range(61, len(seq)):
            bar, previous = seq[i], seq[i-1]
            # Previous bar is complete at this bar's open: no same-bar fill.
            if position is None and 61 <= i <= 180:
                mid = previous.bid_close + previous.spread / 2
                side = 1 if mid > high + 5*TICK else -1 if mid < low - 5*TICK else 0
                if side:
                    entry = bar.bid_open + bar.spread + TICK if side == 1 else bar.bid_open - TICK
                    stop = low if side == 1 else high
                    if side * (entry-stop) <= 0:
                        continue
                    units = size(entry, stop)
                    if units < 1:
                        continue
                    position = (side, entry, stop, entry + side*2*abs(entry-stop), units, bar.time, previous.time+timedelta(minutes=1))
            if position is None:
                continue
            side, entry, stop, target, units, entered, signal = position
            offset = bar.spread if side == -1 else D(0)
            opened, hi, lo = bar.bid_open+offset, bar.bid_high+offset, bar.bid_low+offset
            stop_hit = lo <= stop if side == 1 else hi >= stop
            target_hit = hi >= target if side == 1 else lo <= target
            gap_stop = opened <= stop if side == 1 else opened >= stop
            gap_target = opened >= target if side == 1 else opened <= target
            price, reason = None, None
            if i == 540:
                price, reason = opened, "session_close"
            elif gap_stop:
                price, reason = opened, "gap_stop"
            elif gap_target:
                price, reason = opened, "gap_target"
            elif stop_hit:  # Conservative when both levels occur within a candle.
                price, reason = stop, "stop"
            elif target_hit:
                price, reason = target, "target"
            if price is not None:
                exit_price = price-side*TICK
                pnl = side*(exit_price-entry)*units-2*FEE*units
                trades.append({"session": str(day), "side": "buy" if side==1 else "sell",
                               "signal_at": signal.isoformat(), "entry_at": entered.isoformat(),
                               "exit_bar_at": bar.time.isoformat(), "units": units,
                               "entry": str(entry), "stop": str(stop), "target": str(target),
                               "exit": str(exit_price), "net_usd": str(pnl), "reason": reason})
                break  # At most one entry per instrument/session.
    return {"data_kind": "synthetic_fixture", "trades": trades, "rejected_sessions": rejected}

def fixture():
    bars = []
    for day in (27, 30):  # Across UK DST transition, 2026-03-29.
        start = datetime(2026, 3, day, 7, tzinfo=LONDON).astimezone(timezone.utc)
        for i in range(541):
            p = D("1.10000") if i < 60 else D("1.10040")
            hi, lo = p+TICK, p-TICK
            if i == 62:
                hi, lo = D("1.10400"), D("1.09600")  # Ambiguous: stop first.
            bars.append(Bar(start+timedelta(minutes=i), p, hi, lo, p))
    return bars
