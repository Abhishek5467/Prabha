import numpy as np

class DAC:
    """
    Ideal N-bit unipolar Digital-to-Analog Converter.

    Converts a digital code into an analog voltage.

    Parameters
    ----------
    bits : int
        DAC resolution [bits].

    V_min : float
        Minimum output voltage [V].

    V_max : float
        Maximum output voltage [V].
    """
    
    def __init__(self, bits=8, V_min=0.0, V_max=1.0):
        
        if bits<=0:
            raise ValueError("DAC resolution must be positive.")
        
        if V_max<=V_min:
            raise ValueError("V_max must be greater than V_min.")
        
        self.bits=bits
        self.V_min=V_min
        self.V_max=V_max
        
        self.n_codes=2**bits
        
        self.max_code=self.n_codes-1
        
        self.lsb=((V_max-V_min)/self.max_code)
        
    def code_to_voltage(self,code):
        """
        Convert digital code to analog voltage.

        Parameters
        ----------
        code : int or ndarray
            Digital DAC code.

        Returns
        -------
        voltage : float or ndarray
            Analog output voltage [V].
        """
        
        code = np.asarray(code,dtype=int)
        
        if np.any(code<0) or np.any(code>self.max_code):
            raise ValueError("DAC code is outside the valid range.")
        
        voltage=(self.V_min+code*self.lsb)
        
        return voltage
    
    
    def voltage_to_code(self, voltage):
        voltage=np.asarray(voltage,dtype=float)
        
        if np.any(voltage<self.V_min) or np.any(voltage>self.V_max):
            raise ValueError("Voltage is outside the DAC range.")
        
        code=np.rint((voltage-self.V_min)/(self.lsb))
        
        return code.astype(int)
    
    
    def quantize(self,voltage):
        code=self.voltage_to_code(voltage)
        voltage_actual=self.code_to_voltage(code)
        return code,voltage_actual