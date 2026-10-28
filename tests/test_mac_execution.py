from pathlib import Path
import shutil
import numpy as np
import pytest
from prabha.product import dispatch
from prabha.systems.mac import PhysicalMAC, MACConfig
from prabha.systems.cnn_assets import load_assets


@pytest.mark.parametrize('converters', [
    {'dac_bits': None}, {'dac_bits': 1}, {'dac_bits': 4},
    {'dac_bits': 12, 'dac_rounding': 'nearest_lower'},
    {'dac_bits': 12, 'adc_bits': 8, 'adc_full_scale': 64.},
    {'dac_bits': None, 'adc_bits': 12, 'adc_full_scale': 64.},
])
@pytest.mark.parametrize('length,tile', [(9, 64), (137, 16)])
def test_symbol_matrix_matches_waveforms_with_signed_inputs_and_tiles(converters, length, tile):
    rng = np.random.default_rng(437)
    x, w = rng.normal(size=(3, length)), rng.normal(size=(4, length))
    cfg = MACConfig(**converters, tile_size=tile, power_mw=.3,
                    responsivity=.8, capacitance_f=2e-12,
                    mzm_extinction_ratio_db=23., weight_extinction_ratio_db=27.)
    fast, sampled = PhysicalMAC(cfg, execution='symbol'), PhysicalMAC(cfg)
    actual, expected = fast.matrix(x, w), sampled.matrix(x, w)
    np.testing.assert_allclose(actual, expected, rtol=1e-12, atol=2e-12)
    assert fast.calls == sampled.calls == 12
    assert fast.device_passes == sampled.device_passes
    assert fast.waveform_samples == sampled.waveform_samples
    assert fast.materialized_waveform_samples < sampled.materialized_waveform_samples


def test_scalar_symbol_fixed_scales_and_waveform_trace_are_preserved():
    cfg = MACConfig(dac_bits=12, dac_rounding='nearest_lower')
    fast, sampled = PhysicalMAC(cfg, execution='auto'), PhysicalMAC(cfg)
    x, w = [.9, .3, .7, .5], [.8, -.6, .4, -.9]
    np.testing.assert_allclose(fast.dot(x, w, input_scale=1, weight_scale=1),
                               sampled.dot(x, w, input_scale=1, weight_scale=1), atol=1e-14)
    assert fast.materialized_waveform_samples == 0
    fast.dot(x, w, record=True)
    assert fast.last_trace and len(fast.last_trace[0]['drive_voltage_v']) == 64
    assert fast.materialized_waveform_samples == 64
    with pytest.raises(ValueError): fast.matrix([[2.]], [[1.]], input_scale=1)


def test_adc_zero_and_half_code_reduction_uses_waveform_rounding():
    cfg = MACConfig(dac_bits=None, adc_bits=8, adc_full_scale=1., samples_per_symbol=7)
    x = np.array([[0., 0., 0.], [.5, .5, .5], [1., 0., 1.]])
    w = np.array([[0., 0., 0.], [.5, 0., -.5]])
    a, b = PhysicalMAC(cfg, execution='symbol'), PhysicalMAC(cfg)
    np.testing.assert_array_equal(a.matrix(x, w), b.matrix(x, w))
    assert a.materialized_waveform_samples > 0


@pytest.mark.parametrize('noise', [{'shot_enabled': True}, {'rin_enabled': True},
                                  {'linewidth_enabled': True, 'linewidth_hz': 1e6}])
def test_auto_noise_execution_preserves_seeded_waveform_stream(noise):
    cfg = MACConfig(**noise)
    a, b = PhysicalMAC(cfg, execution='auto'), PhysicalMAC(cfg)
    assert not a.supports_matrix and a.execution_mode == 'waveform'
    x, w = [.1, .2, -.8], [.4, -.3, .2]
    np.testing.assert_array_equal([a.dot(x, w) for _ in range(4)], [b.dot(x, w) for _ in range(4)])
    with pytest.raises(ValueError): PhysicalMAC(cfg, execution='symbol')


def test_asset_cache_returns_private_values_and_rechecks_modified_bytes(tmp_path):
    root = Path(__file__).resolve().parents[1]
    names = ['results/cnn_digits/trained_cnn.npz', 'results/cnn_digits/training_metadata.json',
             'validation/datasets/digits_8x8_split.npz']
    for name in names:
        target = tmp_path / name; target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(root / name, target)
    parameters, images, labels, ids, metadata = load_assets(tmp_path)
    expected = parameters['conv_weight'].copy()
    parameters['conv_weight'][:] = 0
    np.testing.assert_array_equal(load_assets(tmp_path)[0]['conv_weight'], expected)
    path = tmp_path / names[0]
    data = bytearray(path.read_bytes()); data[-1] ^= 1; path.write_bytes(data)
    with pytest.raises(ValueError, match='differs'): load_assets(tmp_path)


def test_cnn_request_reuses_first_image_tensors_and_runs_each_path_once(monkeypatch):
    from prabha.systems import cnn_workspace as workspace
    seen, reference_calls = [], []
    stages, forward = workspace._stages, workspace.forward
    def tracked(x, p, backend):
        seen.append(type(backend).__name__)
        return stages(x, p, backend)
    def reference(x, p):
        reference_calls.append(len(x))
        return forward(x, p)
    monkeypatch.setattr(workspace, '_stages', tracked)
    monkeypatch.setattr(workspace, 'forward', reference)
    response = dispatch({'action': 'cnn', 'count': 2})
    assert response['ok'], response
    result = response['result']
    assert seen == ['DigitalMAC', 'PhysicalMAC'] and reference_calls == [2]
    assert result['execution_mode'] == 'symbol'
    assert result['materialized_waveform_samples'] == 0
    np.testing.assert_array_equal(result['inspection']['layers'][-1]['prabha'], result['rows'][0]['prabha_logits'])
