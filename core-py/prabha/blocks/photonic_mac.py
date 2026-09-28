import numpy as np

class PhotonicMAC:
    """
    Ideal differential Photonic Multiply-Accumulate (MAC).

    Computes:

        y = sum(w_i * x_i)

    and represents the physical optical output as:

        P_diff = P0 * y

    where:

        P0     = input laser power [W]
        x_i    = normalized input
        w_i    = signed weight
        P_diff = differential optical power [W]
    """
    
    def __init__(self, P0_mW=1.0):
        self.P0_mW=P0_mW
        
        self.P0=P0_mW*1e-3
        
    def split_weights(self,w):
        
        """
        Split signed wieghts into positive and negative components.
        
        w = w+ - w-
        
        where: 
            w+ = max(0,w)
            w- = max(0,-w)
        """
        
        w = np.asarray(w,dtype=float)
        
        w_plus = np.maximum(0,w)
        w_minus = np.maximum(0,-w)
        
        return w_plus, w_minus
        
    def compute(self, x, w):
        
        """
        Perform ideal differential Photonic MAC.
        
        Parameters:
            x : array-like, normalized input vector
            w : array-like, signed weight vector
            
        Returns: 
            result : dict
                Contains mathematical MAC and optical quantites.
        """
    
        x = np.asarray(x,dtype=float)
        w = np.asarray(w,dtype=float)
        
        if x.ndim != 1 or w.ndim != 1:
            raise ValueError("Input and weight vectors must be 1D arrays.")
        
        if len(x) != len(w):
            raise ValueError("Input and weight vectors must have the same length.")
        
        y=np.dot(w,x)
        
        w_plus, w_minus = self.split_weights(w)
        
        P_in = self.P0*x
        
        P_plus_channels = P_in*w_plus 
        
        P_plus = np.sum(P_plus_channels)
        
        P_in = self.P0*x
                
        P_minus_channels = P_in*w_minus
                
        P_minus = np.sum(P_minus_channels)
        
        P_diff = P_plus - P_minus
        
        y_recovered = P_diff/self.P0
        
        return {
            "x":x,
            "w":w,
            "w_plus":w_plus,
            "w_minus":w_minus,
            "P_in":P_in,
            "P_plus_channels":P_plus_channels,
            "P_minus_channels":P_minus_channels,
            "P_plus":P_plus,
            "P_minus":P_minus,
            "P_diff":P_diff,
            "mac":y,
            "mac_recovered":y_recovered,
        }
    