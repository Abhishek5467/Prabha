import json
from pathlib import Path
import numpy as np
import pytest
from prabha.product import dispatch

ROOT=Path(__file__).resolve().parents[1]

def test_trained_cnn_metadata_is_exposed_by_shared_dispatcher():
    response=dispatch({'action':'cnn_info'})
    assert response['ok']
    assert response['result']['parameters']==410
    assert response['result']['test_images']==360
    assert 'cnn' in dispatch({'action':'meta'})['result']['actions']

@pytest.mark.parametrize('payload',[{'count':0},{'count':361},{'count':True},{'count':1.5},{'count':1,'start':360},{'count':30,'start':350}])
def test_invalid_cnn_workloads_are_rejected(payload):
    assert dispatch({'action':'cnn',**payload})['ok'] is False

def test_complete_trained_cnn_matches_frozen_reference_on_all_held_out_images():
    response=dispatch({'action':'cnn','count':360})
    assert response['ok'],response
    r=response['result']
    with np.load(ROOT/'results/cnn_digits/test_logits.npz',allow_pickle=False) as saved:
        np.testing.assert_allclose([row['numpy_logits'] for row in r['rows']],saved['reference_logits'],rtol=1e-12,atol=1e-12)
        np.testing.assert_allclose([row['prabha_logits'] for row in r['rows']],saved['prabha_logits'],rtol=1e-12,atol=1e-12)
    assert r['prabha_correct']==r['numpy_correct']==354
    assert r['prediction_disagreements']==0
    assert r['mac_calls']==55440 and r['waveform_samples']==9538560
    assert r['prabha_seconds']>0 and r['numpy_seconds']>0
    assert len(r['rows'])==360
    # Keep the new live measurement distinct from the archived training run.
    (ROOT/'results/cnn_integration').mkdir(exist_ok=True)
    (ROOT/'results/cnn_integration/live_comparison.json').write_text(json.dumps(r,indent=2)+'\n')
