import numpy as np


class Activation:
    """
    Behavioral nonlinear activation block.

    Supported activation functions:

        sigmoid
        tanh
        relu
        linear

    This is a system-level nonlinear device model,
    not a transistor-level circuit model.
    """

    def __init__(
        self,
        kind="sigmoid",
        gain=1.0,
        threshold=0.0
    ):

        kind = kind.lower()

        supported = {
            "sigmoid",
            "tanh",
            "relu",
            "linear",
        }


        if kind not in supported:

            raise ValueError(
                f"Unsupported activation: {kind}"
            )


        self.kind = kind

        self.gain = float(
            gain
        )

        self.threshold = float(
            threshold
        )


    def activate(
        self,
        voltage
    ):

        voltage = np.asarray(
            voltage,
            dtype=float
        )


        z = (
            self.gain
            *
            (
                voltage
                -
                self.threshold
            )
        )


        if self.kind == "sigmoid":

            # Numerically stable clipping.
            z = np.clip(
                z,
                -60.0,
                60.0
            )

            return (
                1.0
                /
                (
                    1.0
                    +
                    np.exp(
                        -z
                    )
                )
            )


        elif self.kind == "tanh":

            return np.tanh(
                z
            )


        elif self.kind == "relu":

            return np.maximum(
                0.0,
                z
            )


        elif self.kind == "linear":

            return z


        raise RuntimeError(
            "Invalid activation state."
        )


    def __call__(
        self,
        voltage
    ):

        return self.activate(
            voltage
        )