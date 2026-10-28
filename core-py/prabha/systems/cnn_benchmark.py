"""Explicit repeated software benchmark, separate from ordinary inference."""
from dataclasses import asdict
import os
import platform
import sys
import time
import numpy as np
from .cnn_training import forward
from .cnn_workspace import _experiment, _integer, _stages
from .mac import PhysicalMAC


def benchmark(root, payload):
    accepted, parameters, raw, x, labels, ids, positions, cfg, metadata = _experiment(root, payload)
    blocks = _integer(payload.get('blocks', 5), 'blocks', 1, 21)
    warmups = _integer(payload.get('warmups', 1), 'warmups', 0, 5)
    order_seed = _integer(payload.get('order_seed', 20261028), 'order_seed', 0, 2**32 - 1)
    rng = np.random.default_rng(order_seed)
    rows, last, counters = [], {}, {}
    maximum = 0.
    for block in range(-warmups, blocks):
        order = rng.permutation(['numpy', 'waveform', 'symbol']).tolist()
        outputs = {}
        for position, method in enumerate(order):
            backend = None if method == 'numpy' else PhysicalMAC(cfg, execution=method)
            started = time.perf_counter()
            logits = forward(x, parameters) if backend is None else _stages(x, parameters, backend)['logits']
            elapsed = time.perf_counter() - started
            outputs[method] = logits
            if block >= 0:
                rows.append({'block': block + 1, 'order': position + 1, 'method': method, 'seconds': elapsed})
            if backend is not None:
                counters[method] = {'mac_calls': backend.calls, 'device_passes': backend.device_passes,
                                    'equivalent_samples': backend.waveform_samples,
                                    'materialized_samples': backend.materialized_waveform_samples}
        delta = outputs['symbol'] - outputs['waveform']
        maximum = max(maximum, float(np.max(abs(delta))))
        if not np.allclose(outputs['symbol'], outputs['waveform'], rtol=1e-12, atol=1e-11):
            raise ValueError('Symbol and waveform outputs failed the accuracy gate; no speed claim is available.')
        if not np.array_equal(outputs['symbol'].argmax(1), outputs['waveform'].argmax(1)):
            raise ValueError('Symbol and waveform predictions differ; no speed claim is available.')
        last = outputs
    medians = {method: float(np.median([r['seconds'] for r in rows if r['method'] == method]))
               for method in ['numpy', 'waveform', 'symbol']}
    known = [i for i, label in enumerate(labels) if label is not None]
    correct = {method: sum(int(logits[i].argmax() == labels[i]) for i in known)
               for method, logits in last.items()}
    error = last['symbol'] - last['numpy']
    return {'schema': 'prabha.cnn-benchmark.v1', 'count': len(x), 'blocks': blocks,
            'warmups_excluded': warmups, 'order_seed': order_seed, 'rows': rows,
            'median_seconds': medians, 'waveform_over_symbol': medians['waveform'] / medians['symbol'],
            'symbol_over_numpy': medians['symbol'] / medians['numpy'],
            'maximum_symbol_waveform_logit_difference': maximum,
            'symbol_waveform_prediction_disagreements': 0, 'correct': correct,
            'labelled_images': len(known), 'settings': accepted['settings'], 'configuration': asdict(cfg),
            'rms_logit_error_vs_numpy': float(np.sqrt(np.mean(error**2))),
            'maximum_logit_error_vs_numpy': float(np.max(abs(error))), 'counters': counters,
            'model_sha256': metadata['model_sha256'], 'dataset_sha256': metadata['dataset_sha256'],
            'environment': {'python': sys.version, 'numpy': np.__version__, 'platform': platform.platform(),
                            'thread_environment': {k: os.environ.get(k) for k in
                                                   ['OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS']}},
            'timing_scope': 'Resident-input forward passes. Backend construction, loading, validation, accuracy gates and exports excluded. Method order randomized within each block. Ratios use medians of whole-workload times.',
            'claim_scope': 'Software CNN comparison on this computer. No INTERCONNECT CNN execution or photonic hardware measurement. Do not combine this ratio with the archived scalar native ratio.'}
