use crate::{
    XPyResult,
    simulation::{PyArrayPair, vec_to_pyarray},
};
use diffusionx::simulation::{
    continuous::{AsymmetricLevy, Levy},
    prelude::*,
};
use pyo3::prelude::*;
#[cfg(feature = "stub_gen")]
use pyo3_stub_gen::derive::gen_stub_pyfunction;

/// Simulate Levy process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn levy_simulate(
    py: Python<'_>,
    start_position: f64,
    alpha: f64,
    duration: f64,
    time_step: f64,
) -> XPyResult<PyArrayPair<'_>> {
    let levy = Levy::new(start_position, alpha)?;
    let (times, positions) = levy.simulate(duration, time_step)?;
    Ok(vec_to_pyarray(py, times, positions))
}

/// Get the first passage time of Levy process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn levy_fpt(
    start_position: f64,
    alpha: f64,
    time_step: f64,
    domain: (f64, f64),
    max_duration: f64,
) -> XPyResult<Option<f64>> {
    let levy = Levy::new(start_position, alpha)?;
    let result = levy.fpt(domain, max_duration, time_step)?;
    Ok(result)
}

/// Get the raw moment of the first passage time of Levy process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn levy_fpt_raw_moment(
    start_position: f64,
    alpha: f64,
    domain: (f64, f64),
    order: i32,
    particles: usize,
    max_duration: f64,
    time_step: f64,
) -> XPyResult<Option<f64>> {
    let levy = Levy::new(start_position, alpha)?;
    let fpt = FirstPassageTime::new(&levy, domain)?;
    let result = fpt.raw_moment(order, particles, max_duration, time_step)?;
    Ok(result)
}

/// Get the central moment of the first passage time of Levy process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn levy_fpt_central_moment(
    start_position: f64,
    alpha: f64,
    domain: (f64, f64),
    order: i32,
    particles: usize,
    max_duration: f64,
    time_step: f64,
) -> XPyResult<Option<f64>> {
    let levy = Levy::new(start_position, alpha)?;
    let fpt = FirstPassageTime::new(&levy, domain)?;
    let result = fpt.central_moment(order, particles, max_duration, time_step)?;
    Ok(result)
}

/// Get the occupation time of Levy process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn levy_occupation_time(
    start_position: f64,
    alpha: f64,
    time_step: f64,
    domain: (f64, f64),
    duration: f64,
) -> XPyResult<f64> {
    let levy = Levy::new(start_position, alpha)?;
    let result = levy.occupation_time(domain, duration, time_step)?;
    Ok(result)
}

/// Get the raw moment of the occupation time of Levy process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn levy_occupation_time_raw_moment(
    start_position: f64,
    alpha: f64,
    domain: (f64, f64),
    duration: f64,
    order: i32,
    particles: usize,
    time_step: f64,
) -> XPyResult<f64> {
    let levy = Levy::new(start_position, alpha)?;
    let oc = OccupationTime::new(&levy, domain, duration)?;
    let result = oc.raw_moment(order, particles, time_step)?;
    Ok(result)
}

/// Get the central moment of the occupation time of Levy process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn levy_occupation_time_central_moment(
    start_position: f64,
    alpha: f64,
    domain: (f64, f64),
    duration: f64,
    order: i32,
    particles: usize,
    time_step: f64,
) -> XPyResult<f64> {
    let levy = Levy::new(start_position, alpha)?;
    let oc = OccupationTime::new(&levy, domain, duration)?;
    let result = oc.central_moment(order, particles, time_step)?;
    Ok(result)
}

/// Get the time-averaged mean squared displacement of Levy process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn levy_tamsd(
    start_position: f64,
    alpha: f64,
    duration: f64,
    delta: f64,
    time_step: f64,
    quad_order: usize,
) -> XPyResult<f64> {
    let levy = Levy::new(start_position, alpha)?;
    let result = levy.tamsd(duration, delta, time_step, quad_order)?;
    Ok(result)
}

