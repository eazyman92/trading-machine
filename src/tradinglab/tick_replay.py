"""Deterministic, single-instrument research replay against actual paired quotes."""
import csv
import hashlib
import io
import json
from datetime import datetime,timedelta
from decimal import Decimal as D, ROUND_FLOOR, ROUND_CEILING
from tradinglab.replay import LONDON

def parse_ticks(text):
    reader=csv.DictReader(io.StringIO(text))
    if reader.fieldnames!=['time','bid','ask']:raise ValueError('Expected time,bid,ask')
    ticks=[];previous=None
    for row in reader:
        t=datetime.fromisoformat(row['time'].replace('Z','+00:00'))
        if t.tzinfo is None or t.utcoffset()!=timedelta(0):raise ValueError('UTC ticks required')
        bid,ask=D(row['bid']),D(row['ask'])
        if any(not v.is_finite() or v<=0 for v in (bid,ask)) or ask<=bid:raise ValueError('Invalid paired quote')
        if previous is not None and t<previous:raise ValueError('Unordered ticks')
        previous=t;ticks.append((t,bid,ask))
        if len(ticks)>2_000_000:raise ValueError('Tick replay limited to two million quotes')
    if not ticks:raise ValueError('Empty quotes')
    return ticks

def replay_ticks(text,spec,rules=None):
    ticks=parse_ticks(text)
    config={'buffer_ticks':5,'reward_multiple':'2','max_spread_usd':None,'slippage_ticks':1}|(rules or {})
    tick,oz,step,minimum,fee,budget,cap=(D(str(spec[k])) for k in ('tick_usd','ounces_per_lot','lot_step','minimum_lots','commission_usd_per_lot_side','risk_budget_usd','notional_cap_usd'))
    if any(not v.is_finite() or v<=0 for v in (tick,oz,step,minimum,budget,cap)) or not fee.is_finite() or fee<0 or minimum%step:
        raise ValueError('Invalid gold contract/cost inputs')
    buffer=config['buffer_ticks'];slips=config['slippage_ticks'];reward=D(str(config['reward_multiple']))
    if type(buffer) is not int or not 0<=buffer<=10000 or type(slips) is not int or not 0<=slips<=100:
        raise ValueError('Invalid integer rule')
    if not reward.is_finite() or not D('.25')<=reward<=10:raise ValueError('Invalid reward multiple')
    max_spread=D(str(config['max_spread_usd'])) if config['max_spread_usd'] is not None else None
    if max_spread is not None and (not max_spread.is_finite() or max_spread<=0):raise ValueError('Invalid maximum spread')
    slip=tick*slips
    days={}
    for sequence,(t,bid,ask) in enumerate(ticks):days.setdefault(t.astimezone(LONDON).date(),[]).append((sequence,t,bid,ask))
    trades=[];ledger=[];excluded=[];curve=[{'trade':0,'net_usd':'0','drawdown_usd':'0'}]
    total=D(0);peak=D(0);drawdown=D(0);fees=D(0)
    def event(kind,seq,t,**fields):ledger.append({'event':kind,'quote_sequence':seq,'time':t.isoformat(),**fields})
    def rounded(value,up):return (value/tick).to_integral_value(rounding=ROUND_CEILING if up else ROUND_FLOOR)*tick
    for day,quotes in days.items():
        start=datetime(day.year,day.month,day.day,7,tzinfo=LONDON)
        minutes={q[1].astimezone(LONDON).replace(second=0,microsecond=0) for q in quotes}
        missing=sum(start+timedelta(minutes=i) not in minutes for i in range(541))
        if day.weekday()>4 or missing:
            excluded.append({'session':str(day),'reason':'offline_incomplete_or_weekend','missing_minutes':missing});continue
        range_high=None;range_low=None;minute=None;last_close=None;pos=None;entered=False
        for seq,t,bid,ask in quotes:
            local=t.astimezone(LONDON);current=local.replace(second=0,microsecond=0)
            mid=(bid+ask)/2
            changed=minute is not None and current!=minute
            if pos:
                side=pos['side'];executable=bid if side==1 else ask
                hit_stop=executable<=pos['stop'] if side==1 else executable>=pos['stop']
                hit_target=executable>=pos['target'] if side==1 else executable<=pos['target']
                reason='stop' if hit_stop else 'target' if hit_target else 'session_close' if local.hour>=16 else None
                if reason:
                    price=executable-side*slip
                    commission=2*fee*pos['lots'];pnl=side*(price-pos['entry'])*pos['lots']*oz-commission
                    total+=pnl;fees+=commission;peak=max(peak,total);drawdown=max(drawdown,peak-total)
                    trade={**{k:str(v) for k,v in pos.items() if k not in ('side','lots')},'side':'buy' if side==1 else 'sell',
                           'quantity_lots':str(pos['lots']),'quantity_oz':str(pos['lots']*oz),'exit_at':t.isoformat(),
                           'exit':str(price),'net_usd':str(pnl),'commission_usd':str(commission),'reason':reason,'session':str(day)}
                    trades.append(trade);event('exit_fill',seq,t,price=str(price),reason=reason,net_usd=str(pnl))
                    curve.append({'trade':len(trades),'net_usd':str(total),'drawdown_usd':str(peak-total)})
                    pos=None
            # Range uses observed midpoint ticks only; no ask approximation.
            if 7<=local.hour<8:
                range_high=mid if range_high is None else max(range_high,mid)
                range_low=mid if range_low is None else min(range_low,mid)
            if changed and not entered and 8<=minute.hour<10 and current==minute+timedelta(minutes=1) and range_high is not None:
                side=1 if last_close>range_high+buffer*tick else -1 if last_close<range_low-buffer*tick else 0
                if side:
                    event('signal',seq,t,side='buy' if side==1 else 'sell',signal_bar_open=minute.isoformat(),
                          signal_available_at=(minute+timedelta(minutes=1)).isoformat(),mid_close=str(last_close),range_high=str(range_high),range_low=str(range_low))
                    if max_spread is not None and ask-bid>max_spread:
                        event('entry_rejected',seq,t,reason='spread_limit')
                    else:
                        entry=(ask if side==1 else bid)+side*slip
                        stop=rounded(range_low if side==1 else range_high,side==-1)
                        if side*(entry-stop)<=0 or (bid<=stop if side==1 else ask>=stop):event('entry_rejected',seq,t,reason='invalid_stop_after_gap')
                        else:
                            per_lot=(abs(entry-stop)+slip)*oz+2*fee
                            lots=(min(budget/per_lot,cap/(entry*oz))/step).to_integral_value(rounding=ROUND_FLOOR)*step
                            if lots<minimum:event('entry_rejected',seq,t,reason='minimum_size_exceeds_limits')
                            else:
                                pos={'side':side,'lots':lots,'entry':entry,'stop':stop,'target':rounded(entry+side*reward*abs(entry-stop),side==1),
                                     'entry_at':t.isoformat(),'signal_available_at':(minute+timedelta(minutes=1)).isoformat(),'estimated_stop_risk_usd':per_lot*lots}
                                entered=True;event('entry_fill',seq,t,price=str(entry),lots=str(lots),stop=str(stop),target=str(pos['target']))
            minute=current;last_close=mid
        if pos:raise ValueError('Position has no post-16:00 executable exit quote')
    signature={'engine':'gold-paired-tick-v1','spec':spec,'rules':config}
    return {'engine':'gold-paired-tick-v1','mode':'research_only','input_sha256':hashlib.sha256(text.encode()).hexdigest(),
            'configuration_sha256':hashlib.sha256(json.dumps(signature,sort_keys=True,default=str).encode()).hexdigest(),
            'tick_count':len(ticks),'trades':trades,'ledger':ledger,'excluded_sessions':excluded,'closed_trade_curve':curve,
            'metrics':{'net_usd':str(total),'commission_usd':str(fees),'closed_trade_drawdown_usd':str(drawdown),'trade_count':len(trades)},
            'assumptions':'Single gold product/USD account; observed quotes plus fixed adverse slippage; no latency, depth, financing, broker margin or partial fills. Equal-time ticks preserve source order; exits cannot precede entry source sequence. Complete-session filtering is offline research only.'}
