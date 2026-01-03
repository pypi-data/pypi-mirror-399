use crate::{
    XPyResult,
    simulation::{PyArrayPair, vec_to_pyarray},
};
use diffusionx::simulation::{continuous::BrownianMeander, prelude::*};
use pyo3::prelude::*;
#[cfg(feature = "stub_gen")]
use pyo3_stub_gen::derive::gen_stub_pyfunction;

/// Simulate Brownian meander.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn meander_simulate(
    py: Python<'_>,
    duration: f64,
    time_step: f64,
) -> XPyResult<PyArrayPair<'_>> {
    let bm = BrownianMeander::new();
    let (times, positions) = bm.simulate(duration, time_step)?;
    Ok(vec_to_pyarray(py, times, positions))
}

/// Get the raw moment of Brownian meander.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn meander_raw_moment(
    duration: f64,
    time_step: f64,
    order: i32,
    particles: usize,
) -> XPyResult<f64> {
    let bm = BrownianMeander::new();
    let result = bm.raw_moment(duration, order, particles, time_step)?;
    Ok(result)
}

/// Get the central moment of Brownian meander.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn meander_central_moment(
    duration: f64,
    time_step: f64,
    order: i32,
    particles: usize,
) -> XPyResult<f64> {
    let bm = BrownianMeander::new();
    let result = bm.central_moment(duration, order, particles, time_step)?;
    Ok(result)
}

/// Get the fractional raw moment of Brownian meander.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn meander_frac_raw_moment(
    duration: f64,
    time_step: f64,
    order: f64,
    particles: usize,
) -> XPyResult<f64> {
    let bm = BrownianMeander::new();
    let result = bm.frac_raw_moment(duration, order, particles, time_step)?;
    Ok(result)
}

/// Get the fractional central moment of Brownian meander.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn meander_frac_central_moment(
    duration: f64,
    time_step: f64,
    order: f64,
    particles: usize,
) -> XPyResult<f64> {
    let bm = BrownianMeander::new();
    let result = bm.frac_central_moment(duration, order, particles, time_step)?;
    Ok(result)
}

/// Get the first passage time of Brownian meander.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn meander_fpt(time_step: f64, domain: (f64, f64)) -> XPyResult<Option<f64>> {
    let bm = BrownianMeander::new();
    let result = bm.fpt(domain, time_step)?;
    Ok(result)
}

/// Get the raw moment of the first passage time of Brownian meander.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn meander_fpt_raw_moment(
    domain: (f64, f64),
    order: i32,
    particles: usize,
    time_step: f64,
) -> XPyResult<Option<f64>> {
    let bm = BrownianMeander::new();
    let fpt = FirstPassageTime::new(&bm, domain)?;
    let result = fpt.raw_moment(order, particles, 1.0, time_step)?;
    Ok(result)
}

/// Get the central moment of the first passage time of Brownian meander.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn meander_fpt_central_moment(
    domain: (f64, f64),
    order: i32,
    particles: usize,
    time_step: f64,
) -> XPyResult<Option<f64>> {
    let bm = BrownianMeander::new();
    let fpt = FirstPassageTime::new(&bm, domain)?;
    let result = fpt.central_moment(order, particles, 1.0, time_step)?;
    Ok(result)
}

/// Get the occupation time of Brownian meander.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn meander_occupation_time(
    domain: (f64, f64),
    time_step: f64,
    duration: f64,
) -> XPyResult<f64> {
    let bm = BrownianMeander::new();
    let result = bm.occupation_time(domain, duration, time_step)?;
    Ok(result)
}

/// Get the raw moment of the occupation time of Brownian meander.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn meander_occupation_time_raw_moment(
    domain: (f64, f64),
    order: i32,
    particles: usize,
    time_step: f64,
    duration: f64,
) -> XPyResult<f64> {
    let bm = BrownianMeander::new();
    let oc = OccupationTime::new(&bm, domain, duration)?;
    let result = oc.raw_moment(order, particles, time_step)?;
    Ok(result)
}

/// Get the central moment of the occupation time of Brownian meander.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn meander_occupation_time_central_moment(
    domain: (f64, f64),
    order: i32,
    particles: usize,
    time_step: f64,
    duration: f64,
) -> XPyResult<f64> {
    let bm = BrownianMeander::new();
    let oc = OccupationTime::new(&bm, domain, duration)?;
    let result = oc.central_moment(order, particles, time_step)?;
    Ok(result)
}

/// Get the time-averaged mean square displacement of Brownian meander.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn meander_tamsd(
    duration: f64,
    delta: f64,
    time_step: f64,
    quad_order: usize,
) -> XPyResult<f64> {
    let bm = BrownianMeander::new();
    let result = bm.tamsd(duration, delta, time_step, quad_order)?;
    Ok(result)
}

/// Get the ensemble average of the time-averaged mean square displacement of Brownian meander.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn meander_eatamsd(
    duration: f64,
    delta: f64,
    particles: usize,
    time_step: f64,
    quad_order: usize,
) -> XPyResult<f64> {
    let bm = BrownianMeander::new();
    let result = bm.eatamsd(duration, delta, particles, time_step, quad_order)?;
    Ok(result)
}

/// Get the mean of Brownian meander.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn meander_mean(duration: f64, particles: usize, time_step: f64) -> XPyResult<f64> {
    let bm = BrownianMeander::new();
    let result = bm.mean(duration, particles, time_step)?;
    Ok(result)
}

/// Get the msd of Brownian meander.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn meander_msd(duration: f64, particles: usize, time_step: f64) -> XPyResult<f64> {
    let bm = BrownianMeander::new();
    let result = bm.msd(duration, particles, time_step)?;
    Ok(result)
}
