use crate::{
    XPyResult,
    simulation::{PyArrayPair, vec_to_pyarray},
};
use diffusionx::simulation::{
    continuous::{AsymmetricCauchy, Cauchy},
    prelude::*,
};
use pyo3::prelude::*;
#[cfg(feature = "stub_gen")]
use pyo3_stub_gen::derive::gen_stub_pyfunction;

/// Simulate Cauchy process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn cauchy_simulate(
    py: Python<'_>,
    start_position: f64,
    duration: f64,
    time_step: f64,
) -> XPyResult<PyArrayPair<'_>> {
    let cauchy = Cauchy::new(start_position);
    let (times, positions) = cauchy.simulate(duration, time_step)?;
    Ok(vec_to_pyarray(py, times, positions))
}

/// Get the raw moment of Cauchy process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn cauchy_raw_moment(
    start_position: f64,
    duration: f64,
    time_step: f64,
    order: i32,
    particles: usize,
) -> XPyResult<f64> {
    let cauchy = Cauchy::new(start_position);
    let result = cauchy.raw_moment(duration, order, particles, time_step)?;
    Ok(result)
}

/// Get the central moment of Cauchy process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn cauchy_central_moment(
    start_position: f64,
    duration: f64,
    time_step: f64,
    order: i32,
    particles: usize,
) -> XPyResult<f64> {
    let cauchy = Cauchy::new(start_position);
    let result = cauchy.central_moment(duration, order, particles, time_step)?;
    Ok(result)
}

/// Get the fractional raw moment of Cauchy process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn cauchy_frac_raw_moment(
    start_position: f64,
    duration: f64,
    time_step: f64,
    order: f64,
    particles: usize,
) -> XPyResult<f64> {
    let cauchy = Cauchy::new(start_position);
    let result = cauchy.frac_raw_moment(duration, order, particles, time_step)?;
    Ok(result)
}

/// Get the fractional central moment of Cauchy process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn cauchy_frac_central_moment(
    start_position: f64,
    duration: f64,
    time_step: f64,
    order: f64,
    particles: usize,
) -> XPyResult<f64> {
    let cauchy = Cauchy::new(start_position);
    let result = cauchy.frac_central_moment(duration, order, particles, time_step)?;
    Ok(result)
}

/// Get the first passage time of Cauchy process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn cauchy_fpt(
    start_position: f64,
    time_step: f64,
    domain: (f64, f64),
    max_duration: f64,
) -> XPyResult<Option<f64>> {
    let cauchy = Cauchy::new(start_position);
    let result = cauchy.fpt(domain, max_duration, time_step)?;
    Ok(result)
}

/// Get the raw moment of the first passage time of Cauchy process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn cauchy_fpt_raw_moment(
    start_position: f64,
    domain: (f64, f64),
    order: i32,
    particles: usize,
    time_step: f64,
    max_duration: f64,
) -> XPyResult<Option<f64>> {
    let cauchy = Cauchy::new(start_position);
    let fpt = FirstPassageTime::new(&cauchy, domain)?;
    let result = fpt.raw_moment(order, particles, max_duration, time_step)?;
    Ok(result)
}

/// Get the central moment of the first passage time of Cauchy process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn cauchy_fpt_central_moment(
    start_position: f64,
    domain: (f64, f64),
    order: i32,
    particles: usize,
    time_step: f64,
    max_duration: f64,
) -> XPyResult<Option<f64>> {
    let cauchy = Cauchy::new(start_position);
    let fpt = FirstPassageTime::new(&cauchy, domain)?;
    let result = fpt.central_moment(order, particles, max_duration, time_step)?;
    Ok(result)
}

/// Get the occupation time of Cauchy process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn cauchy_occupation_time(
    start_position: f64,
    domain: (f64, f64),
    time_step: f64,
    duration: f64,
) -> XPyResult<f64> {
    let cauchy = Cauchy::new(start_position);
    let result = cauchy.occupation_time(domain, duration, time_step)?;
    Ok(result)
}

