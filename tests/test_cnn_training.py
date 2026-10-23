"""Independent forward and finite-difference checks of the trainable CNN."""
import numpy as np
from prabha.systems.cnn_training import initialise,forward,loss_and_grad
from prabha.systems.cnn import conv2d,relu,max_pool2d,linear

class DigitalMAC:
    def dot(self,x,w):return float(x@w)

def test_vectorised_training_forward_matches_existing_operators():
    rng=np.random.default_rng(81)
    x=rng.uniform(.02,.98,(3,1,8,8));p=initialise(73)
    features=max_pool2d(relu(conv2d(x,p['conv_weight'],p['conv_bias'],backend=DigitalMAC())))
    expected=linear(features.reshape(3,-1),p['dense_weight'],p['dense_bias'],backend=DigitalMAC())
    np.testing.assert_allclose(forward(x,p),expected,rtol=1e-12,atol=1e-12)

def test_training_gradients_against_finite_differences():
    rng=np.random.default_rng(411)
    x=rng.uniform(.03,.95,(4,1,8,8));y=np.array([1,3,7,9]);p=initialise(91)
    loss,g=loss_and_grad(x,y,p)
    assert np.isfinite(loss)
    eps=1e-6
    for key,indices in {'conv_weight':[(0,0,0,0),(2,0,1,2),(3,0,2,1)],
                        'conv_bias':[(0,),(2,)],'dense_weight':[(1,2),(7,11)],'dense_bias':[(1,),(9,)]}.items():
        for index in indices:
            original=p[key][index]
            p[key][index]=original+eps;plus=loss_and_grad(x,y,p)[0]
            p[key][index]=original-eps;minus=loss_and_grad(x,y,p)[0]
            p[key][index]=original
            np.testing.assert_allclose(g[key][index],(plus-minus)/(2*eps),rtol=3e-5,atol=3e-7)
