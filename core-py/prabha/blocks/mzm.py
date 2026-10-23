import numpy as np

class MachZehnderModulator:
    """
    Mach-Zehnder intensity modulator with optional finite extinction.
    
    Power transfer function:
    
        P_out = P_in * cos^2(PI * V/(2*V_pi) + phi_bias/2)
        
    Parameters
    ----------
    V_pi : float
        Half-wave voltage [V].
        
    phi_bias : float
        Bias phase [rad].
        
    insertion_loss_dB : float
        Optical Insertion loss [dB].
        Default: 0 dB for the ideal model.
    """
    
    def __init__(self, V_pi=1.0, phi_bias=0.0, insertion_loss_dB=0.0,
                 *, extinction_ratio_dB=None):
        
        if V_pi <= 0:
            raise ValueError("V_pi must be positive.")
        if insertion_loss_dB < 0:
            raise ValueError("Insertion loss must be non-negative.")
        if extinction_ratio_dB is not None and (
                not np.isfinite(extinction_ratio_dB) or extinction_ratio_dB < 0):
            raise ValueError("Extinction ratio must be None or finite and nonnegative.")
        
        self.V_pi = V_pi
        self.phi_bias = phi_bias
        self.insertion_loss_dB = insertion_loss_dB
        self.extinction_ratio_dB = extinction_ratio_dB
        
        self.transmission = 10**(-insertion_loss_dB/10.0)
        
    def transfer(self, V):
        
        """
        Calculate normalized MZM power transmission.
        
        Returns
        -------
        T : ndarray or float
            Power transmission ratio (P_out / P_in)
            between 0 and 1 for the ideal model.
        """
        
        V = np.asarray(V,dtype=float)
        
        phase = (np.pi*V/(2*self.V_pi)+self.phi_bias/2.0)
        
        T = np.cos(phase)**2
        if self.extinction_ratio_dB is not None:
            floor = 10**(-self.extinction_ratio_dB/10.0)
            T = floor+(1-floor)*T
        
        return T * self.transmission
    
    def modulate(self, P_in, V):
        
        """
        Modulate input optical power.
        
        Paramters
        ---------
        P_in: float or ndarray
            Input optical power [W].
        V: float or ndarray
            Applied voltage [V].
        
        Returns
        -------
        P_out: float or ndarray
            Output optical power [W].
        """
        
        P_in = np.asarray(P_in,dtype=float)
        
        if np.any(P_in < 0):
            raise ValueError("Input optical power must be non-negative.")
        
        T = self.transfer(V)
        
        return P_in*T
        
