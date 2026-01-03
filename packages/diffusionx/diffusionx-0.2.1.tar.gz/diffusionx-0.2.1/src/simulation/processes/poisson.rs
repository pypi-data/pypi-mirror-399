use crate::{
    XPyResult,
    simulation::{PyArrayPair, vec_to_pyarray},
};
use diffusionx::simulation::{point::Poisson, prelude::*};
use pyo3::prelude::*;
#[cfg(feature = "stub_gen")]
use pyo3_stub_gen::derive::gen_stub_pyfunction;

/// Simulate Poisson process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn poisson_simulate_duration(
    py: Python<'_>,
    lambda_: f64,
    duration: f64,
) -> XPyResult<PyArrayPair<'_>> {
    let poisson = Poisson::new(lambda_)?;
    let (times, positions) = poisson.simulate_with_duration(duration)?;
    Ok(vec_to_pyarray(py, times, positions))
}

/// Simulate Poisson process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn poisson_simulate_step(
    py: Python<'_>,
    lambda_: f64,
    num_step: usize,
) -> XPyResult<PyArrayPair<'_>> {
    let poisson = Poisson::new(lambda_)?;
    let (times, positions) = poisson.simulate_with_step(num_step)?;
    Ok(vec_to_pyarray(py, times, positions))
}

/// Get the raw moment of Poisson process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn poisson_raw_moment(
    lambda_: f64,
    duration: f64,
    order: i32,
    particles: usize,
) -> XPyResult<f64> {
    let poisson: Poisson<f64, f64> = Poisson::new(lambda_)?;
    let result = poisson.raw_moment(duration, order, particles)?;
    Ok(result)
}

/// Get the central moment of Poisson process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn poisson_central_moment(
    lambda_: f64,
    duration: f64,
    order: i32,
    particles: usize,
) -> XPyResult<f64> {
    let poisson: Poisson<f64, f64> = Poisson::new(lambda_)?;
    let result = poisson.central_moment(duration, order, particles)?;
    Ok(result)
}

/// Get the fractional raw moment of Poisson process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn poisson_frac_raw_moment(
    lambda_: f64,
    duration: f64,
    order: f64,
    particles: usize,
) -> XPyResult<f64> {
    let poisson: Poisson<f64, f64> = Poisson::new(lambda_)?;
    let result = poisson.frac_raw_moment(duration, order, particles)?;
    Ok(result)
}

/// Get the fractional central moment of Poisson process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn poisson_frac_central_moment(
    lambda_: f64,
    duration: f64,
    order: f64,
    particles: usize,
) -> XPyResult<f64> {
    let poisson: Poisson<f64, f64> = Poisson::new(lambda_)?;
    let result = poisson.frac_central_moment(duration, order, particles)?;
    Ok(result)
}

/// Get the first passage time of Poisson process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn poisson_fpt(lambda_: f64, domain: (f64, f64), max_duration: f64) -> XPyResult<Option<f64>> {
    let poisson: Poisson<f64, f64> = Poisson::new(lambda_)?;
    let result = poisson.fpt(domain, max_duration)?;
    Ok(result)
}

/// Get the raw moment of the first passage time of Poisson process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn poisson_fpt_raw_moment(
    lambda_: f64,
    domain: (f64, f64),
    max_duration: f64,
    order: i32,
    particles: usize,
) -> XPyResult<Option<f64>> {
    let poisson: Poisson<f64, f64> = Poisson::new(lambda_)?;
    let fpt = FirstPassageTime::new(&poisson, domain)?;
    let result = fpt.raw_moment_p(order, particles, max_duration)?;
    Ok(result)
}

/// Get the central moment of the first passage time of Poisson process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn poisson_fpt_central_moment(
    lambda_: f64,
    domain: (f64, f64),
    max_duration: f64,
    order: i32,
    particles: usize,
) -> XPyResult<Option<f64>> {
    let poisson: Poisson<f64, f64> = Poisson::new(lambda_)?;
    let fpt = FirstPassageTime::new(&poisson, domain)?;
    let result = fpt.central_moment_p(order, particles, max_duration)?;
    Ok(result)
}

/// Get the occupation time of Poisson process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn poisson_occupation_time(lambda_: f64, domain: (f64, f64), duration: f64) -> XPyResult<f64> {
    let poisson: Poisson<f64, f64> = Poisson::new(lambda_)?;
    let result = poisson.occupation_time(domain, duration)?;
    Ok(result)
}

/// Get the raw moment of the occupation time of Poisson process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn poisson_occupation_time_raw_moment(
    lambda_: f64,
    domain: (f64, f64),
    duration: f64,
    order: i32,
    particles: usize,
) -> XPyResult<f64> {
    let poisson: Poisson<f64, f64> = Poisson::new(lambda_)?;
    let oc = OccupationTime::new(&poisson, domain, duration)?;
    let result = oc.raw_moment_p(order, particles)?;
    Ok(result)
}

/// Get the central moment of the occupation time of Poisson process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn poisson_occupation_time_central_moment(
    lambda_: f64,
    domain: (f64, f64),
    duration: f64,
    order: i32,
    particles: usize,
) -> XPyResult<f64> {
    let poisson: Poisson<f64, f64> = Poisson::new(lambda_)?;
    let oc = OccupationTime::new(&poisson, domain, duration)?;
    let result = oc.central_moment_p(order, particles)?;
    Ok(result)
}

/// Get the mean of Poisson process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn poisson_mean(lambda_: f64, duration: f64, particles: usize) -> XPyResult<f64> {
    let poisson: Poisson<f64, f64> = Poisson::new(lambda_)?;
    let result = poisson.mean(duration, particles)?;
    Ok(result)
}

/// Get the msd of Poisson process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn poisson_msd(lambda_: f64, duration: f64, particles: usize) -> XPyResult<f64> {
    let poisson: Poisson<f64, f64> = Poisson::new(lambda_)?;
    let result = poisson.msd(duration, particles)?;
    Ok(result)
}
