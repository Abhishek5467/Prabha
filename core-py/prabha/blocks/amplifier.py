import numpy as np


class Amplifier:
    """
    Behavioral voltage amplifier.

    Ideal transfer:

        V_out = gain * V_in + offset

    Optional output limits can model rail saturation.
    """

    def __init__(
        self,
        gain=1.0,
        offset_V=0.0,
        v_min=None,
        v_max=None
    ):

        self.gain = float(
            gain
        )

        self.offset_V = float(
            offset_V
        )

        self.v_min = v_min
        self.v_max = v_max


        if (
            v_min is not None
            and
            v_max is not None
            and
            v_min >= v_max
        ):

            raise ValueError(
                "v_min must be less than v_max."
            )


    def amplify(
        self,
        voltage
    ):

        voltage = np.asarray(
            voltage,
            dtype=float
        )


        output = (
            self.gain
            *
            voltage

            +

            self.offset_V
        )


        if self.v_min is not None:

            output = np.maximum(
                output,
                self.v_min
            )


        if self.v_max is not None:

            output = np.minimum(
                output,
                self.v_max
            )


        return output