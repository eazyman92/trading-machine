"""Separate research process; bounded synthetic workloads only."""
import hashlib
import json
import time
import threading
from dataclasses import asdict
from tradinglab.replay import fixture, replay
from tradinglab.store import Store

def process_one(store):
    job = store.claim()
    if job is None: return False
    stopped=threading.Event()
    def beat():
        while not stopped.wait(10):
            try:
                if not store.heartbeat(job['id']):return
            except Exception:return
    heartbeat=threading.Thread(target=beat,daemon=True);heartbeat.start()
    def progress(stage,done,total):
        if not store.heartbeat(job['id'],{'stage':stage,'done':done,'total':total}):raise RuntimeError('Job cancelled or lease lost')
    try:
        config = job['config']
        if config.get('symbol')=='XAU_USD':
            from tradinglab.gold import run_gold
            store.finish(job['id'],result=run_gold(config,progress=progress))
            return True
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
    finally:
        stopped.set();heartbeat.join(timeout=2)
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
