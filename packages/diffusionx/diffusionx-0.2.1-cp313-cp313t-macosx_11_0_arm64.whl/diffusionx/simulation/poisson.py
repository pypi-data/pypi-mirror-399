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


class Poisson:
    def __init__(
        self,
        lambda_: real = 1.0,
    ):
        """
        Initialize a Poisson process object.

        Args:
            lambda_ (real, optional): Rate parameter (lambda > 0) of the Poisson process. Defaults to 1.0.

        """
        lambda_ = validate_positive_float(lambda_, "lambda_")
        self.lambda_ = lambda_

    def simulate(self, duration: real) -> tuple[Vector, Vector]:
        """
        Simulate the Poisson process based on total duration.
        Args:
            duration (real): Total duration of the simulation (must be positive).

        Returns:
            tuple[Vector, Vector]: Times and event counts of the Poisson process.
        """
        duration = validate_positive_float(duration, "duration")
        return _core.poisson_simulate_duration(
            self.lambda_,
            duration,
        )

    def simulate_step(self, num_step: int) -> tuple[Vector, Vector]:
        """
        Simulate the Poisson process for a specified number of events (steps).

        Args:
            num_step (int): Number of events (steps) in the simulation (must be positive).

        Returns:
            tuple[Vector, Vector]: Times and event counts of the Poisson process.
        """
        num_step = validate_positive_integer(num_step, "num_step")
        return _core.poisson_simulate_step(
            self.lambda_,
            num_step,
        )

    def moment(
        self,
        duration: real,
        order: int | float,
        center: bool = False,
        particles: int = 10_000,
    ) -> float:
        """
        Calculate the moment of the Poisson process at a given duration.

        Args:
            duration (real): Duration of the process (must be positive).
            order (int | float): Order of the moment (integer or float).
            particles (int): Number of particles for ensemble average (must be positive).

        Returns:
            float: The moment of the Poisson process.
        """
        validate_bool(center, "center")
        validate_order(order)
        particles = validate_particles(particles)
        duration = validate_positive_float(duration, "duration")

        return (
            (
                _core.poisson_raw_moment(
                    self.lambda_,
                    duration,
                    order,
                    particles,
                )
                if not center
                else _core.poisson_central_moment(
                    self.lambda_,
                    duration,
                    order,
                    particles,
                )
            )
            if isinstance(order, int)
            else (
                _core.poisson_frac_raw_moment(
                    self.lambda_,
                    duration,
                    order,
                    particles,
                )
                if not center
                else _core.poisson_frac_central_moment(
                    self.lambda_,
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
        Calculate the first passage time for the Poisson process to reach a certain count/level.

        Args:
            domain (tuple[real, real]): Domain (start_count, target_count).     max_duration (real, optional): Maximum physical time to wait. Defaults to 1000.

        Returns:
            float | None: The first passage time (physical time), or None if max_duration is reached.
        """
        a, b = validate_domain(
            domain, domain_type="poisson_fpt", process_name="Poisson FPT"
        )
        max_duration = validate_positive_float(max_duration, "max_duration")

        return _core.poisson_fpt(
            self.lambda_,
            (a, b),
            max_duration,
        )

    def occupation_time(
        self,
        domain: tuple[real, real],
        duration: real,
    ) -> float:
        """
        Calculate the occupation time of the Poisson process (i.e., time spent where N(t) is within a given count range).

        Args:
            domain (tuple[real, real]): The count range [a,b]. a must be less than or equal to b.
            duration (real): The total physical time duration of the observation (must be positive).

        Returns:
            float: The total time N(t) spent in the count range [a,b].
        """
        a, b = validate_domain(
            domain,
            domain_type="poisson_occupation",
            process_name="Poisson Occupation Time",
        )
        duration = validate_positive_float(duration, "duration")

        return _core.poisson_occupation_time(
            self.lambda_,
            (a, b),
            duration,
        )

    def fpt_moment(
        self,
        domain: tuple[real, real],  # (start_count, target_count)
        order: int,
        center: bool = False,
        particles: int = 10_000,
        max_duration: real = 1000,
    ) -> float | None:
        validate_bool(center, "center")
        validate_order(order)
        a, b = validate_domain(
            domain, domain_type="poisson_fpt", process_name="Poisson FPT raw moment"
        )
        particles = validate_particles(particles)
        max_duration = validate_positive_float(max_duration, "max_duration")

        return (
            _core.poisson_fpt_raw_moment(
                self.lambda_,
                (a, b),
                max_duration,
                order,
                particles,
            )
            if not center
            else _core.poisson_fpt_central_moment(
                self.lambda_,
                (a, b),
                max_duration,
                order,
                particles,
            )
        )

    def occupation_time_moment(
        self,
        domain: tuple[real, real],  # (min_count, max_count)
        duration: real,
        order: int,
        center: bool = False,
        particles: int = 10_000,
    ) -> float:
        validate_bool(center, "center")
        validate_order(order)
        a, b = validate_domain(
            domain,
            process_name="Poisson Occupation raw moment",
        )
        particles = validate_particles(particles)
        duration = validate_positive_float(duration, "duration")

        return (
            _core.poisson_occupation_time_raw_moment(
                self.lambda_,
                (a, b),
                duration,
                order,
                particles,
            )
            if not center
            else _core.poisson_occupation_time_central_moment(
                self.lambda_,
                (a, b),
                duration,
                order,
                particles,
            )
        )

    def mean(self, duration: real, particles: int = 10_000) -> float:
        """
        Calculate the mean of the Poisson process.

        Args:
            duration (real): The total duration of the simulation.
            particles (int, optional): Number of particles (positive integer) for ensemble averaging. Defaults to 10_000.

        Returns:
            float: The mean of the Poisson process.
        """
        duration = validate_positive_float(duration, "duration (motion duration)")
        particles = validate_particles(particles)

        return _core.poisson_mean(
            self.lambda_,
            duration,
            particles,
        )

    def msd(
        self,
        duration: real,
        particles: int = 10_000,
    ) -> float:
        """
        Calculate the mean squared displacement (MSD) of the Poisson process.

        Args:
            duration (real): The total duration of the simulation.
            particles (int, optional): Number of particles (positive integer) for ensemble averaging. Defaults to 10_000.

        Returns:
            float: The mean squared displacement of the Poisson process.
        """
        duration = validate_positive_float(duration, "duration (motion duration)")
        particles = validate_particles(particles)

        return _core.poisson_msd(
            self.lambda_,
            duration,
            particles,
        )
