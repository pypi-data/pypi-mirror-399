use crate::{
    XPyResult,
    simulation::{PyArrayPair, vec_to_pyarray},
};
use diffusionx::simulation::{continuous::OrnsteinUhlenbeck, prelude::*};
use pyo3::prelude::*;
#[cfg(feature = "stub_gen")]
use pyo3_stub_gen::derive::gen_stub_pyfunction;

/// Simulate Ornstein-Uhlenbeck process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn ou_simulate(
    py: Python<'_>,
    theta: f64,
    sigma: f64,
    start_position: f64,
    duration: f64,
    time_step: f64,
) -> XPyResult<PyArrayPair<'_>> {
    let ou = OrnsteinUhlenbeck::new(theta, sigma, start_position)?;
    let (times, positions) = ou.simulate(duration, time_step)?;
    Ok(vec_to_pyarray(py, times, positions))
}

/// Get the raw moment of Ornstein-Uhlenbeck process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn ou_raw_moment(
    theta: f64,
    sigma: f64,
    start_position: f64,
    duration: f64,
    time_step: f64,
    order: i32,
    particles: usize,
) -> XPyResult<f64> {
    let ou = OrnsteinUhlenbeck::new(theta, sigma, start_position)?;
    let result = ou.raw_moment(duration, order, particles, time_step)?;
    Ok(result)
}

/// Get the central moment of Ornstein-Uhlenbeck process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn ou_central_moment(
    theta: f64,
    sigma: f64,
    start_position: f64,
    duration: f64,
    time_step: f64,
    order: i32,
    particles: usize,
) -> XPyResult<f64> {
    let ou = OrnsteinUhlenbeck::new(theta, sigma, start_position)?;
    let result = ou.central_moment(duration, order, particles, time_step)?;
    Ok(result)
}

/// Get the fractional raw moment of Ornstein-Uhlenbeck process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn ou_frac_raw_moment(
    theta: f64,
    sigma: f64,
    start_position: f64,
    duration: f64,
    time_step: f64,
    order: f64,
    particles: usize,
) -> XPyResult<f64> {
    let ou = OrnsteinUhlenbeck::new(theta, sigma, start_position)?;
    let result = ou.frac_raw_moment(duration, order, particles, time_step)?;
    Ok(result)
}

/// Get the fractional central moment of Ornstein-Uhlenbeck process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn ou_frac_central_moment(
    theta: f64,
    sigma: f64,
    start_position: f64,
    duration: f64,
    time_step: f64,
    order: f64,
    particles: usize,
) -> XPyResult<f64> {
    let ou = OrnsteinUhlenbeck::new(theta, sigma, start_position)?;
    let result = ou.frac_central_moment(duration, order, particles, time_step)?;
    Ok(result)
}

/// Get the first passage time of Ornstein-Uhlenbeck process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn ou_fpt(
    theta: f64,
    sigma: f64,
    start_position: f64,
    time_step: f64,
    domain: (f64, f64),
    max_duration: f64,
) -> XPyResult<Option<f64>> {
    let ou = OrnsteinUhlenbeck::new(theta, sigma, start_position)?;
    let result = ou.fpt(domain, max_duration, time_step)?;
    Ok(result)
}

/// Get the raw moment of the first passage time of Ornstein-Uhlenbeck process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn ou_fpt_raw_moment(
    theta: f64,
    sigma: f64,
    start_position: f64,
    domain: (f64, f64),
    order: i32,
    particles: usize,
    time_step: f64,
    max_duration: f64,
) -> XPyResult<Option<f64>> {
    let ou = OrnsteinUhlenbeck::new(theta, sigma, start_position)?;
    let fpt = FirstPassageTime::new(&ou, domain)?;
    let result = fpt.raw_moment(order, particles, max_duration, time_step)?;
    Ok(result)
}

