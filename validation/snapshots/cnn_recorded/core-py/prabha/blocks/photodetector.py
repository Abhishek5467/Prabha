import numpy as np


Q_E = 1.602176634e-19


class Photodetector:

    def __init__(
        self,
        responsivity_A_per_W=1.0,
        dark_current_A=0.0,
        seed=1
    ):

        if responsivity_A_per_W < 0:
            raise ValueError(
                "Responsivity must be non-negative."
            )

        if dark_current_A < 0:
            raise ValueError(
                "Dark current must be non-negative."
            )

        self.responsivity = (
            responsivity_A_per_W
        )

        self.dark_current_A = (
            dark_current_A
        )

        self.seed = seed


    def detect(
        self,
        P_opt,
        bandwidth_Hz=None,
        include_dark_current=True,
        include_shot_noise=False
    ):

        P_opt = np.asarray(
            P_opt,
            dtype=float
        )

        if np.any(P_opt < 0):
            raise ValueError(
                "Optical power must be non-negative."
            )

        # Photocurrent

        I_ph = (
            self.responsivity
            *
            P_opt
        )


        # --------------------------------------------
        # Dark current
        # --------------------------------------------

        if include_dark_current:

            I_dark = self.dark_current_A

        else:

            I_dark = 0.0


        I_mean = (
            I_ph
            +
            I_dark
        )


        # No shot noise

        if not include_shot_noise:

            return I_mean


        # Shot noise requires bandwidth

        if bandwidth_Hz is None:

            raise ValueError(
                "bandwidth_Hz is required "
                "when shot noise is enabled."
            )

        if bandwidth_Hz < 0:

            raise ValueError(
                "bandwidth_Hz must be non-negative."
            )

        sigma_shot = np.sqrt(
            2.0
            *
            Q_E
            *
            I_mean
            *
            bandwidth_Hz
        )


        rng = np.random.default_rng(
            self.seed
        )


        shot_noise = rng.normal(
            loc=0.0,
            scale=sigma_shot,
            size=I_mean.shape
        )


        return (
            I_mean
            +
            shot_noise
        )
        
        
    def shot_noise_density(
        self,
        P_opt,
        include_dark_current=True
    ):

        P_opt = np.asarray(
            P_opt,
            dtype=float
        )

        if np.any(P_opt < 0):
            raise ValueError(
                "Optical power must be non-negative."
            )

        I_ph = (
            self.responsivity
            *
            P_opt
        )

        if include_dark_current:
            I_dark = self.dark_current_A
        else:
            I_dark = 0.0

        I_mean = (
            I_ph
            +
            I_dark
        )

        density = np.sqrt(
            2.0
            *
            Q_E
            *
            I_mean
        )

        return density
    
    def detect_white_shot(
        self,
        P_opt,
        fs,
        include_dark_current=True,
        include_shot_noise=True
    ):

        P_opt = np.asarray(
            P_opt,
            dtype=float
        )

        if np.any(P_opt < 0):
            raise ValueError(
                "Optical power must be non-negative."
            )

        if fs <= 0:
            raise ValueError(
                "Sampling frequency must be positive."
            )

        I_ph = (
            self.responsivity
            *
            P_opt
        )

        if include_dark_current:
            I_dark = self.dark_current_A
        else:
            I_dark = 0.0

        I_mean = (
            I_ph
            +
            I_dark
        )

        if not include_shot_noise:
            return I_mean

        density = np.sqrt(
            2.0
            *
            Q_E
            *
            I_mean
        )

        # One-sided PSD convention:
        # variance of discrete white samples =
        # density^2 * fs/2
        
        sigma_sample = (
            density
            *
            np.sqrt(fs / 2.0)
        )

        rng = np.random.default_rng(
            self.seed
        )

        noise = rng.normal(
            loc=0.0,
            scale=sigma_sample,
            size=I_mean.shape
        )

        return (
            I_mean
            +
            noise
        )