/// Get the effective time-averaged mean squared displacement of Levy process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn levy_eatamsd(
    start_position: f64,
    alpha: f64,
    duration: f64,
    delta: f64,
    particles: usize,
    time_step: f64,
    quad_order: usize,
) -> XPyResult<f64> {
    let levy = Levy::new(start_position, alpha)?;
    let result = levy.eatamsd(duration, delta, particles, time_step, quad_order)?;
    Ok(result)
}

/// Get the raw moment of Levy process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn levy_raw_moment(
    start_position: f64,
    alpha: f64,
    duration: f64,
    time_step: f64,
    order: i32,
    particles: usize,
) -> XPyResult<f64> {
    let levy = Levy::new(start_position, alpha)?;
    let result = levy.raw_moment(duration, order, particles, time_step)?;
    Ok(result)
}

/// Get the central moment of Levy process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn levy_central_moment(
    start_position: f64,
    alpha: f64,
    duration: f64,
    time_step: f64,
    order: i32,
    particles: usize,
) -> XPyResult<f64> {
    let levy = Levy::new(start_position, alpha)?;
    let result = levy.central_moment(duration, order, particles, time_step)?;
    Ok(result)
}

/// Get the fractional raw moment of Levy process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn levy_frac_raw_moment(
    start_position: f64,
    alpha: f64,
    duration: f64,
    time_step: f64,
    order: f64,
    particles: usize,
) -> XPyResult<f64> {
    let levy = Levy::new(start_position, alpha)?;
    let result = levy.frac_raw_moment(duration, order, particles, time_step)?;
    Ok(result)
}

/// Get the fractional central moment of Levy process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn levy_frac_central_moment(
    start_position: f64,
    alpha: f64,
    duration: f64,
    time_step: f64,
    order: f64,
    particles: usize,
) -> XPyResult<f64> {
    let levy = Levy::new(start_position, alpha)?;
    let result = levy.frac_central_moment(duration, order, particles, time_step)?;
    Ok(result)
}

/// Simulate AsymmetricLevy process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn asymmetric_levy_simulate(
    py: Python<'_>,
    start_position: f64,
    alpha: f64,
    beta: f64,
    duration: f64,
    time_step: f64,
) -> XPyResult<PyArrayPair<'_>> {
    let levy = AsymmetricLevy::new(start_position, alpha, beta)?;
    let (times, positions) = levy.simulate(duration, time_step)?;
    Ok(vec_to_pyarray(py, times, positions))
}

/// Get the first passage time of AsymmetricLevy process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn asymmetric_levy_fpt(
    start_position: f64,
    alpha: f64,
    beta: f64,
    time_step: f64,
    domain: (f64, f64),
    max_duration: f64,
) -> XPyResult<Option<f64>> {
    let levy = AsymmetricLevy::new(start_position, alpha, beta)?;
    let result = levy.fpt(domain, max_duration, time_step)?;
    Ok(result)
}

/// Get the raw moment of the first passage time of AsymmetricLevy process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn asymmetric_levy_fpt_raw_moment(
    start_position: f64,
    alpha: f64,
    beta: f64,
    domain: (f64, f64),
    order: i32,
    particles: usize,
    max_duration: f64,
    time_step: f64,
) -> XPyResult<Option<f64>> {
    let levy = AsymmetricLevy::new(start_position, alpha, beta)?;
    let fpt = FirstPassageTime::new(&levy, domain)?;
    let result = fpt.raw_moment(order, particles, max_duration, time_step)?;
    Ok(result)
}

/// Get the central moment of the first passage time of AsymmetricLevy process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn asymmetric_levy_fpt_central_moment(
    start_position: f64,
    alpha: f64,
    beta: f64,
    domain: (f64, f64),
    order: i32,
    particles: usize,
    max_duration: f64,
    time_step: f64,
) -> XPyResult<Option<f64>> {
    let levy = AsymmetricLevy::new(start_position, alpha, beta)?;
    let fpt = FirstPassageTime::new(&levy, domain)?;
    let result = fpt.central_moment(order, particles, max_duration, time_step)?;
    Ok(result)
}

/// Get the occupation time of AsymmetricLevy process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn asymmetric_levy_occupation_time(
    start_position: f64,
    alpha: f64,
    beta: f64,
    time_step: f64,
    domain: (f64, f64),
    duration: f64,
) -> XPyResult<f64> {
    let levy = AsymmetricLevy::new(start_position, alpha, beta)?;
    let result = levy.occupation_time(domain, duration, time_step)?;
    Ok(result)
}

