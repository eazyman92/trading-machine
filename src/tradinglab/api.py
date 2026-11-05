"""Loopback development API. Not authenticated or suitable for public exposure."""
from typing import Literal
from uuid import UUID
from fastapi import FastAPI, Header, HTTPException, Query, Request
from pydantic import BaseModel, ConfigDict, Field
from decimal import Decimal
from datetime import date
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

class DatasetRequest(BaseModel):
    model_config=ConfigDict(extra='forbid')
    csv_text: str = Field(min_length=1,max_length=500000)
    start_date: date | None = None
    end_date: date | None = None

@app.post('/api/v1/research/gold/validate')
def validate_gold_dataset(body: DatasetRequest):
    from tradinglab.gold import prepare_dataset
    try:return prepare_dataset(body.csv_text,body.start_date,body.end_date)[1]
    except (ValueError,ArithmeticError,TypeError,KeyError) as exc:raise HTTPException(422,'Invalid CSV/date range: '+str(exc))

class StrategyRules(BaseModel):
    model_config=ConfigDict(extra='forbid')
    buffer_ticks: int=Field(default=5,ge=0,le=10000,strict=True)
    reward_multiple: Decimal=Field(default=Decimal('2'),ge=Decimal('.25'),le=10)
    max_spread_usd: Decimal | None=Field(default=None,gt=0,le=100)

class GoldRequest(DatasetRequest):
    provenance: str = Field(min_length=10,max_length=2000)
    rights_confirmed: Literal[True]
    spec: GoldSpec
    rules: StrategyRules=Field(default_factory=StrategyRules)

class DatasetMetadata(BaseModel):
    model_config=ConfigDict(extra='forbid')
    csv_text: str=Field(min_length=1,max_length=20_000_000)
    source: str=Field(min_length=10,max_length=2000)
    rights_reference: str=Field(min_length=10,max_length=2000)
    rights_confirmed: Literal[True]

@app.post('/api/v1/research/datasets',status_code=201)
async def register_dataset(request: Request):
    # Bound the body while streaming, before JSON decoding/validation.
    data=bytearray()
    async for chunk in request.stream():
        data.extend(chunk)
        if len(data)>23_000_000:raise HTTPException(413,'Upload exceeds 23 MB request limit')
    try:
        body=DatasetMetadata.model_validate_json(data)
    except ValueError:raise HTTPException(422,'Invalid dataset registration fields')
    from tradinglab.datasets import register
    from starlette.concurrency import run_in_threadpool
    try:return await run_in_threadpool(register,body.csv_text,body.source,body.rights_reference)
    except (ValueError,ArithmeticError,TypeError,KeyError):raise HTTPException(422,'Dataset rejected: check format, UTC ordering, 20 MB / 200000-row limits')

@app.get('/api/v1/research/datasets')
def dataset_list():
    from tradinglab.datasets import list_datasets
    return {'items':list_datasets()}

@app.get('/api/v1/research/datasets/{dataset_id}/split-plan')
def dataset_split(dataset_id: str):
    from tradinglab.datasets import split_plan
    try:return split_plan(dataset_id)
    except FileNotFoundError:raise HTTPException(404,'Dataset not found')
    except ValueError as exc:raise HTTPException(422,str(exc))

@app.get('/api/v1/research/datasets/{dataset_id}/quality')
def dataset_quality(dataset_id: str,start_date: date | None=None,end_date: date | None=None):
    from tradinglab.datasets import read,MAX_ROWS
    from tradinglab.gold import prepare_dataset
    try:return prepare_dataset(read(dataset_id),start_date,end_date,max_rows=MAX_ROWS)[1]
    except FileNotFoundError:raise HTTPException(404,'Dataset not found')
    except (ValueError,ArithmeticError) as exc:raise HTTPException(422,str(exc))

class StoredGoldRequest(BaseModel):
    model_config=ConfigDict(extra='forbid')
    dataset_id: str=Field(pattern='^[a-f0-9]{64}$')
    start_date: date | None=None
    end_date: date | None=None
    spec: GoldSpec
    rules: StrategyRules=Field(default_factory=StrategyRules)

@app.post('/api/v1/research/gold/stored-jobs',status_code=202)
def create_stored_gold(body: StoredGoldRequest,idempotency_key: UUID=Header()):
    from tradinglab.datasets import describe,read,MAX_ROWS
    from tradinglab.gold import prepare_dataset
    try:
        metadata=describe(body.dataset_id)
        prepare_dataset(read(body.dataset_id),body.start_date,body.end_date,max_rows=MAX_ROWS)
        if body.spec.minimum_lots % body.spec.lot_step != 0:raise ValueError('Invalid lot step')
    except FileNotFoundError:raise HTTPException(404,'Dataset not found')
    except (ValueError,ArithmeticError):raise HTTPException(422,'Invalid dataset, date range or lot step')
    config=body.model_dump(mode='json') | {'symbol':'XAU_USD','strategy':'gold-session-breakout-v0.2','dataset':'stored-csv-v1','provenance':metadata['source']+'; rights: '+metadata['rights_reference']}
    try:return Store().create(str(idempotency_key),config)
    except Conflict as exc:raise HTTPException(409,str(exc))

@app.post('/api/v1/research/gold/jobs',status_code=202)
def create_gold(body: GoldRequest,idempotency_key: UUID=Header()):
    from tradinglab.gold import prepare_dataset
    try:
        prepare_dataset(body.csv_text,body.start_date,body.end_date)
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

@app.get('/api/v1/research/comparison')
def compare_jobs(left: UUID,right: UUID):
    from tradinglab.comparison import compare
    a,b=Store().get(str(left)),Store().get(str(right))
    if not a or not b:raise HTTPException(404,'Research job not found')
    try:return compare(a,b)
    except ValueError as exc:raise HTTPException(422,str(exc))

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
