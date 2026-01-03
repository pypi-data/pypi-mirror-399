use crate::{
    XPyResult,
    simulation::{PyArrayPair, vec_to_pyarray},
};
use diffusionx::simulation::{continuous::Gamma, prelude::*};
use pyo3::prelude::*;
#[cfg(feature = "stub_gen")]
use pyo3_stub_gen::derive::gen_stub_pyfunction;

/// Simulate Gamma.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn gamma_simulate(
    py: Python<'_>,
    shape: f64,
    rate: f64,
    duration: f64,
    time_step: f64,
) -> XPyResult<PyArrayPair<'_>> {
    let gamma = Gamma::new(shape, rate)?;
    let (times, positions) = gamma.simulate(duration, time_step)?;
    Ok(vec_to_pyarray(py, times, positions))
}

/// Get the raw moment of Gamma.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn gamma_raw_moment(
    shape: f64,
    rate: f64,
    duration: f64,
    time_step: f64,
    order: i32,
    particles: usize,
) -> XPyResult<f64> {
    let gamma = Gamma::new(shape, rate)?;
    let result = gamma.raw_moment(duration, order, particles, time_step)?;
    Ok(result)
}

/// Get the central moment of Gamma.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn gamma_central_moment(
    shape: f64,
    rate: f64,
    duration: f64,
    time_step: f64,
    order: i32,
    particles: usize,
) -> XPyResult<f64> {
    let gamma = Gamma::new(shape, rate)?;
    let result = gamma.central_moment(duration, order, particles, time_step)?;
    Ok(result)
}

/// Get the fractional raw moment of Gamma.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn gamma_frac_raw_moment(
    shape: f64,
    rate: f64,
    duration: f64,
    time_step: f64,
    order: f64,
    particles: usize,
) -> XPyResult<f64> {
    let gamma = Gamma::new(shape, rate)?;
    let result = gamma.frac_raw_moment(duration, order, particles, time_step)?;
    Ok(result)
}

/// Get the fractional central moment of Gamma.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn gamma_frac_central_moment(
    shape: f64,
    rate: f64,
    duration: f64,
    time_step: f64,
    order: f64,
    particles: usize,
) -> XPyResult<f64> {
    let gamma = Gamma::new(shape, rate)?;
    let result = gamma.frac_central_moment(duration, order, particles, time_step)?;
    Ok(result)
}

/// Get the first passage time of Gamma.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn gamma_fpt(
    shape: f64,
    rate: f64,
    time_step: f64,
    domain: (f64, f64),
    max_duration: f64,
) -> XPyResult<Option<f64>> {
    let gamma = Gamma::new(shape, rate)?;
    let result = gamma.fpt(domain, max_duration, time_step)?;
    Ok(result)
}

/// Get the raw moment of the first passage time of Gamma.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn gamma_fpt_raw_moment(
    shape: f64,
    rate: f64,
    domain: (f64, f64),
    order: i32,
    particles: usize,
    time_step: f64,
    max_duration: f64,
) -> XPyResult<Option<f64>> {
    let gamma = Gamma::new(shape, rate)?;
    let fpt = FirstPassageTime::new(&gamma, domain)?;
    let result = fpt.raw_moment(order, particles, max_duration, time_step)?;
    Ok(result)
}

/// Get the central moment of the first passage time of Gamma.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn gamma_fpt_central_moment(
    shape: f64,
    rate: f64,
    domain: (f64, f64),
    order: i32,
    particles: usize,
    time_step: f64,
    max_duration: f64,
) -> XPyResult<Option<f64>> {
    let gamma = Gamma::new(shape, rate)?;
    let fpt = FirstPassageTime::new(&gamma, domain)?;
    let result = fpt.central_moment(order, particles, max_duration, time_step)?;
    Ok(result)
}

/// Get the occupation time of Gamma.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn gamma_occupation_time(
    shape: f64,
    rate: f64,
    domain: (f64, f64),
    time_step: f64,
    duration: f64,
) -> XPyResult<f64> {
    let gamma = Gamma::new(shape, rate)?;
    let result = gamma.occupation_time(domain, duration, time_step)?;
    Ok(result)
}

/// Get the raw moment of the occupation time of Gamma.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn gamma_occupation_time_raw_moment(
    shape: f64,
    rate: f64,
    domain: (f64, f64),
    order: i32,
    particles: usize,
    time_step: f64,
    duration: f64,
) -> XPyResult<f64> {
    let gamma = Gamma::new(shape, rate)?;
    let oc = OccupationTime::new(&gamma, domain, duration)?;
    let result = oc.raw_moment(order, particles, time_step)?;
    Ok(result)
}

/// Get the central moment of the occupation time of Gamma.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn gamma_occupation_time_central_moment(
    shape: f64,
    rate: f64,
    domain: (f64, f64),
    order: i32,
    particles: usize,
    time_step: f64,
    duration: f64,
) -> XPyResult<f64> {
    let gamma = Gamma::new(shape, rate)?;
    let oc = OccupationTime::new(&gamma, domain, duration)?;
    let result = oc.central_moment(order, particles, time_step)?;
    Ok(result)
}

/// Get the time-averaged mean squared displacement of Gamma.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn gamma_tamsd(
    shape: f64,
    rate: f64,
    duration: f64,
    delta: f64,
    time_step: f64,
    quad_order: usize,
) -> XPyResult<f64> {
    let gamma = Gamma::new(shape, rate)?;
    let result = gamma.tamsd(duration, delta, time_step, quad_order)?;
    Ok(result)
}

/// Get the effective time-averaged mean squared displacement of Gamma.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn gamma_eatamsd(
    shape: f64,
    rate: f64,
    duration: f64,
    delta: f64,
    particles: usize,
    time_step: f64,
    quad_order: usize,
) -> XPyResult<f64> {
    let gamma = Gamma::new(shape, rate)?;
    let result = gamma.eatamsd(duration, delta, particles, time_step, quad_order)?;
    Ok(result)
}

/// Get the mean of Gamma.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn gamma_mean(
    shape: f64,
    rate: f64,
    duration: f64,
    particles: usize,
    time_step: f64,
) -> XPyResult<f64> {
    let gamma = Gamma::new(shape, rate)?;
    let result = gamma.mean(duration, particles, time_step)?;
    Ok(result)
}

/// Get the msd of Gamma.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn gamma_msd(
    shape: f64,
    rate: f64,
    duration: f64,
    particles: usize,
    time_step: f64,
) -> XPyResult<f64> {
    let gamma = Gamma::new(shape, rate)?;
    let result = gamma.msd(duration, particles, time_step)?;
    Ok(result)
}
