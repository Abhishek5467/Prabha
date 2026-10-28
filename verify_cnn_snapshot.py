"""Quick offline consistency audit of the frozen CNN data, weights and results."""
from pathlib import Path
import hashlib,json
import numpy as np

root=Path(__file__).resolve().parent
result=json.loads((root/'results/cnn_digits/cnn_digits_results.json').read_text())
for path,key in [(root/'validation/datasets/digits_8x8_split.npz','dataset_sha256'),
                 (root/'results/cnn_digits/trained_cnn.npz','model_sha256')]:
    assert hashlib.sha256(path.read_bytes()).hexdigest()==result['training'][key],path
with np.load(root/'validation/datasets/digits_8x8_split.npz',allow_pickle=False) as data:
    groups=[set(data[k].tolist()) for k in ['train_indices','validation_indices','test_indices']]
    assert [len(g) for g in groups]==[1149,288,360]
    assert not any(groups[i]&groups[j] for i in range(3) for j in range(i))
    assert set.union(*groups)==set(range(1797))
    test_ids=data['test_indices'].copy();labels=data['labels'][test_ids].copy()
with np.load(root/'results/cnn_digits/test_logits.npz',allow_pickle=False) as records:
    np.testing.assert_array_equal(test_ids,records['dataset_indices'])
    np.testing.assert_array_equal(labels,records['labels'])
    ref=records['reference_logits'];actual=records['prabha_logits']
    assert ref.shape==actual.shape==(360,10)
    assert np.isfinite(ref).all() and np.isfinite(actual).all()
    assert int(np.sum(ref.argmax(1)==labels))==result['reference_correct']==354
    assert int(np.sum(actual.argmax(1)==labels))==result['prabha_correct']==354
    assert int(np.sum(ref.argmax(1)!=actual.argmax(1)))==result['prediction_disagreements']==0
    np.testing.assert_allclose(np.sqrt(np.mean((actual-ref)**2)),result['logit_rms_error'],rtol=1e-14)
    np.testing.assert_allclose(np.max(abs(actual-ref)),result['logit_max_abs_error'],rtol=1e-14)
for relative,digest in result['source_sha256'].items():
    path=root/'validation/snapshots/cnn_recorded'/relative
    if not path.exists(): path=root/relative
    assert hashlib.sha256(path.read_bytes()).hexdigest()==digest,relative
print('Verified: disjoint 1149/288/360 split, frozen model/data hashes, all 360 test outputs, metrics and recorded source hashes (original source retained separately from the updated release).')
