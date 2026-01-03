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


class BrownianExcursion:
    def __init__(self):
        """
        Initialize a Brownian Excursion object.
        A Brownian excursion is a Brownian motion conditioned to be positive and to return to 0 at a specified duration.
        """

    def simulate(
        self, duration: real, time_step: float = 0.01
    ) -> tuple[Vector, Vector]:
        """
        Simulate the Brownian excursion.

        Args:
            duration (real): Total duration of the simulation.
            time_step (float, optional): Step size for the simulation. Defaults to 0.01.

        Returns:
            tuple[np.ndarray, np.ndarray]: A tuple containing the times and positions of the Brownian excursion.
        """
        duration = validate_positive_float(duration, "duration")
        time_step = validate_positive_float(time_step, "time_step")

        return _core.be_simulate(
            duration,
            time_step,
        )

    def moment(
        self,
        duration: real,
        order: int | float,
        particles: int = 10_000,
        time_step: float = 0.01,
        central: bool = True,
    ) -> float:
        """
        Calculate the moment of the Brownian excursion.

        Args:
            duration (real): Duration of the simulation for moment calculation.
            order (int | float): Order of the moment (integer or float).
            particles (int, optional): Number of particles (positive integer) for ensemble averaging. Defaults to 10_000.
            time_step (real, optional): Step size for the simulation. Defaults to 0.01.
            central (bool, optional): Whether to calculate the central moment. Defaults to True.

        Returns:
            float: The moment of the Brownian excursion.
        """
        validate_bool(central, "central")
        validate_order(order)
        particles = validate_particles(particles)
        duration = validate_positive_float(duration, "duration")
        time_step = validate_positive_float(time_step, "time_step")

        return (
            (
                _core.be_raw_moment(
                    duration,
                    time_step,
                    order,
                    particles,
                )
                if not central
                else _core.be_central_moment(
                    duration,
                    time_step,
                    order,
                    particles,
                )
            )
            if isinstance(order, int)
            else (
                _core.be_raw_moment(
                    duration,
                    time_step,
                    order,
                    particles,
                )
                if not central
                else _core.be_central_moment(
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
        """
        Calculate the first passage time of the Brownian excursion.

        Args:
            domain (tuple[real, real]): The domain (a, b). a must be less than b.
            time_step (real, optional): Step size. Defaults to 0.01.

        Returns:
            float | None: The first passage time, or None if max_duration is reached before FPT.
        """
        a, b = validate_domain(domain, process_name="Be FPT")
        time_step = validate_positive_float(time_step, "time_step")

        return _core.be_fpt(
            time_step,
            (a, b),
        )

    def fpt_moment(
        self,
        domain: tuple[real, real],
        order: int,
        central: bool = True,
        particles: int = 10_000,
        time_step: float = 0.01,
    ) -> float | None:
        """
        Calculate the moment of the first passage time for Brownian excursion.

        Args:
            domain (tuple[real, real]): The domain (a, b). a must be less than b.
            order (int): Order of the moment (non-negative integer).
            particles (int, optional): Number of particles (positive integer) for ensemble averaging. Defaults to 10_000.
            time_step (real, optional): Step size. Defaults to 0.01.
            central (bool, optional): Whether to calculate the central moment. Defaults to True.

        Returns:
            Optional[float]: The moment of FPT, or None if no passage for some particles.
        """
        validate_bool(central, "central")
        validate_order(order)
        a, b = validate_domain(domain, process_name="Brownian excursion FPT raw moment")
        particles = validate_particles(particles)
        time_step = validate_positive_float(time_step, "time_step")

        result = (
            _core.be_fpt_raw_moment(
                (a, b),
                order,
                particles,
                time_step,
            )
            if not central
            else _core.be_fpt_central_moment(
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
        duration: real,
        time_step: float = 0.01,
    ) -> float:
        """
        Calculate the occupation time of the Brownian excursion in a given domain.

        Args:
            domain (tuple[real, real]): The domain (a, b) for occupation time. a must be less than b.
            duration (real): The total duration of the simulation.
            time_step (real, optional): Step size for the simulation. Defaults to 0.01.

        Returns:
            float: The occupation time of the Brownian excursion.
        """
        a, b = validate_domain(
            domain, process_name="Brownian excursion Occupation Time"
        )
        duration = validate_positive_float(duration, "duration (excursion duration)")
        time_step = validate_positive_float(time_step, "time_step")

        return _core.be_occupation_time(
            (a, b),
            time_step,
            duration,
        )

    def occupation_time_moment(
        self,
        domain: tuple[real, real],
        duration: real,
        order: int,
        central: bool = True,
        particles: int = 10_000,
        time_step: float = 0.01,
    ) -> float:
        """
        Calculate the moment of the occupation time for Brownian excursion.

        Args:
            domain (tuple[real, real]): The domain (a, b). a must be less than b.
            duration (real): The total duration of the simulation.
            order (int): Order of the moment (non-negative integer).
            particles (int, optional): Number of particles (positive integer) for ensemble averaging. Defaults to 10_000.
            time_step (real, optional): Step size for the simulation. Defaults to 0.01.
            central (bool, optional): Whether to calculate the central moment. Defaults to True.

        Returns:
            float: The moment of occupation time.
        """
        validate_bool(central, "central")
        validate_order(order)
        a, b = validate_domain(domain, process_name="Be Occupation raw moment")
        particles = validate_particles(particles)
        duration = validate_positive_float(duration, "duration (excursion duration)")
        time_step = validate_positive_float(time_step, "time_step")

        result = (
            _core.be_occupation_time_raw_moment(
                (a, b),
                order,
                particles,
                time_step,
                duration,
            )
            if not central
            else _core.be_occupation_time_central_moment(
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
        """
        Calculate the time-averaged mean squared displacement (TAMSD) of the Brownian excursion.

        Args:
            duration (real): The total duration of the simulation.
            delta (real): The time interval for the TAMSD calculation.
            time_step (real, optional): Step size for the simulation. Defaults to 0.01.
            quad_order (int, optional): Order of the quadrature rule. Defaults to 10.

        Returns:
            float: The time-averaged mean squared displacement.
        """
        duration = validate_positive_float(duration, "duration (excursion duration)")
        delta = validate_positive_float(delta, "delta")
        time_step = validate_positive_float(time_step, "time_step")
        quad_order = validate_positive_integer(quad_order, "quad_order")

        return _core.be_tamsd(
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
        """
        Calculate the ensemble-averaged time-averaged mean squared displacement (EATAMSD) of the Brownian excursion.

        Args:
            duration (real): The total duration of the simulation.
            delta (real): The time interval for the EATAMSD calculation.
            particles (int, optional): Number of particles (positive integer) for ensemble averaging. Defaults to 10_000.
            time_step (real, optional): Step size for the simulation. Defaults to 0.01.
            quad_order (int, optional): Order of the quadrature rule. Defaults to 10.

        Returns:
            float: The ensemble-averaged time-averaged mean squared displacement.
        """
        duration = validate_positive_float(duration, "duration (excursion duration)")
        delta = validate_positive_float(delta, "delta")
        particles = validate_particles(particles)
        time_step = validate_positive_float(time_step, "time_step")
        quad_order = validate_positive_integer(quad_order, "quad_order")

        return _core.be_eatamsd(
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
        Calculate the mean of the Brownian excursion.

        Args:
            duration (real): The total duration of the simulation.
            time_step (real, optional): Step size for the simulation. Defaults to 0.01.
            particles (int, optional): Number of particles (positive integer) for ensemble averaging. Defaults to 10_000.

        Returns:
            float: The mean of the Brownian excursion.
        """
        duration = validate_positive_float(duration, "duration (excursion duration)")
        particles = validate_particles(particles)
        time_step = validate_positive_float(time_step, "time_step")

        return _core.be_mean(
            duration,
            particles,
            time_step,
        )

    def msd(
        self, duration: real, time_step: float = 0.01, particles: int = 10_000
    ) -> float:
        """
        Calculate the mean squared displacement (MSD) of the Brownian excursion.

        Args:
            duration (real): The total duration of the simulation.
            time_step (real, optional): Step size for the simulation. Defaults to 0.01.
            particles (int, optional): Number of particles (positive integer) for ensemble averaging. Defaults to 10_000.

        Returns:
            float: The mean squared displacement of the Brownian excursion.
        """
        duration = validate_positive_float(duration, "duration (excursion duration)")
        particles = validate_particles(particles)
        time_step = validate_positive_float(time_step, "time_step")

        return _core.be_msd(
            duration,
            particles,
            time_step,
        )
