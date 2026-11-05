from datetime import datetime,timedelta,timezone
from decimal import Decimal as D
import json
from pathlib import Path
import pytest
from tradinglab.tick_replay import replay_ticks,parse_ticks

CONFIG=json.loads((Path(__file__).parents[1]/'contracts/gold-tick-replay.example.json').read_text())

def quotes(short=False,exit_bid='1999',extra=None):
    start=datetime(2024,1,15,7,tzinfo=timezone.utc)
    rows=['time,bid,ask']
    for i in range(541):
        bid=D('2000') if i<60 else D('1998' if short else '2002')
        if i==62:bid=D(exit_bid)
        t=start+timedelta(minutes=i,milliseconds=250)
        rows.append(f'{t.isoformat()},{bid},{bid+D(".2")}')
        if i==62 and extra is not None:rows.append(f'{t.isoformat()},{extra},{D(extra)+D(".2")}')
    return '\n'.join(rows)

def test_completed_bar_next_quote_and_actual_bid_exit():
    result=replay_ticks(quotes(),CONFIG['spec'])
    t=result['trades'][0]
    assert t['entry_at'].startswith('2024-01-15T08:01:00.250')
    assert t['signal_available_at'].startswith('2024-01-15T08:01:00+')
    assert t['quantity_lots']=='0.04'
    assert D(t['entry'])==D('2002.201') and D(t['exit'])==D('1998.999')
    assert D(t['net_usd'])==D('-13.36800')
    assert result==replay_ticks(quotes(),CONFIG['spec'])
    assert D(t['estimated_stop_risk_usd'])<=25

def test_short_ask_side_and_target():
    t=replay_ticks(quotes(short=True,exit_bid='1990'),CONFIG['spec'])['trades'][0]
    assert t['side']=='sell' and D(t['entry'])==D('1997.999')
    assert D(t['exit'])==D('1990.201') and t['reason']=='target'

def test_source_order_resolves_equal_timestamp_quotes():
    win=replay_ticks(quotes(exit_bid='2010',extra='1990'),CONFIG['spec'])['trades'][0]
    loss=replay_ticks(quotes(exit_bid='1990',extra='2010'),CONFIG['spec'])['trades'][0]
    assert win['reason']=='target' and loss['reason']=='stop'

def test_spread_filter_sizing_gap_and_force_close():
    filtered=replay_ticks(quotes(),CONFIG['spec'],{'max_spread_usd':'.1'})
    assert not filtered['trades'] and any(e.get('reason')=='spread_limit' for e in filtered['ledger'])
    limited=replay_ticks(quotes(),CONFIG['spec']|{'notional_cap_usd':'1000'})
    assert not limited['trades'] and any(e.get('reason')=='minimum_size_exceeds_limits' for e in limited['ledger'])
    gap=replay_ticks(quotes(exit_bid='1900'),CONFIG['spec'])['trades'][0]
    assert D(gap['net_usd']) < -25
    closed=replay_ticks(quotes(exit_bid='2002'),CONFIG['spec'])['trades'][0]
    assert closed['reason']=='session_close' and '16:00:00.250' in closed['exit_at']

def test_missing_session_and_invalid_quotes_fail_closed():
    source=quotes().splitlines();source.pop(20)
    report=replay_ticks('\n'.join(source),CONFIG['spec'])
    assert not report['trades'] and report['excluded_sessions'][0]['missing_minutes']==1
    for text in ['time,bid,ask\n2024-01-15T07:00:00Z,NaN,2001','time,bid,ask\n2024-01-15T07:00:00,2000,2001']:
        with pytest.raises(ValueError):parse_ticks(text)

def test_entry_rejects_already_crossed_stop():
    rows=quotes().splitlines()
    timestamp=rows[62].split(',')[0]
    rows[62]=timestamp+',1999,2005'
    result=replay_ticks('\n'.join(rows),CONFIG['spec'])
    assert any(e.get('reason')=='invalid_stop_after_gap' for e in result['ledger'])
