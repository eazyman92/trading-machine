from decimal import Decimal as D
from datetime import timedelta
import uuid
import pytest
from fastapi.testclient import TestClient
from tradinglab.api import app
from tradinglab.gold import import_csv, run_gold
from tradinglab.gold import prepare_dataset
from tradinglab.comparison import compare
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

def test_versioned_strategy_rules_and_decision_evidence():
    c=config();baseline=run_gold(c)
    evidence=baseline['trades'][0]['signal_evidence']
    assert evidence['rule']=='completed_close_above_range'
    assert D(evidence['estimated_stop_risk_usd'])<=D('25')
    assert baseline['promotion_status']=='research_only'
    assert baseline['strategy_config_sha256']==run_gold(c)['strategy_config_sha256']
    c['rules']={'buffer_ticks':1000,'reward_multiple':'2','max_spread_usd':None}
    candidate=run_gold(c)
    assert not candidate['trades']
    assert baseline['strategy_config_sha256']!=candidate['strategy_config_sha256']
    report=compare({'id':'a','status':'completed','result':baseline},{'id':'b','status':'completed','result':candidate})
    assert 'buffer_ticks' in report['changed_rules']
    c['rules']={'buffer_ticks':5,'reward_multiple':'2','max_spread_usd':'.10'}
    spread=run_gold(c)
    assert not spread['trades'] and spread['spread_rejected_attempts']>0

def test_bad_gold_data():
    text=config()['csv_text']
    with pytest.raises(ValueError):import_csv(text+'\n'+text.splitlines()[-1])
    with pytest.raises(ValueError):import_csv(text.replace('2000','NaN'))
    with pytest.raises(ValueError):import_csv('time,price\n2026-03-27,2000')

def test_preview_range_gaps_and_curve():
    c=config()
    bars,quality=prepare_dataset(c['csv_text'],'2026-03-27','2026-03-27')
    assert len(bars)==541 and quality['eligible_sessions']==1
    missing='\n'.join(c['csv_text'].splitlines()[:20]+c['csv_text'].splitlines()[21:])
    assert prepare_dataset(missing)[1]['sessions'][0]['missing_session_minutes']==1
    for start,end in [('2026-03-30','2026-03-27'),('2027-01-01',None)]:
        with pytest.raises(ValueError):prepare_dataset(c['csv_text'],start,end)
    result=run_gold(c)
    assert result['closed_trade_curve'][-1]['cumulative_net_usd']==result['metrics']['net_usd']
    assert result['closed_trade_curve'][-1]['drawdown_usd']==result['metrics']['closed_trade_drawdown_usd']

def test_comparison_checks_and_discloses_cost_changes():
    a=run_gold(config());c=config();c['spec']['commission_usd_per_lot_side']='14';b=run_gold(c)
    left={'id':'left','status':'completed','result':a};right={'id':'right','status':'completed','result':b}
    assert 'commission_usd_per_lot_side' in compare(left,right)['changed_settings']
    b['dataset_sha256']='different'
    with pytest.raises(ValueError):compare(left,right)
    b['dataset_sha256']=a['dataset_sha256'];b['data_quality']['start_date']='2026-03-27'
    with pytest.raises(ValueError):compare(left,right)

def test_dataset_preview_api():
    with TestClient(app) as client:
        body={'csv_text':config()['csv_text'],'start_date':'2026-03-27','end_date':'2026-03-27'}
        response=client.post('/api/v1/research/gold/validate',json=body)
        assert response.status_code==200 and response.json()['eligible_sessions']==1
        body['end_date']='2026-03-26'
        assert client.post('/api/v1/research/gold/validate',json=body).status_code==422

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

def test_gold_no_trade_diagnostics():
    small=config();small['spec']['notional_cap_usd']='1000'
    result=run_gold(small)
    assert not result['trades']
    assert result['sizing_rejections']['notional_cap_below_minimum']>0
    assert 'Minimum trade size' in result['no_trade_explanation']
    small=config();small['spec']['risk_budget_usd']='0.01'
    assert run_gold(small)['sizing_rejections']['risk_budget_below_minimum']>0

def test_submission_recovery_without_duplicate(tmp_path,monkeypatch):
    monkeypatch.setenv('DATABASE_URL','sqlite:///'+str(tmp_path/'recover.db'))
    store=Store();store.migrate()
    key=str(uuid.uuid4())
    with TestClient(app) as client:
        route='/api/v1/research/requests/'+key
        assert client.get(route).status_code==404
        first=client.post('/api/v1/research/gold/jobs',json=config(),headers={'Idempotency-Key':key})
        assert first.status_code==202
        # Model a lost POST response: recover using only its original request key.
        recovered=client.get(route)
        assert recovered.status_code==200 and recovered.json()['id']==first.json()['id']
        retried=client.post('/api/v1/research/gold/jobs',json=config(),headers={'Idempotency-Key':key})
        assert retried.json()['id']==first.json()['id']
        assert len(store.list_jobs()['items'])==1
        changed=config();changed['spec']['risk_budget_usd']='30'
        assert client.post('/api/v1/research/gold/jobs',json=changed,headers={'Idempotency-Key':key}).status_code==409
