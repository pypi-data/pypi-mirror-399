use crate::{
    XPyResult,
    simulation::{PyArrayPair, vec_to_pyarray},
};
use diffusionx::simulation::{continuous::LevyWalk, prelude::*};
use pyo3::prelude::*;
#[cfg(feature = "stub_gen")]
use pyo3_stub_gen::derive::gen_stub_pyfunction;

/// Simulate Levy walk.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn levy_walk_simulate(
    py: Python<'_>,
    alpha: f64,
    velocity: f64,
    start_position: f64,
    duration: f64,
) -> XPyResult<PyArrayPair<'_>> {
    let levy_walk = LevyWalk::new(alpha, velocity, start_position)?;
    let (times, positions) = levy_walk.simulate_with_duration(duration)?;
    Ok(vec_to_pyarray(py, times, positions))
}

/// Get the raw moment of Levy walk.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn levy_walk_raw_moment(
    alpha: f64,
    velocity: f64,
    start_position: f64,
    duration: f64,
    order: i32,
    particles: usize,
) -> XPyResult<f64> {
    let levy_walk = LevyWalk::new(alpha, velocity, start_position)?;
    let result = levy_walk.raw_moment(duration, order, particles, 0.1)?;
    Ok(result)
}

/// Get the central moment of Levy walk.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn levy_walk_central_moment(
    alpha: f64,
    velocity: f64,
    start_position: f64,
    duration: f64,
    order: i32,
    particles: usize,
) -> XPyResult<f64> {
    let levy_walk = LevyWalk::new(alpha, velocity, start_position)?;
    let result = levy_walk.central_moment(duration, order, particles, 0.1)?;
    Ok(result)
}

/// Get the fractional raw moment of Levy walk.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn levy_walk_frac_raw_moment(
    alpha: f64,
    velocity: f64,
    start_position: f64,
    duration: f64,
    order: f64,
    particles: usize,
) -> XPyResult<f64> {
    let levy_walk = LevyWalk::new(alpha, velocity, start_position)?;
    let result = levy_walk.frac_raw_moment(duration, order, particles, 0.1)?;
    Ok(result)
}

/// Get the fractional central moment of Levy walk.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn levy_walk_frac_central_moment(
    alpha: f64,
    velocity: f64,
    start_position: f64,
    duration: f64,
    order: f64,
    particles: usize,
) -> XPyResult<f64> {
    let levy_walk = LevyWalk::new(alpha, velocity, start_position)?;
    let result = levy_walk.frac_central_moment(duration, order, particles, 0.1)?;
    Ok(result)
}

/// Get the first passage time of Levy walk.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn levy_walk_fpt(
    alpha: f64,
    velocity: f64,
    start_position: f64,
    domain: (f64, f64),
    max_duration: f64,
) -> XPyResult<Option<f64>> {
    let levy_walk = LevyWalk::new(alpha, velocity, start_position)?;
    let result = levy_walk.fpt(domain, max_duration, 0.1)?;
    Ok(result)
}

/// Get the mean of Levy walk.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn levy_walk_mean(
    alpha: f64,
    velocity: f64,
    start_position: f64,
    duration: f64,
    particles: usize,
    time_step: f64,
) -> XPyResult<f64> {
    let levy_walk = LevyWalk::new(alpha, velocity, start_position)?;
    let result = levy_walk.mean(duration, particles, time_step)?;
    Ok(result)
}

/// Get the msd of Levy walk.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn levy_walk_msd(
    alpha: f64,
    velocity: f64,
    start_position: f64,
    duration: f64,
    particles: usize,
    time_step: f64,
) -> XPyResult<f64> {
    let levy_walk = LevyWalk::new(alpha, velocity, start_position)?;
    let result = levy_walk.msd(duration, particles, time_step)?;
    Ok(result)
}
