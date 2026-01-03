use crate::{
    XPyResult,
    simulation::{PyArrayPair, vec_to_pyarray},
};
use diffusionx::simulation::{continuous::FBm, prelude::*};
use pyo3::prelude::*;
#[cfg(feature = "stub_gen")]
use pyo3_stub_gen::derive::gen_stub_pyfunction;

/// Simulate FBm.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn fbm_simulate(
    py: Python<'_>,
    start_position: f64,
    hurst_exponent: f64,
    duration: f64,
    time_step: f64,
) -> XPyResult<PyArrayPair<'_>> {
    let fbm = FBm::new(start_position, hurst_exponent)?;
    let (times, positions) = fbm.simulate(duration, time_step)?;
    Ok(vec_to_pyarray(py, times, positions))
}

/// Get the raw moment of FBm.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn fbm_raw_moment(
    start_position: f64,
    hurst_exponent: f64,
    duration: f64,
    time_step: f64,
    order: i32,
    particles: usize,
) -> XPyResult<f64> {
    let fbm = FBm::new(start_position, hurst_exponent)?;
    let result = fbm.raw_moment(duration, order, particles, time_step)?;
    Ok(result)
}

/// Get the central moment of FBm.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn fbm_central_moment(
    start_position: f64,
    hurst_exponent: f64,
    duration: f64,
    time_step: f64,
    order: i32,
    particles: usize,
) -> XPyResult<f64> {
    let fbm = FBm::new(start_position, hurst_exponent)?;
    let result = fbm.central_moment(duration, order, particles, time_step)?;
    Ok(result)
}

/// Get the fractional raw moment of FBm.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn fbm_frac_raw_moment(
    start_position: f64,
    hurst_exponent: f64,
    duration: f64,
    time_step: f64,
    order: f64,
    particles: usize,
) -> XPyResult<f64> {
    let fbm = FBm::new(start_position, hurst_exponent)?;
    let result = fbm.frac_raw_moment(duration, order, particles, time_step)?;
    Ok(result)
}

/// Get the fractional central moment of FBm.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn fbm_frac_central_moment(
    start_position: f64,
    hurst_exponent: f64,
    duration: f64,
    time_step: f64,
    order: f64,
    particles: usize,
) -> XPyResult<f64> {
    let fbm = FBm::new(start_position, hurst_exponent)?;
    let result = fbm.frac_central_moment(duration, order, particles, time_step)?;
    Ok(result)
}

/// Get the first passage time of FBm.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn fbm_fpt(
    start_position: f64,
    hurst_exponent: f64,
    time_step: f64,
    domain: (f64, f64),
    max_duration: f64,
) -> XPyResult<Option<f64>> {
    let fbm = FBm::new(start_position, hurst_exponent)?;
    let result = fbm.fpt(domain, max_duration, time_step)?;
    Ok(result)
}

/// Get the raw moment of the first passage time of FBm.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn fbm_fpt_raw_moment(
    start_position: f64,
    hurst_exponent: f64,
    domain: (f64, f64),
    order: i32,
    particles: usize,
    time_step: f64,
    max_duration: f64,
) -> XPyResult<Option<f64>> {
    let fbm = FBm::new(start_position, hurst_exponent)?;
    let fpt = FirstPassageTime::new(&fbm, domain)?;
    let result = fpt.raw_moment(order, particles, max_duration, time_step)?;
    Ok(result)
}

/// Get the central moment of the first passage time of FBm.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn fbm_fpt_central_moment(
    start_position: f64,
    hurst_exponent: f64,
    domain: (f64, f64),
    order: i32,
    particles: usize,
    time_step: f64,
    max_duration: f64,
) -> XPyResult<Option<f64>> {
    let fbm = FBm::new(start_position, hurst_exponent)?;
    let fpt = FirstPassageTime::new(&fbm, domain)?;
    let result = fpt.central_moment(order, particles, max_duration, time_step)?;
    Ok(result)
}

/// Get the occupation time of FBm.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn fbm_occupation_time(
    start_position: f64,
    hurst_exponent: f64,
    time_step: f64,
    domain: (f64, f64),
    duration: f64,
) -> XPyResult<f64> {
    let fbm = FBm::new(start_position, hurst_exponent)?;
    let result = fbm.occupation_time(domain, duration, time_step)?;
    Ok(result)
}

/// Get the raw moment of the occupation time of FBm.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn fbm_occupation_time_raw_moment(
    start_position: f64,
    hurst_exponent: f64,
    domain: (f64, f64),
    order: i32,
    particles: usize,
    time_step: f64,
    duration: f64,
) -> XPyResult<f64> {
    let fbm = FBm::new(start_position, hurst_exponent)?;
    let oc = OccupationTime::new(&fbm, domain, duration)?;
    let result = oc.raw_moment(order, particles, time_step)?;
    Ok(result)
}

/// Get the central moment of the occupation time of FBm.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn fbm_occupation_time_central_moment(
    start_position: f64,
    hurst_exponent: f64,
    domain: (f64, f64),
    order: i32,
    particles: usize,
    time_step: f64,
    duration: f64,
) -> XPyResult<f64> {
    let fbm = FBm::new(start_position, hurst_exponent)?;
    let oc = OccupationTime::new(&fbm, domain, duration)?;
    let result = oc.central_moment(order, particles, time_step)?;
    Ok(result)
}

/// Get the time-averaged mean squared displacement of FBm.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn fbm_tamsd(
    start_position: f64,
    hurst_exponent: f64,
    duration: f64,
    delta: f64,
    time_step: f64,
    quad_order: usize,
) -> XPyResult<f64> {
    let fbm = FBm::new(start_position, hurst_exponent)?;
    let result = fbm.tamsd(duration, delta, time_step, quad_order)?;
    Ok(result)
}

/// Get the effective time-averaged mean squared displacement of FBm.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn fbm_eatamsd(
    start_position: f64,
    hurst_exponent: f64,
    duration: f64,
    delta: f64,
    particles: usize,
    time_step: f64,
    quad_order: usize,
) -> XPyResult<f64> {
    let fbm = FBm::new(start_position, hurst_exponent)?;
    let result = fbm.eatamsd(duration, delta, particles, time_step, quad_order)?;
    Ok(result)
}

/// Get the mean of FBm.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn fbm_mean(
    start_position: f64,
    hurst_exponent: f64,
    duration: f64,
    particles: usize,
    time_step: f64,
) -> XPyResult<f64> {
    let fbm = FBm::new(start_position, hurst_exponent)?;
    let result = fbm.mean(duration, particles, time_step)?;
    Ok(result)
}

/// Get the msd of FBm.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn fbm_msd(
    start_position: f64,
    hurst_exponent: f64,
    duration: f64,
    particles: usize,
    time_step: f64,
) -> XPyResult<f64> {
    let fbm = FBm::new(start_position, hurst_exponent)?;
    let result = fbm.msd(duration, particles, time_step)?;
    Ok(result)
}
