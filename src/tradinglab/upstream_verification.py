"""Compare an independent port to hash-checked upstream functions only."""
import ast
from datetime import datetime,timedelta,timezone
import hashlib
from pathlib import Path

SHA256='8b5a0f672c2c5a44fb5a72564fcb0b20a5bd2b0d3d9da3e2f4a52b2d047f8e3a'
COMMIT='611b73f2c3f577ac5b28aaa19ac8c43d3236c7a5'
ROOT=Path(__file__).resolve().parents[2]

def reference_functions():
    import pandas as pd
    source=ROOT/'vendor/quant_trading/london_breakout_reference.py'
    data=source.read_bytes()
    if hashlib.sha256(data).hexdigest()!=SHA256:raise ValueError('Upstream source hash mismatch')
    tree=ast.parse(data)
    nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('london_breakout','signal_generation')]
    if len(nodes)!=2:raise ValueError('Expected exactly two reviewed upstream functions')
    # No os.chdir, plotting, main(), other imports or file access from the script executes.
    namespace={'pd':pd}
    exec(compile(ast.Module(body=nodes,type_ignores=[]),str(source),'exec'),namespace)
    return namespace

def fixture(direction=1,overshoot=False):
    start=datetime(2024,1,15,2,tzinfo=timezone(timedelta(hours=-5)))
    dates=[start+timedelta(minutes=i) for i in range(601)]
    prices=[]
    for i in range(len(dates)):
        delta=0 if i<=60 else direction*(.02 if overshoot else .001) if i<180 else direction*.008
        prices.append(1.25+delta)
    return dates,prices

def verify(dates,prices):
    import pandas as pd
    from tradinglab.upstream_london import reproduce
    if not 1<=len(prices)<=5000:raise ValueError('Reviewed reference parity runs require 1–5000 rows; the upstream loop is quadratic')
    upstream=reference_functions()
    frame=pd.DataFrame({'date':dates,'price':prices})
    expected=upstream['signal_generation'](frame.copy(),upstream['london_breakout'])
    actual=reproduce(dates,prices)
    for column,values in actual.items():
        if values!=expected[column].tolist():raise AssertionError('Upstream parity failed: '+column)
    return {'rows':len(prices),'nonzero_signals':sum(v!=0 for v in actual['signals']),
            'columns_matched':list(actual),'source_sha256':SHA256,'upstream_commit':COMMIT,
            'signal_events':[{'time':dates[i].isoformat(),'signal':s,'price':prices[i]} for i,s in enumerate(actual['signals']) if s]}
