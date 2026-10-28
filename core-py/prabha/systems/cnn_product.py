"""Trained digit-CNN operations shared by Studio, HTTP and desktop Python."""
from .cnn import conv2d,relu,max_pool2d,linear
from .mac import DigitalMAC
from .cnn_assets import load_assets as _assets


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


__all__ = ['DigitalMAC', '_assets', '_forward', 'info', 'compare']
