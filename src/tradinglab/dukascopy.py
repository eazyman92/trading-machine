"""Bounded XAUUSD hourly public-feed adapter. No credentials or paid S3 access."""
import csv
import hashlib
import io
import json
import lzma
import math
from datetime import datetime,timedelta,timezone
from decimal import Decimal
from pathlib import Path
import struct
import time
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError

BASE='https://datafeed.dukascopy.com/datafeed/XAUUSD'
MAX_COMPRESSED=5_000_000
MAX_RAW=40_000_000

def hour_url(hour):
    if hour.tzinfo is None or hour.utcoffset()!=timedelta(0) or hour.minute or hour.second or hour.microsecond:
        raise ValueError('An exact UTC hour is required')
    return f'{BASE}/{hour.year}/{hour.month-1:02d}/{hour.day:02d}/{hour.hour:02d}h_ticks.bi5'

def decode(data,hour,scale):
    hour_url(hour)
    scale=Decimal(str(scale))
    if not scale.is_finite() or scale<=0:raise ValueError('Explicit finite positive price scale required')
    decoder=lzma.LZMADecompressor()
    raw=decoder.decompress(data,max_length=MAX_RAW+1)
    if len(raw)>MAX_RAW or not decoder.eof or decoder.unused_data:raise ValueError('Oversized, incomplete or trailing compressed stream')
    if not raw or len(raw)%20:raise ValueError('Empty or partial 20-byte records')
    ticks=[];previous=-1
    for ms,ask,bid,av,bv in struct.iter_unpack('>IIIff',raw):
        if ms>=3_600_000 or ms<previous:raise ValueError('Not ordered hourly millisecond timestamps')
        if bid<=0 or ask<=bid or any(not math.isfinite(v) or v<0 for v in (av,bv)):raise ValueError('Invalid bid/ask/volume record')
        previous=ms
        ticks.append((hour+timedelta(milliseconds=ms),Decimal(bid)/scale,Decimal(ask)/scale))
    return ticks

def fetch_hour(hour,cache,offline=False):
    url=hour_url(hour);path=Path(cache)/(hour.strftime('%Y%m%dT%H')+'.bi5')
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():data=path.read_bytes();origin='cache'
    else:
        if offline:raise FileNotFoundError('Offline cache missing: '+str(path))
        for attempt in range(3):
            try:
                with urlopen(Request(url,headers={'User-Agent':'TradingMachineResearch/0.1'}),timeout=30) as response:
                    data=response.read(MAX_COMPRESSED+1)
                break
            except HTTPError as exc:
                if exc.code not in (429,500,502,503,504) or attempt==2:raise
                time.sleep(2**attempt)
            except (URLError,TimeoutError):
                if attempt==2:raise
                time.sleep(2**attempt)
        origin='download'
        if len(data)>MAX_COMPRESSED:raise ValueError('Compressed response too large')
        decode(data,hour,1)  # Structural validation before an HTTP error page can poison the cache.
        # Store only a complete write; a failed download never becomes cache.
        from tradinglab.datasets import atomic_write
        atomic_write(path,data)
    if len(data)>MAX_COMPRESSED:raise ValueError('Cached response too large')
    return data,{'url':url,'raw_sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'origin':origin,
                 'cache_written_at':datetime.fromtimestamp(path.stat().st_mtime,timezone.utc).isoformat()}

def acquire(start,hours,scale,output,reference_price=None,reference_source=None,offline=False):
    hour_url(start)
    if not 1<=hours<=24:raise ValueError('Sample acquisition is limited to 1–24 hours')
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    ticks=[];receipts=[]
    previous_manifest=output/'manifest.json'
    expected={f['url']:f['raw_sha256'] for f in json.loads(previous_manifest.read_text()).get('files',[])} if previous_manifest.exists() else {}
    for index in range(hours):
        hour=start+timedelta(hours=index)
        data,receipt=fetch_hour(hour,output/'raw',offline=offline)
        if receipt['url'] in expected and expected[receipt['url']]!=receipt['raw_sha256']:raise ValueError('Cached bytes differ from previous manifest')
        decoded=decode(data,hour,scale);ticks.extend(decoded)
        receipt.update(tick_count=len(decoded),first_utc=decoded[0][0].isoformat(),last_utc=decoded[-1][0].isoformat())
        receipts.append(receipt)
        print(f'Validated {index+1}/{hours} UTC hours: {hour.isoformat()} · {len(decoded)} ticks',flush=True)
        if receipt['origin']=='download':time.sleep(.25)
    if any(a[0]>b[0] for a,b in zip(ticks,ticks[1:])):raise ValueError('Cross-file timestamps unordered')
    text=io.StringIO();writer=csv.writer(text,lineterminator='\n');writer.writerow(['time','bid','ask'])
    for t,bid,ask in ticks:writer.writerow([t.isoformat(),str(bid),str(ask)])
    normalized=text.getvalue()
    reference_check=None
    if reference_price is not None:
        reference=Decimal(str(reference_price))
        if not reference.is_finite() or reference<=0 or not reference_source:raise ValueError('Reference price needs a positive decimal and source')
        deviation=max(abs(bid/reference-1) for _,bid,_ in ticks)
        if deviation>Decimal('.05'):raise ValueError('Scale sanity check failed: sample differs by more than 5% from supplied daily reference')
        reference_check={'reference_price':str(reference),'source':reference_source,'maximum_bid_relative_deviation':str(deviation),
                         'result':'daily-order-of-magnitude-check-passed','limitation':'Daily reference is not a same-timestamp provider quote; it does not certify every tick.'}
    # Preserve paired ticks; the dashboard candle projection is explicitly approximate.
    from tradinglab.tick_import import convert
    candles,quality=convert(normalized)
    from tradinglab.gold import prepare_dataset
    _,sessions=prepare_dataset(candles,max_rows=200000)
    manifest={'adapter':'dukascopy-xauusd-hourly-v1','instrument':'XAUUSD','data_kind':'provider_downloaded_not_commercially_qualified',
              'manifest_created_at':datetime.now(timezone.utc).isoformat(),'start_utc':start.isoformat(),'hours':hours,
              'price_scale':str(scale),'scale_status':'explicit configuration; must be corroborated against provider decimal reference',
              'independent_reference_check':reference_check,
              'time_basis':'UTC hour from URL plus record milliseconds (strictly less than one hour)',
              'files':receipts,'tick_sha256':hashlib.sha256(normalized.encode()).hexdigest(),
              'candle_sha256':hashlib.sha256(candles.encode()).hexdigest(),'quality':quality,'sessions':sessions,
              'minimum_bid':str(min(t[1] for t in ticks)),'maximum_ask':str(max(t[2] for t in ticks)),
              'rights_status':'Public endpoint technical sample; commercial use and redistribution not approved',
              'warning':'Source authenticity is based on HTTPS provider origin and retained bytes, not independent price accuracy. Candle projection uses first spread per minute, not true ask OHLC or tick execution.'}
    from tradinglab.datasets import atomic_write
    atomic_write(output/'ticks.csv',normalized.encode())
    atomic_write(output/'candles.csv',candles.encode())
    atomic_write(output/'manifest.json',json.dumps(manifest,indent=2).encode())
    return manifest
