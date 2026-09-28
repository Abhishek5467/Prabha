import csv, importlib.util, json
from pathlib import Path
import numpy as np
import pytest
from fastapi.testclient import TestClient
from prabha.product import dispatch
ROOT=Path(__file__).resolve().parents[1]

def test_all_archived_ann_outputs():
    rows=list(csv.DictReader((ROOT/'core-py/ann_batch_validation.csv').open()))
    result=dispatch({'action':'batch','count':100,'seed':12345})
    assert result['ok']
    actual=result['result']
    for archived,computed in zip(rows,actual['rows'],strict=True):
        np.testing.assert_allclose(computed['inputs'],[float(archived[f'x{i}']) for i in range(1,5)],atol=1e-15,rtol=0)
        np.testing.assert_allclose(computed['physical'],[float(archived[f'physical_y{i}']) for i in [1,2]],atol=1e-12,rtol=0)
    assert actual['winner_mismatches']==0
    assert actual['rms_error']==pytest.approx(7.864411795585e-5,abs=1e-15)

def test_converter_setting_changes_computation():
    reference=dispatch({'action':'infer'})['result']
    low=dispatch({'action':'infer','dac_bits':3,'adc_bits':3})['result']
    assert low['physical_output']!=reference['physical_output']
    assert low['rms_error']>reference['rms_error']

@pytest.mark.parametrize('payload',[
    {'action':'infer','inputs':[1,2,3,4]}, {'action':'infer','inputs':[float('nan')]*4},
    {'action':'infer','network':{}}, {'action':'batch','count':100000},
    {'action':'batch','seed':-1}, {'action':'infer','adc_bits':True},
    {'action':'component','kind':'laser','power_mw':float('inf')}, ['not','object']])
def test_invalid_requests(payload):
    assert dispatch(payload)['ok'] is False

def test_graph_allocation_guard_and_original_design():
    design=dispatch({'action':'example'})['result']
    valid=dispatch({'action':'graph','design':design,'noise':False})
    assert valid['ok']
    assert 'act' in valid['result']['probes']
    design['blocks'][0]['params']['fs']=1e20
    blocked=dispatch({'action':'graph','design':design})
    assert not blocked['ok']
    assert 'fs' in blocked['error']

def test_http_transport_and_body_limit():
    spec=importlib.util.spec_from_file_location('prabha_http',ROOT/'frontend/web/server.py')
    server=importlib.util.module_from_spec(spec);spec.loader.exec_module(server)
    with TestClient(server.app) as client:
        assert client.get('/api/health').json()['engine']=='native-python'
        response=client.post('/api/execute',json={'action':'infer'})
        assert response.status_code==200
        assert response.json()==dispatch({'action':'infer'})
        assert client.post('/api/execute',json={'action':'batch','count':0}).status_code==422
        assert client.post('/api/execute',content='x'*1_000_001).status_code==400
        assert client.post('/api/execute',content='{bad').status_code==400

@pytest.mark.parametrize('params',[{'sps':1e12},{'rate':1e6},{'values':''},{'values':'1,'*300}])
def test_graph_derived_source_limits(params):
    design=dispatch({'action':'example'})['result']
    drive=next(b for b in design['blocks'] if b['ref']=='drive_source')
    drive['params'].update(params)
    assert not dispatch({'action':'graph','design':design})['ok']
