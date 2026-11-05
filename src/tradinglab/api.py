"""Loopback development API. Not authenticated or suitable for public exposure."""
from typing import Literal
from uuid import UUID
from fastapi import FastAPI, Header, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field
from decimal import Decimal
from tradinglab.store import Store, Conflict

app = FastAPI(title='Trading research API', version='0.1.0', openapi_url='/api/v1/openapi.json', docs_url='/api/v1/docs', redoc_url=None)

class JobRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    dataset: Literal['synthetic-london-dst-v1'] = 'synthetic-london-dst-v1'
    strategy: Literal['session-breakout-v0.1'] = 'session-breakout-v0.1'
    symbol: Literal['EUR_USD'] = 'EUR_USD'

class GoldSpec(BaseModel):
    model_config=ConfigDict(extra='forbid')
    tick_usd: Decimal = Field(gt=0,le=100)
    ounces_per_lot: Decimal = Field(gt=0,le=10000)
    lot_step: Decimal = Field(gt=0,le=100)
    minimum_lots: Decimal = Field(gt=0,le=100)
    commission_usd_per_lot_side: Decimal = Field(ge=0,le=10000)
    risk_budget_usd: Decimal = Field(gt=0,le=100000)
    notional_cap_usd: Decimal = Field(gt=0,le=10000000)

class GoldRequest(BaseModel):
    model_config=ConfigDict(extra='forbid')
    csv_text: str = Field(min_length=1,max_length=500000)
    provenance: str = Field(min_length=10,max_length=2000)
    rights_confirmed: Literal[True]
    spec: GoldSpec

@app.post('/api/v1/research/gold/jobs',status_code=202)
def create_gold(body: GoldRequest,idempotency_key: UUID=Header()):
    from tradinglab.gold import import_csv
    try:
        import_csv(body.csv_text)
        if body.spec.minimum_lots % body.spec.lot_step != 0: raise ValueError('Minimum lots must be a multiple of lot step')
    except (ValueError,ArithmeticError,TypeError,KeyError): raise HTTPException(422,'Invalid CSV or contract settings; check UTC timestamps, finite positive OHLC/spread, ordering and row limit')
    config=body.model_dump(mode='json') | {'symbol':'XAU_USD','strategy':'gold-session-breakout-v0.1','dataset':'user-csv-v1'}
    try:return Store().create(str(idempotency_key),config)
    except Conflict as exc:raise HTTPException(409,str(exc))

@app.get('/api/v1/health')
def health():
    try: Store().health()
    except Exception: raise HTTPException(503, 'Research database unavailable')
    return {'status': 'ok', 'mode': 'local-synthetic-research'}

@app.get('/api/v1/research/requests/{request_key}')
def recover_request(request_key: UUID):
    job=Store().get_by_request(str(request_key))
    if job is None: raise HTTPException(404,'Submission not found yet; its outcome may still be unknown')
    return job

@app.post('/api/v1/research/jobs', status_code=202)
def create_job(body: JobRequest, idempotency_key: UUID = Header()):
    try: return Store().create(str(idempotency_key), body.model_dump())
    except Conflict as exc: raise HTTPException(409, str(exc))

@app.get('/api/v1/research/jobs/{job_id}')
def get_job(job_id: UUID):
    job = Store().get(str(job_id))
    if job is None: raise HTTPException(404, 'Research job not found')
    return job

@app.get('/api/v1/research/jobs')
def list_jobs(limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0, le=100000)):
    return Store().list_jobs(limit, offset)

@app.post('/api/v1/research/jobs/{job_id}/cancel')
def cancel_job(job_id: UUID):
    job = Store().cancel(str(job_id))
    if job is None: raise HTTPException(404, 'Research job not found')
    return job
