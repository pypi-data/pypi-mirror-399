use crate::{
    XPyResult,
    simulation::{PyArrayPair, vec_to_pyarray},
};
use diffusionx::simulation::{point::CTRW, prelude::*};
use pyo3::prelude::*;
#[cfg(feature = "stub_gen")]
use pyo3_stub_gen::derive::gen_stub_pyfunction;

/// Simulate CTRW.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn ctrw_simulate_duration(
    py: Python<'_>,
    alpha: f64,
    beta: f64,
    start_position: f64,
    duration: f64,
) -> XPyResult<PyArrayPair<'_>> {
    let ctrw = CTRW::new(alpha, beta, start_position)?;
    let (times, positions) = ctrw.simulate_with_duration(duration)?;
    Ok(vec_to_pyarray(py, times, positions))
}

/// Simulate CTRW.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn ctrw_simulate_step(
    py: Python<'_>,
    alpha: f64,
    beta: f64,
    start_position: f64,
    num_step: usize,
) -> XPyResult<PyArrayPair<'_>> {
    let ctrw = CTRW::new(alpha, beta, start_position)?;
    let (times, positions) = ctrw.simulate_with_step(num_step)?;
    Ok(vec_to_pyarray(py, times, positions))
}

/// Get the raw moment of CTRW.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn ctrw_raw_moment(
    alpha: f64,
    beta: f64,
    start_position: f64,
    duration: f64,
    order: i32,
    particles: usize,
) -> XPyResult<f64> {
    let ctrw = CTRW::new(alpha, beta, start_position)?;
    let result = ctrw.raw_moment(duration, order, particles)?;
    Ok(result)
}

/// Get the central moment of CTRW.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn ctrw_central_moment(
    alpha: f64,
    beta: f64,
    start_position: f64,
    duration: f64,
    order: i32,
    particles: usize,
) -> XPyResult<f64> {
    let ctrw = CTRW::new(alpha, beta, start_position)?;
    let result = ctrw.central_moment(duration, order, particles)?;
    Ok(result)
}

/// Get the fractional raw moment of CTRW.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn ctrw_frac_raw_moment(
    alpha: f64,
    beta: f64,
    start_position: f64,
    duration: f64,
    order: f64,
    particles: usize,
) -> XPyResult<f64> {
    let ctrw = CTRW::new(alpha, beta, start_position)?;
    let result = ctrw.frac_raw_moment(duration, order, particles)?;
    Ok(result)
}

/// Get the fractional central moment of CTRW.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn ctrw_frac_central_moment(
    alpha: f64,
    beta: f64,
    start_position: f64,
    duration: f64,
    order: f64,
    particles: usize,
) -> XPyResult<f64> {
    let ctrw = CTRW::new(alpha, beta, start_position)?;
    let result = ctrw.frac_central_moment(duration, order, particles)?;
    Ok(result)
}

/// Get the first passage time of CTRW.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn ctrw_fpt(
    alpha: f64,
    beta: f64,
    start_position: f64,
    domain: (f64, f64),
    max_duration: f64,
) -> XPyResult<Option<f64>> {
    let ctrw = CTRW::new(alpha, beta, start_position)?;
    let result = ctrw.fpt(domain, max_duration)?;
    Ok(result)
}

/// Get the raw moment of the first passage time of CTRW.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn ctrw_fpt_raw_moment(
    alpha: f64,
    beta: f64,
    start_position: f64,
    domain: (f64, f64),
    order: i32,
    particles: usize,
    max_duration: f64,
) -> XPyResult<Option<f64>> {
    let ctrw = CTRW::new(alpha, beta, start_position)?;
    let fpt = FirstPassageTime::new(&ctrw, domain)?;
    let result = fpt.raw_moment_p(order, particles, max_duration)?;
    Ok(result)
}

/// Get the central moment of the first passage time of CTRW.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn ctrw_fpt_central_moment(
    alpha: f64,
    beta: f64,
    start_position: f64,
    domain: (f64, f64),
    order: i32,
    particles: usize,
    max_duration: f64,
) -> XPyResult<Option<f64>> {
    let ctrw = CTRW::new(alpha, beta, start_position)?;
    let fpt = FirstPassageTime::new(&ctrw, domain)?;
    let result = fpt.central_moment_p(order, particles, max_duration)?;
    Ok(result)
}

/// Get the occupation time of CTRW.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn ctrw_occupation_time(
    alpha: f64,
    beta: f64,
    start_position: f64,
    domain: (f64, f64),
    duration: f64,
) -> XPyResult<f64> {
    let ctrw = CTRW::new(alpha, beta, start_position)?;
    let result = ctrw.occupation_time(domain, duration)?;
    Ok(result)
}

/// Get the raw moment of the occupation time of CTRW.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn ctrw_occupation_time_raw_moment(
    alpha: f64,
    beta: f64,
    start_position: f64,
    domain: (f64, f64),
    duration: f64,
    order: i32,
    particles: usize,
) -> XPyResult<f64> {
    let ctrw = CTRW::new(alpha, beta, start_position)?;
    let oc = OccupationTime::new(&ctrw, domain, duration)?;
    let result = oc.raw_moment_p(order, particles)?;
    Ok(result)
}

/// Get the central moment of the occupation time of CTRW.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn ctrw_occupation_time_central_moment(
    alpha: f64,
    beta: f64,
    start_position: f64,
    domain: (f64, f64),
    duration: f64,
    order: i32,
    particles: usize,
) -> XPyResult<f64> {
    let ctrw = CTRW::new(alpha, beta, start_position)?;
    let oc = OccupationTime::new(&ctrw, domain, duration)?;
    let result = oc.central_moment_p(order, particles)?;
    Ok(result)
}

/// Get the mean of CTRW.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn ctrw_mean(
    alpha: f64,
    beta: f64,
    start_position: f64,
    duration: f64,
    particles: usize,
) -> XPyResult<f64> {
    let ctrw = CTRW::new(alpha, beta, start_position)?;
    let result = ctrw.mean(duration, particles)?;
    Ok(result)
}

/// Get the msd of CTRW.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn ctrw_msd(
    alpha: f64,
    beta: f64,
    start_position: f64,
    duration: f64,
    particles: usize,
) -> XPyResult<f64> {
    let ctrw = CTRW::new(alpha, beta, start_position)?;
    let result = ctrw.msd(duration, particles)?;
    Ok(result)
}
