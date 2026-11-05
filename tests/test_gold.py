from decimal import Decimal as D
from datetime import timedelta
import uuid
import pytest
from fastapi.testclient import TestClient
from tradinglab.api import app
from tradinglab.gold import import_csv, run_gold
from tradinglab.replay import fixture
from tradinglab.store import Store
from tradinglab.worker import process_one

def config():
    rows=['time,bid_open,bid_high,bid_low,bid_close,spread']
    source=fixture()[:541]
    for b in source:
        p=D('2000') if b.time<source[0].time+timedelta(minutes=60) else D('2002')
        high,low=p+D('.01'),p-D('.01')
        if len(rows)==63:high,low=D('2010'),D('1990')
        rows.append(','.join(map(str,[b.time.isoformat(),p,high,low,p,D('.20')])))
    return {'csv_text':'\n'.join(rows),'provenance':'Synthetic test only, not market history','rights_confirmed':True,
            'spec':dict(tick_usd='.01',ounces_per_lot='100',lot_step='.01',minimum_lots='.01',commission_usd_per_lot_side='7',risk_budget_usd='25',notional_cap_usd='10000')}

def test_gold_contract_costs_and_lot_floor():
    result=run_gold(config());trade=result['trades'][0]
    # Five ounces would exceed the $10,000 cap at the actual ask+slippage entry.
    assert trade['quantity_lots']=='0.04' and trade['quantity_oz']=='4.00'
    assert D(trade['net_usd'])==D('-9.08')
    assert result['data_kind']=='user_supplied_unverified'
    assert result['metrics']['trade_count']==1

def test_bad_gold_data():
    text=config()['csv_text']
    with pytest.raises(ValueError):import_csv(text+'\n'+text.splitlines()[-1])
    with pytest.raises(ValueError):import_csv(text.replace('2000','NaN'))
    with pytest.raises(ValueError):import_csv('time,price\n2026-03-27,2000')

def test_gold_api_worker(tmp_path,monkeypatch):
    monkeypatch.setenv('DATABASE_URL','sqlite:///'+str(tmp_path/'gold.db'))
    store=Store();store.migrate()
    with TestClient(app) as client:
        headers={'Idempotency-Key':str(uuid.uuid4())}
        response=client.post('/api/v1/research/gold/jobs',json=config(),headers=headers)
        assert response.status_code==202,response.text
        assert process_one(store)
        job=store.get(response.json()['id'])
        assert job['status']=='completed' and job['result']['symbol']=='XAU_USD'
        bad=config();bad['rights_confirmed']=False
        assert client.post('/api/v1/research/gold/jobs',json=bad,headers=headers).status_code==422
