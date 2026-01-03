from diffusionx import _core

from .basic import Vector, real
from .utils import (
    validate_bool,
    validate_domain,
    validate_order,
    validate_particles,
    validate_positive_float,
    validate_positive_integer,
)


class Gamma:
    def __init__(
        self,
        shape: real,  # Also known as alpha or k
        rate: real,  # Also known as beta or 1/theta (if theta is scale)
    ):
        """
        Initialize a Gamma process object.
        A Gamma process is a Lévy process with non-decreasing sample paths.
        It is characterized by a shape (or concentration) and a rate parameter.

        Args:
            shape (real): Shape parameter (k > 0).
            rate (real): Rate parameter (beta > 0). The scale parameter is 1/rate.
            start_position (real, optional): Starting position. Defaults to 0.0.
        """
        self.shape: float = validate_positive_float(shape, "shape")
        self.rate: float = validate_positive_float(rate, "rate")

    def simulate(
        self, duration: real, time_step: float = 0.01
    ) -> tuple[Vector, Vector]:
        duration = validate_positive_float(duration, "duration")
        time_step = validate_positive_float(time_step, "time_step")

        return _core.gamma_simulate(
            self.shape,
            self.rate,
            duration,
            time_step,
        )

    def moment(
        self,
        duration: real,
        order: int | float,
        central: bool = False,
        particles: int = 10_000,
        time_step: float = 0.01,
    ) -> float:
        validate_bool(central, "central")
        validate_order(order)
        particles = validate_particles(particles)
        duration = validate_positive_float(duration, "duration")
        time_step = validate_positive_float(time_step, "time_step")
        validate_bool(central, "central")

        return (
            (
                _core.gamma_raw_moment(
                    self.shape,
                    self.rate,
                    duration,
                    time_step,
                    order,
                    particles,
                )
                if not central
                else _core.gamma_central_moment(
                    self.shape,
                    self.rate,
                    duration,
                    time_step,
                    order,
                    particles,
                )
            )
            if isinstance(order, int)
            else (
                _core.gamma_frac_raw_moment(
                    self.shape,
                    self.rate,
                    duration,
                    time_step,
                    order,
                    particles,
                )
                if not central
                else _core.gamma_frac_central_moment(
                    self.shape,
                    self.rate,
                    duration,
                    time_step,
                    order,
                    particles,
                )
            )
        )

    def fpt(
        self,
        domain: tuple[real, real],
        time_step: float = 0.01,
        max_duration: real = 1000,
    ) -> float | None:
        a, b = validate_domain(domain, process_name="Gamma FPT")
        time_step = validate_positive_float(time_step, "time_step")
        max_duration = validate_positive_float(max_duration, "max_duration")

        return _core.gamma_fpt(
            self.shape,
            self.rate,
            time_step,
            (a, b),
            max_duration,
        )

    def fpt_moment(
        self,
        domain: tuple[real, real],
        order: int,
        central: bool = False,
        particles: int = 10_000,
        time_step: float = 0.01,
        max_duration: real = 1000,
    ) -> float | None:
        validate_bool(central, "central")
        validate_order(order)
        a, b = validate_domain(domain, process_name="Gamma FPT raw moment")
        particles = validate_particles(particles)
        time_step = validate_positive_float(time_step, "time_step")
        max_duration = validate_positive_float(max_duration, "max_duration")

        result = (
            _core.gamma_fpt_raw_moment(
                self.shape,
                self.rate,
                (a, b),
                order,
                particles,
                time_step,
                max_duration,
            )
            if not central
            else _core.gamma_fpt_central_moment(
                self.shape,
                self.rate,
                (a, b),
                order,
                particles,
                time_step,
                max_duration,
            )
        )

        return result

    def occupation_time(
        self,
        domain: tuple[real, real],
        duration: real,
        time_step: float = 0.01,
    ) -> float:
        a, b = validate_domain(domain, process_name="Gamma Occupation Time")
        duration = validate_positive_float(duration, "duration")
        time_step = validate_positive_float(time_step, "time_step")

        return _core.gamma_occupation_time(
            self.shape,
            self.rate,
            (a, b),
            time_step,
            duration,
        )

    def occupation_time_moment(
        self,
        domain: tuple[real, real],
        duration: real,
        order: int,
        central: bool = False,
        particles: int = 10_000,
        time_step: float = 0.01,
    ) -> float:
        validate_bool(central, "central")
        validate_order(order)
        a, b = validate_domain(domain, process_name="Gamma Occupation raw moment")
        particles = validate_particles(particles)
        duration = validate_positive_float(duration, "duration")
        time_step = validate_positive_float(time_step, "time_step")

        result = (
            _core.gamma_occupation_time_raw_moment(
                self.shape,
                self.rate,
                (a, b),
                order,
                particles,
                time_step,
                duration,
            )
            if not central
            else _core.gamma_occupation_time_central_moment(
                self.shape,
                self.rate,
                (a, b),
                order,
                particles,
                time_step,
                duration,
            )
        )

        return result

    def tamsd(
        self,
        duration: real,
        delta: real,
        time_step: float = 0.01,
        quad_order: int = 10,
    ) -> float:
        duration = validate_positive_float(duration, "duration")
        delta = validate_positive_float(delta, "delta")
        time_step = validate_positive_float(time_step, "time_step")
        quad_order = validate_positive_integer(quad_order, "quad_order")

        return _core.gamma_tamsd(
            self.shape,
            self.rate,
            duration,
            delta,
            time_step,
            quad_order,
        )

    def eatamsd(
        self,
        duration: real,
        delta: real,
        particles: int = 10_000,
        time_step: float = 0.01,
        quad_order: int = 10,
    ) -> float:
        duration = validate_positive_float(duration, "duration")
        delta = validate_positive_float(delta, "delta")
        particles = validate_particles(particles)
        time_step = validate_positive_float(time_step, "time_step")
        quad_order = validate_positive_integer(quad_order, "quad_order")

        return _core.gamma_eatamsd(
            self.shape,
            self.rate,
            duration,
            delta,
            particles,
            time_step,
            quad_order,
        )

    def mean(
        self, duration: real, time_step: float = 0.01, particles: int = 10_000
    ) -> float:
        """
        Calculate the mean of the Gamma process.

        Args:
            duration (real): The total duration of the simulation.
            time_step (float, optional): Step size for the simulation. Defaults to 0.01.
            particles (int, optional): Number of particles (positive integer) for ensemble averaging. Defaults to 10_000.

        Returns:
            float: The mean of the Gamma process.
        """
        duration = validate_positive_float(duration, "duration (motion duration)")
        particles = validate_particles(particles)
        time_step = validate_positive_float(time_step, "time_step")

        return _core.gamma_mean(
            self.shape,
            self.rate,
            duration,
            time_step,
            particles,
        )

    def msd(
        self,
        duration: real,
        time_step: float = 0.01,
        particles: int = 10_000,
    ) -> float:
        """
        Calculate the mean squared displacement (MSD) of the Gamma process.

        Args:
            duration (real): The total duration of the simulation.
            time_step (float, optional): Step size for the simulation. Defaults to 0.01.
            particles (int, optional): Number of particles (positive integer) for ensemble averaging. Defaults to 10_000.

        Returns:
            float: The mean squared displacement of the Gamma process.
        """
        duration = validate_positive_float(duration, "duration (motion duration)")
        particles = validate_particles(particles)
        time_step = validate_positive_float(time_step, "time_step")

        return _core.gamma_msd(
            self.shape,
            self.rate,
            duration,
            time_step,
            particles,
        )
