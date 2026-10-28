import numpy as np


class Capacitor:
    """
    Charge-domain capacitor model.

    Fundamental relation:

        Q = C V

    For a current integrated over time:

        dQ = I dt

    therefore:

        dV = I dt / C

    Multiple currents entering the same node are combined
    according to Kirchhoff's current law.
    """

    def __init__(
        self,
        capacitance_F=1e-12,
        leakage_resistance_ohm=None,
        initial_voltage_V=0.0,
    ):

        if capacitance_F <= 0:
            raise ValueError(
                "Capacitance must be positive."
            )

        if (
            leakage_resistance_ohm is not None
            and
            leakage_resistance_ohm <= 0
        ):
            raise ValueError(
                "Leakage resistance must be positive."
            )

        self.capacitance_F = float(
            capacitance_F
        )

        self.leakage_resistance_ohm = (
            leakage_resistance_ohm
        )

        self.initial_voltage_V = float(
            initial_voltage_V
        )

        self.voltage_V = float(
            initial_voltage_V
        )


    def reset(
        self,
        voltage_V=None
    ):

        if voltage_V is None:
            voltage_V = (
                self.initial_voltage_V
            )

        self.voltage_V = float(
            voltage_V
        )

        return self.voltage_V


    def voltage_from_charge(
        self,
        charge_C
    ):

        return (
            np.asarray(
                charge_C,
                dtype=float
            )
            /
            self.capacitance_F
        )


    def charge_from_voltage(
        self,
        voltage_V
    ):

        return (
            self.capacitance_F
            *
            np.asarray(
                voltage_V,
                dtype=float
            )
        )


    def integrate_current(
        self,
        current_A,
        dt_s
    ):
        """
        Integrate a single total current sample.

        If leakage is disabled:

            V_new = V_old + I dt / C

        If leakage is enabled, a first-order RC leakage
        term is included.
        """

        if dt_s <= 0:
            raise ValueError(
                "dt_s must be positive."
            )

        current_A = float(
            current_A
        )


        if (
            self.leakage_resistance_ohm
            is None
        ):

            self.voltage_V += (
                current_A
                *
                dt_s
                /
                self.capacitance_F
            )

        else:

            R = (
                self.leakage_resistance_ohm
            )

            C = (
                self.capacitance_F
            )

            tau = R * C

            decay = np.exp(
                -dt_s / tau
            )

            # Exact solution for constant current
            # during one integration interval.

            self.voltage_V = (
                self.voltage_V
                *
                decay

                +

                current_A
                *
                R
                *
                (
                    1.0
                    -
                    decay
                )
            )


        return self.voltage_V


    def integrate_currents(
        self,
        currents_A,
        integration_time_s,
        reset=True
    ):
        """
        Integrate multiple branch currents flowing into
        the same capacitor node.

        KCL:

            I_total = sum(I_i)

        Then:

            Delta V = I_total T / C

        for the ideal capacitor.
        """

        currents_A = np.asarray(
            currents_A,
            dtype=float
        )

        if integration_time_s <= 0:
            raise ValueError(
                "Integration time must be positive."
            )

        if reset:
            self.reset()


        total_current_A = np.sum(
            currents_A
        )


        voltage = self.integrate_current(
            total_current_A,
            integration_time_s
        )


        return voltage