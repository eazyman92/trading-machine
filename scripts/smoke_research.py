"""Check a running stack through its public HTTP boundary; synthetic jobs only."""
import argparse
import json
import time
import uuid
from urllib.error import HTTPError
from urllib.request import Request, urlopen

CONFIG = {'dataset': 'synthetic-london-dst-v1', 'strategy': 'session-breakout-v0.1', 'symbol': 'EUR_USD'}

def request(base, path, body=None, key=None):
    headers = {'Content-Type': 'application/json'}
    if key: headers['Idempotency-Key'] = key
    req = Request(base+path, data=json.dumps(body).encode() if body is not None else None, headers=headers)
    with urlopen(req, timeout=10) as response:
        return response.status, json.load(response)

def check(base):
    status, health = request(base, '/api/v1/health')
    assert status == 200 and health['status'] == 'ok', health
    key = str(uuid.uuid4())
    status, job = request(base, '/api/v1/research/jobs', CONFIG, key)
    assert status == 202, status
    _, duplicate = request(base, '/api/v1/research/jobs', CONFIG, key)
    assert duplicate['id'] == job['id'], 'Retry created a duplicate job'
    deadline = time.monotonic()+45
    while time.monotonic() < deadline:
        _, job = request(base, '/api/v1/research/jobs/'+job['id'])
        if job['status'] in ('completed', 'failed', 'cancelled'): break
        time.sleep(0.25)
    assert job['status'] == 'completed', job
    result = job['result']
    assert result['data_kind'] == 'synthetic_fixture'
    assert result['bar_count'] == 1082 and len(result['trades']) == 2
    assert len(result['dataset_sha256']) == 64
    try:
        request(base, '/api/v1/research/jobs', CONFIG | {'symbol': 'INVALID'}, str(uuid.uuid4()))
    except HTTPError as exc:
        assert exc.code == 422, exc.code
    else:
        raise AssertionError('Unsupported configuration accepted')
    print('PASS: HTTP readiness, job completion, retry deduplication, fixture result and input rejection')
    print('Job:', job['id'])
    print('Dataset SHA-256:', result['dataset_sha256'])

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--base-url', default='http://127.0.0.1:4173')
    args = parser.parse_args()
    check(args.base_url.rstrip('/'))
