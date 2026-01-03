from diffusionx import _core

from .basic import Vector, real
from .utils import (
    ensure_float,
    validate_bool,
    validate_domain,
    validate_order,
    validate_particles,
    validate_positive_float,
)


class LevyWalk:
    def __init__(
        self,
        alpha: real,
        velocity: real = 1.0,
        start_position: real = 0.0,
    ):
        """
        Initialize a Lévy Walk object.

        Args:
            alpha (real): Exponent for jump length distribution (typically (0, 2]).
            velocity (real): The velocity. Defaults to 1.0
            start_position (real, optional): Starting position. Defaults to 0.0.
        """
        alpha = validate_positive_float(alpha, "alpha")
        velocity = validate_positive_float(velocity, "velocity")
        start_position = ensure_float(start_position)

        if not (alpha <= 2):
            raise ValueError(f"alpha must be in (0, 2], got {alpha}")
        self.alpha = alpha
        self.velocity = velocity
        self.start_position = start_position

    def simulate(
        self,
        duration: real,
        time_step: float = 0.01,  # time_step interpretation can vary for LW
    ) -> tuple[Vector, Vector]:
        duration = validate_positive_float(duration, "duration")
        time_step = validate_positive_float(time_step, "time_step")

        return _core.levy_walk_simulate(
            self.alpha,
            self.velocity,
            self.start_position,
            duration,
        )

    def moment(
        self,
        duration: real,
        order: int | float,
        center: bool = False,
        particles: int = 10_000,
    ) -> float:
        validate_bool(center, "center")
        validate_order(order)
        particles = validate_particles(particles)
        duration = validate_positive_float(duration, "duration")

        return (
            (
                _core.levy_walk_raw_moment(
                    self.alpha,
                    self.velocity,
                    self.start_position,
                    duration,
                    order,
                    particles,
                )
                if not center
                else _core.levy_walk_central_moment(
                    self.alpha,
                    self.velocity,
                    self.start_position,
                    duration,
                    order,
                    particles,
                )
            )
            if isinstance(order, int)
            else (
                _core.levy_walk_frac_raw_moment(
                    self.alpha,
                    self.velocity,
                    self.start_position,
                    duration,
                    order,
                    particles,
                )
                if not center
                else _core.levy_walk_frac_central_moment(
                    self.alpha,
                    self.velocity,
                    self.start_position,
                    duration,
                    order,
                    particles,
                )
            )
        )

    def fpt(
        self,
        domain: tuple[real, real],
        max_duration: real = 1000,
    ) -> float | None:
        a, b = validate_domain(domain, process_name="LevyWalk FPT")
        max_duration = validate_positive_float(max_duration, "max_duration")

        return _core.levy_walk_fpt(
            self.alpha,
            self.velocity,
            self.start_position,
            (a, b),
            max_duration,
        )
