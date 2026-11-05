"""Descriptive comparison only. Never ranks incompatible runs."""
from decimal import Decimal

def compare(left,right):
    if any(j['status']!='completed' or not j.get('result') or j['result'].get('symbol')!='XAU_USD' for j in (left,right)):
        raise ValueError('Select two completed gold runs')
    a,b=left['result'],right['result']
    if a['dataset_sha256']!=b['dataset_sha256']:raise ValueError('Runs must use the exact same CSV')
    if not a.get('data_quality') or not b.get('data_quality'):raise ValueError('Rerun older reports to record date-range metadata')
    if any(a['data_quality'].get(k)!=b['data_quality'].get(k) for k in ('start_date','end_date')):raise ValueError('Runs must use identical selected date ranges')
    changed={k:{'left':a['contract_spec'].get(k),'right':b['contract_spec'].get(k)} for k in set(a['contract_spec'])|set(b['contract_spec']) if a['contract_spec'].get(k)!=b['contract_spec'].get(k)}
    return {'left_id':left['id'],'right_id':right['id'],'left_metrics':a['metrics'],'right_metrics':b['metrics'],
            'changed_settings':changed,'left_strategy':a['strategy_version'],'right_strategy':b['strategy_version'],
            'net_delta_usd':str(Decimal(b['metrics']['net_usd'])-Decimal(a['metrics']['net_usd'])),
            'warning':'Descriptive comparison on unverified user data. Changed costs or sizing confound strategy comparisons; this is not independent holdout evidence.'}
