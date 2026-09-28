from dataclasses import dataclass

import numpy as np

@dataclass
class OpticalSignal:
    """
    Optical signal representation.

    Parameters
    ----------
    power_W : float or np.ndarray
        Optical power in watts.

    wavelength_nm : float
        Optical wavelength in nanometers.
    """
    
    power_W: np.ndarray
    wavelength_nm: float
    
    def __post_init__(self):
        self.power_W = np.asarray(self.power_W, dtype=float)
        
        if np.any(self.power_W<0):
            raise ValueError("Optical power cannot be negative.")
        
        if self.wavelength_nm<=0:
            raise ValueError("Wavelength must be positive.")
        
    @property
    def power_mW(self):
        return self.power_W*1e3
    
    @property
    def power_dBm(self):
        with np.errstate(divide="ignore"):
            return 10*np.log10(self.power_mW)
        
    def copy(self):
        return OpticalSignal(power_W=self.power_W.copy(), wavelength_nm=self.wavelength_nm,)
    
    
    