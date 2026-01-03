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


class Levy:
    def __init__(
        self,
        alpha: real,
        start_position: real = 0.0,
    ):
        """
        Initialize a Lévy process object.

        Args:
            alpha (real): Stability index of the Lévy process. Must be in the range (0, 2].
            start_position (real, optional): Starting position of the Lévy process. Defaults to 0.0.
        """
        alpha = validate_positive_float(alpha, "alpha")
        if not (alpha <= 2):
            raise ValueError(f"alpha must be in the range (0, 2], got {alpha}")

        self.start_position = ensure_float(start_position)
        self.alpha = alpha

    def simulate(
        self, duration: real, time_step: float = 0.01
    ) -> tuple[Vector, Vector]:
        """
        Simulate the Lévy process.

        Args:
            duration (real): Total duration of the simulation.
            time_step (real, optional): Step size for the simulation. Defaults to 0.01.

        Returns:
            tuple[Vector, Vector]: Simulation times and positions.
        """
        duration = validate_positive_float(duration, "duration")
        time_step = validate_positive_float(time_step, "time_step")

        return _core.levy_simulate(
            self.start_position,
            self.alpha,
            duration,
            time_step,
        )

    def fpt(
        self,
        domain: tuple[real, real],
        time_step: float = 0.01,
        max_duration: real = 1000,
    ) -> float | None:
        """
        Calculate the first passage time of the Lévy process.

        Args:
            domain (tuple[real, real]): The domain (a, b) for FPT. a must be less than b.
            time_step (real, optional): Step size for the simulation. Defaults to 0.01.
            max_duration (real, optional): Maximum duration to simulate for FPT. Defaults to 1000.

        Returns:
            float | None: First passage time, or None if max_duration is reached first.
        """
        a, b = validate_domain(domain, process_name="Levy FPT")
        time_step = validate_positive_float(time_step, "time_step")
        max_duration = validate_positive_float(max_duration, "max_duration")

        return _core.levy_fpt(
            self.start_position,
            self.alpha,
            time_step,
            (a, b),
            max_duration,
        )

    def occupation_time(
        self,
        domain: tuple[real, real],
        duration: real,
        time_step: float = 0.01,
    ) -> float:
        """
        Calculate the occupation time of the Lévy process in a given domain.

        Args:
            domain (tuple[real, real]): The domain (a, b) for occupation time. a must be less than b.
            duration (real): The total duration of the simulation.
            time_step (real, optional): Step size for the simulation. Defaults to 0.01.

        Returns:
            float: The occupation time of the Lévy process in the domain.
        """
        a, b = validate_domain(domain, process_name="Levy Occupation Time")
        duration = validate_positive_float(duration, "duration")
        time_step = validate_positive_float(time_step, "time_step")

        return _core.levy_occupation_time(
            self.start_position,
            self.alpha,
            time_step,
            (a, b),
            duration,
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
        a, b = validate_domain(domain, process_name="Levy FPT raw moment")
        particles = validate_particles(particles)
        time_step = validate_positive_float(time_step, "time_step")
        max_duration = validate_positive_float(max_duration, "max_duration")

        result = (
            _core.levy_fpt_raw_moment(
                self.start_position,
                self.alpha,
                (a, b),
                order,
                particles,
                max_duration,
                time_step,
            )
            if not center
            else _core.levy_fpt_central_moment(
                self.start_position,
                self.alpha,
                (a, b),
                order,
                particles,
                max_duration,
                time_step,
            )
        )

        return result

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
        a, b = validate_domain(domain, process_name="Levy Occupation raw moment")
        particles = validate_particles(particles)
        duration = validate_positive_float(duration, "duration")
        time_step = validate_positive_float(time_step, "time_step")

        result = (
            _core.levy_occupation_time_raw_moment(
                self.start_position,
                self.alpha,
                (a, b),
                duration,
                order,
                particles,
                time_step,
            )
            if not center
            else _core.levy_occupation_time_central_moment(
                self.start_position,
                self.alpha,
                (a, b),
                duration,
                order,
                particles,
                time_step,
            )
        )

        return result


class Subordinator:
    def __init__(
        self,
        alpha: real,
    ):
        """
        Initialize a subordinator object.

        Args:
            alpha (real): The alpha parameter of the subordinator, the value must be in the range (0, 1).

        Returns:
            Subordinator: A subordinator object.
        """
        alpha = validate_positive_float(alpha, "alpha")
        if alpha >= 1:
            raise ValueError("alpha must be in the range (0, 1) for Subordinator")

        self.alpha = alpha

    def simulate(
        self, duration: real, time_step: float = 0.01
    ) -> tuple[Vector, Vector]:
        duration = validate_positive_float(duration, "duration")
        time_step = validate_positive_float(time_step, "time_step")
        return _core.subordinator_simulate(
            self.alpha,
            duration,
            time_step,
        )

    def fpt(
        self,
        domain: tuple[real, real],
        time_step: float = 0.01,
        max_duration: real = 1000,
    ) -> float | None:
        a, b = validate_domain(domain, process_name="Subordinator FPT")
        time_step = validate_positive_float(time_step, "time_step")
        max_duration = validate_positive_float(max_duration, "max_duration")

        return _core.subordinator_fpt(
            self.alpha,
            (a, b),
            max_duration,
            time_step,
        )

    def occupation_time(
        self,
        domain: tuple[real, real],
        duration: real,
        time_step: float = 0.01,
    ) -> float:
        a, b = validate_domain(domain, process_name="Subordinator Occupation Time")
        duration = validate_positive_float(duration, "duration")
        time_step = validate_positive_float(time_step, "time_step")

        return _core.subordinator_occupation_time(
            self.alpha,
            (a, b),
            duration,
            time_step,
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
        a, b = validate_domain(domain, process_name="Subordinator FPT raw moment")
        particles = validate_particles(particles)
        time_step = validate_positive_float(time_step, "time_step")
        max_duration = validate_positive_float(max_duration, "max_duration")

        result = (
            _core.subordinator_fpt_raw_moment(
                self.alpha,
                (a, b),
                max_duration,
                time_step,
                order,
                particles,
            )
            if not center
            else _core.subordinator_fpt_central_moment(
                self.alpha,
                (a, b),
                max_duration,
                time_step,
                order,
                particles,
            )
        )

        return result

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
        a, b = validate_domain(
            domain, process_name="Subordinator Occupation raw moment"
        )
        particles = validate_particles(particles)
        duration = validate_positive_float(duration, "duration")
        time_step = validate_positive_float(time_step, "time_step")

        result = (
            _core.subordinator_occupation_time_raw_moment(
                self.alpha,
                (a, b),
                duration,
                time_step,
                order,
                particles,
            )
            if not center
            else _core.subordinator_occupation_time_central_moment(
                self.alpha,
                (a, b),
                duration,
                time_step,
                order,
                particles,
            )
        )

        return result


class InvSubordinator:
    def __init__(
        self,
        alpha: real,
    ):
        """
        Initialize an inverse subordinator object.

        Args:
            alpha (real): The alpha parameter of the inverse subordinator, value must be in (0, 1).
        """
        alpha = validate_positive_float(alpha, "alpha")
        if alpha >= 1:
            raise ValueError("alpha must be in the range (0, 1) for InvSubordinator")
        self.alpha = alpha

    def simulate(
        self, duration: real, time_step: float = 0.01
    ) -> tuple[Vector, Vector]:
        duration = validate_positive_float(duration, "duration")
        time_step = validate_positive_float(time_step, "time_step")
        return _core.inv_subordinator_simulate(
            self.alpha,
            duration,
            time_step,
        )

    def fpt(
        self,
        domain: tuple[real, real],
        time_step: float = 0.01,
        max_duration: real = 1000,
    ) -> float | None:
        a, b = validate_domain(domain, process_name="InvSubordinator FPT")
        time_step = validate_positive_float(time_step, "time_step")
        max_duration = validate_positive_float(max_duration, "max_duration")

        return _core.inv_subordinator_fpt(
            self.alpha,
            (a, b),
            max_duration,
            time_step,
        )

    def occupation_time(
        self,
        domain: tuple[real, real],
        duration: real,
        time_step: float = 0.01,
    ) -> float:
        a, b = validate_domain(domain, process_name="InvSubordinator Occupation Time")
        duration = validate_positive_float(duration, "duration")
        time_step = validate_positive_float(time_step, "time_step")

        return _core.inv_subordinator_occupation_time(
            self.alpha,
            (a, b),
            duration,
            time_step,
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
        a, b = validate_domain(domain, process_name="InvSubordinator FPT raw moment")
        particles = validate_particles(particles)
        time_step = validate_positive_float(time_step, "time_step")
        max_duration = validate_positive_float(max_duration, "max_duration")

        result = (
            _core.inv_subordinator_fpt_raw_moment(
                self.alpha,
                (a, b),
                max_duration,
                time_step,
                order,
                particles,
            )
            if not center
            else _core.inv_subordinator_fpt_central_moment(
                self.alpha,
                (a, b),
                max_duration,
                time_step,
                order,
                particles,
            )
        )

        return result

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
        a, b = validate_domain(
            domain, process_name="InvSubordinator Occupation raw moment"
        )
        particles = validate_particles(particles)
        duration = validate_positive_float(duration, "duration")
        time_step = validate_positive_float(time_step, "time_step")

        result = (
            _core.inv_subordinator_occupation_time_raw_moment(
                self.alpha,
                (a, b),
                duration,
                time_step,
                order,
                particles,
            )
            if not center
            else _core.inv_subordinator_occupation_time_central_moment(
                self.alpha,
                (a, b),
                duration,
                time_step,
                order,
                particles,
            )
        )

        return result


class AsymmetricLevy:
    def __init__(
        self,
        alpha: real,
        beta: real,
        start_position: real = 0.0,
    ):
        """
        Initialize an Asymmetric Lévy process object.

        Args:
            alpha (real): Stability index of the Asymmetric Lévy process. Must be in (0, 2].
            beta (real): Skewness parameter. Must be in [-1, 1].
            start_position (real, optional): Starting position. Defaults to 0.0.
        """
        alpha = validate_positive_float(alpha, "alpha")
        beta = ensure_float(beta)
        start_position = ensure_float(start_position)

        if not (alpha <= 2):
            raise ValueError(f"alpha must be in the range (0, 2], got {alpha}")
        if not (-1 <= beta <= 1):
            raise ValueError(f"beta must be in the range [-1, 1], got {beta}")

        self.alpha = alpha
        self.beta = beta
        self.start_position = start_position

    def simulate(
        self, duration: real, time_step: float = 0.01
    ) -> tuple[Vector, Vector]:
        duration = validate_positive_float(duration, "duration")
        time_step = validate_positive_float(time_step, "time_step")

        return _core.asymmetric_levy_simulate(
            self.start_position,
            self.alpha,
            self.beta,
            duration,
            time_step,
        )

    def fpt(
        self,
        domain: tuple[real, real],
        time_step: float = 0.01,
        max_duration: real = 1000,
    ) -> float | None:
        a, b = validate_domain(domain, process_name="AsymmetricLevy FPT")
        time_step = validate_positive_float(time_step, "time_step")
        max_duration = validate_positive_float(max_duration, "max_duration")

        return _core.asymmetric_levy_fpt(
            self.start_position,
            self.alpha,
            self.beta,
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
        a, b = validate_domain(domain, process_name="AsymmetricLevy FPT raw moment")
        particles = validate_particles(particles)
        time_step = validate_positive_float(time_step, "time_step")
        max_duration = validate_positive_float(max_duration, "max_duration")

        result = (
            _core.asymmetric_levy_fpt_raw_moment(
                self.start_position,
                self.alpha,
                self.beta,
                (a, b),
                order,
                particles,
                max_duration,
                time_step,
            )
            if not center
            else _core.asymmetric_levy_fpt_central_moment(
                self.start_position,
                self.alpha,
                self.beta,
                (a, b),
                order,
                particles,
                max_duration,
                time_step,
            )
        )

        return result

    def occupation_time(
        self,
        domain: tuple[real, real],
        duration: real,
        time_step: float = 0.01,
    ) -> float:
        a, b = validate_domain(domain, process_name="AsymmetricLevy Occupation Time")
        duration = validate_positive_float(duration, "duration")
        time_step = validate_positive_float(time_step, "time_step")

        return _core.asymmetric_levy_occupation_time(
            self.start_position,
            self.alpha,
            self.beta,
            time_step,
            (a, b),
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
        a, b = validate_domain(
            domain, process_name="AsymmetricLevy Occupation raw moment"
        )
        particles = validate_particles(particles)
        duration = validate_positive_float(duration, "duration")
        time_step = validate_positive_float(time_step, "time_step")

        result = (
            _core.asymmetric_levy_occupation_time_raw_moment(
                self.start_position,
                self.alpha,
                self.beta,
                (a, b),
                duration,
                order,
                particles,
                time_step,
            )
            if not center
            else _core.asymmetric_levy_occupation_time_central_moment(
                self.start_position,
                self.alpha,
                self.beta,
                (a, b),
                duration,
                order,
                particles,
                time_step,
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

        return _core.asymmetric_levy_tamsd(
            self.start_position,
            self.alpha,
            self.beta,
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

        return _core.asymmetric_levy_eatamsd(
            self.start_position,
            self.alpha,
            self.beta,
            duration,
            delta,
            particles,
            time_step,
            quad_order,
        )
