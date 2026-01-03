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


class CTRW:
    def __init__(
        self,
        alpha: real = 1.0,
        beta: real = 2.0,
        start_position: real = 0.0,
    ):
        """
        Continuous Time Random Walk.

        Args:
            alpha (real, optional): Waiting time exponent (0, 1]. Defaults to 1.0.
            beta (real, optional): Jump length exponent (0, 2]. Defaults to 2.0.
            start_position (real, optional): Starting position. Defaults to 0.0.
        """
        self.alpha: float = validate_positive_float(alpha, "alpha")
        self.beta: float = validate_positive_float(beta, "beta")
        self.start_position: float = ensure_float(start_position)

        if not (self.alpha <= 1):
            raise ValueError(f"alpha must be in the range (0, 1], got {self.alpha}")
        if not (self.beta <= 2):
            raise ValueError(f"beta must be in the range (0, 2], got {self.beta}")

    def simulate(
        self,
        duration: real | None = None,
        num_step: int | None = None,
    ) -> tuple[Vector, Vector]:
        """
        Simulate the CTRW based on total duration.

        Args:
            duration (real, optional): Total duration of the simulation.
            num_step (int, optional): Number of steps in the simulation.

        Returns:
            tuple[np.ndarray, np.ndarray]: Times and positions of the CTRW.
        """
        if duration is not None:
            duration = validate_positive_float(duration, "duration")
            return _core.ctrw_simulate_duration(
                self.alpha,
                self.beta,
                self.start_position,
                duration,
            )

        if num_step is not None:
            num_step = validate_positive_integer(num_step, "num_step")
            return _core.ctrw_simulate_step(
                self.alpha,
                self.beta,
                self.start_position,
                num_step,
            )

        raise ValueError("Either duration or num_step must be provided")

    def moment(
        self,
        duration: real,
        order: int | float,
        central: bool = True,
        particles: int = 10_000,
    ) -> float:
        validate_bool(central, "central")
        validate_order(order)
        particles = validate_particles(particles)
        duration = validate_positive_float(duration, "duration")

        return (
            (
                _core.ctrw_raw_moment(
                    self.alpha,
                    self.beta,
                    self.start_position,
                    duration,
                    order,
                    particles,
                )
                if not central
                else _core.ctrw_central_moment(
                    self.alpha,
                    self.beta,
                    self.start_position,
                    duration,
                    order,
                    particles,
                )
            )
            if isinstance(order, int)
            else (
                _core.ctrw_frac_raw_moment(
                    self.alpha,
                    self.beta,
                    self.start_position,
                    duration,
                    order,
                    particles,
                )
                if not central
                else _core.ctrw_frac_central_moment(
                    self.alpha,
                    self.beta,
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
        """
        Calculate the first passage time of the CTRW.

        Args:
            domain (tuple[real, real]): Domain (a, b) for FPT. a must be less than b.
            max_duration (real, optional): Maximum duration to simulate for FPT. Defaults to 1000.

        Returns:
            Optional[float]: The FPT, or None if max_duration reached first.
        """
        a, b = validate_domain(domain, process_name="CTRW FPT")
        max_duration = validate_positive_float(max_duration, "max_duration")

        return _core.ctrw_fpt(
            self.alpha,
            self.beta,
            self.start_position,
            (a, b),
            max_duration,
        )

    def fpt_moment(
        self,
        domain: tuple[real, real],
        order: int,
        central: bool = True,
        particles: int = 10_000,
        max_duration: real = 1000,
    ) -> float | None:
        validate_bool(central, "central")
        validate_order(order)
        a, b = validate_domain(domain, process_name="CTRW FPT raw moment")
        particles = validate_particles(particles)
        max_duration = validate_positive_float(max_duration, "max_duration")

        result = (
            _core.ctrw_fpt_raw_moment(
                self.alpha,
                self.beta,
                self.start_position,
                (a, b),
                order,
                particles,
                max_duration,
            )
            if not central
            else _core.ctrw_fpt_central_moment(
                self.alpha,
                self.beta,
                self.start_position,
                (a, b),
                order,
                particles,
                max_duration,
            )
        )
        return result

    def occupation_time(
        self,
        domain: tuple[real, real],
        duration: real,
    ) -> float:
        """
        Calculate the occupation time of the CTRW in a domain.

        Args:
            domain (tuple[real, real]): Domain (a, b). a must be less than b.
            duration (real): Total simulation duration.

        Returns:
            float: Occupation time.
        """
        a, b = validate_domain(domain, process_name="CTRW Occupation Time")
        duration = validate_positive_float(duration, "duration")

        return _core.ctrw_occupation_time(
            self.alpha,
            self.beta,
            self.start_position,
            (a, b),
            duration,
        )

    def occupation_time_moment(
        self,
        domain: tuple[real, real],
        duration: real,
        order: int,
        central: bool = True,
        particles: int = 10_000,
    ) -> float:
        validate_bool(central, "central")
        validate_order(order)
        a, b = validate_domain(domain, process_name="CTRW Occupation raw moment")
        particles = validate_particles(particles)
        duration = validate_positive_float(duration, "duration")

        result = (
            _core.ctrw_occupation_time_raw_moment(
                self.alpha,
                self.beta,
                self.start_position,
                (a, b),
                duration,
                order,
                particles,
            )
            if not central
            else _core.ctrw_occupation_time_central_moment(
                self.alpha,
                self.beta,
                self.start_position,
                (a, b),
                duration,
                order,
                particles,
            )
        )
        return result

    def mean(self, duration: real, particles: int = 10_000) -> float:
        """
        Calculate the mean of the CTRW.

        Args:
            duration (real): The total duration of the simulation.
            particles (int, optional): Number of particles (positive integer) for ensemble averaging. Defaults to 10_000.

        Returns:
            float: The mean of the CTRW.
        """
        duration = validate_positive_float(duration, "duration (motion duration)")
        particles = validate_particles(particles)

        return _core.ctrw_mean(
            self.alpha,
            self.beta,
            self.start_position,
            duration,
            particles,
        )

    def msd(self, duration: real, particles: int = 10_000) -> float:
        """
        Calculate the mean squared displacement (MSD) of the CTRW.

        Args:
            duration (real): The total duration of the simulation.
            particles (int, optional): Number of particles (positive integer) for ensemble averaging. Defaults to 10_000.

        Returns:
            float: The mean squared displacement of the CTRW.
        """
        duration = validate_positive_float(duration, "duration (motion duration)")
        particles = validate_particles(particles)

        return _core.ctrw_msd(
            self.alpha,
            self.beta,
            self.start_position,
            duration,
            particles,
        )
