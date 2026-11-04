"""Separate research process; bounded synthetic workloads only."""
import hashlib
import json
import time
from dataclasses import asdict
from tradinglab.replay import fixture, replay
from tradinglab.store import Store

def process_one(store):
    job = store.claim()
    if job is None: return False
    try:
        config = job['config']
        if config != {'dataset': 'synthetic-london-dst-v1', 'strategy': 'session-breakout-v0.1', 'symbol': 'EUR_USD'}:
            raise ValueError('unsupported_configuration')
        bars = fixture()
        result = replay(bars)
        result.update({'strategy_version': config['strategy'], 'symbol': config['symbol'],
                       'bar_count': len(bars), 'dataset_version': config['dataset'],
                       'dataset_sha256': hashlib.sha256(json.dumps([asdict(b) for b in bars], default=str, sort_keys=True).encode()).hexdigest(),
                       'cost_model': 'fixture-v1: fixed spread, 1 adverse tick/fill, $35/million units/side',
                       'warning': 'Synthetic engineering fixtures; not historical performance or evidence of profitability.'})
        store.finish(job['id'], result=result)
    except Exception:
        # Do not expose stack traces, database URLs or credentials to API clients.
        store.finish(job['id'], error='replay_failed')
    return True

if __name__ == '__main__':
    store = Store()
    print('Synthetic research worker ready', flush=True)
    while True:
        try:
            if not process_one(store): time.sleep(0.5)
        except Exception:
            print('Queue unavailable; retrying', flush=True)
            time.sleep(2)
