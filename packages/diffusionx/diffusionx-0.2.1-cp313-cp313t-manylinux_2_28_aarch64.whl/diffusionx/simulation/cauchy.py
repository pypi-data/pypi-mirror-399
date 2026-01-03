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


class Cauchy:
    def __init__(
        self,
        start_position: real = 0.0,
    ):
        """
        Initialize a Cauchy process object.

        Args:
            start_position (real, optional): Starting position. Defaults to 0.0.
        """
        self.start_position: float = ensure_float(start_position)

    def simulate(
        self,
        duration: real,
        time_step: float = 0.01,
    ) -> tuple[Vector, Vector]:
        """
        Simulate the Cauchy process.

        Args:
            duration (real): Total duration of the simulation.
            time_step (float, optional): Step size of the simulation. Defaults to 0.01.

        Returns:
            tuple[np.ndarray, np.ndarray]: A tuple containing the times and positions of the Cauchy process.
        """
        duration = validate_positive_float(duration, "duration")
        time_step = validate_positive_float(time_step, "time_step")

        return _core.cauchy_simulate(
            self.start_position,
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
        Calculate the raw moment of the Cauchy process.

        Args:
            duration (real): Duration of the simulation for moment calculation.
            order (int | float): Order of the moment (integer or float).
            particles (int, optional): Number of particles (positive integer) for ensemble averaging. Defaults to 10_000.
            time_step (real, optional): Step size for the simulation. Defaults to 0.01.
            central (bool, optional): Whether to calculate the central moment. Defaults to True.

        Returns:
            float: The raw moment of the Cauchy process.
        """
        validate_bool(central, "central")
        validate_order(order)
        particles = validate_particles(particles)
        duration = validate_positive_float(duration, "duration")
        time_step = validate_positive_float(time_step, "time_step")

        return (
            (
                _core.cauchy_raw_moment(
                    self.start_position,
                    duration,
                    time_step,
                    order,
                    particles,
                )
                if not central
                else _core.cauchy_central_moment(
                    self.start_position,
                    duration,
                    time_step,
                    order,
                    particles,
                )
            )
            if isinstance(order, int)
            else (
                _core.cauchy_frac_raw_moment(
                    self.start_position,
                    duration,
                    time_step,
                    order,
                    particles,
                )
                if not central
                else _core.cauchy_frac_central_moment(
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
        max_duration: real = 1000,
        time_step: float = 0.01,
    ) -> float | None:
        """
        Calculate the first passage time of the Cauchy process.

        Args:
            domain (tuple[real, real]): The domain (a, b) for FPT. a must be less than b.
            max_duration (real, optional): Maximum duration to simulate for FPT. Defaults to 1000.
            time_step (real, optional): Step size for the simulation. Defaults to 0.01.

        Returns:
            Optional[float]: The first passage time, or None if max_duration is reached before FPT.
        """
        a, b = validate_domain(domain, process_name="Cauchy FPT")
        time_step = validate_positive_float(time_step, "time_step")
        max_duration = validate_positive_float(max_duration, "max_duration")

        return _core.cauchy_fpt(
            self.start_position,
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
        Calculate the moment of the first passage time for the Cauchy process.

        Args:
            domain (tuple[real, real]): The domain (a, b). a must be less than b.
            order (int): Order of the moment (non-negative integer).
            particles (int): Number of particles for ensemble average (positive integer).
            time_step (real, optional): Step size. Defaults to 0.01.
            max_duration (real, optional): Maximum duration. Defaults to 1000.
            central (bool, optional): Whether to calculate the central moment. Defaults to True.

        Returns:
            float | None: The moment of FPT, or None if no passage for some particles.
        """
        validate_bool(central, "central")
        validate_order(order)
        a, b = validate_domain(domain, process_name="Cauchy FPT raw moment")
        particles = validate_particles(particles)
        time_step = validate_positive_float(time_step, "time_step")
        max_duration = validate_positive_float(max_duration, "max_duration")

        result = (
            _core.cauchy_fpt_raw_moment(
                self.start_position,
                (a, b),
                order,
                particles,
                time_step,
                max_duration,
            )
            if not central
            else _core.cauchy_fpt_central_moment(
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
        """
        Calculate the occupation time of the Cauchy process in a given domain.

        Args:
            domain (tuple[real, real]): The domain (a, b) for occupation time. a must be less than b.
            duration (real): The total duration of the simulation.
            time_step (real, optional): Step size for the simulation. Defaults to 0.01.

        Returns:
            float: The occupation time of the Cauchy process in the domain.
        """
        a, b = validate_domain(domain, process_name="Cauchy Occupation Time")
        duration = validate_positive_float(duration, "duration")
        time_step = validate_positive_float(time_step, "time_step")

        return _core.cauchy_occupation_time(
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
        central: bool = True,
        particles: int = 10_000,
        time_step: float = 0.01,
    ) -> float:
        """
        Calculate the moment of the occupation time of the Cauchy process in a given domain.

        Args:
            domain (tuple[real, real]): The domain (a, b) for occupation time. a must be less than b.
            duration (real): The total duration of the simulation.
            order (int): Order of the moment (non-negative integer).
            particles (int, optional): Number of particles (positive integer) for ensemble averaging. Defaults to 10_000.
            time_step (real, optional): Step size for the simulation. Defaults to 0.01.
            central (bool, optional): Whether to calculate the central moment. Defaults to True.

        Returns:
            float: The moment of the occupation time of the Cauchy process in the domain.
        """
        validate_bool(central, "central")
        validate_order(order)
        a, b = validate_domain(domain, process_name="Cauchy Occupation raw moment")
        particles = validate_particles(particles)
        duration = validate_positive_float(duration, "duration")
        time_step = validate_positive_float(time_step, "time_step")

        result = (
            _core.cauchy_occupation_time_raw_moment(
                self.start_position,
                (a, b),
                order,
                particles,
                time_step,
                duration,
            )
            if not central
            else _core.cauchy_occupation_time_central_moment(
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
        """
        Calculate the time-averaged mean squared displacement (TAMS) of the Cauchy process.

        Args:
            duration (real): The total duration of the simulation.
            delta (real): The time interval for TAMS calculation.
            time_step (real, optional): Step size for the simulation. Defaults to 0.01.
            quad_order (int, optional): Order of the quadrature for integration. Defaults to 10.

        Returns:
            float: The time-averaged mean squared displacement of the Cauchy process.
        """
        duration = validate_positive_float(duration, "duration")
        delta = validate_positive_float(delta, "delta")
        time_step = validate_positive_float(time_step, "time_step")
        quad_order = validate_positive_integer(quad_order, "quad_order")

        return _core.cauchy_tamsd(
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
        particles: int = 10_000,
        time_step: float = 0.01,
        quad_order: int = 10,
    ) -> float:
        """
        Calculate the ensemble-averaged time-averaged mean squared displacement (EATAMS) of the Cauchy process.

        Args:
            duration (real): The total duration of the simulation.
            delta (real): The time interval for EATAMS calculation.
            particles (int, optional): Number of particles (positive integer) for ensemble averaging. Defaults to 10_000.
            time_step (real, optional): Step size for the simulation. Defaults to 0.01.
            quad_order (int, optional): Order of the quadrature for integration. Defaults to 10.

        Returns:
            float: The ensemble-averaged time-averaged mean squared displacement of the Cauchy process.
        """
        duration = validate_positive_float(duration, "duration")
        delta = validate_positive_float(delta, "delta")
        particles = validate_particles(particles)
        time_step = validate_positive_float(time_step, "time_step")
        quad_order = validate_positive_integer(quad_order, "quad_order")

        return _core.cauchy_eatamsd(
            self.start_position,
            duration,
            delta,
            particles,
            time_step,
            quad_order,
        )


class AsymmetricCauchy:
    def __init__(
        self,
        beta: real = 0.0,
        start_position: real = 0.0,
    ):
        """
        Initialize an Asymmetric Cauchy process object.

        Args:
            beta (real, optional): Skewness parameter. Must be in [-1, 1]. Defaults to 0.0 (symmetric Cauchy).
            start_position (real, optional): Starting position. Defaults to 0.0.
        """
        beta = ensure_float(beta)
        start_position = ensure_float(start_position)
        if not (-1 <= beta <= 1):
            raise ValueError(
                f"beta (skewness) must be in the range [-1, 1], got {beta}"
            )

        self.start_position: float = start_position
        self.beta: float = beta

    def simulate(
        self, duration: real, time_step: float = 0.01
    ) -> tuple[Vector, Vector]:
        """
        Simulate the Asymmetric Cauchy process.

        Args:
            duration (real): Total duration of the simulation.
            time_step (float, optional): Step size of the simulation. Defaults to 0.01.

        Returns:
            tuple[np.ndarray, np.ndarray]: A tuple containing the times and positions of the Asymmetric Cauchy process.
        """
        duration = validate_positive_float(duration, "duration")
        time_step = validate_positive_float(time_step, "time_step")

        return _core.asymmetric_cauchy_simulate(
            self.start_position,
            self.beta,
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
        Calculate the moment of the Asymmetric Cauchy process.

        Args:
            duration (real): Total duration of the simulation.
            order (int): Order of the moment (non-negative integer).
            particles (int, optional): Number of particles (positive integer) for ensemble averaging. Defaults to 10_000.
            time_step (float, optional): Step size of the simulation. Defaults to 0.01.
            central (bool, optional): Whether to calculate the central moment. Defaults to True.

        Returns:
            float: The moment of the Asymmetric Cauchy process.
        """
        validate_bool(central, "central")
        validate_order(order)
        particles = validate_particles(particles)
        duration = validate_positive_float(duration, "duration")
        time_step = validate_positive_float(time_step, "time_step")

        return (
            (
                _core.asymmetric_cauchy_raw_moment(
                    self.start_position,
                    self.beta,
                    duration,
                    time_step,
                    order,
                    particles,
                )
                if not central
                else _core.asymmetric_cauchy_central_moment(
                    self.start_position,
                    self.beta,
                    duration,
                    time_step,
                    order,
                    particles,
                )
            )
            if isinstance(order, int)
            else (
                _core.asymmetric_cauchy_frac_raw_moment(
                    self.start_position,
                    self.beta,
                    duration,
                    time_step,
                    order,
                    particles,
                )
                if not central
                else _core.asymmetric_cauchy_frac_central_moment(
                    self.start_position,
                    self.beta,
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
        Calculate the first passage time of the Asymmetric Cauchy process.

        Args:
            domain (tuple[real, real]): The domain (a, b) for FPT. a must be less than b.
            max_duration (real, optional): Maximum duration to simulate for FPT. Defaults to 1000.
            time_step (real, optional): Step size for the simulation. Defaults to 0.01.

        Returns:
            Optional[float]: The first passage time, or None if max_duration is reached before FPT.
        """
        a, b = validate_domain(domain, process_name="AsymmetricCauchy FPT")
        time_step = validate_positive_float(time_step, "time_step")
        max_duration = validate_positive_float(max_duration, "max_duration")

        return _core.asymmetric_cauchy_fpt(
            self.start_position,
            self.beta,
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
        Calculate the raw moment of the first passage time for the Asymmetric Cauchy process.

        Args:
            domain (tuple[real, real]): The domain (a, b). a must be less than b.
            order (int | float): Order of the moment (integer or float).
            particles (int): Number of particles for ensemble average (positive integer).
            time_step (real, optional): Step size. Defaults to 0.01.
            max_duration (real, optional): Maximum duration. Defaults to 1000.
            central (bool, optional): Whether to calculate the central moment. Defaults to True.

        Returns:
            Optional[float]: The raw moment of FPT, or None if no passage for some particles.
        """
        validate_bool(central, "central")
        validate_order(order)
        a, b = validate_domain(domain, process_name="AsymmetricCauchy FPT raw moment")
        particles = validate_particles(particles)
        time_step = validate_positive_float(time_step, "time_step")
        max_duration = validate_positive_float(max_duration, "max_duration")

        result = (
            _core.asymmetric_cauchy_fpt_raw_moment(
                self.start_position,
                self.beta,
                (a, b),
                order,
                particles,
                time_step,
                max_duration,
            )
            if not central
            else _core.asymmetric_cauchy_fpt_central_moment(
                self.start_position,
                self.beta,
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
        Calculate the occupation time of the Asymmetric Cauchy process in a given domain.

        Args:
            domain (tuple[real, real]): The domain (a, b) for occupation time. a must be less than b.
            duration (real): The total duration of the simulation.
            time_step (real, optional): Step size for the simulation. Defaults to 0.01.

        Returns:
            float: The occupation time of the Asymmetric Cauchy process in the domain.
        """
        a, b = validate_domain(domain, process_name="AsymmetricCauchy Occupation Time")
        duration = validate_positive_float(duration, "duration")
        time_step = validate_positive_float(time_step, "time_step")

        return _core.asymmetric_cauchy_occupation_time(
            self.start_position,
            self.beta,
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
        Calculate the raw moment of the occupation time for the Asymmetric Cauchy process.

        Args:
            domain (tuple[real, real]): The domain (a, b). a must be less than b.
            duration (real): The total duration of the simulation.
            order (int): Order of the moment (non-negative integer).
            particles (int): Number of particles for ensemble average (positive integer).
            time_step (real, optional): Step size. Defaults to 0.01.
            central (bool, optional): Whether to calculate the central moment. Defaults to True.

        Returns:
            float: The raw moment of occupation time, or None if no passage for some particles.
        """
        validate_bool(central, "central")
        validate_order(order)
        a, b = validate_domain(
            domain, process_name="AsymmetricCauchy Occupation raw moment"
        )
        particles = validate_particles(particles)
        duration = validate_positive_float(duration, "duration")
        time_step = validate_positive_float(time_step, "time_step")

        result = (
            _core.asymmetric_cauchy_occupation_time_raw_moment(
                self.start_position,
                self.beta,
                (a, b),
                order,
                particles,
                time_step,
                duration,
            )
            if not central
            else _core.asymmetric_cauchy_occupation_time_central_moment(
                self.start_position,
                self.beta,
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
        Calculate the time-averaged mean squared displacement (TAMS) of the Asymmetric Cauchy process.

        Args:
            duration (real): The total duration of the simulation.
            delta (real): The time interval for TAMS calculation.
            time_step (real, optional): Step size. Defaults to 0.01.
            quad_order (int, optional): Order of the quadrature. Defaults to 10.

        Returns:
            float: The time-averaged mean squared displacement of the Asymmetric Cauchy process.
        """
        duration = validate_positive_float(duration, "duration")
        delta = validate_positive_float(delta, "delta")
        time_step = validate_positive_float(time_step, "time_step")
        quad_order = validate_positive_integer(quad_order, "quad_order")

        return _core.asymmetric_cauchy_tamsd(
            self.start_position,
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
        particles: int = 10_000,
        time_step: float = 0.01,
        quad_order: int = 10,
    ) -> float:
        """
        Calculate the ensemble-averaged time-averaged mean squared displacement (EATAMS) of the Asymmetric Cauchy process.

        Args:
            duration (real): The total duration of the simulation.
            delta (real): The time interval for EATAMS calculation.
            particles (int, optional): Number of particles for ensemble average (positive integer). Defaults to 10_000.
            time_step (real, optional): Step size. Defaults to 0.01.
            quad_order (int, optional): Order of the quadrature. Defaults to 10.

        Returns:
            float: The ensemble-averaged time-averaged mean squared displacement of the Asymmetric Cauchy process.
        """
        duration = validate_positive_float(duration, "duration")
        delta = validate_positive_float(delta, "delta")
        particles = validate_particles(particles)
        time_step = validate_positive_float(time_step, "time_step")
        quad_order = validate_positive_integer(quad_order, "quad_order")

        return _core.asymmetric_cauchy_eatamsd(
            self.start_position,
            self.beta,
            duration,
            delta,
            particles,
            time_step,
            quad_order,
        )
