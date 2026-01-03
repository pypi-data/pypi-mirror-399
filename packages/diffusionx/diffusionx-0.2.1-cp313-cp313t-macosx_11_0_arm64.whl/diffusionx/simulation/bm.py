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


class Bm:
    def __init__(
        self,
        start_position: real = 0.0,
        diffusion_coefficient: real = 0.5,
    ):
        """
        Initialize a Brownian motion object.

        Args:
            start_position (real, optional): Starting position of the Brownian motion. Defaults to 0.0.
            diffusion_coefficient (real, optional): Diffusion coefficient of the Brownian motion. Defaults to 0.5.
        """
        self.diffusion_coefficient: float = validate_positive_float(
            diffusion_coefficient, "diffusion_coefficient"
        )
        self.start_position: float = ensure_float(start_position)

    def simulate(
        self, duration: real, time_step: float = 0.01
    ) -> tuple[Vector, Vector]:
        """
        Simulate the Brownian motion.

        Args:
            duration (real): Total duration of the simulation.
            time_step (float, optional): Step size of the Brownian motion. Defaults to 0.01.

        Returns:
            tuple[np.ndarray, np.ndarray]: A tuple containing the times and positions of the Brownian motion.
        """
        duration = validate_positive_float(duration, "duration")
        time_step = validate_positive_float(time_step, "time_step")

        return _core.bm_simulate(
            self.start_position,
            self.diffusion_coefficient,
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
        Calculate the raw moment of the Brownian motion.

        Args:
            duration (real): Duration of the simulation for moment calculation.
            order (int | float): Order of the moment (integer or float).
            particles (int, optional): Number of particles (positive integer) for ensemble averaging. Defaults to 10_000.
            time_step (real, optional): Step size for the simulation. Defaults to 0.01.
            central (bool, optional): Whether to calculate the central moment. Defaults to True.

        Returns:
            float: The raw moment of the Brownian motion.
        """
        validate_bool(central, "central")
        validate_order(order)
        particles = validate_particles(particles)
        duration = validate_positive_float(duration, "duration")
        time_step = validate_positive_float(time_step, "time_step")

        return (
            (
                _core.bm_raw_moment(
                    self.start_position,
                    self.diffusion_coefficient,
                    duration,
                    time_step,
                    order,
                    particles,
                )
                if not central
                else _core.bm_central_moment(
                    self.start_position,
                    self.diffusion_coefficient,
                    duration,
                    time_step,
                    order,
                    particles,
                )
            )
            if isinstance(order, int)
            else (
                _core.bm_frac_raw_moment(
                    self.start_position,
                    self.diffusion_coefficient,
                    duration,
                    time_step,
                    order,
                    particles,
                )
                if not central
                else _core.bm_frac_central_moment(
                    self.start_position,
                    self.diffusion_coefficient,
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
        max_duration: real = 1000,
        time_step: float = 0.01,
    ) -> float | None:
        """
        Calculate the first passage time of the Brownian motion.

        Args:
            domain (tuple[real, real]): The domain (a, b) for FPT. a must be less than b.
            time_step (real, optional): Step size for the simulation. Defaults to 0.01.
            max_duration (real, optional): Maximum duration to simulate for FPT. Defaults to 1000.

        Returns:
            Optional[float]: The first passage time, or None if max_duration is reached before FPT.
        """
        a, b = validate_domain(domain, process_name="Bm FPT")
        time_step = validate_positive_float(time_step, "time_step")
        max_duration = validate_positive_float(max_duration, "max_duration")

        return _core.bm_fpt(
            self.start_position,
            self.diffusion_coefficient,
            time_step,
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
        time_step: float = 0.01,
    ) -> float | None:
        """
        Calculate the raw moment of the first passage time for Brownian motion.

        Args:
            domain (tuple[real, real]): The domain (a, b). a must be less than b.
            order (int): Order of the moment (non-negative integer).
            particles (int): Number of particles for ensemble average (positive integer).
            time_step (real, optional): Step size. Defaults to 0.01.
            max_duration (real, optional): Maximum duration. Defaults to 1000.
            central (bool, optional): Whether to calculate the central moment. Defaults to True.

        Returns:
            Optional[float]: The raw moment of FPT, or None if no passage for some particles.
        """
        validate_bool(central, "central")
        validate_order(order)
        a, b = validate_domain(domain, process_name="Bm FPT raw moment")
        particles = validate_particles(particles)
        time_step = validate_positive_float(time_step, "time_step")
        max_duration = validate_positive_float(max_duration, "max_duration")

        result = (
            _core.bm_fpt_raw_moment(
                self.start_position,
                self.diffusion_coefficient,
                (a, b),
                order,
                particles,
                time_step,
                max_duration,
            )
            if not central
            else _core.bm_fpt_central_moment(
                self.start_position,
                self.diffusion_coefficient,
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
        """
        Calculate the occupation time of the Brownian motion in a given domain.

        Args:
            domain (tuple[real, real]): The domain (a, b) for occupation time. a must be less than b.
            duration (real): The total duration of the simulation.
            time_step (real, optional): Step size for the simulation. Defaults to 0.01.

        Returns:
            float: The occupation time of the Brownian motion in the domain.
        """
        a, b = validate_domain(domain, process_name="Bm Occupation time")
        duration = validate_positive_float(duration, "duration")
        time_step = validate_positive_float(time_step, "time_step")

        return _core.bm_occupation_time(
            self.start_position,
            self.diffusion_coefficient,
            time_step,
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
        time_step: float = 0.01,
    ) -> float:
        """
        Calculate the raw moment of the occupation time for Brownian motion.

        Args:
            domain (tuple[real, real]): The domain (a, b). a must be less than b.
            order (int): Order of the moment (non-negative integer).
            particles (int, optional): Number of particles for ensemble average (positive integer). Defaults to 10_000.
            duration (real): Total duration of the simulation.
            time_step (real, optional): Step size. Defaults to 0.01.
            central (bool, optional): Whether to calculate the central moment. Defaults to True.

        Returns:
            float: The raw moment of occupation time.
        """
        validate_bool(central, "central")
        validate_order(order)
        a, b = validate_domain(domain, process_name="Bm Occupation raw moment")
        particles = validate_particles(particles)
        duration = validate_positive_float(duration, "duration")
        time_step = validate_positive_float(time_step, "time_step")

        result = (
            _core.bm_occupation_time_raw_moment(
                self.start_position,
                self.diffusion_coefficient,
                (a, b),
                order,
                particles,
                time_step,
                duration,
            )
            if not central
            else _core.bm_occupation_time_central_moment(
                self.start_position,
                self.diffusion_coefficient,
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
        Calculate the time-averaged mean-square displacement of the Brownian motion.

        Args:
            duration (real): Total duration of the simulation.
            delta (real): Time lag for the mean-square displacement.
            time_step (real, optional): Step size. Defaults to 0.01.
            quad_order (int, optional): Quadrature order. Defaults to 10.

        Returns:
            float: The time-averaged mean-square displacement.
        """
        duration = validate_positive_float(duration, "duration")
        delta = validate_positive_float(delta, "delta")
        time_step = validate_positive_float(time_step, "time_step")
        quad_order = validate_positive_integer(quad_order, "quad_order")

        return _core.bm_tamsd(
            self.start_position,
            self.diffusion_coefficient,
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
        Calculate the time-averaged mean-square displacement of the Brownian motion.

        Args:
            duration (real): Total duration of the simulation.
            delta (real): Time lag for the mean-square displacement.
            particles (int, optional): Number of particles for ensemble average (positive integer). Defaults to 10_000.
            time_step (real, optional): Step size. Defaults to 0.01.
            quad_order (int, optional): Quadrature order. Defaults to 10.

        Returns:
            float: The time-averaged mean-square displacement.
        """
        duration = validate_positive_float(duration, "duration")
        delta = validate_positive_float(delta, "delta")
        particles = validate_particles(particles)
        time_step = validate_positive_float(time_step, "time_step")
        quad_order = validate_positive_integer(quad_order, "quad_order")

        return _core.bm_eatamsd(
            self.start_position,
            self.diffusion_coefficient,
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
        Calculate the mean of the Brownian motion.

        Args:
            duration (real): The total duration of the simulation.
            time_step (real, optional): Step size for the simulation. Defaults to 0.01.
            particles (int, optional): Number of particles (positive integer) for ensemble averaging. Defaults to 10_000.

        Returns:
            float: The mean of the Brownian motion.
        """
        duration = validate_positive_float(duration, "duration (motion duration)")
        particles = validate_particles(particles)
        time_step = validate_positive_float(time_step, "time_step")

        return _core.bm_mean(
            self.start_position,
            self.diffusion_coefficient,
            duration,
            particles,
            time_step,
        )

    def msd(
        self, duration: real, time_step: float = 0.01, particles: int = 10_000
    ) -> float:
        """
        Calculate the mean squared displacement (MSD) of the Brownian motion.

        Args:
            duration (real): The total duration of the simulation.
            time_step (real, optional): Step size for the simulation. Defaults to 0.01.
            particles (int, optional): Number of particles (positive integer) for ensemble averaging. Defaults to 10_000.

        Returns:
            float: The mean squared displacement of the Brownian motion.
        """
        duration = validate_positive_float(duration, "duration (motion duration)")
        particles = validate_particles(particles)
        time_step = validate_positive_float(time_step, "time_step")

        return _core.bm_msd(
            self.start_position,
            self.diffusion_coefficient,
            duration,
            particles,
            time_step,
        )
