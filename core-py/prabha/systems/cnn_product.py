"""Trained digit-CNN operations shared by Studio, HTTP and desktop Python."""
from pathlib import Path
import hashlib,json
import numpy as np
from .cnn_training import forward
from .cnn import conv2d,relu,max_pool2d,linear
from .mac import MACConfig,PhysicalMAC


class DigitalMAC:
    def dot(self,x,w):return float(np.dot(x,w))


def _assets(root):
    root=Path(root)
    model=root/'results/cnn_digits/trained_cnn.npz'
    data=root/'validation/datasets/digits_8x8_split.npz'
    try:
        metadata=json.loads((root/'results/cnn_digits/training_metadata.json').read_text())
        for path,key in [(model,'model_sha256'),(data,'dataset_sha256')]:
            if hashlib.sha256(path.read_bytes()).hexdigest()!=metadata[key]:
                raise ValueError('The CNN model/data differs from its trained checkpoint. Restore the supplied CNN assets.')
        with np.load(model,allow_pickle=False) as a:parameters={k:a[k].copy() for k in a.files}
        with np.load(data,allow_pickle=False) as a:
            ids=a['test_indices'].copy();images=a['images'][ids].copy();labels=a['labels'][ids].copy()
    except OSError as error:
        raise ValueError('CNN model/data files are missing. Apply the complete CNN update and rebuild the browser/desktop assets.') from error
    return parameters,images,labels,ids,metadata


def _forward(x,p,backend):
    features=max_pool2d(relu(conv2d(x,p['conv_weight'],p['conv_bias'],backend=backend)))
    return linear(features.reshape(len(x),-1),p['dense_weight'],p['dense_bias'],backend=backend)


def info(root, payload=None):
    """Compatibility entry point for the editable application workspace."""
    from .cnn_workspace import info as workspace_info
    return workspace_info(root, payload)


def compare(root, payload):
    """Compatibility entry point; all controls use the shared validated path."""
    from .cnn_workspace import compare as workspace_compare
    return workspace_compare(root, payload)
