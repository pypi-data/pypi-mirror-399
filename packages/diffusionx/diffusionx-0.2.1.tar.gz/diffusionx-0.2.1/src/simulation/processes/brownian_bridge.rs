use crate::{
    XPyResult,
    simulation::{PyArrayPair, vec_to_pyarray},
};
use diffusionx::simulation::{continuous::BrownianBridge, prelude::*};
use pyo3::prelude::*;

#[cfg(feature = "stub_gen")]
use pyo3_stub_gen::derive::gen_stub_pyfunction;

/// Simulate Brownian bridge.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn bb_simulate(py: Python<'_>, duration: f64, time_step: f64) -> XPyResult<PyArrayPair<'_>> {
    let bb = BrownianBridge::new();
    let (times, positions) = bb.simulate(duration, time_step)?;
    Ok(vec_to_pyarray(py, times, positions))
}

/// Get the raw moment of Brownian bridge.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn bb_raw_moment(
    duration: f64,
    time_step: f64,
    order: i32,
    particles: usize,
) -> XPyResult<f64> {
    let bb = BrownianBridge::new();
    let result = bb.raw_moment(duration, order, particles, time_step)?;
    Ok(result)
}

/// Get the central moment of Brownian bridge.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn bb_central_moment(
    duration: f64,
    time_step: f64,
    order: i32,
    particles: usize,
) -> XPyResult<f64> {
    let bb = BrownianBridge::new();
    let result = bb.central_moment(duration, order, particles, time_step)?;
    Ok(result)
}

/// Get the fractional raw moment of Brownian bridge.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn bb_frac_raw_moment(
    duration: f64,
    time_step: f64,
    order: f64,
    particles: usize,
) -> XPyResult<f64> {
    let bb = BrownianBridge::new();
    let result = bb.frac_raw_moment(duration, order, particles, time_step)?;
    Ok(result)
}

/// Get the fractional central moment of Brownian bridge.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn bb_frac_central_moment(
    duration: f64,
    time_step: f64,
    order: f64,
    particles: usize,
) -> XPyResult<f64> {
    let bb = BrownianBridge::new();
    let result = bb.frac_central_moment(duration, order, particles, time_step)?;
    Ok(result)
}

/// Get the first passage time of Brownian bridge.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn bb_fpt(time_step: f64, domain: (f64, f64), max_duration: f64) -> XPyResult<Option<f64>> {
    let bb = BrownianBridge::new();
    let result = bb.fpt(domain, max_duration, time_step)?;
    Ok(result)
}

/// Get the raw moment of the first passage time of Brownian bridge.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn bb_fpt_raw_moment(
    domain: (f64, f64),
    order: i32,
    particles: usize,
    time_step: f64,
    max_duration: f64,
) -> XPyResult<Option<f64>> {
    let bb = BrownianBridge::new();
    let fpt = FirstPassageTime::new(&bb, domain)?;
    let result = fpt.raw_moment(order, particles, max_duration, time_step)?;
    Ok(result)
}

/// Get the central moment of the first passage time of Brownian bridge.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn bb_fpt_central_moment(
    domain: (f64, f64),
    order: i32,
    particles: usize,
    time_step: f64,
    max_duration: f64,
) -> XPyResult<Option<f64>> {
    let bb = BrownianBridge::new();
    let fpt = FirstPassageTime::new(&bb, domain)?;
    let result = fpt.central_moment(order, particles, max_duration, time_step)?;
    Ok(result)
}

/// Get the occupation time of Brownian bridge.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn bb_occupation_time(domain: (f64, f64), time_step: f64, duration: f64) -> XPyResult<f64> {
    let bb = BrownianBridge::new();
    let result = bb.occupation_time(domain, duration, time_step)?;
    Ok(result)
}

/// Get the raw moment of the occupation time of Brownian bridge.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn bb_occupation_time_raw_moment(
    domain: (f64, f64),
    order: i32,
    particles: usize,
    time_step: f64,
    duration: f64,
) -> XPyResult<f64> {
    let bb = BrownianBridge::new();
    let oc = OccupationTime::new(&bb, domain, duration)?;
    let result = oc.raw_moment(order, particles, time_step)?;
    Ok(result)
}

/// Get the central moment of the occupation time of Brownian bridge.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn bb_occupation_time_central_moment(
    domain: (f64, f64),
    order: i32,
    particles: usize,
    time_step: f64,
    duration: f64,
) -> XPyResult<f64> {
    let bb = BrownianBridge::new();
    let oc = OccupationTime::new(&bb, domain, duration)?;
    let result = oc.central_moment(order, particles, time_step)?;
    Ok(result)
}

/// Get the time-averaged mean square displacement of Brownian bridge.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn bb_tamsd(duration: f64, delta: f64, time_step: f64, quad_order: usize) -> XPyResult<f64> {
    let bb = BrownianBridge::new();
    let result = bb.tamsd(duration, delta, time_step, quad_order)?;
    Ok(result)
}

/// Get the ensemble average of the time-averaged mean square displacement of Brownian bridge.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn bb_eatamsd(
    duration: f64,
    delta: f64,
    particles: usize,
    time_step: f64,
    quad_order: usize,
) -> XPyResult<f64> {
    let bb = BrownianBridge::new();
    let result = bb.eatamsd(duration, delta, particles, time_step, quad_order)?;
    Ok(result)
}

/// Get the mean of Brownian bridge.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn bb_mean(duration: f64, particles: usize, time_step: f64) -> XPyResult<f64> {
    let bb = BrownianBridge::new();
    let result = bb.mean(duration, particles, time_step)?;
    Ok(result)
}

/// Get the msd of Brownian bridge.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn bb_msd(duration: f64, particles: usize, time_step: f64) -> XPyResult<f64> {
    let bb = BrownianBridge::new();
    let result = bb.msd(duration, particles, time_step)?;
    Ok(result)
}
