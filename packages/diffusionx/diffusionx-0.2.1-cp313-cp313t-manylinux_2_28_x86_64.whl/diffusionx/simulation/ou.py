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


class OU:
    def __init__(
        self,
        theta: real,
        mu: real,
        sigma: real,
        start_position: real = 0.0,
    ):
        """
        Initialize an Ornstein-Uhlenbeck (OU) process object.
        dX_t = theta * (mu - X_t) dt + sigma * dW_t

        Args:
            theta (real): Mean reversion rate (theta > 0).
            sigma (real): Volatility (sigma > 0).
            start_position (real, optional): Starting position of the process. Defaults to mu.

        """
        self.theta = validate_positive_float(theta, "theta")
        self.sigma = validate_positive_float(sigma, "sigma")
        self.start_position = ensure_float(start_position)

    def simulate(
        self, duration: real, time_step: float = 0.01
    ) -> tuple[Vector, Vector]:
        duration = validate_positive_float(duration, "duration")
        time_step = validate_positive_float(time_step, "time_step")

        return _core.ou_simulate(
            self.theta,
            self.sigma,
            self.start_position,
            duration,
            time_step,
        )

    def moment(
        self,
        duration: real,
        order: int | float,
        center: bool = False,
        particles: int = 10_000,
        time_step: float = 0.01,
    ) -> float:
        validate_bool(center, "center")
        validate_order(order)
        particles = validate_particles(particles)
        duration = validate_positive_float(duration, "duration")
        time_step = validate_positive_float(time_step, "time_step")

        return (
            (
                _core.ou_raw_moment(
                    self.theta,
                    self.sigma,
                    self.start_position,
                    duration,
                    time_step,
                    order,
                    particles,
                )
                if not center
                else _core.ou_central_moment(
                    self.theta,
                    self.sigma,
                    self.start_position,
                    duration,
                    time_step,
                    order,
                    particles,
                )
            )
            if isinstance(order, int)
            else (
                _core.ou_frac_raw_moment(
                    self.theta,
                    self.sigma,
                    self.start_position,
                    duration,
                    time_step,
                    order,
                    particles,
                )
                if not center
                else _core.ou_frac_central_moment(
                    self.theta,
                    self.sigma,
                    self.start_position,
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
        a, b = validate_domain(domain, process_name="Ou FPT")
        time_step = validate_positive_float(time_step, "time_step")
        max_duration = validate_positive_float(max_duration, "max_duration")

        return _core.ou_fpt(
            self.theta,
            self.sigma,
            self.start_position,
            time_step,
            (a, b),
            max_duration,
        )

    def fpt_moment(
        self,
        domain: tuple[real, real],
        order: int,
        center: bool = False,
        particles: int = 10_000,
        time_step: float = 0.01,
        max_duration: real = 1000,
    ) -> float | None:
        validate_bool(center, "center")
        validate_order(order)
        a, b = validate_domain(domain, process_name="Ou FPT raw moment")
        particles = validate_particles(particles)
        time_step = validate_positive_float(time_step, "time_step")
        max_duration = validate_positive_float(max_duration, "max_duration")

        result = (
            _core.ou_fpt_raw_moment(
                self.theta,
                self.sigma,
                self.start_position,
                (a, b),
                order,
                particles,
                time_step,
                max_duration,
            )
            if not center
            else _core.ou_fpt_central_moment(
                self.theta,
                self.sigma,
                self.start_position,
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
        a, b = validate_domain(domain, process_name="Ou Occupation Time")
        duration = validate_positive_float(duration, "duration")
        time_step = validate_positive_float(time_step, "time_step")

        return _core.ou_occupation_time(
            self.theta,
            self.sigma,
            self.start_position,
            (a, b),
            time_step,
            duration,
        )

    def occupation_time_moment(
        self,
        domain: tuple[real, real],
        duration: real,
        order: int,
        center: bool = False,
        particles: int = 10_000,
        time_step: float = 0.01,
    ) -> float:
        validate_bool(center, "center")
        validate_order(order)
        a, b = validate_domain(domain, process_name="Ou Occupation raw moment")
        particles = validate_particles(particles)
        duration = validate_positive_float(duration, "duration")
        time_step = validate_positive_float(time_step, "time_step")

        result = (
            _core.ou_occupation_time_raw_moment(
                self.theta,
                self.sigma,
                self.start_position,
                (a, b),
                order,
                particles,
                time_step,
                duration,
            )
            if not center
            else _core.ou_occupation_time_central_moment(
                self.theta,
                self.sigma,
                self.start_position,
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

        return _core.ou_tamsd(
            self.theta,
            self.sigma,
            self.start_position,
            duration,
            delta,
            time_step,
            quad_order,
        )

    def eatamsd(
        self,
        duration: real,
        delta: real,
        particles: int,
        time_step: float = 0.01,
        quad_order: int = 10,
    ) -> float:
        duration = validate_positive_float(duration, "duration")
        delta = validate_positive_float(delta, "delta")
        particles = validate_particles(particles)
        time_step = validate_positive_float(time_step, "time_step")
        quad_order = validate_positive_integer(quad_order, "quad_order")

        return _core.ou_eatamsd(
            self.theta,
            self.sigma,
            self.start_position,
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
        Calculate the mean of the Ornstein-Uhlenbeck process.

        Args:
            duration (real): The total duration of the simulation.
            time_step (float, optional): Step size for the simulation. Defaults to 0.01.
            particles (int, optional): Number of particles (positive integer) for ensemble averaging. Defaults to 10_000.

        Returns:
            float: The mean of the Ornstein-Uhlenbeck process.
        """
        duration = validate_positive_float(duration, "duration (motion duration)")
        particles = validate_particles(particles)
        time_step = validate_positive_float(time_step, "time_step")

        return _core.ou_mean(
            self.theta,
            self.sigma,
            self.start_position,
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
        Calculate the mean squared displacement (MSD) of the Ornstein-Uhlenbeck process.

        Args:
            duration (real): The total duration of the simulation.
            time_step (float, optional): Step size for the simulation. Defaults to 0.01.
            particles (int, optional): Number of particles (positive integer) for ensemble averaging. Defaults to 10_000.

        Returns:
            float: The mean squared displacement of the Ornstein-Uhlenbeck process.
        """
        duration = validate_positive_float(duration, "duration (motion duration)")
        particles = validate_particles(particles)
        time_step = validate_positive_float(time_step, "time_step")

        return _core.ou_msd(
            self.theta,
            self.sigma,
            self.start_position,
            duration,
            time_step,
            particles,
        )
