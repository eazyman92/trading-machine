"""Loopback development API. Not authenticated or suitable for public exposure."""
from typing import Literal
from uuid import UUID
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, ConfigDict
from tradinglab.store import Store, Conflict

app = FastAPI(title='Trading research API', version='0.1.0', openapi_url='/api/v1/openapi.json', docs_url='/api/v1/docs', redoc_url=None)

class JobRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    dataset: Literal['synthetic-london-dst-v1'] = 'synthetic-london-dst-v1'
    strategy: Literal['session-breakout-v0.1'] = 'session-breakout-v0.1'
    symbol: Literal['EUR_USD'] = 'EUR_USD'

@app.get('/api/v1/health')
def health():
    try: Store().health()
    except Exception: raise HTTPException(503, 'Research database unavailable')
    return {'status': 'ok', 'mode': 'local-synthetic-research'}

@app.post('/api/v1/research/jobs', status_code=202)
def create_job(body: JobRequest, idempotency_key: UUID = Header()):
    try: return Store().create(str(idempotency_key), body.model_dump())
    except Conflict as exc: raise HTTPException(409, str(exc))

@app.get('/api/v1/research/jobs/{job_id}')
def get_job(job_id: UUID):
    job = Store().get(str(job_id))
    if job is None: raise HTTPException(404, 'Research job not found')
    return job

@app.post('/api/v1/research/jobs/{job_id}/cancel')
def cancel_job(job_id: UUID):
    job = Store().cancel(str(job_id))
    if job is None: raise HTTPException(404, 'Research job not found')
    return job