/// Get the raw moment of the occupation time of Cauchy process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn cauchy_occupation_time_raw_moment(
    start_position: f64,
    domain: (f64, f64),
    order: i32,
    particles: usize,
    time_step: f64,
    duration: f64,
) -> XPyResult<f64> {
    let cauchy = Cauchy::new(start_position);
    let oc = OccupationTime::new(&cauchy, domain, duration)?;
    let result = oc.raw_moment(order, particles, time_step)?;
    Ok(result)
}

/// Get the central moment of the occupation time of Cauchy process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn cauchy_occupation_time_central_moment(
    start_position: f64,
    domain: (f64, f64),
    order: i32,
    particles: usize,
    time_step: f64,
    duration: f64,
) -> XPyResult<f64> {
    let cauchy = Cauchy::new(start_position);
    let oc = OccupationTime::new(&cauchy, domain, duration)?;
    let result = oc.central_moment(order, particles, time_step)?;
    Ok(result)
}

/// Get the time-averaged mean square displacement of Cauchy process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn cauchy_tamsd(
    start_position: f64,
    duration: f64,
    delta: f64,
    time_step: f64,
    quad_order: usize,
) -> XPyResult<f64> {
    let cauchy = Cauchy::new(start_position);
    let result = cauchy.tamsd(duration, delta, time_step, quad_order)?;
    Ok(result)
}

/// Get the ensemble average of the time-averaged mean square displacement of Cauchy process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn cauchy_eatamsd(
    start_position: f64,
    duration: f64,
    delta: f64,
    particles: usize,
    time_step: f64,
    quad_order: usize,
) -> XPyResult<f64> {
    let cauchy = Cauchy::new(start_position);
    let result = cauchy.eatamsd(duration, delta, particles, time_step, quad_order)?;
    Ok(result)
}

/// Simulate asymmetric Cauchy process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn asymmetric_cauchy_simulate(
    py: Python<'_>,
    start_position: f64,
    beta: f64,
    duration: f64,
    time_step: f64,
) -> XPyResult<PyArrayPair<'_>> {
    let cauchy = AsymmetricCauchy::new(start_position, beta)?;
    let (times, positions) = cauchy.simulate(duration, time_step)?;
    Ok(vec_to_pyarray(py, times, positions))
}

/// Get the raw moment of asymmetric Cauchy process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn asymmetric_cauchy_raw_moment(
    start_position: f64,
    beta: f64,
    duration: f64,
    time_step: f64,
    order: i32,
    particles: usize,
) -> XPyResult<f64> {
    let cauchy = AsymmetricCauchy::new(start_position, beta)?;
    let result = cauchy.raw_moment(duration, order, particles, time_step)?;
    Ok(result)
}

/// Get the central moment of asymmetric Cauchy process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn asymmetric_cauchy_central_moment(
    start_position: f64,
    beta: f64,
    duration: f64,
    time_step: f64,
    order: i32,
    particles: usize,
) -> XPyResult<f64> {
    let cauchy = AsymmetricCauchy::new(start_position, beta)?;
    let result = cauchy.central_moment(duration, order, particles, time_step)?;
    Ok(result)
}

/// Get the fractional raw moment of asymmetric Cauchy process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn asymmetric_cauchy_frac_raw_moment(
    start_position: f64,
    beta: f64,
    duration: f64,
    time_step: f64,
    order: f64,
    particles: usize,
) -> XPyResult<f64> {
    let cauchy = AsymmetricCauchy::new(start_position, beta)?;
    let result = cauchy.frac_raw_moment(duration, order, particles, time_step)?;
    Ok(result)
}

/// Get the fractional central moment of asymmetric Cauchy process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn asymmetric_cauchy_frac_central_moment(
    start_position: f64,
    beta: f64,
    duration: f64,
    time_step: f64,
    order: f64,
    particles: usize,
) -> XPyResult<f64> {
    let cauchy = AsymmetricCauchy::new(start_position, beta)?;
    let result = cauchy.frac_central_moment(duration, order, particles, time_step)?;
    Ok(result)
}

