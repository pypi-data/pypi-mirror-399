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


class BrownianMeander:
    def __init__(
        self,
    ):
        """
        Initialize a Brownian Meander object.
        A Brownian meander is a Brownian motion conditioned to be positive up to a specified duration.
        """

    def simulate(
        self, duration: real, time_step: float = 0.01
    ) -> tuple[Vector, Vector]:
        duration = validate_positive_float(duration, "duration")
        time_step = validate_positive_float(time_step, "time_step")

        return _core.meander_simulate(
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
                _core.meander_raw_moment(
                    duration,
                    time_step,
                    order,
                    particles,
                )
                if not center
                else _core.meander_central_moment(
                    duration,
                    time_step,
                    order,
                    particles,
                )
            )
            if isinstance(order, int)
            else (
                _core.meander_frac_raw_moment(
                    duration,
                    time_step,
                    order,
                    particles,
                )
                if not center
                else _core.meander_frac_central_moment(
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
    ) -> float | None:
        a, b = validate_domain(domain, process_name="Meander FPT")
        time_step = validate_positive_float(time_step, "time_step")
        return _core.meander_fpt(
            time_step,
            (a, b),
        )

    def fpt_moment(
        self,
        domain: tuple[real, real],
        order: int,
        center: bool = False,
        particles: int = 10_000,
        time_step: float = 0.01,
    ) -> float | None:
        validate_bool(center, "center")
        validate_order(order)
        a, b = validate_domain(domain, process_name="Meander FPT raw moment")
        particles = validate_particles(particles)
        time_step = validate_positive_float(time_step, "time_step")

        result = (
            _core.meander_fpt_raw_moment(
                (a, b),
                order,
                particles,
                time_step,
            )
            if not center
            else _core.meander_fpt_central_moment(
                (a, b),
                order,
                particles,
                time_step,
            )
        )

        return result

    def occupation_time(
        self,
        domain: tuple[real, real],
        duration: real,  # Meander duration
        time_step: float = 0.01,
    ) -> float:
        a, b = validate_domain(domain, process_name="Meander Occupation Time")
        duration = validate_positive_float(duration, "duration (meander duration)")
        time_step = validate_positive_float(time_step, "time_step")

        return _core.meander_occupation_time(
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
        a, b = validate_domain(domain, process_name="Meander Occupation raw moment")
        particles = validate_particles(particles)
        duration = validate_positive_float(duration, "duration (meander duration)")
        time_step = validate_positive_float(time_step, "time_step")

        result = (
            _core.meander_occupation_time_raw_moment(
                (a, b),
                order,
                particles,
                time_step,
                duration,
            )
            if not center
            else _core.meander_occupation_time_central_moment(
                (a, b), order, particles, time_step, duration
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
        duration = validate_positive_float(duration, "duration (meander duration)")
        delta = validate_positive_float(delta, "delta")
        time_step = validate_positive_float(time_step, "time_step")
        quad_order = validate_positive_integer(quad_order, "quad_order")

        return _core.meander_tamsd(
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
        duration = validate_positive_float(duration, "duration (meander duration)")
        delta = validate_positive_float(delta, "delta")
        particles = validate_particles(particles)
        time_step = validate_positive_float(time_step, "time_step")
        quad_order = validate_positive_integer(quad_order, "quad_order")

        return _core.meander_eatamsd(
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
        Calculate the mean of the Brownian meander.

        Args:
            duration (real): The total duration of the simulation.
            time_step (float, optional): Step size for the simulation. Defaults to 0.01.
            particles (int, optional): Number of particles (positive integer) for ensemble averaging. Defaults to 10_000.

        Returns:
            float: The mean of the Brownian meander.
        """
        duration = validate_positive_float(duration, "duration (motion duration)")
        particles = validate_particles(particles)
        time_step = validate_positive_float(time_step, "time_step")

        return _core.meander_mean(
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
        Calculate the mean squared displacement (MSD) of the Brownian meander.

        Args:
            duration (real): The total duration of the simulation.
            time_step (float, optional): Step size for the simulation. Defaults to 0.01.
            particles (int, optional): Number of particles (positive integer) for ensemble averaging. Defaults to 10_000.

        Returns:
            float: The mean squared displacement of the Brownian meander.
        """
        duration = validate_positive_float(duration, "duration (motion duration)")
        particles = validate_particles(particles)
        time_step = validate_positive_float(time_step, "time_step")

        return _core.meander_msd(
            duration,
            time_step,
            particles,
        )
