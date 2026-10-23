from copy import deepcopy
import json
import numpy as np
import pytest
from prabha.product import dispatch


def settings():
    return deepcopy(dispatch({'action': 'cnn_info'})['result']['default_settings'])


def run(action, s, **kwargs):
    response = dispatch({'action': action, 'settings': s, **kwargs})
    assert response['ok'], response
    return response['result']


def test_settings_roundtrip_and_imported_weights_are_used_in_fresh_inference():
    s = settings(); s['input'].update(mode='custom', label=None)
    s['converters'].update(dac_bits=None, adc_bits=None)
    original = run('cnn', s)
    s['model']['dense_bias'][2] += .75
    restored = json.loads(json.dumps(s))
    accepted = run('cnn_validate', restored)
    assert accepted['settings'] == s
    assert not accepted['weights_match_checkpoint']
    edited = run('cnn', restored)
    assert edited['numpy_accuracy'] is None and edited['labelled_images'] == 0
    for key in ['numpy_logits', 'prabha_logits']:
        delta = np.array(edited['rows'][0][key]) - original['rows'][0][key]
        np.testing.assert_allclose(delta, np.eye(10)[2] * .75, atol=1e-12)
    assert edited['effective_weights_sha256'] != original['effective_weights_sha256']


def test_input_pixel_edits_and_converter_controls_change_actual_computation():
    s = settings(); s['input'].update(mode='custom')
    original = run('cnn', s)
    s['input']['pixels'] = [[0.] * 8 for _ in range(8)]
    blank = run('cnn', s)
    assert not np.allclose(blank['rows'][0]['numpy_logits'], original['rows'][0]['numpy_logits'])
    s = settings(); s['input'].update(mode='custom')
    s['converters'].update(dac_bits=4, adc_bits=8, adc_full_scale=64., dac_rounding='nearest_even')
    quantized = run('cnn', s)
    assert quantized['configuration']['dac_bits'] == 4
    assert quantized['configuration']['adc_bits'] == 8
    assert not np.allclose(quantized['rows'][0]['prabha_logits'], original['rows'][0]['prabha_logits'])
    np.testing.assert_allclose(quantized['rows'][0]['numpy_logits'], original['rows'][0]['numpy_logits'])


def test_selected_image_inspection_matches_run_outputs_and_each_stage_definition():
    s = settings(); s['input'].update(start=13, count=2)
    result = run('cnn', s)
    inspected = run('cnn_inspect', s, index=1)
    layers = {v['name']: v for v in inspected['layers']}
    assert [v['shape'] for v in inspected['layers']] == [[1,8,8], [4,6,6], [4,6,6], [4,3,3], [36], [10]]
    assert inspected['test_position'] == 14
    for path, key in [('numpy', 'numpy_logits'), ('prabha', 'prabha_logits')]:
        np.testing.assert_allclose(layers['logits'][path], result['rows'][1][key], atol=1e-12)
        np.testing.assert_array_equal(layers['relu'][path], np.maximum(layers['convolution'][path], 0.))
        pooled=np.asarray(layers['relu'][path]).reshape(4,3,2,3,2).max(axis=(2,4))
        np.testing.assert_array_equal(layers['pool'][path], pooled)
        np.testing.assert_array_equal(layers['flatten'][path], pooled.reshape(-1))
    for layer in layers.values():
        error=np.asarray(layer['prabha'])-np.asarray(layer['numpy'])
        assert layer['maximum_error']==float(np.max(abs(error)))
        assert layer['rms_error']==float(np.sqrt(np.mean(error**2)))


@pytest.mark.parametrize('key,value', [('pixels', [[0.]*8]*7), ('pixels', [[True]*8]*8), ('label', 10), ('count', 1.5), ('start', -1)])
def test_invalid_custom_inputs_are_rejected(key, value):
    s=settings();s['input'][key]=value
    assert not dispatch({'action':'cnn_validate','settings':s})['ok']


@pytest.mark.parametrize('key,value', [('dac_bits', True), ('dac_bits', 25), ('adc_bits', 0), ('adc_full_scale', float('nan')), ('dac_rounding', 'stochastic')])
def test_invalid_converter_settings_are_rejected(key, value):
    s=settings();s['converters'][key]=value
    assert not dispatch({'action':'cnn_validate','settings':s})['ok']


@pytest.mark.parametrize('value', [[0.]*10, [[0.]*35]*10, [[False]*36]*10, [[float('inf')]*36]*10])
def test_invalid_weight_tensors_are_rejected(value):
    s=settings();s['model']['dense_weight']=value
    assert not dispatch({'action':'cnn_validate','settings':s})['ok']


def test_adc_range_violations_are_reported_without_silent_clipping():
    s=settings();s['input'].update(mode='custom');s['converters'].update(adc_bits=8,adc_full_scale=.001)
    response=dispatch({'action':'cnn','settings':s})
    assert not response['ok'] and 'ADC range' in response['error']


def test_inspection_and_sample_indices_are_bounded():
    s=settings();s['input'].update(count=1)
    assert not dispatch({'action':'cnn_inspect','settings':s,'index':1})['ok']
    assert not dispatch({'action':'cnn_info','sample_index':360})['ok']
