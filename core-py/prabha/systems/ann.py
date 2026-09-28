"""Fixed-architecture 4-3-2 inference using the B23/B24 physical neuron."""
import numpy as np
from .perceptron import NeuronConfig, physical_neuron, vector

DEFAULT_NETWORK = {
    'w1': [[.8, -.6, .4, -.9], [-.3, .7, .5, .2], [.6, .1, -.8, .7]],
    'b1': [.2, -.1, .05],
    'w2': [[.7, -.5, .6], [-.4, .9, -.7]], 'b2': [.1, -.05]}


def network_arrays(network):
    if not isinstance(network, dict) or set(network) != {'w1', 'b1', 'w2', 'b2'}:
        raise ValueError('Network requires exactly w1, b1, w2 and b2.')
    out = {}
    for k, shape in [('w1', (3, 4)), ('b1', (3,)), ('w2', (2, 3)), ('b2', (2,))]:
        a = np.asarray(network[k], dtype=float)
        limit = 1 if k.startswith('w') else 10
        if a.shape != shape or not np.all(np.isfinite(a)) or np.any(np.abs(a) > limit):
            raise ValueError(f'{k} must have shape {shape}, finite values and absolute values <= {limit}.')
        out[k] = a
    return out


def infer(inputs, network=None, config=None):
    config = config or NeuronConfig()
    x = vector(inputs, 'Inputs', 0, 1, 4)
    n = network_arrays(DEFAULT_NETWORK if network is None else network)
    hidden = [physical_neuron(x, w, b, config) for w, b in zip(n['w1'], n['b1'])]
    h = np.array([v['output'] for v in hidden])
    output = [physical_neuron(h, w, b, config) for w, b in zip(n['w2'], n['b2'])]
    ideal_hidden = 1 / (1 + np.exp(-(n['w1'] @ x + n['b1'])))
    ideal_out = 1 / (1 + np.exp(-(n['w2'] @ ideal_hidden + n['b2'])))
    physical = np.array([v['output'] for v in output])
    e = physical - ideal_out
    return {'inputs': x.tolist(), 'hidden': hidden, 'output_neurons': output,
            'ideal_hidden': ideal_hidden.tolist(), 'physical_hidden': h.tolist(),
            'ideal_output': ideal_out.tolist(), 'physical_output': physical.tolist(),
            'error': e.tolist(), 'max_error': float(np.max(np.abs(e))),
            'rms_error': float(np.sqrt(np.mean(e ** 2))),
            'dac_bits': config.dac_bits, 'adc_bits': config.adc_bits,
            'model_scope': 'deterministic behavioural inference with converter quantization'}


def batch(count=100, seed=12345, network=None, config=None, inputs=None):
    if isinstance(count, bool) or not isinstance(count, int) or not 1 <= count <= 256:
        raise ValueError('Batch count must be an integer from 1 to 256.')
    if isinstance(seed, bool) or not isinstance(seed, int) or not 0 <= seed < 2**32:
        raise ValueError('Seed must be an integer from 0 to 4294967295.')
    if inputs is None:
        x = np.random.default_rng(seed).uniform(.05, .95, (count, 4))
        x[0] = [.9, .3, .7, .5]
    else:
        x = np.asarray(inputs, dtype=float)
        if x.ndim != 2 or x.shape[1] != 4 or not 1 <= len(x) <= 256:
            raise ValueError('Batch inputs must have shape [1..256, 4].')
    results = [infer(row, network, config) for row in x]
    e = np.array([r['error'] for r in results])
    ideal = np.array([r['ideal_output'] for r in results])
    actual = np.array([r['physical_output'] for r in results])
    h_e = np.array([np.array(r['physical_hidden']) - r['ideal_hidden'] for r in results])
    rows = [{'sample': i, 'inputs': r['inputs'], 'ideal': r['ideal_output'],
             'physical': r['physical_output'], 'error': r['error']} for i, r in enumerate(results)]
    return {'count': len(results), 'seed': seed, 'max_error': float(np.max(np.abs(e))),
            'rms_error': float(np.sqrt(np.mean(e ** 2))), 'mean_error': float(e.mean()),
            'hidden_max_error': float(np.max(np.abs(h_e))),
            'hidden_rms_error': float(np.sqrt(np.mean(h_e ** 2))),
            'winner_mismatches': int(np.sum(np.argmax(ideal, 1) != np.argmax(actual, 1))),
            'worst_index': int(np.argmax(np.max(np.abs(e), axis=1))), 'rows': rows,
            'scope': 'fixed-weight operating-range validation, not classification accuracy'}
