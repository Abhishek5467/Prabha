"""
prabha.signal — runtime counterpart of spec/schema/signal.schema.json.

The schema defines the TYPE CONTRACT (kind/domain/fs/units/channels metadata).
This class carries that metadata PLUS the sample data, which never appears in
schema or .prabha files (RAM at runtime, HDF5 when persisted).

Conventions locked in the spec:
  optical  -> data is complex128, envelope in sqrt(W); shape (n_channels, n)
  voltage  -> float64, Volts;  shape (n,)
  current  -> float64, Amps;   shape (n,)
  digital  -> float64, code;   shape (n,)
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
import numpy as np

KINDS = ("optical", "voltage", "current", "digital")
DOMAINS = ("time", "frequency")

DEFAULT_UNITS = {"optical": "sqrt(W)", "voltage": "V", "current": "A", "digital": "code"}


@dataclass
class Channel:
    """Lumerical-faithful channel identity: frequency canonical, polarization
    lives inside mode_label (TE0/TM0), orthogonal_id disambiguates."""
    frequency: float                  # Hz, canonical
    mode_label: str = "TE0"
    orthogonal_id: int = 0

    @property
    def wavelength(self) -> float:    # derived, display-only — never stored
        return 299792458.0 / self.frequency


DEFAULT_CHANNEL = Channel(frequency=299792458.0 / 1550e-9)


@dataclass
class Signal:
    kind: str
    fs: float                          # Hz; sample rate (time) / grid spacing (frequency)
    data: np.ndarray
    domain: str = "time"
    units: Optional[str] = None
    channels: Optional[List[Channel]] = None   # optical only

    def __post_init__(self):
        if self.kind not in KINDS:
            raise ValueError(f"unknown kind {self.kind!r}")
        if self.domain not in DOMAINS:
            raise ValueError(f"unknown domain {self.domain!r}")
        if self.fs <= 0:
            raise ValueError("fs must be > 0")
        if self.units is None:
            self.units = DEFAULT_UNITS[self.kind]
        if self.kind == "optical":
            if not self.channels:
                self.channels = [DEFAULT_CHANNEL]
            self.data = np.atleast_2d(np.asarray(self.data, dtype=np.complex128))
            if self.data.shape[0] != len(self.channels):
                raise ValueError(
                    f"optical data has {self.data.shape[0]} rows but {len(self.channels)} channels")
        else:
            if self.channels is not None:
                raise ValueError(f"{self.kind} signal must not carry channels")
            self.data = np.asarray(self.data, dtype=np.float64)

    # ---- helpers used by blocks ----
    @property
    def n(self) -> int:
        return self.data.shape[-1]

    def single_channel(self) -> np.ndarray:
        """Guard for single-channel blocks (the forward-compat assertion from the spec)."""
        if self.kind != "optical":
            raise TypeError("single_channel() on non-optical signal")
        if len(self.channels) != 1:
            raise ValueError(
                f"block supports 1 optical channel, got {len(self.channels)} (WDM not supported here)")
        return self.data[0]

    def like(self, data: np.ndarray) -> "Signal":
        """New signal with same metadata, new samples (same kind/fs/domain/channels)."""
        return Signal(kind=self.kind, fs=self.fs, data=data, domain=self.domain,
                      units=self.units, channels=self.channels)