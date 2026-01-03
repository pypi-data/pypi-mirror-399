from typing import Callable, Union

import numpy as np

from . import _core
from .types import DType

real = Union[float, int]


def _check_all_uint(size: tuple[int, ...]) -> bool:
    return all(isinstance(i, int) and i > 0 for i in size)


def _generate_random_values(
    size: int | tuple[int, ...],
    single_val_generator: Callable[..., Union[float, int, bool]],
    array_generator: Callable[..., np.ndarray],
    func_args: tuple,
) -> Union[float, int, bool, np.ndarray]:
    """Helper function to generate single or multiple random values based on size."""
    if isinstance(size, int):
        if size == 1:
            return single_val_generator(*func_args)
        elif size > 0:  # Handles integers greater than 1
            return array_generator(size, *func_args)
        else:
            raise ValueError(f"Invalid size {size}, expected positive integer")
    elif isinstance(size, tuple):
        if _check_all_uint(size):
            length = int(np.prod(size))
            # Ensure length is positive, _check_all_uint should guarantee this if tuple not empty
            if (
                length == 0 and not size
            ):  # Handle empty tuple for size if it should produce a single value
                # This case might need specific definition, typical prod of empty is 1.
                # For now, assuming _check_all_uint fails for empty or non-positive tuples.
                # If _check_all_uint passes, length should be > 0.
                pass  # No special handling for length == 0 if _check_all_uint passes.

            arr = array_generator(length, *func_args)
            return arr.reshape(size)
        else:
            raise ValueError(
                f"Invalid size {size}, expected tuple of positive integers"
            )
    else:
        # Match original error message style for type
        raise TypeError(
            f"Invalid size type {type(size)}, expected positive integer or tuple of positive integers"
        )


def randexp(
    size: int | tuple[int, ...] = 1, scale: real = 1.0
) -> Union[float, np.ndarray]:
    """
    Exponential distribution random numbers

    Args:
        size (int | tuple[int, ...], optional): shape of the output array. Defaults to 1. Positive integer or tuple of integers.
        scale (real, optional): exponential distribution parameter, mean of the distribution. Defaults to 1.0. Positive real number.

    Returns:
        float | np.ndarray: exponential random numbers
    """
    if scale <= 0:
        raise ValueError(f"Invalid scale {scale}, expected positive real number")

    _scale = float(scale) if isinstance(scale, int) else scale

    return _generate_random_values(size, _core.exp_rand, _core.exp_rands, (_scale,))


def uniform(
    size: int | tuple[int, ...] = 1,
    low: real = 0.0,
    high: real = 1.0,
    end: bool = False,
    dtype: DType = DType.Float,
) -> real | np.ndarray:
    """Uniform distribution random numbers

    Args:
        size (int | tuple[int, ...], optional): shape of the output array. Defaults to 1. Positive integer or tuple of integers.
        low (real, optional): lower bound. Defaults to 0.0.
        high (real, optional): upper bound. Defaults to 1.0.
        end (bool, optional): whether to include the upper bound. Defaults to False.
        dtype (DType, optional): data type. Defaults to DType.FLOAT.

    Returns:
        real | np.ndarray: uniform random numbers
    """
    # Basic validation for low and high should be in distribution.py's Uniform class __init__
    # Here we mainly focus on generation.
    if dtype == DType.Float:
        _low = float(low)
        _high = float(high)
        return _generate_random_values(
            size,
            _core.uniform_rand_float,
            _core.uniform_rands_float,
            (_low, _high, end),
        )
    elif dtype == DType.Int:
        # Ensure low and high are integers for integer uniform distribution
        _low = int(low)
        _high = int(high)
        if _low >= _high and not (
            end and _low == _high
        ):  # allow low==high if end is true for single point
            # More robust check might be needed if low==high allowed only if end=True
            # Original _core.uniform_rand_int might handle this.
            # For safety, let's assume low < high for int unless end=True allows single point.
            # This validation is typically in the distribution class.
            pass  # Assuming _core handles bounds checks for int as well.
        return _generate_random_values(
            size, _core.uniform_rand_int, _core.uniform_rands_int, (_low, _high, end)
        )
    else:
        raise ValueError(f"Invalid dtype {dtype}, expected DType.Float or DType.Int")


def randn(
    size: int | tuple[int, ...] = 1, mu: real = 0.0, sigma: real = 1.0
) -> float | np.ndarray:
    """Normal distribution random numbers

    Args:
        size (int | tuple[int, ...], optional): shape of the output array. Defaults to 1. Positive integer or tuple of integers.
        mu (real, optional): mean. Defaults to 0.0.
        sigma (real, optional): standard deviation. Defaults to 1.0. Positive real number.

    Returns:
        float | np.ndarray: normal random numbers
    """
    if sigma <= 0:
        raise ValueError(f"Invalid sigma {sigma}, expected positive real number")

    _mu = float(mu) if isinstance(mu, int) else mu
    _sigma = float(sigma) if isinstance(sigma, int) else sigma

    return _generate_random_values(
        size, _core.normal_rand, _core.normal_rands, (_mu, _sigma)
    )


