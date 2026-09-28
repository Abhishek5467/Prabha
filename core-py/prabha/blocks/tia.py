import numpy as np


class TIA:
    """
    Transimpedance Amplifier (TIA).

    DC relationship:

        V_out = I_in * R_f

    Optional first-order finite-bandwidth model:

        H(s) = 1 / (1 + s*tau)

    where:

        tau = 1 / (2*pi*f_3dB)

    Optional input-referred white current noise:

        i_n [A/sqrt(Hz)]

    Parameters
    ----------
    R_f : float
        Transimpedance gain [Ohm].

    bandwidth_Hz : float or None
        TIA -3 dB bandwidth [Hz].
        None or np.inf gives ideal infinite bandwidth.

    noise_current_density_A_per_sqrtHz : float
        Input-referred white current-noise density [A/sqrt(Hz)].

    seed : int
        Random seed for deterministic noise generation.
    """

    def __init__(
        self,
        R_f=1000.0,
        bandwidth_Hz=None,
        noise_current_density_A_per_sqrtHz=0.0,
        seed=1,
    ):

        if R_f <= 0:
            raise ValueError("R_f must be positive.")

        if bandwidth_Hz is not None:
            if bandwidth_Hz <= 0:
                raise ValueError(
                    "bandwidth_Hz must be positive or None."
                )

        if noise_current_density_A_per_sqrtHz < 0:
            raise ValueError(
                "Noise current density must be non-negative."
            )

        self.R_f = R_f
        self.bandwidth_Hz = bandwidth_Hz
        self.noise_current_density = (
            noise_current_density_A_per_sqrtHz
        )
        self.seed = seed

    def _lowpass(self, signal, fs):
        """
        First-order discrete-time low-pass filter.
        """

        if self.bandwidth_Hz is None or np.isinf(self.bandwidth_Hz):
            return signal

        if fs is None:
            raise ValueError(
                "fs must be provided when using finite TIA bandwidth."
            )

        if fs <= 0:
            raise ValueError(
                "Sampling frequency must be positive."
            )

        tau = 1.0 / (
            2.0 * np.pi * self.bandwidth_Hz
        )

        dt = 1.0 / fs

        alpha = dt / (tau + dt)

        output = np.empty_like(signal)

        if signal.ndim == 0:
            return signal

        output[0] = signal[0]

        for n in range(1, len(signal)):
            output[n] = (
                output[n - 1]
                + alpha * (
                    signal[n] - output[n - 1]
                )
            )

        return output

    def amplify(
        self,
        I_in,
        fs=None,
        include_noise=False,
    ):
        """
        Convert input current into TIA output voltage.

        Parameters
        ----------
        I_in : float or ndarray
            Input current [A].

        fs : float or None
            Sampling frequency [Hz].

        include_noise : bool
            Include input-referred TIA current noise.

        Returns
        -------
        V_out : float or ndarray
            Output voltage [V].
        """

        I_in = np.asarray(I_in, dtype=float)


        # Scalar DC operation

        if I_in.ndim == 0:

            if include_noise:
                raise ValueError(
                    "Noise requires a time-domain array and fs."
                )

            return I_in * self.R_f


        # Deterministic signal

        I_signal = I_in.copy()


        # Add input-referred white current noise

        if include_noise:

            if fs is None:
                raise ValueError(
                    "fs must be provided when including TIA noise."
                )

            if fs <= 0:
                raise ValueError(
                    "Sampling frequency must be positive."
                )

            noise_density = (
                self.noise_current_density
            )

            # One-sided noise density:
            # variance = S_i * fs / 2

            noise_sigma = (
                noise_density
                * np.sqrt(fs / 2.0)
            )

            rng = np.random.default_rng(
                self.seed
            )

            noise_current = rng.normal(
                loc=0.0,
                scale=noise_sigma,
                size=I_signal.shape,
            )

            I_total = I_signal + noise_current

        else:

            I_total = I_signal


        # Convert current to voltage

        V_ideal = I_total * self.R_f


        # Apply TIA bandwidth

        V_out = self._lowpass(
            V_ideal,
            fs,
        )

        return V_out