import numpy as np


class ADC:
    """
    Ideal Analog-to-Digital Converter.

    Converts an analog voltage into an integer digital code.

    Parameters
    ----------
    resolution_bits : int
        ADC resolution in bits.

    v_min : float
        Minimum input voltage [V].

    v_max : float
        Maximum input voltage [V].
    """

    def __init__(
        self,
        resolution_bits=3,
        v_min=0.0,
        v_max=1.0,
    ):
        if resolution_bits <= 0:
            raise ValueError("Resolution must be positive.")

        if v_max <= v_min:
            raise ValueError("v_max must be greater than v_min.")

        self.resolution_bits = resolution_bits
        self.v_min = v_min
        self.v_max = v_max

        self.n_codes = 2 ** resolution_bits

        self.lsb = (
            (v_max - v_min)
            / (self.n_codes - 1)
        )

    def convert(self, voltage):
        """
        Convert analog voltage into ADC digital code.

        Parameters
        ----------
        voltage : float or ndarray
            Analog input voltage [V].

        Returns
        -------
        code : int or ndarray
            Quantized digital ADC code.
        """

        voltage = np.asarray(
            voltage,
            dtype=float
        )

        if np.any(voltage < self.v_min):
            raise ValueError(
                "Input voltage below ADC range."
            )

        if np.any(voltage > self.v_max):
            raise ValueError(
                "Input voltage above ADC range."
            )

        normalized = (
            voltage - self.v_min
        ) / (
            self.v_max - self.v_min
        )

        code = np.rint(
            normalized * (self.n_codes - 1)
        ).astype(int)

        return code

    def code_to_voltage(self, code):
        """
        Convert ADC digital code back to
        the corresponding quantized voltage.
        """

        code = np.asarray(
            code,
            dtype=int
        )

        if np.any(code < 0):
            raise ValueError(
                "ADC code cannot be negative."
            )

        if np.any(code >= self.n_codes):
            raise ValueError(
                "ADC code exceeds ADC range."
            )

        voltage = (
            self.v_min
            + code * self.lsb
        )

        return voltage