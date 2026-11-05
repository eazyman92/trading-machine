"""Bounded gold research import. User-declared specifications, never broker defaults."""
import csv
import hashlib
import io
from datetime import datetime, timezone
from decimal import Decimal as D, ROUND_FLOOR, InvalidOperation
from tradinglab.replay import Bar, replay

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

def run_gold(config):
    bars=import_csv(config['csv_text'])
    spec=config['spec']
    tick, ounces, step, minimum, commission, budget, cap = (D(spec[k]) for k in
        ('tick_usd','ounces_per_lot','lot_step','minimum_lots','commission_usd_per_lot_side','risk_budget_usd','notional_cap_usd'))
    if any(not v.is_finite() or v<=0 for v in (tick,ounces,step,minimum,budget,cap)) or not commission.is_finite() or commission<0:
        raise ValueError('Invalid contract settings')
    if minimum % step != 0: raise ValueError('Minimum lots must be a multiple of lot step')
    def sizing(entry,stop):
        per_lot=(abs(entry-stop)+tick)*ounces+2*commission
        lots=(min(budget/per_lot,cap/(entry*ounces))/step).to_integral_value(rounding=ROUND_FLOOR)*step
        return lots*ounces if lots>=minimum else D(0)
    result=replay(bars,tick=tick,fee=commission/ounces,sizing=sizing)
    result['data_kind']='user_supplied_unverified'
    equity=D(0);peak=D(0);drawdown=D(0);wins=0;fees=D(0)
    for trade in result['trades']:
        quantity=D(trade.pop('units'))
        trade['quantity_lots']=str(quantity/ounces)
        trade['quantity_oz']=str(quantity)
        pnl=D(trade['net_usd']);equity+=pnl;peak=max(peak,equity);drawdown=max(drawdown,peak-equity)
        fees+=2*commission*quantity/ounces
        wins+=pnl>0
    n=len(result['trades'])
    result.update(symbol='XAU_USD',strategy_version='gold-session-breakout-v0.1',bar_count=len(bars),
                  dataset_sha256=hashlib.sha256(config['csv_text'].encode()).hexdigest(),
                  provenance=config['provenance'],contract_spec=spec,
                  cost_model='User-declared constant intra-candle spread, one adverse tick per fill, per-lot commission',
                  metrics={'net_usd':str(equity),'closed_trade_drawdown_usd':str(drawdown),'commission_usd':str(fees),
                           'trade_count':n,'win_rate':str(D(wins)/n) if n else None},
                  warning='User-supplied data and contract assumptions are unverified. Drawdown uses closed trades only; no intratrade equity, financing, broker margin or holiday model. No live-trading approval.')
    return result
