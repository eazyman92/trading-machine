# SPDX-License-Identifier: Apache-2.0
# Reproduction/adaptation of je-suis-tm/quant-trading London Breakout.
# Pinned revision and original license: vendor/quant_trading/PROVENANCE.md.
"""Faithful signal semantics, including legacy clock/threshold/cumsum quirks."""
from itertools import accumulate

def reproduce(dates,prices):
    if len(dates)!=len(prices):raise ValueError('Mismatched dates/prices')
    signals=[0]*len(prices);cumsum=[0]*len(prices);upper_col=[0.0]*len(prices);lower_col=[0.0]*len(prices)
    tokyo=[];executed=0.0
    for i,(t,p) in enumerate(zip(dates,prices)):
        if t.hour==2:tokyo.append(p)
        elif t.hour==3 and t.minute==0:
            upper=max(tokyo);lower=min(tokyo);upper_col[i]=upper;lower_col[i]=lower;tokyo=[]
        elif t.hour==3 and t.minute<30:
            upper_col[i]=upper;lower_col[i]=lower
            if p-upper>0:
                signals[i]=1;cumsum=list(accumulate(signals))
                if p-upper>0.01:signals[i]=0
                elif cumsum[i]>1:signals[i]=0
                else:executed=p
            if p-lower<0:
                signals[i]=-1;cumsum=list(accumulate(signals))
                if lower-p>0.01:signals[i]=0
                elif cumsum[i]<-1:signals[i]=0
                else:executed=p
        elif t.hour==12:
            cumsum=list(accumulate(signals));signals[i]=-cumsum[i]
        else:
            cumsum=list(accumulate(signals))
            if cumsum[i]!=0:
                if p>executed+0.01/2:signals[i]=-cumsum[i]
                if p<executed-0.01/2:signals[i]=-cumsum[i]
    return {'signals':signals,'cumsum':cumsum,'upper':upper_col,'lower':lower_col}
