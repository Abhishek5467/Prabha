"""Integration gates: public graph operations against established component classes."""
import copy
import zlib
import numpy as np
import pytest
from prabha.product import dispatch, registry
from prabha import System, RunContext
from prabha.blocks.tia import TIA
from prabha.blocks.capacitor import Capacitor
from prabha.blocks.amplifier import Amplifier
from prabha.blocks.activation import Activation
from prabha.blocks.photodetector import Q_E


def example(name='neuron'):
    return dispatch({'action':'example','name':name})['result']


def request(e, **overrides):
    s=e['settings']
    return {'action':'graph','design':e['design'],'duration':s['duration_ns']*1e-9,'noise':s['noise'],'seed':s['seed'],**overrides}


def run(e, **overrides):
    out=dispatch(request(e, **overrides))
    assert out['ok'], out
    return out['result']


def params(e, id, **values):
    next(b for b in e['design']['blocks'] if b['id']==id)['params'].update(values)


@pytest.mark.parametrize('bits',[3,8,12,16])
@pytest.mark.parametrize('x,w', [([.9,.3,.7,.5],[.8,-.6,.4,-.9]),([0,1,0,1],[-1,1,1,-1])])
def test_graph_final_value_matches_b22(bits,x,w):
    e=example();params(e,'x',values=','.join(map(str,x)));params(e,'w',values=','.join(map(str,w)))
    params(e,'mac',dac_bits=bits);params(e,'adc',bits=bits)
    probes=run(e)['probes']
    reference=dispatch({'action':'neuron','inputs':x,'weights':w,'dac_bits':bits,'adc_bits':bits})['result']
    assert probes['cap']['out']['last']==pytest.approx(reference['capacitor_voltage_V'],abs=1e-14)
    assert probes['adc']['code']['last']==reference['adc_code']
    assert probes['adc']['voltage']['last']==reference['output']


@pytest.mark.parametrize('noise',[False,True])
def test_compact_expanded_chain_parity(noise):
    compact,expanded=example(),example('expanded')
    for e in (compact,expanded):params(e,'laser',rin_db_hz=-120,linewidth_hz=2e6)
    params(compact,'mac',dark_current_A=2e-8,dac_bits=8,loss_dB=2,ratio=.4)
    params(expanded,'dac',bits=8);params(expanded,'mzm',loss_dB=2);params(expanded,'split',ratio=.4)
    for id in ('mac/pd_upper','mac/pd_lower'):params(expanded,id,dark_current_A=2e-8)
    a,b=run(compact,noise=noise),run(expanded,noise=noise)
    for id in ['cap','amp','act']:
        np.testing.assert_allclose(a['probes'][id]['out']['data'],b['probes'][id]['out']['data'],atol=1e-14,rtol=0)
    assert a['probes']['adc']==b['probes']['adc']


def test_noise_streams_and_phase_observable():
    e=example('receiver')
    a=run(e,seed=1);b=run(e,seed=1);c=run(e,seed=2)
    assert a==b
    assert a['probes']['tia']!=c['probes']['tia']
    assert run(e,noise=False,seed=1)['probes']==run(e,noise=False,seed=2)['probes']
    params(e,'laser',rin_enabled=False)
    phase_on=run(e)['probes']['laser']['out']
    params(e,'laser',linewidth_enabled=False)
    phase_off=run(e)['probes']['laser']['out']
    np.testing.assert_allclose(phase_on['data'],phase_off['data'],atol=1e-18,rtol=0)
    assert np.std(phase_on['phase_rad'])>0
    assert np.std(phase_off['phase_rad'])==0


def test_tia_uses_noise_density_and_bandwidth():
    e=example('receiver');params(e,'tia',resistance_ohm=2000,noise_A_sqrtHz=3e-12,bandwidth_Hz=5e8)
    actual=run(e)
    pd=actual['probes']['pd']['out'];seed=(zlib.crc32(b'tia')+1)&0xffffffff
    reference=TIA(2000,5e8,3e-12,seed).amplify(pd['data'],pd['fs'],True)
    np.testing.assert_array_equal(actual['probes']['tia']['out']['data'],reference)
    params(e,'tia',bandwidth_enabled=False)
    assert run(e)['probes']['tia']!=actual['probes']['tia']


