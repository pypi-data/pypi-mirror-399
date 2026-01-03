use crate::{
    XPyResult,
    simulation::{PyArrayPair, vec_to_pyarray},
};
use diffusionx::simulation::{continuous::GeometricBm, prelude::*};
use pyo3::prelude::*;
#[cfg(feature = "stub_gen")]
use pyo3_stub_gen::derive::gen_stub_pyfunction;

/// Simulate Geometric Brownian Motion.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn gb_simulate(
    py: Python<'_>,
    start_position: f64,
    mu: f64,
    sigma: f64,
    duration: f64,
    time_step: f64,
) -> XPyResult<PyArrayPair<'_>> {
    let gb = GeometricBm::new(start_position, mu, sigma)?;
    let (times, positions) = gb.simulate(duration, time_step)?;
    Ok(vec_to_pyarray(py, times, positions))
}

/// Get the raw moment of Geometric Brownian Motion.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn gb_raw_moment(
    start_position: f64,
    mu: f64,
    sigma: f64,
    duration: f64,
    time_step: f64,
    order: i32,
    particles: usize,
) -> XPyResult<f64> {
    let gb = GeometricBm::new(start_position, mu, sigma)?;
    let result = gb.raw_moment(duration, order, particles, time_step)?;
    Ok(result)
}

/// Get the central moment of Geometric Brownian Motion.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn gb_central_moment(
    start_position: f64,
    mu: f64,
    sigma: f64,
    duration: f64,
    time_step: f64,
    order: i32,
    particles: usize,
) -> XPyResult<f64> {
    let gb = GeometricBm::new(start_position, mu, sigma)?;
    let result = gb.central_moment(duration, order, particles, time_step)?;
    Ok(result)
}

/// Get the fractional raw moment of Geometric Brownian Motion.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn gb_frac_raw_moment(
    start_position: f64,
    mu: f64,
    sigma: f64,
    duration: f64,
    time_step: f64,
    order: f64,
    particles: usize,
) -> XPyResult<f64> {
    let gb = GeometricBm::new(start_position, mu, sigma)?;
    let result = gb.frac_raw_moment(duration, order, particles, time_step)?;
    Ok(result)
}

/// Get the fractional central moment of Geometric Brownian Motion.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn gb_frac_central_moment(
    start_position: f64,
    mu: f64,
    sigma: f64,
    duration: f64,
    time_step: f64,
    order: f64,
    particles: usize,
) -> XPyResult<f64> {
    let gb = GeometricBm::new(start_position, mu, sigma)?;
    let result = gb.frac_central_moment(duration, order, particles, time_step)?;
    Ok(result)
}

/// Get the first passage time of Geometric Brownian Motion.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn gb_fpt(
    start_position: f64,
    mu: f64,
    sigma: f64,
    time_step: f64,
    domain: (f64, f64),
    max_duration: f64,
) -> XPyResult<Option<f64>> {
    let gb = GeometricBm::new(start_position, mu, sigma)?;
    let result = gb.fpt(domain, max_duration, time_step)?;
    Ok(result)
}

/// Get the raw moment of the first passage time of Geometric Brownian Motion.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn gb_fpt_raw_moment(
    start_position: f64,
    mu: f64,
    sigma: f64,
    domain: (f64, f64),
    order: i32,
    particles: usize,
    time_step: f64,
    max_duration: f64,
) -> XPyResult<Option<f64>> {
    let gb = GeometricBm::new(start_position, mu, sigma)?;
    let fpt = FirstPassageTime::new(&gb, domain)?;
    let result = fpt.raw_moment(order, particles, max_duration, time_step)?;
    Ok(result)
}

/// Get the central moment of the first passage time of Geometric Brownian Motion.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn gb_fpt_central_moment(
    start_position: f64,
    mu: f64,
    sigma: f64,
    domain: (f64, f64),
    order: i32,
    particles: usize,
    time_step: f64,
    max_duration: f64,
) -> XPyResult<Option<f64>> {
    let gb = GeometricBm::new(start_position, mu, sigma)?;
    let fpt = FirstPassageTime::new(&gb, domain)?;
    let result = fpt.central_moment(order, particles, max_duration, time_step)?;
    Ok(result)
}

/// Get the occupation time of Geometric Brownian Motion.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn gb_occupation_time(
    start_position: f64,
    mu: f64,
    sigma: f64,
    domain: (f64, f64),
    time_step: f64,
    duration: f64,
) -> XPyResult<f64> {
    let gb = GeometricBm::new(start_position, mu, sigma)?;
    let result = gb.occupation_time(domain, duration, time_step)?;
    Ok(result)
}

/// Get the raw moment of the occupation time of Geometric Brownian Motion.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn gb_occupation_time_raw_moment(
    start_position: f64,
    mu: f64,
    sigma: f64,
    domain: (f64, f64),
    order: i32,
    particles: usize,
    time_step: f64,
    duration: f64,
) -> XPyResult<f64> {
    let gb = GeometricBm::new(start_position, mu, sigma)?;
    let oc = OccupationTime::new(&gb, domain, duration)?;
    let result = oc.raw_moment(order, particles, time_step)?;
    Ok(result)
}

/// Get the central moment of the occupation time of Geometric Brownian Motion.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn gb_occupation_time_central_moment(
    start_position: f64,
    mu: f64,
    sigma: f64,
    domain: (f64, f64),
    order: i32,
    particles: usize,
    time_step: f64,
    duration: f64,
) -> XPyResult<f64> {
    let gb = GeometricBm::new(start_position, mu, sigma)?;
    let oc = OccupationTime::new(&gb, domain, duration)?;
    let result = oc.central_moment(order, particles, time_step)?;
    Ok(result)
}

/// Get the time-averaged mean squared displacement of Geometric Brownian Motion.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn gb_tamsd(
    start_position: f64,
    mu: f64,
    sigma: f64,
    duration: f64,
    delta: f64,
    time_step: f64,
    quad_order: usize,
) -> XPyResult<f64> {
    let gb = GeometricBm::new(start_position, mu, sigma)?;
    let result = gb.tamsd(duration, delta, time_step, quad_order)?;
    Ok(result)
}

/// Get the effective time-averaged mean squared displacement of Geometric Brownian Motion.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn gb_eatamsd(
    start_position: f64,
    mu: f64,
    sigma: f64,
    duration: f64,
    delta: f64,
    particles: usize,
    time_step: f64,
    quad_order: usize,
) -> XPyResult<f64> {
    let gb = GeometricBm::new(start_position, mu, sigma)?;
    let result = gb.eatamsd(duration, delta, particles, time_step, quad_order)?;
    Ok(result)
}

/// Get the mean of Geometric Brownian Motion.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn gb_mean(
    start_position: f64,
    mu: f64,
    sigma: f64,
    duration: f64,
    particles: usize,
    time_step: f64,
) -> XPyResult<f64> {
    let gb = GeometricBm::new(start_position, mu, sigma)?;
    let result = gb.mean(duration, particles, time_step)?;
    Ok(result)
}

/// Get the msd of Geometric Brownian Motion.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn gb_msd(
    start_position: f64,
    mu: f64,
    sigma: f64,
    duration: f64,
    particles: usize,
    time_step: f64,
) -> XPyResult<f64> {
    let gb = GeometricBm::new(start_position, mu, sigma)?;
    let result = gb.msd(duration, particles, time_step)?;
    Ok(result)
}
