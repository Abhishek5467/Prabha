"""Reusable systems composed from the independently validated device models."""
from .perceptron import NeuronConfig, physical_neuron
from .ann import infer, batch, DEFAULT_NETWORK



__all__ = ['NeuronConfig', 'physical_neuron', 'infer', 'batch', 'DEFAULT_NETWORK']