/// Get the first passage time of asymmetric Cauchy process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn asymmetric_cauchy_fpt(
    start_position: f64,
    beta: f64,
    time_step: f64,
    domain: (f64, f64),
    max_duration: f64,
) -> XPyResult<Option<f64>> {
    let cauchy = AsymmetricCauchy::new(start_position, beta)?;
    let result = cauchy.fpt(domain, max_duration, time_step)?;
    Ok(result)
}

/// Get the raw moment of the first passage time of asymmetric Cauchy process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn asymmetric_cauchy_fpt_raw_moment(
    start_position: f64,
    beta: f64,
    domain: (f64, f64),
    order: i32,
    particles: usize,
    time_step: f64,
    max_duration: f64,
) -> XPyResult<Option<f64>> {
    let cauchy = AsymmetricCauchy::new(start_position, beta)?;
    let fpt = FirstPassageTime::new(&cauchy, domain)?;
    let result = fpt.raw_moment(order, particles, max_duration, time_step)?;
    Ok(result)
}

/// Get the central moment of the first passage time of asymmetric Cauchy process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn asymmetric_cauchy_fpt_central_moment(
    start_position: f64,
    beta: f64,
    domain: (f64, f64),
    order: i32,
    particles: usize,
    time_step: f64,
    max_duration: f64,
) -> XPyResult<Option<f64>> {
    let cauchy = AsymmetricCauchy::new(start_position, beta)?;
    let fpt = FirstPassageTime::new(&cauchy, domain)?;
    let result = fpt.central_moment(order, particles, max_duration, time_step)?;
    Ok(result)
}

/// Get the occupation time of asymmetric Cauchy process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn asymmetric_cauchy_occupation_time(
    start_position: f64,
    beta: f64,
    domain: (f64, f64),
    time_step: f64,
    duration: f64,
) -> XPyResult<f64> {
    let cauchy = AsymmetricCauchy::new(start_position, beta)?;
    let result = cauchy.occupation_time(domain, duration, time_step)?;
    Ok(result)
}

/// Get the raw moment of the occupation time of asymmetric Cauchy process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn asymmetric_cauchy_occupation_time_raw_moment(
    start_position: f64,
    beta: f64,
    domain: (f64, f64),
    order: i32,
    particles: usize,
    time_step: f64,
    duration: f64,
) -> XPyResult<f64> {
    let cauchy = AsymmetricCauchy::new(start_position, beta)?;
    let oc = OccupationTime::new(&cauchy, domain, duration)?;
    let result = oc.raw_moment(order, particles, time_step)?;
    Ok(result)
}

/// Get the central moment of the occupation time of asymmetric Cauchy process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn asymmetric_cauchy_occupation_time_central_moment(
    start_position: f64,
    beta: f64,
    domain: (f64, f64),
    order: i32,
    particles: usize,
    time_step: f64,
    duration: f64,
) -> XPyResult<f64> {
    let cauchy = AsymmetricCauchy::new(start_position, beta)?;
    let oc = OccupationTime::new(&cauchy, domain, duration)?;
    let result = oc.central_moment(order, particles, time_step)?;
    Ok(result)
}

/// Get the time-averaged mean square displacement of asymmetric Cauchy process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn asymmetric_cauchy_tamsd(
    start_position: f64,
    beta: f64,
    duration: f64,
    delta: f64,
    time_step: f64,
    quad_order: usize,
) -> XPyResult<f64> {
    let cauchy = AsymmetricCauchy::new(start_position, beta)?;
    let result = cauchy.tamsd(duration, delta, time_step, quad_order)?;
    Ok(result)
}

/// Get the ensemble average of the time-averaged mean square displacement of asymmetric Cauchy process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn asymmetric_cauchy_eatamsd(
    start_position: f64,
    beta: f64,
    duration: f64,
    delta: f64,
    particles: usize,
    time_step: f64,
    quad_order: usize,
) -> XPyResult<f64> {
    let cauchy = AsymmetricCauchy::new(start_position, beta)?;
    let result = cauchy.eatamsd(duration, delta, particles, time_step, quad_order)?;
    Ok(result)
}
