from dataclasses import replace
from decimal import Decimal as D
import json
from pathlib import Path
import pytest
from tradinglab.replay import fixture, replay, size
from tradinglab.contracts import validate

def test_dst_and_no_same_bar_fill():
    bars = fixture()
    assert bars[0].time.hour == 7
    assert bars[541].time.hour == 6
    trades = replay(bars)["trades"]
    assert len(trades) == 2
    assert all(t["entry_at"] == t["signal_at"] for t in trades)
    assert trades[0]["entry_at"].endswith("08:01:00+00:00")
    assert all(t["reason"] == "stop" and D(t["net_usd"]) < 0 for t in trades)

def test_missing_and_duplicate_fail_closed():
    bars = fixture()[:541]
    result = replay(bars[:25]+bars[26:])
    assert not result["trades"] and result["rejected_sessions"]
    with pytest.raises(ValueError): replay([bars[0], bars[0]])

def test_sizing_rounds_down_and_accounts_for_costs():
    entry, stop = D("1.10051"), D("1.10004")
    units = size(entry, stop)
    assert units*(entry-stop+D("0.00001")+D("0.00007")) <= 25
    assert units*entry <= 10000
    assert size(entry, stop, D("0.000001")) == 0

def test_gap_stop_can_exceed_budget():
    bars = fixture()[:541]
    bars[62] = replace(bars[62], bid_open=D("1.09000"), bid_high=D("1.09001"), bid_low=D("1.08999"), bid_close=D("1.09000"))
    trade = replay(bars)["trades"][0]
    assert trade["reason"] == "gap_stop" and D(trade["net_usd"]) < -25

def test_target_and_forced_session_exit():
    bars = fixture()[:541]
    bars[62] = replace(bars[62], bid_open=D("1.10200"), bid_high=D("1.10201"), bid_low=D("1.10199"), bid_close=D("1.10200"))
    assert replay(bars)["trades"][0]["reason"] == "gap_target"
    bars[62] = bars[63]
    bars[62] = replace(bars[62], time=bars[61].time.replace(minute=2))
    trade = replay(bars)["trades"][0]
    assert trade["reason"] == "session_close"
    assert trade["exit_bar_at"].endswith("16:00:00+00:00")

def test_short_uses_ask_to_exit():
    bars = fixture()[:541]
    for i in range(60, 541):
        bars[i] = replace(bars[i], bid_open=D("1.09960"), bid_high=D("1.09961"), bid_low=D("1.09959"), bid_close=D("1.09960"))
    trade = replay(bars)["trades"][0]
    assert trade["side"] == "sell"
    assert D(trade["entry"]) == D("1.09959")
    assert D(trade["exit"]) == D("1.09971")

def test_invalid_prices_and_out_of_order_rejected():
    bars = fixture()[:2]
    with pytest.raises(ValueError): replace(bars[0], bid_open=D("NaN"))
    with pytest.raises(ValueError): replace(bars[0], time=bars[0].time.replace(tzinfo=None))
    with pytest.raises(ValueError): replay(list(reversed(bars)))

def test_contract_vectors():
    cases = json.loads((Path(__file__).parents[1]/"contracts/vectors.json").read_text())
    for c in cases:
        assert validate(c["order"], c["now_ms"]) == c["accepted"], c["name"]
