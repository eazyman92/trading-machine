from concurrent.futures import ThreadPoolExecutor
import json
import uuid
import pytest
from fastapi.testclient import TestClient
from tradinglab.api import app
from tradinglab.store import Store, Conflict
from tradinglab.worker import process_one

CONFIG = {'dataset':'synthetic-london-dst-v1','strategy':'session-breakout-v0.1','symbol':'EUR_USD'}

@pytest.fixture
def store(tmp_path, monkeypatch):
    monkeypatch.setenv('DATABASE_URL', 'sqlite:///'+str(tmp_path/'jobs.db'))
    s=Store(); s.migrate(); return s

def test_api_worker_persistence_and_idempotency(store):
    with TestClient(app) as client:
        key={'Idempotency-Key':str(uuid.uuid4())}
        response=client.post('/api/v1/research/jobs',json=CONFIG,headers=key)
        assert response.status_code==202
        job=response.json()
        assert client.post('/api/v1/research/jobs',json=CONFIG,headers=key).json()['id']==job['id']
        assert process_one(store)
        done=client.get('/api/v1/research/jobs/'+job['id']).json()
        assert done['status']=='completed' and len(done['result']['trades'])==2
        assert len(done['result']['dataset_sha256'])==64
        assert Store().get(job['id'])['result']==done['result']
        assert not process_one(store)

def test_validation_and_unknown_jobs(store):
    with TestClient(app) as client:
        key={'Idempotency-Key':str(uuid.uuid4())}
        assert client.post('/api/v1/research/jobs',json=CONFIG|{'symbol':'GBP_USD'},headers=key).status_code==422
        assert client.post('/api/v1/research/jobs',json=CONFIG|{'live':True},headers=key).status_code==422
        assert client.post('/api/v1/research/jobs',json=CONFIG).status_code==422
        assert client.get('/api/v1/research/jobs/'+str(uuid.uuid4())).status_code==404

def test_concurrent_claim_and_cancel_wins(store):
    job=store.create(str(uuid.uuid4()),CONFIG)
    with ThreadPoolExecutor(max_workers=2) as pool:
        claimed=list(pool.map(lambda _:store.claim(),range(2)))
    assert sum(c is not None for c in claimed)==1
    store.cancel(job['id'])
    store.finish(job['id'],result={'late':True})
    assert store.get(job['id'])['status']=='cancelled'
    assert store.get(job['id'])['result'] is None

def test_expired_worker_and_failure(store):
    job=store.create(str(uuid.uuid4()),CONFIG)
    store.claim()
    with store.connection() as conn:
        store.sql(conn,'UPDATE research_jobs SET lease_until=0 WHERE id=?',(job['id'],))
    assert store.claim() is None
    assert store.get(job['id'])['error']=='worker_lease_expired'
    store.finish(job['id'],result={'late':True})
    assert store.get(job['id'])['status']=='failed'
    broken=store.create(str(uuid.uuid4()),{'invalid':True})
    assert process_one(store)
    assert store.get(broken['id'])['error']=='replay_failed'

def test_idempotency_configuration_conflict(store):
    key=str(uuid.uuid4());store.create(key,CONFIG)
    with pytest.raises(Conflict):store.create(key,CONFIG|{'symbol':'other'})

def test_history_pagination_and_reopen(store):
    ids=[store.create(str(uuid.uuid4()),CONFIG)['id'] for _ in range(3)]
    assert process_one(store)
    with TestClient(app) as client:
        page=client.get('/api/v1/research/jobs?limit=2').json()
        assert [j['id'] for j in page['items']]==list(reversed(ids))[0:2]
        assert page['next_offset']==2
        assert 'result' not in page['items'][0] and 'request_key' not in page['items'][0]
        last=client.get('/api/v1/research/jobs?limit=2&offset=2').json()
        assert last['items'][0]['id']==ids[0] and last['next_offset'] is None
        reopened=client.get('/api/v1/research/jobs/'+ids[0]).json()
        assert reopened['status']=='completed' and len(reopened['result']['trades'])==2
        for query in ('limit=0','limit=101','offset=-1'):
            assert client.get('/api/v1/research/jobs?'+query).status_code==422
