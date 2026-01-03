from typing import Callable

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


class Langevin:
    """
    Langevin equation:

    dx(t) = f(x(t), t) dt + g(x(t), t) dW(t), x(0) = x0

    The underlying implementation has been optimized with an efficient callback mechanism
    for interaction between Python functions and Rust code.

    Parameters
    ----------
    drift_func : Callable[[float, float], float]
        Drift function f(x, t).
    diffusion_func : Callable[[float, float], float]
        Diffusion function g(x, t).
    start_position : float, optional
        Initial position x0. Defaults to 0.0.
    """

    def __init__(
        self,
        drift_func: Callable[[float, float], float],
        diffusion_func: Callable[[float, float], float],
        start_position: real = 0.0,
    ) -> None:
        if not callable(drift_func):
            raise TypeError(
                f"drift_func must be a callable function, got {type(drift_func).__name__}"
            )
        if not callable(diffusion_func):
            raise TypeError(
                f"diffusion_func must be a callable function, got {type(diffusion_func).__name__}"
            )
        self.drift_func = drift_func
        self.diffusion_func = diffusion_func
        self.start_position = ensure_float(start_position)

    def simulate(self, duration: real, time_step: real) -> tuple[Vector, Vector]:
        """
        Simulate the Langevin process.

        Parameters
        ----------
        duration : real
            Simulation duration (must be positive).
        time_step : real
            Time step size (must be positive).

        Returns
        -------
        tuple[numpy.ndarray, numpy.ndarray]
            (time points array, position array)
        """
        duration = validate_positive_float(duration, "duration")
        time_step = validate_positive_float(time_step, "time_step")

        return _core.langevin_simulate(
            self.drift_func,
            self.diffusion_func,
            self.start_position,
            duration,
            time_step,
        )

    def moment(
        self,
        duration: real,
        order: int | float,
        central: bool = True,
        particles: int = 10_000,
        time_step: real = 0.01,
    ) -> float:
        """
        Calculate the moment of the Langevin process.

        Parameters
        ----------
        duration : real
            Simulation duration (must be positive).
        order : int | float
            Order of the moment (integer or float).
        particles : int
            Number of particles to simulate (must be positive).
        time_step : real
            Time step size (must be positive).

        Returns
        -------
        float
            Raw moment.
        """
        validate_bool(central, "central")
        validate_order(order)
        particles = validate_particles(particles)
        duration = validate_positive_float(duration, "duration")
        time_step = validate_positive_float(time_step, "time_step")

        return (
            (
                _core.langevin_raw_moment(
                    self.drift_func,
                    self.diffusion_func,
                    self.start_position,
                    duration,
                    order,
                    particles,
                    time_step,
                )
                if not central
                else _core.langevin_central_moment(
                    self.drift_func,
                    self.diffusion_func,
                    self.start_position,
                    duration,
                    order,
                    particles,
                    time_step,
                )
            )
            if isinstance(order, int)
            else (
                _core.langevin_frac_raw_moment(
                    self.drift_func,
                    self.diffusion_func,
                    self.start_position,
                    duration,
                    order,
                    particles,
                    time_step,
                )
                if not central
                else _core.langevin_frac_central_moment(
                    self.drift_func,
                    self.diffusion_func,
                    self.start_position,
                    duration,
                    order,
                    particles,
                    time_step,
                )
            )
        )

    def fpt(
        self,
        domain: tuple[real, real],
        time_step: float = 0.01,
        max_duration: real = 1000,
    ) -> float | None:
        a, b = validate_domain(domain, process_name="Langevin FPT")
        time_step = validate_positive_float(time_step, "time_step")
        max_duration = validate_positive_float(max_duration, "max_duration")

        return _core.langevin_fpt(
            self.drift_func,
            self.diffusion_func,
            self.start_position,
            (a, b),
            max_duration,
            time_step,
        )

    def fpt_moment(
        self,
        domain: tuple[real, real],
        order: int,
        central: bool = False,
        particles: int = 10_000,
        time_step: real = 0.01,
        max_duration: real = 1000,
    ) -> float | None:
        validate_bool(central, "central")
        validate_order(order)
        a, b = validate_domain(domain, process_name="Langevin FPT raw moment")
        particles = validate_particles(particles)
        time_step = validate_positive_float(time_step, "time_step")
        max_duration = validate_positive_float(max_duration, "max_duration")

        result = (
            _core.langevin_fpt_raw_moment(
                self.drift_func,
                self.diffusion_func,
                self.start_position,
                (a, b),
                max_duration,
                order,
                particles,
                time_step,
            )
            if not central
            else _core.langevin_fpt_central_moment(
                self.drift_func,
                self.diffusion_func,
                self.start_position,
                (a, b),
                max_duration,
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
        time_step: real = 0.01,
    ) -> float:
        a, b = validate_domain(domain, process_name="Langevin Occupation Time")
        duration = validate_positive_float(duration, "duration")
        time_step = validate_positive_float(time_step, "time_step")

        return _core.langevin_occupation_time(
            self.drift_func,
            self.diffusion_func,
            self.start_position,
            (a, b),
            duration,
            time_step,
        )

    def occupation_time_moment(
        self,
        domain: tuple[real, real],
        duration: real,
        order: int,
        central: bool = False,
        particles: int = 10_000,
        time_step: real = 0.01,
    ) -> float:
        validate_bool(central, "central")
        validate_order(order)
        a, b = validate_domain(domain, process_name="Langevin Occupation raw moment")
        particles = validate_particles(particles)
        duration = validate_positive_float(duration, "duration")
        time_step = validate_positive_float(time_step, "time_step")

        result = (
            _core.langevin_occupation_time_raw_moment(
                self.drift_func,
                self.diffusion_func,
                self.start_position,
                (a, b),
                duration,
                order,
                particles,
                time_step,
            )
            if not central
            else _core.langevin_occupation_time_central_moment(
                self.drift_func,
                self.diffusion_func,
                self.start_position,
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

        return _core.langevin_tamsd(
            self.drift_func,
            self.diffusion_func,
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
        duration = validate_positive_float(duration, "duration")
        delta = validate_positive_float(delta, "delta")
        particles = validate_particles(particles)
        time_step = validate_positive_float(time_step, "time_step")
        quad_order = validate_positive_integer(quad_order, "quad_order")

        return _core.langevin_eatamsd(
            self.drift_func,
            self.diffusion_func,
            self.start_position,
            duration,
            delta,
            particles,
            time_step,
            quad_order,
        )


class GeneralizedLangevin:
    """
    Generalized Langevin equation:

    dx(t) = f(x(t), t) dt + g(x(t), t) dL_alpha(t), x(0) = x0

    dL_alpha(t) is a Lévy stable noise source.

    Parameters
    ----------
    alpha : real
        Stability index of the stable noise (0, 2].
    drift_func : Callable[[float, float], float]
        Drift function f(x, t).
    diffusion_func : Callable[[float, float], float]
        Diffusion function g(x, t).
    start_position : real, optional
        Initial position x0. Defaults to 0.0.
    """

    def __init__(
        self,
        alpha: real,
        drift_func: Callable[[float, float], float],
        diffusion_func: Callable[[float, float], float],
        start_position: real = 0.0,
    ) -> None:
        if not callable(drift_func):
            raise TypeError(
                f"drift_func must be a callable function, got {type(drift_func).__name__}"
            )
        if not callable(diffusion_func):
            raise TypeError(
                f"diffusion_func must be a callable function, got {type(diffusion_func).__name__}"
            )

        start_position = ensure_float(start_position)
        alpha = validate_positive_float(alpha, "alpha")

        if not (alpha <= 2):
            raise ValueError(
                f"alpha (stability index) must be in the range (0, 2], got {alpha}"
            )

        self.drift_func = drift_func
        self.diffusion_func = diffusion_func
        self.start_position = start_position
        self.alpha = alpha

    def simulate(
        self, duration: real, time_step: float = 0.01
    ) -> tuple[Vector, Vector]:
        """
        Simulate the Generalized Langevin process.

        Parameters
        ----------
        duration : real
            Simulation duration (must be positive).
        time_step : real
            Time step size (must be positive).

        Returns
        -------
        tuple[numpy.ndarray, numpy.ndarray]
            (time points array, position array)
        """
        duration = validate_positive_float(duration, "duration")
        time_step = validate_positive_float(time_step, "time_step")

        return _core.generalized_langevin_simulate(
            self.drift_func,
            self.diffusion_func,
            self.start_position,
            self.alpha,
            duration,
            time_step,
        )

    def moment(
        self,
        duration: real,
        order: int | float,
        central: bool = True,
        particles: int = 10_000,
        time_step: real = 0.01,
    ) -> float:
        """
        Calculate the moment of the Generalized Langevin process.

        Parameters
        ----------
        duration : real
            Simulation duration (must be positive).
        order : int | float
            Order of the moment (integer or float).
        particles : int
            Number of particles (must be positive).
        time_step : real
            Time step size (must be positive).

        Returns
        -------
        float
            Raw moment.
        """
        validate_bool(central, "central")
        validate_order(order)
        particles = validate_particles(particles)
        duration = validate_positive_float(duration, "duration")
        time_step = validate_positive_float(time_step, "time_step")

        return (
            (
                _core.generalized_langevin_raw_moment(
                    self.drift_func,
                    self.diffusion_func,
                    self.start_position,
                    self.alpha,
                    duration,
                    order,
                    particles,
                    time_step,
                )
                if not central
                else _core.generalized_langevin_central_moment(
                    self.drift_func,
                    self.diffusion_func,
                    self.start_position,
                    self.alpha,
                    duration,
                    order,
                    particles,
                    time_step,
                )
            )
            if isinstance(order, int)
            else (
                _core.generalized_langevin_frac_raw_moment(
                    self.drift_func,
                    self.diffusion_func,
                    self.start_position,
                    self.alpha,
                    duration,
                    order,
                    particles,
                    time_step,
                )
                if not central
                else _core.generalized_langevin_frac_central_moment(
                    self.drift_func,
                    self.diffusion_func,
                    self.start_position,
                    self.alpha,
                    duration,
                    order,
                    particles,
                    time_step,
                )
            )
        )

    def fpt(
        self,
        domain: tuple[real, real],
        time_step: float = 0.01,
        max_duration: real = 1000,
    ) -> float | None:
        a, b = validate_domain(domain, process_name="GeneralizedLangevin FPT")
        time_step = validate_positive_float(time_step, "time_step")
        max_duration = validate_positive_float(max_duration, "max_duration")

        return _core.generalized_langevin_fpt(
            self.drift_func,
            self.diffusion_func,
            self.start_position,
            self.alpha,
            (a, b),
            max_duration,
            time_step,
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
        a, b = validate_domain(
            domain, process_name="GeneralizedLangevin FPT raw moment"
        )
        particles = validate_particles(particles)
        time_step = validate_positive_float(time_step, "time_step")
        max_duration = validate_positive_float(max_duration, "max_duration")

        result = (
            _core.generalized_langevin_fpt_raw_moment(
                self.drift_func,
                self.diffusion_func,
                self.start_position,
                self.alpha,
                (a, b),
                max_duration,
                order,
                particles,
                time_step,
            )
            if not central
            else _core.generalized_langevin_fpt_central_moment(
                self.drift_func,
                self.diffusion_func,
                self.start_position,
                self.alpha,
                (a, b),
                max_duration,
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
        time_step: real = 0.01,
    ) -> float:
        a, b = validate_domain(
            domain, process_name="GeneralizedLangevin Occupation Time"
        )
        duration = validate_positive_float(duration, "duration")
        time_step = validate_positive_float(time_step, "time_step")

        return _core.generalized_langevin_occupation_time(
            self.drift_func,
            self.diffusion_func,
            self.start_position,
            self.alpha,
            (a, b),
            duration,
            time_step,
        )

    def occupation_time_moment(
        self,
        domain: tuple[real, real],
        duration: real,
        order: int,
        central: bool = False,
        particles: int = 10_000,
        time_step: real = 0.01,
    ) -> float:
        validate_bool(central, "central")
        validate_order(order)
        a, b = validate_domain(
            domain, process_name="GeneralizedLangevin Occupation raw moment"
        )
        particles = validate_particles(particles)
        duration = validate_positive_float(duration, "duration")
        time_step = validate_positive_float(time_step, "time_step")

        result = (
            _core.generalized_langevin_occupation_time_raw_moment(
                self.drift_func,
                self.diffusion_func,
                self.start_position,
                self.alpha,
                (a, b),
                duration,
                order,
                particles,
                time_step,
            )
            if not central
            else _core.generalized_langevin_occupation_time_central_moment(
                self.drift_func,
                self.diffusion_func,
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

        return _core.generalized_langevin_tamsd(
            self.drift_func,
            self.diffusion_func,
            self.start_position,
            self.alpha,
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
        duration = validate_positive_float(duration, "duration")
        delta = validate_positive_float(delta, "delta")
        particles = validate_particles(particles)
        time_step = validate_positive_float(time_step, "time_step")
        quad_order = validate_positive_integer(quad_order, "quad_order")

        return _core.generalized_langevin_eatamsd(
            self.drift_func,
            self.diffusion_func,
            self.start_position,
            self.alpha,
            duration,
            delta,
            particles,
            time_step,
            quad_order,
        )


class SubordinatedLangevin:
    """
    Subordinated Langevin equation driven by a subordinator process for operational time.

    Parameters
    ----------
    alpha : real
        Alpha parameter for the subordinator (0, 1).
    drift_func : Callable[[float, float], float]
        Drift function f(x, u) where u is operational time.
    diffusion_func : Callable[[float, float], float]
        Diffusion function g(x, u) where u is operational time.
    start_position : real, optional
        Initial position x0. Defaults to 0.0.
    """

    def __init__(
        self,
        alpha: real,
        drift_func: Callable[[float, float], float],
        diffusion_func: Callable[[float, float], float],
        start_position: real = 0.0,
    ) -> None:
        if not callable(drift_func):
            raise TypeError(
                f"drift_func must be a callable function, got {type(drift_func).__name__}"
            )
        if not callable(diffusion_func):
            raise TypeError(
                f"diffusion_func must be a callable function, got {type(diffusion_func).__name__}"
            )
        start_position = ensure_float(start_position)
        alpha = validate_positive_float(alpha, "alpha")
        if not (alpha < 1):
            raise ValueError(
                f"subordinator_alpha must be in the range (0, 1), got {alpha}"
            )

        self.alpha = alpha
        self.drift_func = drift_func
        self.diffusion_func = diffusion_func
        self.start_position = start_position

    def simulate(
        self, duration: real, time_step: float = 0.01
    ) -> tuple[Vector, Vector]:
        """
        Simulate the Subordinated Langevin process.
        (Parameters, Raises, Returns are similar to Langevin.simulate)
        """
        duration = validate_positive_float(duration, "duration")
        time_step = validate_positive_float(time_step, "time_step")

        return _core.subordinated_langevin_simulate(
            self.drift_func,
            self.diffusion_func,
            self.start_position,
            self.alpha,
            duration,
            time_step,
        )

    def moment(
        self,
        duration: real,
        order: int | float,
        central: bool = True,
        particles: int = 10_000,
        time_step: float = 0.01,
    ) -> float:
        validate_bool(central, "central")
        validate_order(order)
        particles = validate_particles(particles)
        duration = validate_positive_float(duration, "duration")
        time_step = validate_positive_float(time_step, "time_step")

        return (
            (
                _core.subordinated_langevin_raw_moment(
                    self.drift_func,
                    self.diffusion_func,
                    self.start_position,
                    self.alpha,
                    duration,
                    order,
                    particles,
                    time_step,
                )
                if not central
                else _core.subordinated_langevin_central_moment(
                    self.drift_func,
                    self.diffusion_func,
                    self.start_position,
                    self.alpha,
                    duration,
                    order,
                    particles,
                    time_step,
                )
            )
            if isinstance(order, int)
            else (
                _core.subordinated_langevin_frac_raw_moment(
                    self.drift_func,
                    self.diffusion_func,
                    self.start_position,
                    self.alpha,
                    duration,
                    order,
                    particles,
                    time_step,
                )
                if not central
                else _core.subordinated_langevin_frac_central_moment(
                    self.drift_func,
                    self.diffusion_func,
                    self.start_position,
                    self.alpha,
                    duration,
                    order,
                    particles,
                    time_step,
                )
            )
        )

    def fpt(
        self,
        domain: tuple[real, real],
        max_duration: real = 1000,
        time_step: real = 0.01,
    ) -> float | None:  # No time_step here as per _core
        a, b = validate_domain(domain, process_name="SubordinatedLangevin FPT")
        max_duration = validate_positive_float(max_duration, "max_duration")
        time_step = validate_positive_float(time_step, "time_step")

        return _core.subordinated_langevin_fpt(
            self.drift_func,
            self.diffusion_func,
            self.start_position,
            self.alpha,
            (a, b),
            max_duration,
            time_step,
        )

    def fpt_moment(
        self,
        domain: tuple[real, real],
        order: int,
        central: bool = True,
        particles: int = 10_000,
        time_step: real = 0.01,
        max_duration: real = 1000,
    ) -> float | None:
        validate_bool(central, "central")
        validate_order(order)
        a, b = validate_domain(
            domain, process_name="SubordinatedLangevin FPT raw moment"
        )
        particles = validate_particles(particles)
        time_step = validate_positive_float(time_step, "time_step")
        max_duration = validate_positive_float(max_duration, "max_duration")

        result = (
            _core.subordinated_langevin_fpt_raw_moment(
                self.drift_func,
                self.diffusion_func,
                self.start_position,
                self.alpha,
                (a, b),
                max_duration,
                order,
                particles,
                time_step,
            )
            if not central
            else _core.subordinated_langevin_fpt_central_moment(
                self.drift_func,
                self.diffusion_func,
                self.start_position,
                self.alpha,
                (a, b),
                max_duration,
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
        a, b = validate_domain(
            domain, process_name="SubordinatedLangevin Occupation Time"
        )
        duration = validate_positive_float(duration, "duration")
        time_step = validate_positive_float(time_step, "time_step")

        return _core.subordinated_langevin_occupation_time(
            self.drift_func,
            self.diffusion_func,
            self.start_position,
            self.alpha,
            (a, b),
            duration,
            time_step,
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
        validate_bool(central, "central")
        validate_order(order)
        a, b = validate_domain(
            domain, process_name="SubordinatedLangevin Occupation raw moment"
        )
        particles = validate_particles(particles)
        duration = validate_positive_float(duration, "duration")
        time_step = validate_positive_float(time_step, "time_step")

        result = (
            _core.subordinated_langevin_occupation_time_raw_moment(
                self.drift_func,
                self.diffusion_func,
                self.start_position,
                self.alpha,
                (a, b),
                duration,
                order,
                particles,
                time_step,
            )
            if not central
            else _core.subordinated_langevin_occupation_time_central_moment(
                self.drift_func,
                self.diffusion_func,
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

        return _core.subordinated_langevin_tamsd(
            self.drift_func,
            self.diffusion_func,
            self.start_position,
            self.alpha,
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
        duration = validate_positive_float(duration, "duration")
        delta = validate_positive_float(delta, "delta")
        particles = validate_particles(particles)
        time_step = validate_positive_float(time_step, "time_step")
        quad_order = validate_positive_integer(quad_order, "quad_order")

        return _core.subordinated_langevin_eatamsd(
            self.drift_func,
            self.diffusion_func,
            self.start_position,
            self.alpha,
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
        Calculate the mean of the Langevin process.

        Args:
            duration (real): The total duration of the simulation.
            time_step (float, optional): Step size for the simulation. Defaults to 0.01.
            particles (int, optional): Number of particles (positive integer) for ensemble averaging. Defaults to 10_000.

        Returns:
            float: The mean of the Langevin process.
        """
        duration = validate_positive_float(duration, "duration (motion duration)")
        particles = validate_particles(particles)
        time_step = validate_positive_float(time_step, "time_step")

        return _core.langevin_mean(
            self.drift_func,
            self.diffusion_func,
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
        Calculate the mean squared displacement (MSD) of the Langevin process.

        Args:
            duration (real): The total duration of the simulation.
            time_step (float, optional): Step size for the simulation. Defaults to 0.01.
            particles (int, optional): Number of particles (positive integer) for ensemble averaging. Defaults to 10_000.

        Returns:
            float: The mean squared displacement of the Langevin process.
        """
        duration = validate_positive_float(duration, "duration (motion duration)")
        particles = validate_particles(particles)
        time_step = validate_positive_float(time_step, "time_step")

        return _core.langevin_msd(
            self.drift_func,
            self.diffusion_func,
            self.start_position,
            duration,
            time_step,
            particles,
        )
