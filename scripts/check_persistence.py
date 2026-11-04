"""Snapshot one completed job, then compare it after a container restart."""
import argparse
import hashlib
import json
from pathlib import Path
from smoke_research import request

def digest(job):
    return hashlib.sha256(json.dumps(job, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('mode', choices=['save','verify'])
    parser.add_argument('--base-url', default='http://127.0.0.1:4173')
    parser.add_argument('--file', default='output/persistence-check.json')
    args=parser.parse_args()
    base=args.base_url.rstrip('/')
    path=Path(args.file)
    if args.mode=='save':
        _, listing=request(base,'/api/v1/research/jobs?limit=100')
        completed=next((j for j in listing['items'] if j['status']=='completed'),None)
        if not completed: raise SystemExit('Run the smoke test or a dashboard job first.')
        _, job=request(base,'/api/v1/research/jobs/'+completed['id'])
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps({'id':job['id'],'sha256':digest(job)}),encoding='utf-8')
        print('Saved completed-job fingerprint:',job['id'])
    else:
        saved=json.loads(path.read_text(encoding='utf-8'))
        _, job=request(base,'/api/v1/research/jobs/'+saved['id'])
        if digest(job)!=saved['sha256']:raise SystemExit('FAIL: saved job changed')
        print('PASS: completed job and result survived unchanged:',job['id'])
