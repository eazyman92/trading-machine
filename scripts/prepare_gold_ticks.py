"""Prepare a permitted real-data export; keep source files out of Git."""
import argparse
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from tradinglab.tick_import import convert

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('input',type=Path)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--source',required=True,help='Provider, product, export settings and period')
    p.add_argument('--rights-reference',required=True,help='Recorded permission/terms reference for your research use')
    args=p.parse_args()
    data,manifest=convert(args.input.read_text(encoding='utf-8-sig'))
    if manifest['minute_count']>200000 or len(data.encode())>20000000:
        raise SystemExit('Export a shorter period: dataset library accepts at most 200000 candles / 20 MB. No silent truncation performed.')
    manifest.update(source=args.source,rights_reference=args.rights_reference,data_kind='user_supplied_unverified')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x',encoding='utf-8',newline='') as f:f.write(data)
    with args.output.with_suffix('.manifest.json').open('x',encoding='utf-8') as f:json.dump(manifest,f,indent=2)
    print('Prepared:',args.output)
    print('Inspect manifest and validate in dashboard before running research.')
