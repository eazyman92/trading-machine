"""EC2/local parity check; signal reproduction, not a profit simulation."""
import argparse
from datetime import timezone,timedelta
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'.local-deps')]
from tradinglab.upstream_verification import verify,fixture,COMMIT,SHA256

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--ticks',type=Path,help='Optional actual normalized time,bid,ask CSV')
    parser.add_argument('--output',type=Path,default=ROOT/'output/upstream-reproduction/report.json')
    args=parser.parse_args()
    cases={}
    for name,direction,overshoot in [('long',1,False),('short',-1,False),('overshoot',1,True)]:cases[name]=verify(*fixture(direction,overshoot))
    if args.ticks:
        from tradinglab.tick_replay import parse_ticks
        source=args.ticks.read_text();buckets={}
        for t,bid,ask in parse_ticks(source):buckets[t.replace(second=0,microsecond=0)]=float((bid+ask)/2)
        dates=[t.astimezone(timezone(timedelta(hours=-5))) for t in buckets]
        cases['actual_gold']=verify(dates,list(buckets.values()))
        cases['actual_gold']['input_sha256']=__import__('hashlib').sha256(source.encode()).hexdigest()
        cases['actual_gold']['adaptation']='Observed minute midpoint close; fixed UTC-5, no DST correction. Gold input is not the original FX dataset.'
        cases['actual_gold']['has_legacy_12_est_close']=any(t.hour==12 for t in dates)
    report={'status':'upstream_signal_parity_passed','reference':'je-suis-tm/quant-trading','commit':COMMIT,'source_sha256':SHA256,'cases':cases,
            'warning':'Exact signal/threshold reproduction only. No upstream profitability reproduction, broker execution, calibrated gold thresholds, sizing or holdout evidence.'}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({'status':report['status'],'cases':{k:{'rows':v['rows'],'signals':v['nonzero_signals']} for k,v in cases.items()},'report':str(args.output)},indent=2))
