"""Small float64 NumPy CNN reference with analytical backpropagation.

Training is conventional digital optimisation. Physical inference uses the
separate existing cnn.py operators and PhysicalMAC with transferred weights.
"""
import numpy as np


def initialise(seed=20261015, filters=4):
    rng = np.random.default_rng(seed)
    return {'conv_weight': rng.normal(0, np.sqrt(2/9), (filters,1,3,3)),
            'conv_bias': np.zeros(filters),
            'dense_weight': rng.normal(0, np.sqrt(2/(9*filters)), (10,9*filters)),
            'dense_bias': np.zeros(10)}


def forward(x, parameters, *, cache=False):
    x = np.asarray(x, dtype=np.float64)
    if x.ndim != 4 or x.shape[1:] != (1,8,8) or not np.isfinite(x).all():
        raise ValueError('Expected finite NCHW images with shape [N,1,8,8].')
    p = parameters
    n, filters = len(x), len(p['conv_bias'])
    patches = np.lib.stride_tricks.sliding_window_view(x[:,0], (3,3), axis=(1,2)).reshape(n,36,9)
    pre = (np.einsum('npj,kj->npk',patches,p['conv_weight'].reshape(filters,9)) + p['conv_bias']).reshape(n,6,6,filters).transpose(0,3,1,2)
    activation = np.maximum(pre, 0)
    blocks = activation.reshape(n,filters,3,2,3,2).transpose(0,1,2,4,3,5).reshape(n,filters,3,3,4)
    indices = blocks.argmax(-1)
    features = blocks.max(-1).reshape(n,9*filters)
    logits = features @ p['dense_weight'].T + p['dense_bias']
    if cache:
        return logits, (patches,pre,indices,features)
    return logits


def probabilities(logits):
    z = logits - np.max(logits,axis=1,keepdims=True)
    e = np.exp(z)
    return e/e.sum(axis=1,keepdims=True)


def loss_and_grad(x, y, parameters, l2=1e-4):
    logits, (patches,pre,indices,features) = forward(x,parameters,cache=True)
    n, filters = len(x),len(parameters['conv_bias'])
    z = logits-logits.max(axis=1,keepdims=True)
    log_denominator = np.log(np.exp(z).sum(axis=1))
    loss = float(np.mean(log_denominator-z[np.arange(n),y]))
    loss += .5*l2*sum(float(np.sum(parameters[k]**2)) for k in ['conv_weight','dense_weight'])
    dz = probabilities(logits)
    dz[np.arange(n),y] -= 1
    dz /= n
    grad = {'dense_weight':dz.T@features+l2*parameters['dense_weight'],
            'dense_bias':dz.sum(0)}
    dp = (dz@parameters['dense_weight']).reshape(n,filters,3,3)
    dblocks = np.zeros((n,filters,3,3,4))
    np.put_along_axis(dblocks,indices[...,None],dp[...,None],axis=-1)
    da = dblocks.reshape(n,filters,3,3,2,2).transpose(0,1,2,4,3,5).reshape(n,filters,6,6)
    dc = da*(pre>0)
    dc_flat = dc.transpose(0,2,3,1).reshape(n,36,filters)
    grad['conv_weight'] = np.einsum('npk,npj->kj',dc_flat,patches).reshape(filters,1,3,3)+l2*parameters['conv_weight']
    grad['conv_bias'] = dc.sum((0,2,3))
    return loss,grad


def evaluate(x,y,parameters):
    logits=forward(x,parameters)
    z=logits-logits.max(axis=1,keepdims=True)
    loss=float(np.mean(np.log(np.exp(z).sum(1))-z[np.arange(len(y)),y]))
    return loss,float(np.mean(logits.argmax(1)==y))


def train(x,y,x_val,y_val,*,epochs=160,seed=20261015,batch_size=64,learning_rate=.005,l2=1e-4,filters=4):
    p=initialise(seed,filters)
    rng=np.random.default_rng(seed+1)
    m={k:np.zeros_like(v) for k,v in p.items()}
    v={k:np.zeros_like(a) for k,a in p.items()}
    best_loss=np.inf;best=None;best_epoch=0;history=[];step=0
    for epoch in range(1,epochs+1):
        order=rng.permutation(len(x))
        for start in range(0,len(x),batch_size):
            ids=order[start:start+batch_size]
            _,g=loss_and_grad(x[ids],y[ids],p,l2)
            step+=1
            for k in p:
                m[k]=.9*m[k]+.1*g[k]
                v[k]=.999*v[k]+.001*g[k]**2
                p[k]-=learning_rate*(m[k]/(1-.9**step))/(np.sqrt(v[k]/(1-.999**step))+1e-8)
        train_loss,train_accuracy=evaluate(x,y,p)
        val_loss,val_accuracy=evaluate(x_val,y_val,p)
        history.append({'epoch':epoch,'train_loss':train_loss,'validation_loss':val_loss,
                        'train_accuracy':train_accuracy,'validation_accuracy':val_accuracy})
        if val_loss<best_loss:
            best_loss=val_loss;best_epoch=epoch;best={k:a.copy() for k,a in p.items()}
        if epoch%20==0 or epoch==1:
            print(f'Epoch {epoch}/{epochs}: train {train_accuracy:.4f}; validation {val_accuracy:.4f}; validation loss {val_loss:.4f}',flush=True)
    return best,history,best_epoch