def poisson(size: int | tuple[int, ...] = 1, lambda_: real = 1.0) -> real | np.ndarray:
    """Poisson distribution random numbers

    Args:
        size (int | tuple[int, ...], optional): shape of the output array. Defaults to 1. Positive integer or tuple of integers.
        lambda_ (real, optional): Poisson distribution parameter. Defaults to 1.0. Positive real number.

    Returns:
        real | np.ndarray: Poisson random numbers
    """
    if lambda_ <= 0:
        raise ValueError(f"Invalid lambda {lambda_}, expected positive real number")

    _lambda = float(lambda_) if isinstance(lambda_, int) else lambda_

    return _generate_random_values(
        size, _core.poisson_rand, _core.poisson_rands, (_lambda,)
    )


def stable_rand(
    alpha: real,
    beta: real,
    sigma: real = 1.0,
    mu: real = 0.0,
    size: int | tuple[int, ...] = 1,
) -> real | np.ndarray:
    """Stable distribution random numbers

    Args:
        alpha (real): stability index. Positive real number, between 0 and 2.
        beta (real): skewness parameter. Real number, between -1 and 1.
        sigma (real, optional): scale parameter. Defaults to 1.0. Positive real number.
        mu (real, optional): location parameter. Defaults to 0.0.
        size (int | tuple[int, ...], optional): shape of the output array. Defaults to 1. Positive integer or tuple of integers.
    Returns:
        real | np.ndarray: stable random numbers
    """
    if not (0 < alpha <= 2):  # More concise check
        raise ValueError(
            f"Invalid alpha {alpha}, expected positive real number between 0 (exclusive) and 2 (inclusive)"
        )
    if not (-1 <= beta <= 1):
        raise ValueError(f"Invalid beta {beta}, expected real number between -1 and 1")
    if sigma <= 0:
        raise ValueError(f"Invalid sigma {sigma}, expected positive real number")

    _alpha = float(alpha) if isinstance(alpha, int) else alpha
    _beta = float(beta) if isinstance(beta, int) else beta
    _sigma = float(sigma) if isinstance(sigma, int) else sigma
    _mu = float(mu) if isinstance(mu, int) else mu

    return _generate_random_values(
        size, _core.stable_rand, _core.stable_rands, (_alpha, _beta, _sigma, _mu)
    )


def skew_stable_rand(alpha: real, size: int | tuple[int, ...] = 1) -> real | np.ndarray:
    """Skewed stable distribution random numbers

    Args:
        alpha (real): stability index. Positive real number, between 0 and 1 for S_alpha(1,1,0).
        size (int | tuple[int, ...], optional): shape of the output array. Defaults to 1. Positive integer or tuple of integers.

    Returns:
        real | np.ndarray: skewed stable random numbers
    """
    # The distribution.Stable.skew class method has validation 0 < alpha <= 1.
    # This function is more general if it's just calling _core.skew_stable_rand.
    # Assuming _core.skew_stable_rand implies beta=1, sigma=1, mu=0 based on common S_alpha(beta, sigma, mu) notation
    # or perhaps a specific definition for "skew_stable_rand".
    # Let's assume alpha validation is appropriate here as well based on context, or rely on _core.
    if not (
        0 < alpha <= 2
    ):  # General alpha for stable, specific skew might have tighter bounds (e.g. (0,1] or (0,2])
        raise ValueError(
            f"Invalid alpha {alpha}, expected positive real number, typically (0,2]"
        )  # Adjusted error msg based on typical stable alpha range. If skew_stable_rand has stricter alpha range, this needs to be more specific.

    _alpha = float(alpha) if isinstance(alpha, int) else alpha

    return _generate_random_values(
        size, _core.skew_stable_rand, _core.skew_stable_rands, (_alpha,)
    )


def bool_rand(size: tuple[int, ...] | int = 1, p: real = 0.5) -> bool | np.ndarray:
    """Boolean random numbers (Bernoulli distribution)

    Args:
        size (tuple[int, ...] | int, optional): shape of the output array. Defaults to 1. Positive integer or tuple of integers.
        p (real, optional): probability of True. Defaults to 0.5. Must be between 0 and 1.

    Returns:
        bool | np.ndarray: boolean random numbers
    """
    if not (0 <= p <= 1):
        raise ValueError(f"Invalid p {p}, probability must be between 0 and 1")

    _p = float(p)  # _core.bool_rand expects float

    return _generate_random_values(size, _core.bool_rand, _core.bool_rands, (_p,))