/// Get the central moment of the first passage time of Ornstein-Uhlenbeck process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn ou_fpt_central_moment(
    theta: f64,
    sigma: f64,
    start_position: f64,
    domain: (f64, f64),
    order: i32,
    particles: usize,
    time_step: f64,
    max_duration: f64,
) -> XPyResult<Option<f64>> {
    let ou = OrnsteinUhlenbeck::new(theta, sigma, start_position)?;
    let fpt = FirstPassageTime::new(&ou, domain)?;
    let result = fpt.central_moment(order, particles, max_duration, time_step)?;
    Ok(result)
}

/// Get the occupation time of Ornstein-Uhlenbeck process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn ou_occupation_time(
    theta: f64,
    sigma: f64,
    start_position: f64,
    domain: (f64, f64),
    time_step: f64,
    duration: f64,
) -> XPyResult<f64> {
    let ou = OrnsteinUhlenbeck::new(theta, sigma, start_position)?;
    let result = ou.occupation_time(domain, duration, time_step)?;
    Ok(result)
}

/// Get the raw moment of the occupation time of Ornstein-Uhlenbeck process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn ou_occupation_time_raw_moment(
    theta: f64,
    sigma: f64,
    start_position: f64,
    domain: (f64, f64),
    order: i32,
    particles: usize,
    time_step: f64,
    duration: f64,
) -> XPyResult<f64> {
    let ou = OrnsteinUhlenbeck::new(theta, sigma, start_position)?;
    let oc = OccupationTime::new(&ou, domain, duration)?;
    let result = oc.raw_moment(order, particles, time_step)?;
    Ok(result)
}

/// Get the central moment of the occupation time of Ornstein-Uhlenbeck process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn ou_occupation_time_central_moment(
    theta: f64,
    sigma: f64,
    start_position: f64,
    domain: (f64, f64),
    order: i32,
    particles: usize,
    time_step: f64,
    duration: f64,
) -> XPyResult<f64> {
    let ou = OrnsteinUhlenbeck::new(theta, sigma, start_position)?;
    let oc = OccupationTime::new(&ou, domain, duration)?;
    let result = oc.central_moment(order, particles, time_step)?;
    Ok(result)
}

/// Get the time-averaged mean squared displacement of Ornstein-Uhlenbeck process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn ou_tamsd(
    theta: f64,
    sigma: f64,
    start_position: f64,
    duration: f64,
    delta: f64,
    time_step: f64,
    quad_order: usize,
) -> XPyResult<f64> {
    let ou = OrnsteinUhlenbeck::new(theta, sigma, start_position)?;
    let result = ou.tamsd(duration, delta, time_step, quad_order)?;
    Ok(result)
}

/// Get the effective time-averaged mean squared displacement of Ornstein-Uhlenbeck process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn ou_eatamsd(
    theta: f64,
    sigma: f64,
    start_position: f64,
    duration: f64,
    delta: f64,
    particles: usize,
    time_step: f64,
    quad_order: usize,
) -> XPyResult<f64> {
    let ou = OrnsteinUhlenbeck::new(theta, sigma, start_position)?;
    let result = ou.eatamsd(duration, delta, particles, time_step, quad_order)?;
    Ok(result)
}

/// Get the mean of Ornstein-Uhlenbeck process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn ou_mean(
    theta: f64,
    sigma: f64,
    start_position: f64,
    duration: f64,
    particles: usize,
    time_step: f64,
) -> XPyResult<f64> {
    let ou = OrnsteinUhlenbeck::new(theta, sigma, start_position)?;
    let result = ou.mean(duration, particles, time_step)?;
    Ok(result)
}

/// Get the msd of Ornstein-Uhlenbeck process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn ou_msd(
    theta: f64,
    sigma: f64,
    start_position: f64,
    duration: f64,
    particles: usize,
    time_step: f64,
) -> XPyResult<f64> {
    let ou = OrnsteinUhlenbeck::new(theta, sigma, start_position)?;
    let result = ou.msd(duration, particles, time_step)?;
    Ok(result)
}
