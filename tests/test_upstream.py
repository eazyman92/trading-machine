import pytest
from tradinglab.upstream_verification import fixture,verify

@pytest.mark.parametrize('direction,overshoot',[(1,False),(-1,False),(1,True)])
def test_reference_signal_threshold_parity(direction,overshoot):
    result=verify(*fixture(direction,overshoot))
    assert result['rows']==601 and len(result['columns_matched'])==4
    assert result['nonzero_signals']>0 if not overshoot else result['nonzero_signals']==0

def test_reference_forced_close_and_flat_series():
    dates,prices=fixture()
    prices=[1.25 if i<=60 else 1.251 for i in range(len(prices))]
    result=verify(dates,prices)
    assert result['signal_events'][-1]['time'].startswith('2024-01-15T12:00:00')
    assert result['signal_events'][-1]['signal']==-1
    assert verify(dates,[1.25]*len(prices))['nonzero_signals']==0
