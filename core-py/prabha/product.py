"""Shared JSON operations for HTTP, browser Python and desktop sidecar clients."""
from pathlib import Path
import json
import math
import sys
import numpy as np
from . import SpecSchemas, BlockRegistry, System, RunContext, ValidationError
from .systems import infer, batch, physical_neuron, NeuronConfig, DEFAULT_NETWORK
from .blocks.cw_laser import CWLaser
from .blocks.mzm import MachZehnderModulator
from .blocks.component_kernels import MODEL_REVISION

ROOT = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parents[2]))
VERSION = '0.1.0-preview.3'


def registry():
    schemas = SpecSchemas(ROOT / 'spec/schema')
    reg = BlockRegistry(schemas)
    reg.load_dir(ROOT / 'spec/blocks')
    reg.load_dir(ROOT / 'blocks-lib')
    return schemas, reg


def finite(v, name, low, high):
    v = float(v)
    if not math.isfinite(v) or not low <= v <= high:
        raise ValueError(f'{name} must be finite and in [{low}, {high}].')
    return v


def graph(payload):
    design = payload.get('design')
    if not isinstance(design, dict):
        raise ValueError('A .prabha design object is required.')
    schemas, reg = registry()
    schemas.check_netlist(design)
    if len(design['blocks']) > 64 or len(design['connections']) > 256:
        raise ValueError('Preview limit: 64 blocks and 256 connections.')
    duration = finite(payload.get('duration', 4e-10), 'Duration', 1e-15, 1)
    seed = payload.get('seed', 0)
    if not isinstance(seed, int) or isinstance(seed, bool) or not 0 <= seed < 2**32:
        raise ValueError('Seed must be an unsigned 32-bit integer.')
    # Bound all rate-bearing source allocations before the engine can create arrays.
    for b in design['blocks']:
        if b['ref'] not in reg:
            continue  # semantic validation reports R1
        params = {p['name']: p['default'] for p in reg.get(b['ref'])['params']}
        params.update(b.get('params', {}))
        for k in ['fs', 'rate']:
            if k in params:
                rate = finite(params[k], k, 1e-12, 1e15)
                if k == 'fs' and not 1 <= math.ceil(rate * duration) <= 20000:
                    raise ValueError('Preview limit: 1 to 20,000 samples per source. Reduce duration or sample rate.')
        for k, v in params.items():
            if isinstance(v, (float, int)) and not math.isfinite(v):
                raise ValueError(f'{k} must be finite.')
            if isinstance(v, list) and len(v) > 256:
                raise ValueError('Preview vector limit: 256 values.')
    noise = payload.get('noise', True)
    if not isinstance(noise, bool):
        raise ValueError('Noise must be a boolean.')
    sysm = System(design, reg, RunContext(duration, noise, seed))
    if len(sysm.flat['blocks']) > 256:
        raise ValueError('Preview limit: 256 flattened blocks.')
    # Flattened compounds can contain sources absent from the top-level design.
    for block in sysm.flat['blocks']:
        definition = reg.get(block['ref'])
        params = {p['name']: p['default'] for p in definition['params']}
        params.update(block.get('params') or {})
        if definition['implementation'] in {'DriveSource', 'WeightSource', 'ComponentSource'}:
            sps = finite(params['sps'], 'Samples per symbol', 1, 256)
            if int(sps) != sps:
                raise ValueError('Samples per symbol must be an integer.')
            effective_fs = finite(params['rate'], 'Symbol rate (GHz)', 1e-12, 1e6) * 1e9 * sps
            values = str(params['values']).split(',')
            if not 1 <= len(values) <= 256:
                raise ValueError('Preview vector limit: 1 to 256 values.')
            for value in values:
                finite(value, 'Source value', -1e6, 1e6)
        elif 'fs' in params:
            effective_fs = finite(params['fs'], 'Sample rate', 1e-12, 1e15)
        else:
            continue
        if not 1 <= int(effective_fs * duration) <= 20000:
            raise ValueError('Preview limit: 1 to 20,000 samples per source. Reduce duration or sample rate.')
    probes = {}
    for inst, ports in sysm.run().items():
        probes[inst] = {}
        for name, sig in ports.items():
            a = np.asarray(np.abs(sig.data[0]) ** 2 if sig.kind == 'optical' else sig.data, dtype=float).ravel()
            if not len(a) or not np.all(np.isfinite(a)):
                raise ValueError('The model produced a non-finite or empty signal. Check parameters.')
            idx = np.linspace(0, len(a) - 1, min(1200, len(a))).astype(int)
            probe = {'kind': sig.kind, 'fs': sig.fs, 'n': int(sig.n),
                     'unit': 'W' if sig.kind == 'optical' else sig.units,
                     'last': float(a[-1]), 'data': a[idx].tolist(),
                     'sample_indices': idx.tolist()}
            if sig.kind == 'optical':
                probe['phase_rad'] = np.unwrap(np.angle(sig.single_channel()))[idx].tolist()
            probes[inst][name] = probe
    return {'warnings': [vars(v) for v in sysm.warnings], 'probes': probes,
            'model_revision': MODEL_REVISION, 'version': VERSION,
            'settings': {'duration': duration, 'noise': noise, 'seed': seed},
            'model_profiles': sorted({'components' if b['ref'].startswith('model_') else 'legacy-peman'
                                      for b in design['blocks']})}


