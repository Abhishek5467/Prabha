"""Content-verified CNN assets, independent of the application dispatcher."""
from functools import lru_cache
from io import BytesIO
from pathlib import Path
from copy import deepcopy
import hashlib
import json
import numpy as np


@lru_cache(maxsize=4)
def _decode(model_bytes, dataset_bytes, metadata_bytes):
    metadata = json.loads(metadata_bytes)
    for value, key in ((model_bytes, 'model_sha256'), (dataset_bytes, 'dataset_sha256')):
        if hashlib.sha256(value).hexdigest() != metadata[key]:
            raise ValueError('The CNN model/data differs from its trained checkpoint. Restore the supplied CNN assets.')
    with np.load(BytesIO(model_bytes), allow_pickle=False) as archive:
        parameters = {key: archive[key].copy() for key in archive.files}
    with np.load(BytesIO(dataset_bytes), allow_pickle=False) as archive:
        ids = archive['test_indices'].copy()
        images, labels = archive['images'][ids].copy(), archive['labels'][ids].copy()
    return parameters, images, labels, ids, metadata


def load_assets(root):
    """Cache decoding by file content, so even same-size edits invalidate it.

    Each caller receives private arrays and metadata. Cached validated assets
    cannot be changed through an editable model or a returned NumPy view.
    """
    root = Path(root)
    try:
        decoded = _decode((root / 'results/cnn_digits/trained_cnn.npz').read_bytes(),
                          (root / 'validation/datasets/digits_8x8_split.npz').read_bytes(),
                          (root / 'results/cnn_digits/training_metadata.json').read_bytes())
    except OSError as error:
        raise ValueError('CNN model/data files are missing. Apply the complete CNN update and rebuild the browser/desktop assets.') from error
    parameters, images, labels, ids, metadata = decoded
    return ({key: value.copy() for key, value in parameters.items()}, images.copy(), labels.copy(),
            ids.copy(), deepcopy(metadata))
