"""Content-addressed local research files; permissions are declared, not certified."""
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from datetime import datetime, timezone
from tradinglab.gold import prepare_dataset

MAX_BYTES=20_000_000
MAX_ROWS=200000

def root():
    path=Path(os.environ.get('DATASET_DIR','output/datasets')).resolve()
    path.mkdir(parents=True,exist_ok=True)
    return path

def paths(dataset_id):
    if not re.fullmatch(r'[a-f0-9]{64}',dataset_id):raise ValueError('Invalid dataset ID')
    base=root()
    return base/(dataset_id+'.csv'),base/(dataset_id+'.json')

def atomic_write(path,data,exclusive=False):
    with tempfile.NamedTemporaryFile(dir=path.parent,delete=False) as f:
        temp=Path(f.name);f.write(data);f.flush();os.fsync(f.fileno())
    try:
        if exclusive:
            try:os.link(temp,path)
            except FileExistsError:pass
        else:os.replace(temp,path)
    finally:temp.unlink(missing_ok=True)

def register(text,source,rights_reference):
    data=text.encode('utf-8')
    if len(data)>MAX_BYTES:raise ValueError('Dataset exceeds 20 MB')
    _,quality=prepare_dataset(text,max_rows=MAX_ROWS)
    digest=hashlib.sha256(data).hexdigest()
    csv_path,manifest_path=paths(digest)
    if manifest_path.exists():
        # Never silently replace the first recorded provenance with a later claim.
        return describe(digest)
    manifest={'id':digest,'source':source,'rights_reference':rights_reference,
              'registered_at':datetime.now(timezone.utc).isoformat(),'bytes':len(data),
              'quality':quality,'qualification':'user_declared_unverified',
              'warning':'Registration does not certify licensing, prices, timestamps or suitability.'}
    atomic_write(csv_path,data)
    atomic_write(manifest_path,json.dumps(manifest,sort_keys=True).encode(),exclusive=True)
    return describe(digest)

def describe(dataset_id):
    _,path=paths(dataset_id)
    return json.loads(path.read_text(encoding='utf-8'))

def read(dataset_id):
    path,_=paths(dataset_id)
    if path.stat().st_size>MAX_BYTES:raise ValueError('Stored dataset exceeds size bound')
    data=path.read_bytes()
    if hashlib.sha256(data).hexdigest()!=dataset_id:raise ValueError('Dataset integrity mismatch')
    return data.decode('utf-8')

def list_datasets():
    # Bound this local development registry response; no CSV contents in listings.
    files=sorted(root().glob('*.json'),key=lambda p:p.stat().st_mtime,reverse=True)[:100]
    return [describe(p.stem) for p in files]

def split_plan(dataset_id):
    _,quality=prepare_dataset(read(dataset_id),max_rows=MAX_ROWS)
    days=[s['date'] for s in quality['sessions'] if s['eligible']]
    if len(days)<10:raise ValueError('At least 10 complete weekday sessions required for a 60/20/20 split plan')
    a=len(days)*6//10;b=len(days)*8//10
    groups={'development':days[:a],'validation':days[a:b],'holdout':days[b:]}
    plan={'dataset_id':dataset_id,'timezone':'Europe/London',
          'periods':{k:{'start_date':v[0],'end_date':v[-1],'eligible_sessions':len(v)} for k,v in groups.items()},
          'warning':'Chronological plan only; not automatic tuning or enforcement of holdout secrecy. Do not tune on validation/holdout outcomes.'}
    plan['plan_sha256']=hashlib.sha256(json.dumps(plan,sort_keys=True).encode()).hexdigest()
    return plan
