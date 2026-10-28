"""Editable, reproducible CNN experiments and intermediate-layer inspection."""
from dataclasses import asdict
import hashlib
import json
import numbers
import numpy as np
from .cnn_assets import load_assets as _assets
from .cnn import conv2d, relu, max_pool2d, linear
from .cnn_training import forward
from .mac import MACConfig, PhysicalMAC, DigitalMAC
import time

SHAPES = {'conv_weight': (4, 1, 3, 3), 'conv_bias': (4,),
          'dense_weight': (10, 36), 'dense_bias': (10,)}
CONVERTERS = {'dac_bits': 12, 'adc_bits': None, 'adc_full_scale': 64.,
              'dac_rounding': 'nearest_lower'}
LAYERS = ('input', 'convolution', 'relu', 'pool', 'flatten', 'logits')


def _execution(payload):
    value = payload.get('execution', 'auto')
    if not isinstance(value, str) or value not in ('auto', 'symbol', 'waveform'):
        raise ValueError('execution must be auto, symbol or waveform.')
    return value


def _integer(value, name, low, high):
    if isinstance(value, bool) or not isinstance(value, numbers.Integral) or not low <= value <= high:
        raise ValueError(f'{name} must be an integer from {low} to {high}.')
    return int(value)


def _array(value, shape, name, low, high):
    # Reject booleans/strings rather than silently coercing edited JSON.
    def numeric(item):
        if isinstance(item, (list, tuple)): return all(numeric(v) for v in item)
        return isinstance(item, numbers.Real) and not isinstance(item, (bool, np.bool_))
    if not numeric(value): raise ValueError(name + ' must contain only numbers.')
    try: a = np.asarray(value, dtype=np.float64)
    except (ValueError, TypeError) as error: raise ValueError(name + ' is not a rectangular numeric array.') from error
    if a.shape != shape or not np.isfinite(a).all() or np.any(a < low) or np.any(a > high):
        raise ValueError(f'{name} must have shape {list(shape)} with finite values in [{low}, {high}].')
    return a


def defaults(root):
    p, images, labels, ids, metadata = _assets(root)
    return {'input': {'mode': 'heldout', 'count': 360, 'start': 0,
                      'pixels': images[0].astype(float).tolist(), 'label': int(labels[0])},
            'model': {k: p[k].tolist() for k in SHAPES}, 'converters': dict(CONVERTERS)}


