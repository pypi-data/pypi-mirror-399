from abc import ABC, abstractmethod
from typing import Annotated, Literal, Union

import numpy as np
import numpy.typing as npt

from diffusionx import _core
from .utils import (
    validate_bool,
    validate_particles,
    validate_positive_float,
    validate_positive_integer,
)

real = Union[int, float]
Vector = Annotated[npt.NDArray[np.float64], Literal["N"]]


class ContinuousProcess(ABC):
    @abstractmethod
    def start(self) -> real:
        """Return the starting value of the process."""
        pass

    @abstractmethod
    def simulate(
        self, duration: real, time_step: float = 0.01
    ) -> tuple[Vector, Vector]:
        """Simulate the continuous stochastic process.

        Args:
            duration (real): The total duration of the simulation.
            time_step (float): The time step for the simulation.

        Returns:
            tuple[Vector, Vector]: A tuple containing arrays for time points and process values.
        """
        pass

    def moment(
        self,
        duration: real,
        order: int,
        time_step: float = 0.01,
        central: bool = True,
        particles: int = 10_000,
    ) -> float:
        validate_bool(central, "central")
        duration = validate_positive_float(duration, "duration")
        time_step = validate_positive_float(time_step, "time_step")
        particles = validate_particles(particles)
        return _core.moment(
            self.simulate, central, order, duration, time_step, particles
        )

    def mean(
        self, duration: real, time_step: float = 0.01, particles: int = 10_000
    ) -> float:
        duration = validate_positive_float(duration, "duration")
        time_step = validate_positive_float(time_step, "time_step")
        particles = validate_particles(particles)
        return _core.mean(self.simulate, duration, time_step, particles)

    def msd(
        self, duration: real, time_step: float = 0.01, particles: int = 10_000
    ) -> float:
        duration = validate_positive_float(duration, "duration")
        time_step = validate_positive_float(time_step, "time_step")
        particles = validate_particles(particles)
        return _core.msd(self.simulate, duration, time_step, particles)

    def eatamsd(
        self,
        duration: real,
        delta: float,
        time_step: float = 0.01,
        quad_order: int = 5,
        particles: int = 10_000,
    ) -> float:
        duration = validate_positive_float(duration, "duration")
        delta = validate_positive_float(delta, "delta")
        time_step = validate_positive_float(time_step, "time_step")
        quad_order = validate_positive_integer(quad_order, "quad_order")
        particles = validate_particles(particles)
        return _core.eatamsd(
            self.simulate, duration, delta, particles, time_step, quad_order
        )

    def tamsd(
        self, duration: real, delta: float, time_step: float = 0.01, quad_order: int = 5
    ) -> float:
        duration = validate_positive_float(duration, "duration")
        delta = validate_positive_float(delta, "delta")
        time_step = validate_positive_float(time_step, "time_step")
        quad_order = validate_positive_integer(quad_order, "quad_order")
        return _core.tamsd(self.simulate, duration, delta, time_step, quad_order)

    # def fpt(
    #     self,
    #     domain: tuple[real, real],
    #     time_step: float = 0.01,
    #     max_duration: real = 100,
    # ) -> float | None:
    #     domain = validate_domain(domain, "poisson_fpt", self.__class__.__name__)
    #     time_step = validate_positive_float(time_step, "time_step")
    #     max_duration = validate_positive_float(max_duration, "max_duration")
    #     return _core.fpt(self, domain, max_duration, time_step)

    # def occupation_time(
    #     self,
    #     domain: tuple[real, real],
    #     duration: real,
    #     time_step: float = 0.01,
    # ) -> float:
    #     domain = validate_domain(domain, "poisson_fpt", self.__class__.__name__)
    #     time_step = validate_positive_float(time_step, "time_step")
    #     duration = validate_positive_float(duration, "duration")
    #     return _core.occupation_time(self, domain, duration, time_step)
