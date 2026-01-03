from diffusionx import _core

from .basic import Vector, real
from .utils import (
    ensure_float,
    validate_bool,
    validate_domain,
    validate_order,
    validate_particles,
    validate_positive_float,
    validate_positive_integer,
)


class GeometricBm:
    def __init__(
        self,
        start_value: real = 1.0,
        mu: real = 0.0,
        sigma: real = 0.1,
    ):
        """
        Initialize a Geometric Brownian Motion (Gb) object.
        S_t = S_0 * exp((mu - sigma^2/2)t + sigma * W_t)

        Args:
            start_value (real, optional): Initial value of the process (S0 > 0). Defaults to 1.0.
            mu (real, optional): Drift coefficient. Defaults to 0.0.
            sigma (real, optional): Volatility coefficient (sigma > 0). Defaults to 0.1.
        """
        self.start_value = validate_positive_float(start_value, "start_value")
        self.mu = ensure_float(mu)
        self.sigma = validate_positive_float(sigma, "sigma")

    def simulate(
        self, duration: real, time_step: float = 0.01
    ) -> tuple[Vector, Vector]:
        duration = validate_positive_float(duration, "duration")
        time_step = validate_positive_float(time_step, "time_step")

        return _core.gb_simulate(
            self.start_value,
            self.mu,
            self.sigma,
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
                _core.gb_raw_moment(
                    self.start_value,
                    self.mu,
                    self.sigma,
                    duration,
                    time_step,
                    order,
                    particles,
                )
                if not central
                else _core.gb_central_moment(
                    self.start_value,
                    self.mu,
                    self.sigma,
                    duration,
                    time_step,
                    order,
                    particles,
                )
            )
            if isinstance(order, int)
            else (
                _core.gb_frac_raw_moment(
                    self.start_value,
                    self.mu,
                    self.sigma,
                    duration,
                    time_step,
                    order,
                    particles,
                )
                if not central
                else _core.gb_frac_central_moment(
                    self.start_value,
                    self.mu,
                    self.sigma,
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
        a, b = validate_domain(domain, process_name="Gb FPT")
        time_step = validate_positive_float(time_step, "time_step")
        max_duration = validate_positive_float(max_duration, "max_duration")

        return _core.gb_fpt(
            self.start_value,
            self.mu,
            self.sigma,
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
        a, b = validate_domain(domain, process_name="Gb FPT raw moment")
        particles = validate_particles(particles)
        time_step = validate_positive_float(time_step, "time_step")
        max_duration = validate_positive_float(max_duration, "max_duration")

        result = (
            _core.gb_fpt_raw_moment(
                self.start_value,
                self.mu,
                self.sigma,
                (a, b),
                order,
                particles,
                time_step,
                max_duration,
            )
            if not central
            else _core.gb_fpt_central_moment(
                self.start_value,
                self.mu,
                self.sigma,
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
        a, b = validate_domain(domain, process_name="Gb Occupation Time")
        duration = validate_positive_float(duration, "duration")
        time_step = validate_positive_float(time_step, "time_step")
        return _core.gb_occupation_time(
            self.start_value,
            self.mu,
            self.sigma,
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
        a, b = validate_domain(domain, process_name="Gb Occupation raw moment")
        particles = validate_particles(particles)
        duration = validate_positive_float(duration, "duration")
        time_step = validate_positive_float(time_step, "time_step")

        result = (
            _core.gb_occupation_time_raw_moment(
                self.start_value,
                self.mu,
                self.sigma,
                (a, b),
                order,
                particles,
                time_step,
                duration,
            )
            if not central
            else _core.gb_occupation_time_central_moment(
                self.start_value,
                self.mu,
                self.sigma,
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

        return _core.gb_tamsd(
            self.start_value,
            self.mu,
            self.sigma,
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
        quad_order: int = 32,
    ) -> float:
        duration = validate_positive_float(duration, "duration")
        delta = validate_positive_float(delta, "delta")
        particles = validate_particles(particles)
        time_step = validate_positive_float(time_step, "time_step")
        quad_order = validate_positive_integer(quad_order, "quad_order")

        return _core.gb_eatamsd(
            self.start_value,
            self.mu,
            self.sigma,
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
        Calculate the mean of the Geometric Brownian Motion.

        Args:
            duration (real): The total duration of the simulation.
            time_step (float, optional): Step size for the simulation. Defaults to 0.01.
            particles (int, optional): Number of particles (positive integer) for ensemble averaging. Defaults to 10_000.

        Returns:
            float: The mean of the Geometric Brownian Motion.
        """
        duration = validate_positive_float(duration, "duration (motion duration)")
        particles = validate_particles(particles)
        time_step = validate_positive_float(time_step, "time_step")

        return _core.gb_mean(
            self.start_value,
            self.mu,
            self.sigma,
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
        Calculate the mean squared displacement (MSD) of the Geometric Brownian Motion.

        Args:
            duration (real): The total duration of the simulation.
            time_step (float, optional): Step size for the simulation. Defaults to 0.01.
            particles (int, optional): Number of particles (positive integer) for ensemble averaging. Defaults to 10_000.

        Returns:
            float: The mean squared displacement of the Geometric Brownian Motion.
        """
        duration = validate_positive_float(duration, "duration (motion duration)")
        particles = validate_particles(particles)
        time_step = validate_positive_float(time_step, "time_step")

        return _core.gb_msd(
            self.start_value,
            self.mu,
            self.sigma,
            duration,
            time_step,
            particles,
        )
