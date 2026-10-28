from pathlib import Path
import json
import shutil
import numpy as np
import pytest
from prabha.product import dispatch
from prabha.systems.cnn import conv2d
from prabha.systems.mac import DigitalMAC, MACConfig, PhysicalMAC, mac
from prabha.systems.cnn_assets import load_assets


@pytest.mark.parametrize('backend', [DigitalMAC, lambda: PhysicalMAC(MACConfig(dac_bits=None), execution='symbol'),
                                     lambda: PhysicalMAC(MACConfig(dac_bits=None), execution='waveform')])
def test_asymmetric_kernel_proves_cross_correlation_without_flipping(backend):
    image = np.arange(9.).reshape(1, 1, 3, 3)
    kernel = np.arange(4.).reshape(1, 1, 2, 2)
    actual = conv2d(image, kernel, backend=backend())
    np.testing.assert_allclose(actual[0, 0], [[19., 25.], [37., 43.]], atol=1e-12)
    flipped = conv2d(image, kernel[:, :, ::-1, ::-1], backend=backend())
    np.testing.assert_allclose(flipped[0, 0], [[5., 11.], [23., 29.]], atol=1e-12)
    assert not np.allclose(actual, flipped)


@pytest.mark.parametrize('value', [None, True, 1, [], {}, 'fast', 'SYMBOL'])
def test_unknown_execution_modes_fail_at_validation(value):
    result = dispatch({'action': 'cnn_validate', 'count': 1, 'execution': value})
    assert not result['ok'] and 'execution' in result['error']


def test_single_call_execution_option_and_trace_fallback():
    cfg = MACConfig(dac_bits=None)
    sampled = mac([.7, -.2], [-.3, .4], cfg)
    fast = mac([.7, -.2], [-.3, .4], cfg, execution='symbol')
    np.testing.assert_allclose(sampled, fast, atol=1e-13)
    backend = PhysicalMAC(cfg, execution='symbol')
    backend.dot([.7, -.2], [-.3, .4], record=True)
    assert backend.last_trace and backend.materialized_waveform_samples > 0


def test_cached_nested_metadata_cannot_be_mutated_through_a_return_value(tmp_path):
    root = Path(__file__).resolve().parents[1]
    for name in ['results/cnn_digits/trained_cnn.npz', 'results/cnn_digits/training_metadata.json',
                 'validation/datasets/digits_8x8_split.npz']:
        p = tmp_path / name; p.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(root / name, p)
    path = tmp_path / 'results/cnn_digits/training_metadata.json'
    metadata = json.loads(path.read_text()); metadata['note'] = {'ids': [1, 2]}; path.write_text(json.dumps(metadata))
    result = load_assets(tmp_path)
    result[-1]['note']['ids'][0] = 99
    assert load_assets(tmp_path)[-1]['note']['ids'] == [1, 2]


def test_explicit_benchmark_preserves_accuracy_and_excludes_warmups():
    response = dispatch({'action': 'cnn_benchmark', 'count': 1, 'blocks': 2, 'warmups': 1})
    assert response['ok'], response
    result = response['result']
    assert len(result['rows']) == 6 and {r['block'] for r in result['rows']} == {1, 2}
    assert set(result['median_seconds']) == {'numpy', 'symbol', 'waveform'}
    assert result['counters']['symbol']['equivalent_samples'] == result['counters']['waveform']['equivalent_samples']
    assert result['counters']['symbol']['materialized_samples'] == 0
    assert result['counters']['waveform']['materialized_samples'] > 0
    assert result['maximum_symbol_waveform_logit_difference'] < 1e-11
    assert result['symbol_waveform_prediction_disagreements'] == 0


@pytest.mark.parametrize('key,value', [('blocks', 0), ('blocks', True), ('blocks', 22), ('warmups', -1)])
def test_benchmark_workloads_are_bounded(key, value):
    assert not dispatch({'action': 'cnn_benchmark', 'count': 1, key: value})['ok']
