import numpy as np

C=299_792_458.0

class CWLaser:
    """
    Continuous-wave laser.
    
    Supports:
    - Average optical power
    - Wavelength
    - RIN intensity noise
    - Lorentzian linewidth / phase noise
    - Deterministic random seed
    """
    
    def __init__(
        self,
        P0_mW=1.0,
        wavelength_nm=1550.0,
        fs=1e9,
        duration=1e-9,
        phase0=0.0,
        rin_db_hz=-150.0,
        linewidth_hz=0.0,
        seed=1,
    ):
        self.P0_mw = P0_mW
        self.wavelength_nm = wavelength_nm
        self.fs = fs
        self.duration = duration
        self.phase0 = phase0
        
        self.rin_db_hz = rin_db_hz
        self.rin_linear = 10**(self.rin_db_hz/10.0)
        self.linewidth_hz = linewidth_hz
        self.seed = seed
        
        self.P0 = P0_mW * 1e-3
        self.wavelength = wavelength_nm * 1e-9
        self.f0 = C/self.wavelength
    
    def generate(self, include_rin=False, include_linewidth=False):
        """
        Generate the CW optical complex envelope.

        Parameters
        ----------
        include_rin : bool
            Include relative intensity noise.

        include_linewidth : bool
            Include phase noise caused by finite laser linewidth.

        Returns
        -------
        t : ndarray
            Time samples.

        E : ndarray
            Complex optical field envelope.
        """
        
        n_samples = int(self.fs * self.duration)
        t = np.arange(n_samples)/self.fs
        
        rng = np.random.default_rng(self.seed)
        
        if include_rin:
            bandwidth = self.fs/2
            sigma_P = np.sqrt(self.rin_linear*bandwidth)*self.P0
            
            rng = np.random.default_rng(self.seed)
            
            delta_P = rng.normal(
                loc=0.0,
                scale=sigma_P,
                size=n_samples
            )
            
            P = self.P0 + delta_P
        
        else:
            P = np.full(n_samples,self.P0)
            
        if include_linewidth and self.linewidth_hz > 0.0:
            sigma_phi = np.sqrt(
                2.0*np.pi*self.linewidth_hz/self.fs
            )
            
            delta_phi = rng.normal(
                loc=0.0,
                scale=sigma_phi,
                size=n_samples,
            )
            
            phi = (
                self.phase0+np.cumsum(delta_phi)
            )
        
        else:
            phi = np.full(n_samples,self.phase0,)
        
            
        if np.any(P < 0) or not np.all(np.isfinite(P)):
            raise ValueError('Linearized laser RIN produced invalid power; reduce RIN density or sample bandwidth.')
        E = np.sqrt(P)*np.exp(1j*phi)
        
        return t, E
    
    def power(self,E):
        """
        Calculate optical power from complex field.
        """
        return np.abs(E)**2
        
    
