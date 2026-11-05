"""Run repeatable technical replay of acquired quotes, without a broker."""
import argparse
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'.local-deps')]
from tradinglab.tick_replay import replay_ticks

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--input',type=Path,default=ROOT/'output/market-data/xauusd-2024-01-15/ticks.csv')
    parser.add_argument('--output',type=Path,default=ROOT/'output/tick-replay/report.json')
    parser.add_argument('--config',type=Path,required=True)
    args=parser.parse_args();config=json.loads(args.config.read_text())
    text=args.input.read_text()
    report=replay_ticks(text,config['spec'],config.get('rules'))
    assert report==replay_ticks(text,config['spec'],config.get('rules')),'Non-reproducible replay'
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({'status':'reproduced_identically','tick_count':report['tick_count'],'trades':len(report['trades']),'report':str(args.output),'warning':'Inputs are user-declared research assumptions; no broker or strategy approval.'},indent=2))
