"""Acquire a small public technical sample, keeping raw data out of Git."""
import argparse
from datetime import datetime
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'.local-deps')]
from tradinglab.dukascopy import acquire

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--start',required=True,help='UTC hour, e.g. 2024-01-15T07:00:00+00:00')
    parser.add_argument('--hours',type=int,default=10)
    parser.add_argument('--price-scale',required=True,help='Explicit scale; not inferred from symbol')
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--reference-price',help='Independent daily decimal price used only for a 5% scale sanity check')
    parser.add_argument('--reference-source',help='URL/receipt identifying that reference and its date')
    parser.add_argument('--offline',action='store_true',help='Require cached raw files; never contact provider')
    args=parser.parse_args()
    report=acquire(datetime.fromisoformat(args.start.replace('Z','+00:00')),args.hours,args.price_scale,args.output,args.reference_price,args.reference_source,args.offline)
    print('ACTUAL provider ticks:',sum(f['tick_count'] for f in report['files']))
    print('Complete London sessions:',report['sessions']['eligible_sessions'])
    print('Technical sample only; read manifest qualification limits before use.')
