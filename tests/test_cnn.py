import numpy as np
import pytest
from scipy.signal import correlate2d
from prabha.systems.cnn import conv2d, max_pool2d, relu, linear
from prabha.systems.mac import MACConfig, PhysicalMAC
from prabha.systems.perceptron import physical_neuron


class DigitalMAC:
    def dot(self, x, w):
        return float(np.dot(x, w))


def reference(x, w, b, stride=(1,1), padding=(0,0), dilation=(1,1), groups=1):
    n, ci, h, width = x.shape
    co, cig, kh, kw = w.shape
    sh, sw = stride; ph, pw = padding; dh, dw = dilation
    expanded = np.zeros((co, cig, (kh-1)*dh+1, (kw-1)*dw+1))
    expanded[:, :, ::dh, ::dw] = w
    padded = np.pad(x, ((0,0),(0,0),(ph,ph),(pw,pw)))
    results=[]
    for a in range(n):
        channels=[]
        for o in range(co):
            start=(o//(co//groups))*cig
            value=sum(correlate2d(padded[a,start+c], expanded[o,c], mode='valid') for c in range(cig))
            channels.append(value[::sh,::sw]+b[o])
        results.append(channels)
    return np.asarray(results)


@pytest.mark.parametrize('backend',[DigitalMAC,lambda:PhysicalMAC(MACConfig(dac_bits=None))])
@pytest.mark.parametrize('shape,kernel,stride,padding,dilation,groups',[
    ((1,1,4,5),(1,1,2,3),(1,1),(0,0),(1,1),1),
    ((2,2,5,6),(4,2,3,2),(2,1),(1,0),(1,1),1),
    ((1,2,8,9),(3,2,2,3),(1,2),(1,2),(2,2),1),
    ((1,4,5,5),(6,2,3,3),(1,1),(1,1),(1,1),2),
    ((2,3,4,5),(6,1,2,2),(2,2),(0,1),(1,1),3),
])
def test_convolution_against_independent_scipy(backend,shape,kernel,stride,padding,dilation,groups):
    rng=np.random.default_rng(191)
    x=rng.normal(size=shape); w=rng.normal(size=kernel); b=rng.normal(size=kernel[0])
    actual=conv2d(x,w,b,stride=stride,padding=padding,dilation=dilation,groups=groups,backend=backend())
    expected=reference(x,w,b,stride,padding,dilation,groups)
    np.testing.assert_allclose(actual,expected,atol=2e-13,rtol=2e-13)


def test_hand_computed_kernel_orientation_and_bias():
    x=np.arange(1,10,dtype=float).reshape(1,1,3,3)
    w=np.array([[[[1,2],[3,4]]]],dtype=float)
    np.testing.assert_allclose(conv2d(x,w,[.5],backend=PhysicalMAC(MACConfig(dac_bits=None))),
                               [[[[37.5,47.5],[67.5,77.5]]]],atol=1e-12)


def test_mac_matches_existing_neuron_before_activation():
    x=[.9,.3,.7,.5];w=[.8,-.6,.4,-.9]
    value=PhysicalMAC().dot(x,w,input_scale=1,weight_scale=1)
    expected=physical_neuron(x,w,.2)['pre_activation']-.2
    assert value==pytest.approx(expected,abs=5e-15)


def test_signed_mac_tiling_and_readout():
    rng=np.random.default_rng(142)
    x=rng.normal(size=137);w=rng.normal(size=137)
    backend=PhysicalMAC(MACConfig(dac_bits=None,tile_size=16))
    assert backend.dot(x,w)==pytest.approx(x@w,abs=5e-13)
    assert backend.device_passes>9
    adc=PhysicalMAC(MACConfig(dac_bits=None,adc_bits=12,adc_full_scale=1))
    y=adc.dot([.5],[.5],input_scale=1,weight_scale=1)
    assert abs(y-.25)<=1/4095+1e-14
    with pytest.raises(ValueError):
        PhysicalMAC(MACConfig(dac_bits=None,adc_bits=12,adc_full_scale=.1)).dot([1],[1])


def test_higher_dac_precision_reduces_ensemble_error():
    rng=np.random.default_rng(8);x=rng.uniform(0,1,(60,12));w=rng.uniform(-1,1,12)
    errors=[]
    for bits in [4,8,12,16]:
        backend=PhysicalMAC(MACConfig(dac_bits=bits))
        errors.append(np.sqrt(np.mean([(backend.dot(row,w)-row@w)**2 for row in x])))
    assert all(a>b for a,b in zip(errors,errors[1:]))


def test_noise_stream_reproducibility_and_branch_independence():
    config=MACConfig(dac_bits=None,shot_enabled=True,seed=193)
    a,b=PhysicalMAC(config),PhysicalMAC(config)
    ra=[a.dot(np.ones(4),np.zeros(4)) for _ in range(200)]
    rb=[b.dot(np.ones(4),np.zeros(4)) for _ in range(200)]
    np.testing.assert_array_equal(ra,rb)
    assert np.var(ra)>0
    changed=PhysicalMAC(MACConfig(dac_bits=None,shot_enabled=True,seed=194))
    assert changed.dot(np.ones(4),np.zeros(4))!=ra[0]


def test_pooling_relu_and_dense_layer():
    x=np.arange(-8,8,dtype=float).reshape(1,1,4,4)
    pooled=max_pool2d(relu(x))
    np.testing.assert_array_equal(pooled,[[[[0,0],[5,7]]]])
    w=np.array([[1,-2,3,-4],[-1,2,-3,4]],dtype=float)
    out=linear(pooled.reshape(1,-1),w,[.3,-.4],backend=PhysicalMAC(MACConfig(dac_bits=None)))
    np.testing.assert_allclose(out,pooled.reshape(1,-1)@w.T+[.3,-.4],atol=1e-12)


@pytest.mark.parametrize('kwargs',[
    {'stride':0},{'stride':1.5},{'stride':True},{'padding':-1},
    {'dilation':0},{'groups':0},{'groups':2},{'bias':[1,2]},
])
def test_invalid_convolution_contract(kwargs):
    with pytest.raises(ValueError):conv2d(np.ones((1,1,3,3)),np.ones((1,1,2,2)),**kwargs)


def test_nonfinite_data_and_fixed_ranges_rejected():
    with pytest.raises(ValueError):PhysicalMAC().dot([np.nan],[1])
    with pytest.raises(ValueError):PhysicalMAC().dot([2],[1],input_scale=1)
    with pytest.raises(ValueError):conv2d(np.full((1,1,3,3),np.nan),np.ones((1,1,2,2)))
