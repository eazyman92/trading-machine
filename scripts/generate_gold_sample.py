"""Create artificial gold candles for testing the import UI, never historical data."""
from pathlib import Path
import sys
from decimal import Decimal as D
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'.local-deps')]
from tradinglab.replay import fixture

if __name__=='__main__':
    rows=['time,bid_open,bid_high,bid_low,bid_close,spread']
    for b in fixture():
        prices=[D('2000')+(v-D('1.1'))*5000 for v in (b.bid_open,b.bid_high,b.bid_low,b.bid_close)]
        rows.append(','.join(map(str,[b.time.isoformat(),*prices,D('.20')])))
    path=ROOT/'output/gold-synthetic-import.csv'
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text('\n'.join(rows)+'\n',encoding='utf-8')
    print('SYNTHETIC test candles, not historical gold data:',path)