def validate(root, payload):
    _execution(payload)
    settings = payload.get('settings')
    if settings is None:
        settings = defaults(root)
        settings['input'].update(count=payload.get('count', 360), start=payload.get('start', 0))
    if not isinstance(settings, dict) or set(settings) != {'input', 'model', 'converters'}:
        raise ValueError('CNN settings must contain input, model and converters objects.')
    model = settings['model']
    if not isinstance(model, dict) or set(model) != set(SHAPES):
        raise ValueError('Model must contain conv_weight, conv_bias, dense_weight and dense_bias.')
    parameters = {k: _array(model[k], shape, k, -100., 100.) for k, shape in SHAPES.items()}
    source = settings['input']
    if not isinstance(source, dict) or set(source) != {'mode', 'count', 'start', 'pixels', 'label'}:
        raise ValueError('Input settings must contain mode, count, start, pixels and label.')
    mode = source['mode']
    if mode not in ('heldout', 'custom'): raise ValueError('Input mode must be heldout or custom.')
    count = _integer(source['count'], 'count', 1, 360)
    start = _integer(source['start'], 'start', 0, 359)
    if start + count > 360: raise ValueError('The held-out range must end at or before image 360.')
    pixels = _array(source['pixels'], (8, 8), 'pixels', 0., 16.)
    label = source['label']
    if label is not None: label = _integer(label, 'label', 0, 9)
    converters = settings['converters']
    if not isinstance(converters, dict) or set(converters) != set(CONVERTERS):
        raise ValueError('Converters must contain dac_bits, adc_bits, adc_full_scale and dac_rounding.')
    for key in ('dac_bits', 'adc_bits'):
        if converters[key] is not None: _integer(converters[key], key, 1, 24)
    scale = converters['adc_full_scale']
    if isinstance(scale, bool) or not isinstance(scale, numbers.Real) or not np.isfinite(scale) or not .001 <= scale <= 1e6:
        raise ValueError('ADC full scale must be finite and between 0.001 and 1000000.')
    MACConfig(**converters, mzm_extinction_ratio_db=100., weight_extinction_ratio_db=100.)
    normalized = {'input': {'mode': mode, 'count': count, 'start': start,
                           'pixels': pixels.tolist(), 'label': label},
                  'model': {k: a.tolist() for k, a in parameters.items()},
                  'converters': {**converters, 'adc_full_scale': float(scale)}}
    frozen, images, labels, ids, metadata = _assets(root)
    weights_match = all(np.array_equal(parameters[k], frozen[k]) for k in SHAPES)
    weight_hash = hashlib.sha256(json.dumps(normalized['model'], sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    return {'settings': normalized, 'weights_match_checkpoint': weights_match,
            'reference_converter_profile': normalized['converters'] == CONVERTERS,
            'effective_weights_sha256': weight_hash,
            'count': count if mode == 'heldout' else 1}


def info(root, payload=None):
    p, images, labels, ids, metadata = _assets(root)
    position = _integer((payload or {}).get('sample_index', 0), 'sample_index', 0, 359)
    return {'architecture': '8 x 8 -> Conv(1,4,3) -> ReLU -> MaxPool(2) -> Linear(36,10)',
            'parameters': 410, 'test_images': 360, 'training_images': 1149, 'validation_images': 288,
            'selected_epoch': metadata['selected_epoch'], 'default_settings': defaults(root),
            'sample': {'position': position, 'dataset_index': int(ids[position]),
                       'pixels': images[position].tolist(), 'label': int(labels[position])},
            'recorded_validation': {'correct': 354, 'total': 360, 'accuracy': 354 / 360, 'prediction_disagreements': 0},
            'scope': 'Editable fixed-architecture software CNN; noise disabled. Changes require fresh inference.',
            'execution_modes': ['auto', 'symbol', 'waveform'], 'default_execution': 'auto',
            'operator': 'Real cross-correlation with no spatial kernel reversal',
            'model_sha256': metadata['model_sha256'], 'dataset_sha256': metadata['dataset_sha256']}


def _experiment(root, payload):
    accepted = validate(root, payload)
    s = accepted['settings']; source = s['input']
    p = {k: np.asarray(v, dtype=np.float64) for k, v in s['model'].items()}
    frozen, raw, labels, ids, metadata = _assets(root)
    if source['mode'] == 'heldout':
        sl = slice(source['start'], source['start'] + source['count'])
        raw, labels, ids = raw[sl], labels[sl].tolist(), ids[sl].tolist()
        positions = list(range(source['start'], source['start'] + source['count']))
    else:
        raw = np.asarray([source['pixels']], dtype=np.float64)
        labels, ids, positions = [source['label']], [None], [None]
    cfg = MACConfig(**s['converters'], mzm_extinction_ratio_db=100., weight_extinction_ratio_db=100.)
    return accepted, p, raw, raw[:, None].astype(np.float64) / 16., labels, ids, positions, cfg, metadata


def _stages(x, p, backend):
    convolution = conv2d(x, p['conv_weight'], p['conv_bias'], backend=backend)
    activation = relu(convolution)
    pool = max_pool2d(activation)
    flat = pool.reshape(len(x), -1)
    logits = linear(flat, p['dense_weight'], p['dense_bias'], backend=backend)
    return dict(zip(LAYERS, (x, convolution, activation, pool, flat, logits)))


def _describe_layers(reference, actual, scope):
    layers = []
    for name in LAYERS:
        a, b = reference[name][0], actual[name][0]
        delta = b - a
        layers.append({'name': name, 'shape': list(a.shape), 'numpy': a.tolist(), 'prabha': b.tolist(),
                       'rms_error': float(np.sqrt(np.mean(delta ** 2))),
                       'maximum_error': float(np.max(abs(delta))),
                       'numpy_min': float(a.min()), 'numpy_max': float(a.max()),
                       'prabha_min': float(b.min()), 'prabha_max': float(b.max())})
    return {'layers': layers, 'scope': scope}


def _inspection(x, p, cfg, execution='auto'):
    reference = _stages(x, p, DigitalMAC())
    actual = _stages(x, p, PhysicalMAC(cfg, execution=execution))
    return _describe_layers(reference, actual, 'Selected image recomputed on demand. Input normalized by 16. Bias/ReLU/pooling/scaling are digital/software operations.')


def inspect(root, payload):
    accepted, p, raw, x, labels, ids, positions, cfg, metadata = _experiment(root, payload)
    index = _integer(payload.get('index', 0), 'inspection index', 0, len(x) - 1)
    return {**_inspection(x[index:index + 1], p, cfg, _execution(payload)), 'index': index, 'label': labels[index],
            'test_position': positions[index], 'settings': accepted['settings']}


def compare(root, payload):
    accepted, p, raw, x, labels, ids, positions, cfg, metadata = _experiment(root, payload)
    count = len(x)
    began = time.perf_counter(); reference = forward(x, p); seconds = time.perf_counter() - began
    began = time.perf_counter(); shared_stages = _stages(x, p, DigitalMAC()); shared_seconds = time.perf_counter() - began
    shared = shared_stages['logits']
    if not np.allclose(shared, reference, rtol=1e-11, atol=1e-11): raise ValueError('CNN reference and shared operators disagree.')
    requested = _execution(payload)
    backend = PhysicalMAC(cfg, execution=requested)
    began = time.perf_counter(); actual_stages = _stages(x, p, backend); physical_seconds = time.perf_counter() - began
    actual = actual_stages['logits']
    a, b, error = reference.argmax(1), actual.argmax(1), actual - reference
    known = [i for i, label in enumerate(labels) if label is not None]
    ca = sum(int(a[i] == labels[i]) for i in known); cb = sum(int(b[i] == labels[i]) for i in known)
    rows = [{'test_position': positions[i], 'dataset_index': ids[i], 'label': labels[i],
             'numpy_prediction': int(a[i]), 'prabha_prediction': int(b[i]),
             'correct': bool(b[i] == labels[i]) if labels[i] is not None else None,
             'pixels': raw[i].reshape(-1).tolist(), 'numpy_logits': reference[i].tolist(),
             'prabha_logits': actual[i].tolist(), 'maximum_logit_error': float(np.max(abs(error[i])))} for i in range(count)]
    return {'count': count, 'start': accepted['settings']['input']['start'], 'labelled_images': len(known),
            'numpy_correct': ca if known else None, 'prabha_correct': cb if known else None,
            'numpy_accuracy': ca / len(known) if known else None, 'prabha_accuracy': cb / len(known) if known else None,
            'prediction_disagreements': int(np.sum(a != b)),
            'rms_logit_error': float(np.sqrt(np.mean(error ** 2))), 'max_logit_error': float(np.max(abs(error))),
            'numpy_seconds': seconds, 'shared_digital_seconds': shared_seconds, 'prabha_seconds': physical_seconds,
            'slowdown_vs_numpy': physical_seconds / max(seconds, 1e-12),
            'mac_calls': backend.calls, 'device_passes': backend.device_passes, 'waveform_samples': backend.waveform_samples,
            'equivalent_waveform_samples': backend.waveform_samples,
            'materialized_waveform_samples': backend.materialized_waveform_samples,
            'execution_mode': backend.execution_mode,
            'execution_requested': requested,
            'operator': 'cross-correlation (no spatial kernel flip)',
            'execution_scope': 'Symbol mode integrates deterministic constant symbols with the component equations. Waveform mode remains available for sampled noise and traces. waveform_samples is the equivalent sample-grid count.',
            'configuration': asdict(cfg), 'rows': rows, **accepted,
            'inspection': _describe_layers(shared_stages, actual_stages, 'First-image tensors reused from the completed forward passes. No extra physical inference. Input normalized by 16. Bias/ReLU/pooling/scaling are digital/software operations.'),
            'noise_enabled': False, 'native_cnn_run': False,
            'timing_scope': 'Single resident-input forward pass per path. Loading, validation, shared digital comparison, tensor serialization and exports excluded. Explicit repeated benchmarks are separate from ordinary inference.',
            'model_sha256': metadata['model_sha256'], 'dataset_sha256': metadata['dataset_sha256']}