def component(payload):
    kind = payload.get('kind', 'mzm')
    if kind == 'mzm':
        vpi = finite(payload.get('v_pi', 1), 'Vpi', .1, 10)
        bias = finite(payload.get('bias', float(np.pi / 2)), 'Bias', -2 * np.pi, 2 * np.pi)
        v = np.linspace(-vpi, vpi, 401)
        tr = MachZehnderModulator(V_pi=vpi, phi_bias=bias).transfer(v)
        return {'kind': kind, 'x': v.tolist(), 'y': tr.tolist(), 'x_label': 'Drive voltage (V)', 'y_label': 'Transmission',
                'summary': {'minimum': float(tr.min()), 'maximum': float(tr.max())}}
    if kind == 'laser':
        p0 = finite(payload.get('power_mw', 1), 'Power', .01, 100)
        rin = finite(payload.get('rin_db_hz', -150), 'RIN', -180, -140)
        linewidth = finite(payload.get('linewidth_hz', 1e6), 'Linewidth', 0, 1e8)
        seed = payload.get('seed', 1)
        if not isinstance(seed, int) or not 0 <= seed < 2**32:
            raise ValueError('Seed must be an unsigned 32-bit integer.')
        laser = CWLaser(P0_mW=p0, fs=160e9, duration=1e-8, rin_db_hz=rin, linewidth_hz=linewidth, seed=seed)
        t, e = laser.generate(include_rin=True, include_linewidth=True)
        power = laser.power(e) * 1e3
        return {'kind': kind, 'x': (t * 1e9).tolist(), 'y': power.tolist(), 'x_label': 'Time (ns)', 'y_label': 'Power (mW)',
                'summary': {'mean_mW': float(power.mean()), 'std_mW': float(power.std()),
                            'theoretical_std_mW': p0 * np.sqrt(10**(rin / 10) * 80e9)}}
    raise ValueError('Supported live component experiments: laser and mzm.')


def dispatch(payload):
    try:
        if not isinstance(payload, dict):
            raise ValueError('Request must be a JSON object.')
        action = payload.get('action', 'meta')
        cfg = NeuronConfig(payload.get('dac_bits', 12), payload.get('adc_bits', 12))
        if action == 'meta':
            result = {'version': VERSION, 'network': DEFAULT_NETWORK, 'default_inputs': [.9, .3, .7, .5],
                      'model_revision': MODEL_REVISION,
                      'scope': 'behavioural simulation', 'actions': ['infer', 'batch', 'neuron', 'component', 'graph', 'blocks', 'example']}
        elif action == 'infer':
            result = infer(payload.get('inputs', [.9, .3, .7, .5]), payload.get('network'), cfg)
        elif action == 'batch':
            result = batch(payload.get('count', 100), payload.get('seed', 12345), payload.get('network'), cfg, payload.get('inputs'))
        elif action == 'neuron':
            result = physical_neuron(payload.get('inputs', [.9, .3, .7, .5]), payload.get('weights', [.8, -.6, .4, -.9]), payload.get('bias', .2), cfg)
        elif action == 'component':
            result = component(payload)
        elif action == 'graph':
            result = graph(payload)
        elif action == 'blocks':
            result = list(registry()[1].defs.values())
        elif action == 'example':
            name = payload.get('name', 'legacy')
            if name == 'legacy':
                result = json.loads((ROOT / 'peman.prabha').read_text())
            elif name in {'neuron', 'expanded', 'receiver', 'nonlinear'}:
                result = json.loads((ROOT / 'spec/examples' / (name + '.json')).read_text())
            else:
                raise ValueError('Unknown example; choose neuron, expanded, receiver, nonlinear or legacy.')
        else:
            raise ValueError('Unknown operation.')
        return {'ok': True, 'result': result}
    except ValidationError as exc:
        return {'ok': False, 'error': 'The design violates the simulation contract.', 'violations': [vars(v) for v in exc.violations]}
    except (ValueError, TypeError, KeyError, ArithmeticError, IndexError) as exc:
        return {'ok': False, 'error': str(exc)}


if __name__ == '__main__':
    request = json.loads(sys.argv[1] if len(sys.argv) > 1 else sys.stdin.read(1_000_001))
    print(json.dumps(dispatch(request), allow_nan=False))
