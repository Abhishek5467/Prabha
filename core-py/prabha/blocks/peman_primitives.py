"""
prabha.blocks.peman_primitives — the validated PoC physics, as spec kernels.

Each kernel's 'implementation' tag matches the block definition JSON in
spec/blocks/. Physics identical to the PoC that validated against the analytic
neuron math and thesis noise regimes (thermal P^0 / shot P^1 / RIN P^2).
"""
from __future__ import annotations
import numpy as np

from ..signal import Signal, Channel, DEFAULT_CHANNEL
from ..engine import Kernel, kernel

Q = 1.602176634e-19
KB = 1.380649e-23


def _vec(s):  # "0.9,0.3" -> [0.9, 0.3]
    if isinstance(s, (list, tuple)):
        return [float(x) for x in s]
    return [float(x) for x in str(s).split(",") if x.strip()]


@kernel("CWLaser")
class CWLaser(Kernel):
    def process(self, inputs):
        p, ctx = self.p, self.ctx
        fs = float(p["fs"])
        n = int(round(fs * ctx.duration))
        rng = np.random.default_rng(self.seed)
        P0 = p["P0"] * 1e-3
        phi = np.cumsum(rng.normal(0, np.sqrt(2 * np.pi * p["linewidth"] / fs), n)) \
            if ctx.noise else np.zeros(n)
        rin = 10 ** (p["RIN"] / 10)
        dP = rng.normal(0, np.sqrt(rin * fs / 2) * P0, n) if ctx.noise else 0.0
        P = np.clip(P0 + dP, 0, None)
        E = np.sqrt(P) * np.exp(1j * phi)
        return {"out": Signal("optical", fs, E,
                              channels=[Channel(frequency=299792458.0 / (p["wavelength"] * 1e-9))])}


@kernel("DriveSource")
class DriveSource(Kernel):
    def process(self, inputs):
        p, ctx = self.p, self.ctx
        vals = _vec(p["values"])
        rate = p["rate"] * 1e9
        fs = rate * int(p["sps"])
        n = int(round(fs * ctx.duration))
        sps = int(p["sps"])
        idx = np.minimum(np.arange(n) // sps, len(vals) - 1)
        return {"out": Signal("voltage", fs, np.asarray(vals, float)[idx])}


@kernel("WeightSource")
class WeightSource(Kernel):
    """w in [-1,1] -> differential transmissions t_u=(1+w)/2, t_l=(1-w)/2."""
    def process(self, inputs):
        p, ctx = self.p, self.ctx
        w = np.asarray(_vec(p["values"]), float)
        rate = p["rate"] * 1e9
        fs = rate * int(p["sps"])
        n = int(round(fs * ctx.duration))
        sps = int(p["sps"])
        idx = np.minimum(np.arange(n) // sps, len(w) - 1)
        tu = ((1 + w) / 2)[idx]
        tl = ((1 - w) / 2)[idx]
        return {"upper": Signal("voltage", fs, tu), "lower": Signal("voltage", fs, tl)}


@kernel("IntensityModulator")
class IntensityModulator(Kernel):
    """Linearized: drive in [0,1] is the POWER transmission -> field x sqrt(t)."""
    def process(self, inputs):
        E = inputs["in"].single_channel()
        d = np.clip(inputs["drive"].data, 0.0, 1.0)
        n = min(E.size, d.size)
        return {"out": inputs["in"].like((E[:n] * np.sqrt(d[:n]))[None, :])}


@kernel("Splitter")
class Splitter(Kernel):
    def process(self, inputs):
        E = inputs["in"].single_channel()
        r = float(self.p["ratio"])
        return {"out1": inputs["in"].like((E * np.sqrt(r))[None, :]),
                "out2": inputs["in"].like((E * np.sqrt(1 - r))[None, :])}


@kernel("Photodetector")
class Photodetector(Kernel):
    def process(self, inputs):
        p, ctx = self.p, self.ctx
        sin = inputs["in"]
        E = sin.single_channel()
        I = p["resp"] * np.abs(E) ** 2 + p["dark"]
        if ctx.noise:
            rng = np.random.default_rng(self.seed)
            bw = sin.fs / 2
            var = 2 * Q * np.maximum(I, 0) * bw + 4 * KB * p["Trx"] * bw / p["load"]
            I = I + rng.normal(0, np.sqrt(var), I.shape)
        return {"I": Signal("current", sin.fs, I)}


@kernel("BalancedPair")
class BalancedPair(Kernel):
    def process(self, inputs):
        a, b = inputs["i1"], inputs["i2"]
        n = min(a.n, b.n)
        return {"I": a.like(a.data[:n] - b.data[:n])}


@kernel("CapacitorIntegrator")
class CapacitorIntegrator(Kernel):
    def process(self, inputs):
        sin = inputs["I"]
        C = self.p["C"] * 1e-12
        v = np.cumsum(sin.data) / sin.fs / C
        return {"Vc": Signal("voltage", sin.fs, v)}


@kernel("BiasGain")
class BiasGain(Kernel):
    def process(self, inputs):
        sin = inputs["in"]
        return {"out": sin.like(self.p["gain"] * sin.data + self.p["theta"])}


@kernel("ADC")
class ADC(Kernel):
    def process(self, inputs):
        sin = inputs["in"]
        p = self.p
        L = 2 ** int(p["bits"])
        x = np.clip((sin.data - p["vmin"]) / (p["vmax"] - p["vmin"]), 0, 1)
        code = np.round(x * (L - 1))
        val = p["vmin"] + code / (L - 1) * (p["vmax"] - p["vmin"])
        return {"code": Signal("digital", sin.fs, val)}


@kernel("Activation")
class Activation(Kernel):
    def process(self, inputs):
        sin = inputs["in"]
        v = self.p["scale"] * sin.data
        k = self.p["kind"]
        z = 1 / (1 + np.exp(-v)) if k == "sigmoid" else np.tanh(v) if k == "tanh" \
            else np.maximum(0, v)
        return {"z": sin.like(z)}