def test_leakage_initial_voltage_saturation_threshold():
    e=example('nonlinear');params(e,'cap',initial_V=.15)
    actual=run(e)['probes'];cap=Capacitor(1e-12,1000,.15)
    expected=[cap.integrate_current(i,1/16e9) for i in actual['current']['out']['data']]
    np.testing.assert_allclose(actual['cap']['out']['data'],expected,atol=0,rtol=0)
    amp=Amplifier(2,0,-.4,.4).amplify(expected)
    np.testing.assert_array_equal(actual['amp']['out']['data'],amp)
    np.testing.assert_array_equal(actual['act']['out']['data'],Activation('sigmoid',3,.1).activate(amp))
    assert max(amp)==.4 and min(amp)==-.4
    assert run(e,noise=True)['probes']==actual  # this example has no stochastic blocks


def test_shot_noise_variance_uses_fs_over_two():
    e=example('receiver');e['settings']['duration_ns']=1250
    params(e,'laser',rin_enabled=False,linewidth_enabled=False)
    _,reg=registry();system=System(e['design'],reg,RunContext(1250e-9,True,1))
    signal=system.run()['pd']['out']
    expected=2*Q_E*(1e-3+1e-9)*(signal.fs/2)
    assert np.var(signal.data)==pytest.approx(expected,rel=.035)


def test_adc_to_dac_round_trip_and_source_code_guard():
    design={'blocks':[{'id':'s','ref':'model_code_source','params':{'values':'0,1,127,255'}},
                      {'id':'dac','ref':'model_dac','params':{'bits':8,'v_min':0,'v_max':1}},
                      {'id':'adc','ref':'model_adc','params':{'bits':8}}],
            'connections':[{'from':['s','out'],'to':['dac','code']},{'from':['dac','out'],'to':['adc','in']}]}
    a=dispatch({'action':'graph','design':design,'duration':4e-9,'noise':False})
    assert a['ok'],a
    p=a['result']['probes'];assert p['s']['out']['data']==p['adc']['code']['data']
    design['blocks'][0]['params']['values']='0.5'
    assert not dispatch({'action':'graph','design':design,'duration':4e-9})['ok']


@pytest.mark.parametrize('id,values',[
    ('mac',{'dac_bits':8.5}),('mac',{'v_min':1,'v_max':0}),('mac',{'seed':.3}),
    ('x',{'sps':1.5}),('x',{'values':'1,,2'}),('w',{'values':'1.1'}),
    ('amp',{'lower_rail_enabled':True,'upper_rail_enabled':True,'v_min':1,'v_max':0}),
    ('laser',{'fs':17e9}),('laser',{'power_mW':float('nan')}),('adc',{'v_max':.1}),
])
def test_invalid_parameters_report_errors(id,values):
    e=example();params(e,id,**values)
    assert not dispatch(request(e))['ok']


def test_explicit_clipping_and_sample_indices():
    e=example();params(e,'adc',v_max=.1,clip=True)
    a=run(e)['probes']['adc']
    assert a['code']['last']==4095 and a['voltage']['last']==pytest.approx(.1)
    long=example('receiver');long['settings']['duration_ns']=100
    p=run(long)['probes']['laser']['out']
    assert len(p['data'])==1200 and p['sample_indices'][-1]==p['n']-1


def test_invalid_self_loop_is_rejected():
    e=example();e['design']['connections']=[c for c in e['design']['connections'] if c['to'][0]!='amp']
    e['design']['connections'].append({'from':['amp','out'],'to':['amp','in']})
    result=dispatch(request(e));assert not result['ok']
    assert any(v['rule']=='R12' for v in result['violations'])
