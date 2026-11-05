from datetime import datetime,timezone
from decimal import Decimal
import lzma
import struct
import pytest
from urllib.error import HTTPError
from tradinglab.dukascopy import hour_url,decode,acquire,fetch_hour

HOUR=datetime(2024,1,15,8,tzinfo=timezone.utc)
def blob(ms=84,ask=2054495,bid=2054215):return lzma.compress(struct.pack('>IIIff',ms,ask,bid,1.,2.))

def test_hour_layout_and_decimal_scale():
    assert '/2024/00/15/08h_ticks.bi5' in hour_url(HOUR)
    ticks=decode(blob(),HOUR,'1000')
    assert ticks[0][0].microsecond==84000
    assert ticks[0][1:]==(Decimal('2054.215'),Decimal('2054.495'))

@pytest.mark.parametrize('data',[b'html-error',lzma.compress(b'bad'),blob(ms=3600000),blob(ask=1,bid=2),blob()+b'trailing'])
def test_corrupt_or_wrong_time_base_rejected(data):
    with pytest.raises((ValueError,lzma.LZMAError)):decode(data,HOUR,'1000')

def test_reproduction_from_cached_raw(tmp_path,monkeypatch):
    monkeypatch.setattr('tradinglab.dukascopy.time.sleep',lambda _:None)
    raw=tmp_path/'raw';raw.mkdir();(raw/'20240115T08.bi5').write_bytes(blob())
    first=acquire(HOUR,1,'1000',tmp_path)
    second=acquire(HOUR,1,'1000',tmp_path)
    assert first['tick_sha256']==second['tick_sha256']
    assert second['files'][0]['origin']=='cache'
    assert first['sessions']['eligible_sessions']==0

def test_retry_backoff_and_reject_bad_cache(tmp_path,monkeypatch):
    calls=[]
    def unavailable(*args,**kwargs):
        calls.append(1);raise HTTPError('https://provider',503,'Unavailable',{},None)
    monkeypatch.setattr('tradinglab.dukascopy.urlopen',unavailable)
    monkeypatch.setattr('tradinglab.dukascopy.time.sleep',lambda _:None)
    with pytest.raises(HTTPError):fetch_hour(HOUR,tmp_path)
    assert len(calls)==3 and not list(tmp_path.glob('*.bi5'))

def test_offline_requires_cache_and_detects_changes(tmp_path,monkeypatch):
    with pytest.raises(FileNotFoundError):acquire(HOUR,1,'1000',tmp_path,offline=True)
    raw=tmp_path/'raw';raw.mkdir(exist_ok=True);file=raw/'20240115T08.bi5';file.write_bytes(blob())
    first=acquire(HOUR,1,'1000',tmp_path,reference_price='2054.33',reference_source='Independent daily test reference',offline=True)
    assert first['independent_reference_check']['result']=='daily-order-of-magnitude-check-passed'
    with pytest.raises(ValueError):acquire(HOUR,1,'100000',tmp_path,reference_price='2054.33',reference_source='Independent daily test reference',offline=True)
    file.write_bytes(blob(ms=85))
    with pytest.raises(ValueError):acquire(HOUR,1,'1000',tmp_path,offline=True)
