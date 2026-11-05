import pytest
from tradinglab.tick_import import convert

def test_tick_aggregation_and_provenance():
    data,report=convert('time,bid,ask\n2025-01-02T07:00:00Z,2000,2000.2\n2025-01-02T07:00:30Z,2001,2001.4\n2025-01-02T07:02:00Z,1999,1999.1\n')
    assert '2000,2001,2000,2001,0.2' in data
    assert report['minute_count']==2 and report['largest_tick_gap_seconds']==90
    assert '07:01' not in data
    assert len(report['source_sha256'])==64

@pytest.mark.parametrize('row',['2025-01-02T07:00:00,2000,2001','2025-01-02T07:00:00Z,2001,2000','2025-01-02T07:00:00Z,NaN,2001'])
def test_invalid_tick_quotes(row):
    with pytest.raises(ValueError):convert('time,bid,ask\n'+row+'\n')
