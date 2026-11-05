"""Normalize permitted ISO-UTC bid/ask tick exports; no provider scraping."""
import csv
import hashlib
import io
from datetime import datetime, timedelta
from decimal import Decimal as D

def convert(text):
    reader=csv.DictReader(io.StringIO(text))
    if reader.fieldnames!=['time','bid','ask']:raise ValueError('Expected exact columns: time,bid,ask')
    buckets={};previous=None;ticks=0;max_gap=0
    for row in reader:
        t=datetime.fromisoformat(row['time'].replace('Z','+00:00'))
        if t.tzinfo is None or t.utcoffset()!=timedelta(0):raise ValueError('UTC timestamps required; no guessed timezone')
        if previous is not None:
            if t<previous:raise ValueError('Unordered ticks')
            max_gap=max(max_gap,(t-previous).total_seconds())
        previous=t
        bid,ask=D(row['bid']),D(row['ask'])
        if any(not v.is_finite() or v<=0 for v in (bid,ask)) or ask<=bid:raise ValueError('Positive uncrossed bid/ask required')
        minute=t.replace(second=0,microsecond=0)
        spread=ask-bid
        if minute not in buckets:buckets[minute]=[bid,bid,bid,bid,spread]
        else:
            b=buckets[minute];b[1]=max(b[1],bid);b[2]=min(b[2],bid);b[3]=bid
        ticks+=1
    if not ticks:raise ValueError('Empty tick export')
    output=io.StringIO();writer=csv.writer(output,lineterminator='\n')
    writer.writerow(['time','bid_open','bid_high','bid_low','bid_close','spread'])
    for t,values in buckets.items():writer.writerow([t.isoformat(),*values])
    csv_text=output.getvalue()
    return csv_text,{'source_sha256':hashlib.sha256(text.encode()).hexdigest(),'output_sha256':hashlib.sha256(csv_text.encode()).hexdigest(),
                     'tick_count':ticks,'minute_count':len(buckets),'largest_tick_gap_seconds':max_gap,
                     'first_utc':next(iter(buckets)).isoformat(),'last_utc':next(reversed(buckets)).isoformat(),
                     'spread_model':'First observed spread in each minute, applied as constant offset to bid OHLC',
                     'warning':'Approximation is not actual ask OHLC or tick replay. First quote can arrive after minute open; executable-open and within-minute ask prices remain approximations. Research stress model only. Sparse ticks can form apparently complete candles; inspect tick gaps. No missing-minute fill or source authenticity verification.'}
