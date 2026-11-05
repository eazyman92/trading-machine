"""Local technical integration check using downloaded sample; never live orders."""
import hashlib
import json
import os
from pathlib import Path
import sys
import uuid
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'.local-deps')]
from tradinglab.datasets import register
from tradinglab.store import Store
from tradinglab.worker import process_one

if __name__=='__main__':
    folder=ROOT/'output/market-data/xauusd-2024-01-15'
    manifest=json.loads((folder/'manifest.json').read_text())
    text=(folder/'candles.csv').read_text()
    if hashlib.sha256(text.encode()).hexdigest()!=manifest['candle_sha256']:raise SystemExit('Candle hash mismatch')
    if manifest['sessions']['eligible_sessions']!=1:raise SystemExit('Expected one complete technical session')
    # Isolate technical sample records from the dashboard workspace and its settings.
    os.environ['DATASET_DIR']=str(folder/'integration-datasets')
    os.environ['DATABASE_URL']='sqlite:///'+str(folder/'integration.db')
    item=register(text,'Dukascopy HTTPS technical sample 2024-01-15; see acquisition manifest',
                  'Public endpoint technical evaluation only; commercial usage/redistribution unapproved')
    spec=dict(tick_usd='.001',ounces_per_lot='100',lot_step='.01',minimum_lots='.01',commission_usd_per_lot_side='7',risk_budget_usd='25',notional_cap_usd='10000')
    store=Store();store.migrate()
    job=store.create(str(uuid.uuid4()),{'dataset_id':item['id'],'symbol':'XAU_USD','strategy':'gold-session-breakout-v0.2',
                                     'dataset':'stored-csv-v1','provenance':item['source'],'spec':spec})
    while store.get(job['id'])['status']=='queued':
        if not process_one(store):raise SystemExit('No research job processed')
    completed=store.get(job['id'])
    if completed['status']!='completed':raise SystemExit('Research integration failed')
    result=completed['result']
    assert result['dataset_sha256']==manifest['candle_sha256']
    assert result['bar_count']==600 and not result['rejected_sessions']
    receipt={'status':'technical_ingestion_verified','dataset_sha256':result['dataset_sha256'],'bars':result['bar_count'],
             'actual_tick_count':sum(f['tick_count'] for f in manifest['files']),
             'warning':'Sizing/commission inputs are invented engineering fixtures, not broker specs. No strategy effectiveness conclusion.',
             'job_id':job['id']}
    (folder/'ingestion-receipt.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
    print(json.dumps(receipt,indent=2))
