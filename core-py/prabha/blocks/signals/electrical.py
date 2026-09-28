from dataclasses import dataclass

import numpy as np

@dataclass
class ElectricalSignal:
    """
    Electrical signal representation.

    Parameters
    ----------
    voltage_V : float or np.ndarray
        Electrical voltage in volts.
    """
    
    voltage_V: np.ndarray
    
    def __pos_init__(self):
        self.voltage_V=np.asarray(self.voltage_V, dtype=float)
        
    @property
    def voltage_mV(self):
        return self.voltage_V*1e3
    
    def copy(self):
        return ElectricalSignal(voltage_V=self.voltage_V.copy())