/// Get the raw moment of the occupation time of AsymmetricLevy process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn asymmetric_levy_occupation_time_raw_moment(
    start_position: f64,
    alpha: f64,
    beta: f64,
    domain: (f64, f64),
    duration: f64,
    order: i32,
    particles: usize,
    time_step: f64,
) -> XPyResult<f64> {
    let levy = AsymmetricLevy::new(start_position, alpha, beta)?;
    let oc = OccupationTime::new(&levy, domain, duration)?;
    let result = oc.raw_moment(order, particles, time_step)?;
    Ok(result)
}

/// Get the central moment of the occupation time of AsymmetricLevy process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn asymmetric_levy_occupation_time_central_moment(
    start_position: f64,
    alpha: f64,
    beta: f64,
    domain: (f64, f64),
    duration: f64,
    order: i32,
    particles: usize,
    time_step: f64,
) -> XPyResult<f64> {
    let levy = AsymmetricLevy::new(start_position, alpha, beta)?;
    let oc = OccupationTime::new(&levy, domain, duration)?;
    let result = oc.central_moment(order, particles, time_step)?;
    Ok(result)
}

/// Get the time-averaged mean squared displacement of AsymmetricLevy process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn asymmetric_levy_tamsd(
    start_position: f64,
    alpha: f64,
    beta: f64,
    duration: f64,
    delta: f64,
    time_step: f64,
    quad_order: usize,
) -> XPyResult<f64> {
    let levy = AsymmetricLevy::new(start_position, alpha, beta)?;
    let result = levy.tamsd(duration, delta, time_step, quad_order)?;
    Ok(result)
}

/// Get the effective time-averaged mean squared displacement of AsymmetricLevy process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn asymmetric_levy_eatamsd(
    start_position: f64,
    alpha: f64,
    beta: f64,
    duration: f64,
    delta: f64,
    particles: usize,
    time_step: f64,
    quad_order: usize,
) -> XPyResult<f64> {
    let levy = AsymmetricLevy::new(start_position, alpha, beta)?;
    let result = levy.eatamsd(duration, delta, particles, time_step, quad_order)?;
    Ok(result)
}

/// Get the raw moment of asymmetric Levy process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn asymmetric_levy_raw_moment(
    start_position: f64,
    alpha: f64,
    beta: f64,
    duration: f64,
    time_step: f64,
    order: i32,
    particles: usize,
) -> XPyResult<f64> {
    let levy = AsymmetricLevy::new(start_position, alpha, beta)?;
    let result = levy.raw_moment(duration, order, particles, time_step)?;
    Ok(result)
}

/// Get the central moment of asymmetric Levy process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn asymmetric_levy_central_moment(
    start_position: f64,
    alpha: f64,
    beta: f64,
    duration: f64,
    time_step: f64,
    order: i32,
    particles: usize,
) -> XPyResult<f64> {
    let levy = AsymmetricLevy::new(start_position, alpha, beta)?;
    let result = levy.central_moment(duration, order, particles, time_step)?;
    Ok(result)
}

/// Get the fractional raw moment of asymmetric Levy process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn asymmetric_levy_frac_raw_moment(
    start_position: f64,
    alpha: f64,
    beta: f64,
    duration: f64,
    time_step: f64,
    order: f64,
    particles: usize,
) -> XPyResult<f64> {
    let levy = AsymmetricLevy::new(start_position, alpha, beta)?;
    let result = levy.frac_raw_moment(duration, order, particles, time_step)?;
    Ok(result)
}

/// Get the fractional central moment of asymmetric Levy process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn asymmetric_levy_frac_central_moment(
    start_position: f64,
    alpha: f64,
    beta: f64,
    duration: f64,
    time_step: f64,
    order: f64,
    particles: usize,
) -> XPyResult<f64> {
    let levy = AsymmetricLevy::new(start_position, alpha, beta)?;
    let result = levy.frac_central_moment(duration, order, particles, time_step)?;
    Ok(result)
}
