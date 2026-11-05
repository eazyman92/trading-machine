"""Bounded gold research import. User-declared specifications, never broker defaults."""
import csv
import hashlib
import io
from datetime import datetime, timezone, date, timedelta
from decimal import Decimal as D, ROUND_FLOOR, InvalidOperation
from tradinglab.replay import Bar, replay, LONDON

FIELDS = ['time','bid_open','bid_high','bid_low','bid_close','spread']

def import_csv(text):
    reader=csv.DictReader(io.StringIO(text))
    if reader.fieldnames != FIELDS: raise ValueError('CSV columns must be: '+','.join(FIELDS))
    bars=[]
    for row in reader:
        if len(bars)>=3000: raise ValueError('Maximum 3000 candles per research run')
        timestamp=datetime.fromisoformat(row['time'].replace('Z','+00:00'))
        if timestamp.tzinfo is None: raise ValueError('UTC offset required')
        if timestamp.utcoffset().total_seconds()!=0: raise ValueError('CSV timestamps must be UTC')
        try:
            bars.append(Bar(timestamp.astimezone(timezone.utc), *(D(row[k]) for k in FIELDS[1:])))
        except (InvalidOperation,TypeError) as exc:
            raise ValueError('Invalid decimal price') from exc
    if not bars: raise ValueError('CSV is empty')
    if any(a.time>=b.time for a,b in zip(bars,bars[1:])): raise ValueError('Duplicate or unordered timestamps')
    return bars

def prepare_dataset(text, start_date=None, end_date=None):
    bars=import_csv(text)
    start=date.fromisoformat(str(start_date)) if start_date else None
    end=date.fromisoformat(str(end_date)) if end_date else None
    if start and end and start>end: raise ValueError('Start date must precede end date')
    chosen=[b for b in bars if (not start or b.time.astimezone(LONDON).date()>=start) and (not end or b.time.astimezone(LONDON).date()<=end)]
    if not chosen: raise ValueError('No candles in selected London date range')
    sessions=[]
    for day in sorted({b.time.astimezone(LONDON).date() for b in chosen}):
        first=datetime(day.year,day.month,day.day,7,tzinfo=LONDON).astimezone(timezone.utc)
        present={b.time for b in chosen if b.time.astimezone(LONDON).date()==day}
        missing=sum(first+timedelta(minutes=i) not in present for i in range(541))
        sessions.append({'date':str(day),'missing_session_minutes':missing,'eligible':day.weekday()<5 and missing==0})
    report={'data_kind':'user_supplied_unverified','input_rows':len(bars),'selected_rows':len(chosen),
            'first_utc':chosen[0].time.isoformat(),'last_utc':chosen[-1].time.isoformat(),
            'start_date':str(start) if start else None,'end_date':str(end) if end else None,
            'date_timezone':'Europe/London','sessions':sessions,
            'eligible_sessions':sum(s['eligible'] for s in sessions),
            'minimum_spread_usd':str(min(b.spread for b in chosen)),
            'maximum_spread_usd':str(max(b.spread for b in chosen)),
            'duplicate_policy':'Rejected, never deduplicated silently',
            'warning':'Format validation does not verify market authenticity, rights, price accuracy or broker suitability.'}
    return chosen,report

def run_gold(config):
    bars,quality=prepare_dataset(config['csv_text'],config.get('start_date'),config.get('end_date'))
    spec=config['spec']
    tick, ounces, step, minimum, commission, budget, cap = (D(spec[k]) for k in
        ('tick_usd','ounces_per_lot','lot_step','minimum_lots','commission_usd_per_lot_side','risk_budget_usd','notional_cap_usd'))
    if any(not v.is_finite() or v<=0 for v in (tick,ounces,step,minimum,budget,cap)) or not commission.is_finite() or commission<0:
        raise ValueError('Invalid contract settings')
    if minimum % step != 0: raise ValueError('Minimum lots must be a multiple of lot step')
    sizing_rejections={}
    def sizing(entry,stop):
        per_lot=(abs(entry-stop)+tick)*ounces+2*commission
        lots=(min(budget/per_lot,cap/(entry*ounces))/step).to_integral_value(rounding=ROUND_FLOOR)*step
        if lots<minimum:
            reason='notional_cap_below_minimum' if cap<entry*ounces*minimum else 'risk_budget_below_minimum'
            sizing_rejections[reason]=sizing_rejections.get(reason,0)+1
            return D(0)
        return lots*ounces
    result=replay(bars,tick=tick,fee=commission/ounces,sizing=sizing)
    result['data_kind']='user_supplied_unverified'
    equity=D(0);peak=D(0);drawdown=D(0);wins=0;fees=D(0)
    curve=[{'trade':0,'cumulative_net_usd':'0','drawdown_usd':'0','time':None}]
    for trade in result['trades']:
        quantity=D(trade.pop('units'))
        trade['quantity_lots']=str(quantity/ounces)
        trade['quantity_oz']=str(quantity)
        pnl=D(trade['net_usd']);equity+=pnl;peak=max(peak,equity);drawdown=max(drawdown,peak-equity)
        fees+=2*commission*quantity/ounces
        wins+=pnl>0
        curve.append({'trade':len(curve),'cumulative_net_usd':str(equity),'drawdown_usd':str(peak-equity),'time':trade['exit_bar_at']})
    n=len(result['trades'])
    result['sizing_rejections']=sizing_rejections
    result['no_trade_explanation']=None if n else (
        'Minimum trade size exceeded the notional cap or estimated risk budget; inspect sizing rejections.' if sizing_rejections else
        'All sessions were excluded because data was incomplete or the session was closed.' if result['rejected_sessions'] else
        'No eligible breakout entry was found under the configured rules.')
    result.update(symbol='XAU_USD',strategy_version='gold-session-breakout-v0.1',bar_count=len(bars),
                  dataset_sha256=hashlib.sha256(config['csv_text'].encode()).hexdigest(),
                  provenance=config['provenance'],contract_spec=spec,data_quality=quality,closed_trade_curve=curve,
                  cost_model='User-declared constant intra-candle spread, one adverse tick per fill, per-lot commission',
                  metrics={'net_usd':str(equity),'closed_trade_drawdown_usd':str(drawdown),'commission_usd':str(fees),
                           'trade_count':n,'win_rate':str(D(wins)/n) if n else None},
                  warning='User-supplied data and contract assumptions are unverified. Drawdown uses closed trades only; no intratrade equity, financing, broker margin or holiday model. No live-trading approval.')
    return result
