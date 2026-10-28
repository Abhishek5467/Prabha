"""NCHW CNN primitives with explicit patch-to-Prabha-MAC execution.

conv2d follows neural-network cross-correlation: kernels are not reversed.
Bias, activation and pooling are explicit digital/behavioural operations.
"""
import numbers
import numpy as np
from .mac import PhysicalMAC


def _pair(value, name, allow_zero=False):
    if isinstance(value, numbers.Integral) and not isinstance(value, (bool, np.bool_)):
        values = (int(value), int(value))
    elif isinstance(value, (tuple, list)) and len(value) == 2:
        values = tuple(value)
    else:
        raise ValueError(f'{name} must be an integer or a pair of integers.')
    lower = 0 if allow_zero else 1
    if any(isinstance(v, (bool, np.bool_)) or not isinstance(v, numbers.Integral) or v < lower for v in values):
        raise ValueError(f'{name} entries must be integers >= {lower}.')
    return tuple(int(v) for v in values)


def conv2d(x, weight, bias=None, *, stride=1, padding=0, dilation=1,
           groups=1, backend=None):
    """Return real NCHW cross-correlation, named conv2d by CNN convention.

    x: [batch,in_channels,height,width]; weight:
    [out_channels,in_channels/groups,kernel_height,kernel_width]. Padding is
    symmetric zero padding. Arbitrary finite signed values are normalized by
    PhysicalMAC; no clipping or sigmoid is inserted into a convolution.
    Spatial kernel indices are never reversed. Mathematical convolution uses
    a 180-degree spatial kernel rotation instead, changing a fixed checkpoint.
    """
    x, w = np.asarray(x, dtype=float), np.asarray(weight, dtype=float)
    if x.ndim != 4 or w.ndim != 4 or not all(x.shape) or not all(w.shape):
        raise ValueError('x and weight must be nonempty four-dimensional arrays.')
    if not np.all(np.isfinite(x)) or not np.all(np.isfinite(w)):
        raise ValueError('x and weight must be finite.')
    if isinstance(groups, (bool, np.bool_)) or not isinstance(groups, numbers.Integral) or groups < 1:
        raise ValueError('groups must be a positive integer.')
    n, ci, h, width = x.shape
    co, c_group, kh, kw = w.shape
    if ci % groups or co % groups or c_group != ci // groups:
        raise ValueError('Input/output channels and weight channels are incompatible with groups.')
    sh, sw = _pair(stride, 'stride')
    ph, pw = _pair(padding, 'padding', allow_zero=True)
    dh, dw = _pair(dilation, 'dilation')
    eh, ew = dh * (kh - 1) + 1, dw * (kw - 1) + 1
    oh, ow = (h + 2 * ph - eh) // sh + 1, (width + 2 * pw - ew) // sw + 1
    if oh < 1 or ow < 1:
        raise ValueError('Effective kernel is larger than the padded input.')
    if bias is None:
        b = np.zeros(co)
    else:
        b = np.asarray(bias, dtype=float)
        if b.shape != (co,) or not np.all(np.isfinite(b)):
            raise ValueError('bias must be finite with shape [out_channels].')
    backend = backend if backend is not None else PhysicalMAC()
    if not callable(getattr(backend, 'dot', None)):
        raise ValueError('backend must expose dot(input_vector, weight_vector).')
    padded = np.pad(x, ((0, 0), (0, 0), (ph, ph), (pw, pw)))
    out = np.empty((n, co, oh, ow), dtype=float)
    filters = w.reshape(co, -1)
    out_per_group = co // groups
    if getattr(backend, 'supports_matrix', False):
        windows = np.lib.stride_tricks.sliding_window_view(padded, (eh, ew), axis=(-2, -1))
        windows = windows[:, :, :oh * sh:sh, :ow * sw:sw, ::dh, ::dw]
        for group in range(groups):
            channels = slice(group * c_group, (group + 1) * c_group)
            outputs = slice(group * out_per_group, (group + 1) * out_per_group)
            patches = windows[:, channels].transpose(0, 2, 3, 1, 4, 5).reshape(n * oh * ow, -1)
            values = backend.matrix(patches, filters[outputs])
            out[:, outputs] = values.reshape(n, oh, ow, out_per_group).transpose(0, 3, 1, 2) + b[outputs][None, :, None, None]
        return out
    for batch in range(n):
        for channel in range(co):
            group = channel // out_per_group
            channels = slice(group * c_group, (group + 1) * c_group)
            for row in range(oh):
                r = row * sh
                for col in range(ow):
                    c = col * sw
                    patch = padded[batch, channels, r:r + eh:dh, c:c + ew:dw]
                    out[batch, channel, row, col] = backend.dot(patch.reshape(-1), filters[channel]) + b[channel]
    return out


# An explicit name for callers who want the mathematical convention visible.
cross_correlate2d = conv2d


def relu(x):
    return np.maximum(np.asarray(x, dtype=float), 0.0)


def max_pool2d(x, kernel_size=2, stride=None):
    x = np.asarray(x, dtype=float)
    if x.ndim != 4 or not all(x.shape) or not np.all(np.isfinite(x)):
        raise ValueError('Pooling requires finite nonempty NCHW input.')
    kh, kw = _pair(kernel_size, 'kernel_size')
    sh, sw = _pair(kernel_size if stride is None else stride, 'stride')
    n, channels, h, w = x.shape
    oh, ow = (h - kh) // sh + 1, (w - kw) // sw + 1
    if min(oh, ow) < 1:
        raise ValueError('Pooling window exceeds input dimensions.')
    windows = np.lib.stride_tricks.sliding_window_view(x, (kh, kw), axis=(-2, -1))
    return windows[:, :, :oh * sh:sh, :ow * sw:sw].max(axis=(-2, -1))


def linear(x, weight, bias=None, *, backend=None):
    x, w = np.asarray(x, dtype=float), np.asarray(weight, dtype=float)
    if x.ndim != 2 or w.ndim != 2 or not all(x.shape) or not all(w.shape) or x.shape[1] != w.shape[1]:
        raise ValueError('linear expects x=[batch,features] and weight=[outputs,features].')
    if not np.all(np.isfinite(x)) or not np.all(np.isfinite(w)):
        raise ValueError('linear requires finite arrays.')
    b = np.zeros(len(w)) if bias is None else np.asarray(bias, dtype=float)
    if b.shape != (len(w),) or not np.all(np.isfinite(b)):
        raise ValueError('linear bias must match output features and be finite.')
    backend = backend if backend is not None else PhysicalMAC()
    if getattr(backend, 'supports_matrix', False):
        return backend.matrix(x, w) + b
    return np.array([[backend.dot(row, filt) + offset for filt, offset in zip(w, b)] for row in x])
