use crate::{
    XPyResult,
    simulation::{PyArrayPair, call_py_func, vec_to_pyarray},
};
use diffusionx::simulation::{
    continuous::{GeneralizedLangevin, Langevin, SubordinatedLangevin},
    prelude::*,
};
use pyo3::prelude::*;
#[cfg(feature = "stub_gen")]
use pyo3_stub_gen::derive::gen_stub_pyfunction;

/// Simulate Langevin process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn langevin_simulate(
    py: Python<'_>,
    drift_func: Py<PyAny>,
    diffusion_func: Py<PyAny>,
    start_position: f64,
    duration: f64,
    time_step: f64,
) -> XPyResult<PyArrayPair<'_>> {
    let langevin = {
        let drift = |x: f64, t: f64| -> f64 { call_py_func(&drift_func, (x, t)) };

        let diffusion = |x: f64, t: f64| -> f64 { call_py_func(&diffusion_func, (x, t)) };

        Langevin::new(drift, diffusion, start_position)?
    };

    let (times, positions) = langevin.simulate(duration, time_step)?;

    Ok(vec_to_pyarray(py, times, positions))
}

/// Get the raw moment of Langevin process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn langevin_raw_moment(
    drift_func: Py<PyAny>,
    diffusion_func: Py<PyAny>,
    start_position: f64,
    duration: f64,
    order: i32,
    particles: usize,
    time_step: f64,
) -> XPyResult<f64> {
    let langevin = {
        let drift = |x: f64, t: f64| -> f64 { call_py_func(&drift_func, (x, t)) };

        let diffusion = |x: f64, t: f64| -> f64 { call_py_func(&diffusion_func, (x, t)) };

        Langevin::new(drift, diffusion, start_position)?
    };

    let result = langevin.raw_moment(duration, order, particles, time_step)?;
    Ok(result)
}

/// Get the central moment of Langevin process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn langevin_central_moment(
    drift_func: Py<PyAny>,
    diffusion_func: Py<PyAny>,
    start_position: f64,
    duration: f64,
    order: i32,
    particles: usize,
    time_step: f64,
) -> XPyResult<f64> {
    let langevin = {
        let drift = |x: f64, t: f64| -> f64 { call_py_func(&drift_func, (x, t)) };

        let diffusion = |x: f64, t: f64| -> f64 { call_py_func(&diffusion_func, (x, t)) };

        Langevin::new(drift, diffusion, start_position)?
    };

    let result = langevin.central_moment(duration, order, particles, time_step)?;
    Ok(result)
}

/// Get the fractional raw moment of Langevin process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn langevin_frac_raw_moment(
    drift_func: Py<PyAny>,
    diffusion_func: Py<PyAny>,
    start_position: f64,
    duration: f64,
    order: f64,
    particles: usize,
    time_step: f64,
) -> XPyResult<f64> {
    let langevin = {
        let drift = |x: f64, t: f64| -> f64 { call_py_func(&drift_func, (x, t)) };

        let diffusion = |x: f64, t: f64| -> f64 { call_py_func(&diffusion_func, (x, t)) };

        Langevin::new(drift, diffusion, start_position)?
    };

    let result = langevin.frac_raw_moment(duration, order, particles, time_step)?;
    Ok(result)
}

/// Get the fractional central moment of Langevin process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn langevin_frac_central_moment(
    drift_func: Py<PyAny>,
    diffusion_func: Py<PyAny>,
    start_position: f64,
    duration: f64,
    order: f64,
    particles: usize,
    time_step: f64,
) -> XPyResult<f64> {
    let langevin = {
        let drift = |x: f64, t: f64| -> f64 { call_py_func(&drift_func, (x, t)) };

        let diffusion = |x: f64, t: f64| -> f64 { call_py_func(&diffusion_func, (x, t)) };

        Langevin::new(drift, diffusion, start_position)?
    };

    let result = langevin.frac_central_moment(duration, order, particles, time_step)?;
    Ok(result)
}

/// Get the first passage time of Langevin process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn langevin_fpt(
    drift_func: Py<PyAny>,
    diffusion_func: Py<PyAny>,
    start_position: f64,
    domain: (f64, f64),
    max_duration: f64,
    time_step: f64,
) -> XPyResult<Option<f64>> {
    let langevin = {
        let drift = |x: f64, t: f64| -> f64 { call_py_func(&drift_func, (x, t)) };

        let diffusion = |x: f64, t: f64| -> f64 { call_py_func(&diffusion_func, (x, t)) };

        Langevin::new(drift, diffusion, start_position)?
    };

    let result = langevin.fpt(domain, max_duration, time_step)?;
    Ok(result)
}

/// Get the raw moment of the first passage time of Langevin process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn langevin_fpt_raw_moment(
    drift_func: Py<PyAny>,
    diffusion_func: Py<PyAny>,
    start_position: f64,
    domain: (f64, f64),
    max_duration: f64,
    order: i32,
    particles: usize,
    time_step: f64,
) -> XPyResult<Option<f64>> {
    let langevin = {
        let drift = |x: f64, t: f64| -> f64 { call_py_func(&drift_func, (x, t)) };

        let diffusion = |x: f64, t: f64| -> f64 { call_py_func(&diffusion_func, (x, t)) };

        Langevin::new(drift, diffusion, start_position)?
    };
    let fpt = FirstPassageTime::new(&langevin, domain)?;
    let result = fpt.raw_moment(order, particles, max_duration, time_step)?;
    Ok(result)
}

/// Get the central moment of the first passage time of Langevin process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn langevin_fpt_central_moment(
    drift_func: Py<PyAny>,
    diffusion_func: Py<PyAny>,
    start_position: f64,
    domain: (f64, f64),
    max_duration: f64,
    order: i32,
    particles: usize,
    time_step: f64,
) -> XPyResult<Option<f64>> {
    let langevin = {
        let drift = |x: f64, t: f64| -> f64 { call_py_func(&drift_func, (x, t)) };

        let diffusion = |x: f64, t: f64| -> f64 { call_py_func(&diffusion_func, (x, t)) };

        Langevin::new(drift, diffusion, start_position)?
    };
    let fpt = FirstPassageTime::new(&langevin, domain)?;
    let result = fpt.central_moment(order, particles, max_duration, time_step)?;
    Ok(result)
}

/// Get the occupation time of Langevin process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn langevin_occupation_time(
    drift_func: Py<PyAny>,
    diffusion_func: Py<PyAny>,
    start_position: f64,
    domain: (f64, f64),
    duration: f64,
    time_step: f64,
) -> XPyResult<f64> {
    let langevin = {
        let drift = |x: f64, t: f64| -> f64 { call_py_func(&drift_func, (x, t)) };

        let diffusion = |x: f64, t: f64| -> f64 { call_py_func(&diffusion_func, (x, t)) };

        Langevin::new(drift, diffusion, start_position)?
    };
    let result = langevin.occupation_time(domain, duration, time_step)?;
    Ok(result)
}

/// Get the raw moment of the occupation time of Langevin process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn langevin_occupation_time_raw_moment(
    drift_func: Py<PyAny>,
    diffusion_func: Py<PyAny>,
    start_position: f64,
    domain: (f64, f64),
    duration: f64,
    order: i32,
    particles: usize,
    time_step: f64,
) -> XPyResult<f64> {
    let langevin = {
        let drift = |x: f64, t: f64| -> f64 { call_py_func(&drift_func, (x, t)) };

        let diffusion = |x: f64, t: f64| -> f64 { call_py_func(&diffusion_func, (x, t)) };

        Langevin::new(drift, diffusion, start_position)?
    };
    let oc = OccupationTime::new(&langevin, domain, duration)?;
    let result = oc.raw_moment(order, particles, time_step)?;
    Ok(result)
}

/// Get the central moment of the occupation time of Langevin process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn langevin_occupation_time_central_moment(
    drift_func: Py<PyAny>,
    diffusion_func: Py<PyAny>,
    start_position: f64,
    domain: (f64, f64),
    duration: f64,
    order: i32,
    particles: usize,
    time_step: f64,
) -> XPyResult<f64> {
    let langevin = {
        let drift = |x: f64, t: f64| -> f64 { call_py_func(&drift_func, (x, t)) };

        let diffusion = |x: f64, t: f64| -> f64 { call_py_func(&diffusion_func, (x, t)) };

        Langevin::new(drift, diffusion, start_position)?
    };
    let oc = OccupationTime::new(&langevin, domain, duration)?;
    let result = oc.central_moment(order, particles, time_step)?;
    Ok(result)
}

/// Get the time-averaged mean squared displacement of Langevin process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn langevin_tamsd(
    drift_func: Py<PyAny>,
    diffusion_func: Py<PyAny>,
    start_position: f64,
    duration: f64,
    delta: f64,
    time_step: f64,
    quad_order: usize,
) -> XPyResult<f64> {
    let langevin = {
        let drift = |x: f64, t: f64| -> f64 { call_py_func(&drift_func, (x, t)) };

        let diffusion = |x: f64, t: f64| -> f64 { call_py_func(&diffusion_func, (x, t)) };

        Langevin::new(drift, diffusion, start_position)?
    };
    let result = langevin.tamsd(duration, delta, time_step, quad_order)?;
    Ok(result)
}

/// Get the effective time-averaged mean squared displacement of Langevin process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn langevin_eatamsd(
    drift_func: Py<PyAny>,
    diffusion_func: Py<PyAny>,
    start_position: f64,
    duration: f64,
    delta: f64,
    particles: usize,
    time_step: f64,
    quad_order: usize,
) -> XPyResult<f64> {
    let langevin = {
        let drift = |x: f64, t: f64| -> f64 { call_py_func(&drift_func, (x, t)) };

        let diffusion = |x: f64, t: f64| -> f64 { call_py_func(&diffusion_func, (x, t)) };

        Langevin::new(drift, diffusion, start_position)?
    };
    let result = langevin.eatamsd(duration, delta, particles, time_step, quad_order)?;
    Ok(result)
}

/// Get the mean of Langevin process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn langevin_mean(
    drift_func: Py<PyAny>,
    diffusion_func: Py<PyAny>,
    start_position: f64,
    duration: f64,
    particles: usize,
    time_step: f64,
) -> XPyResult<f64> {
    let langevin = {
        let drift = |x: f64, t: f64| -> f64 { call_py_func(&drift_func, (x, t)) };

        let diffusion = |x: f64, t: f64| -> f64 { call_py_func(&diffusion_func, (x, t)) };

        Langevin::new(drift, diffusion, start_position)?
    };
    let result = langevin.mean(duration, particles, time_step)?;
    Ok(result)
}

/// Get the msd of Langevin process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn langevin_msd(
    drift_func: Py<PyAny>,
    diffusion_func: Py<PyAny>,
    start_position: f64,
    duration: f64,
    particles: usize,
    time_step: f64,
) -> XPyResult<f64> {
    let langevin = {
        let drift = |x: f64, t: f64| -> f64 { call_py_func(&drift_func, (x, t)) };

        let diffusion = |x: f64, t: f64| -> f64 { call_py_func(&diffusion_func, (x, t)) };

        Langevin::new(drift, diffusion, start_position)?
    };
    let result = langevin.msd(duration, particles, time_step)?;
    Ok(result)
}

/// Py function wrapper for GeneralizedLangevin simulation
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn generalized_langevin_simulate(
    py: Python<'_>,
    drift_func: Py<PyAny>,
    diffusion_func: Py<PyAny>,
    start_position: f64,
    alpha: f64,
    duration: f64,
    time_step: f64,
) -> XPyResult<PyArrayPair<'_>> {
    let langevin = {
        let drift = |x: f64, t: f64| -> f64 { call_py_func(&drift_func, (x, t)) };

        let diffusion = |x: f64, t: f64| -> f64 { call_py_func(&diffusion_func, (x, t)) };

        GeneralizedLangevin::new(drift, diffusion, start_position, alpha)?
    };

    let (times, positions) = langevin.simulate(duration, time_step)?;

    Ok(vec_to_pyarray(py, times, positions))
}

/// Get the raw moment of GeneralizedLangevin process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn generalized_langevin_raw_moment(
    drift_func: Py<PyAny>,
    diffusion_func: Py<PyAny>,
    start_position: f64,
    alpha: f64,
    duration: f64,
    order: i32,
    particles: usize,
    time_step: f64,
) -> XPyResult<f64> {
    let langevin = {
        let drift = |x: f64, t: f64| -> f64 { call_py_func(&drift_func, (x, t)) };

        let diffusion = |x: f64, t: f64| -> f64 { call_py_func(&diffusion_func, (x, t)) };

        GeneralizedLangevin::new(drift, diffusion, start_position, alpha)?
    };

    let result = langevin.raw_moment(duration, order, particles, time_step)?;
    Ok(result)
}

/// Get the central moment of GeneralizedLangevin process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn generalized_langevin_central_moment(
    drift_func: Py<PyAny>,
    diffusion_func: Py<PyAny>,
    start_position: f64,
    alpha: f64,
    duration: f64,
    order: i32,
    particles: usize,
    time_step: f64,
) -> XPyResult<f64> {
    let langevin = {
        let drift = |x: f64, t: f64| -> f64 { call_py_func(&drift_func, (x, t)) };

        let diffusion = |x: f64, t: f64| -> f64 { call_py_func(&diffusion_func, (x, t)) };

        GeneralizedLangevin::new(drift, diffusion, start_position, alpha)?
    };

    let result = langevin.central_moment(duration, order, particles, time_step)?;
    Ok(result)
}

/// Get the fractional raw moment of GeneralizedLangevin process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn generalized_langevin_frac_raw_moment(
    drift_func: Py<PyAny>,
    diffusion_func: Py<PyAny>,
    start_position: f64,
    alpha: f64,
    duration: f64,
    order: f64,
    particles: usize,
    time_step: f64,
) -> XPyResult<f64> {
    let langevin = {
        let drift = |x: f64, t: f64| -> f64 { call_py_func(&drift_func, (x, t)) };

        let diffusion = |x: f64, t: f64| -> f64 { call_py_func(&diffusion_func, (x, t)) };

        GeneralizedLangevin::new(drift, diffusion, start_position, alpha)?
    };

    let result = langevin.frac_raw_moment(duration, order, particles, time_step)?;
    Ok(result)
}

/// Get the fractional central moment of GeneralizedLangevin process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn generalized_langevin_frac_central_moment(
    drift_func: Py<PyAny>,
    diffusion_func: Py<PyAny>,
    start_position: f64,
    alpha: f64,
    duration: f64,
    order: f64,
    particles: usize,
    time_step: f64,
) -> XPyResult<f64> {
    let langevin = {
        let drift = |x: f64, t: f64| -> f64 { call_py_func(&drift_func, (x, t)) };

        let diffusion = |x: f64, t: f64| -> f64 { call_py_func(&diffusion_func, (x, t)) };

        GeneralizedLangevin::new(drift, diffusion, start_position, alpha)?
    };

    let result = langevin.frac_central_moment(duration, order, particles, time_step)?;
    Ok(result)
}

/// Get the first passage time of GeneralizedLangevin process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn generalized_langevin_fpt(
    drift_func: Py<PyAny>,
    diffusion_func: Py<PyAny>,
    start_position: f64,
    alpha: f64,
    domain: (f64, f64),
    max_duration: f64,
    time_step: f64,
) -> XPyResult<Option<f64>> {
    let langevin = {
        let drift = |x: f64, t: f64| -> f64 { call_py_func(&drift_func, (x, t)) };

        let diffusion = |x: f64, t: f64| -> f64 { call_py_func(&diffusion_func, (x, t)) };

        GeneralizedLangevin::new(drift, diffusion, start_position, alpha)?
    };

    let result = langevin.fpt(domain, max_duration, time_step)?;
    Ok(result)
}

/// Get the raw moment of the first passage time of GeneralizedLangevin process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn generalized_langevin_fpt_raw_moment(
    drift_func: Py<PyAny>,
    diffusion_func: Py<PyAny>,
    start_position: f64,
    alpha: f64,
    domain: (f64, f64),
    max_duration: f64,
    order: i32,
    particles: usize,
    time_step: f64,
) -> XPyResult<Option<f64>> {
    let langevin = {
        let drift = |x: f64, t: f64| -> f64 { call_py_func(&drift_func, (x, t)) };

        let diffusion = |x: f64, t: f64| -> f64 { call_py_func(&diffusion_func, (x, t)) };

        GeneralizedLangevin::new(drift, diffusion, start_position, alpha)?
    };
    let fpt = FirstPassageTime::new(&langevin, domain)?;
    let result = fpt.raw_moment(order, particles, max_duration, time_step)?;
    Ok(result)
}

/// Get the central moment of the first passage time of GeneralizedLangevin process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn generalized_langevin_fpt_central_moment(
    drift_func: Py<PyAny>,
    diffusion_func: Py<PyAny>,
    start_position: f64,
    alpha: f64,
    domain: (f64, f64),
    max_duration: f64,
    order: i32,
    particles: usize,
    time_step: f64,
) -> XPyResult<Option<f64>> {
    let langevin = {
        let drift = |x: f64, t: f64| -> f64 { call_py_func(&drift_func, (x, t)) };

        let diffusion = |x: f64, t: f64| -> f64 { call_py_func(&diffusion_func, (x, t)) };

        GeneralizedLangevin::new(drift, diffusion, start_position, alpha)?
    };
    let fpt = FirstPassageTime::new(&langevin, domain)?;
    let result = fpt.central_moment(order, particles, max_duration, time_step)?;
    Ok(result)
}

/// Get the occupation time of GeneralizedLangevin process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn generalized_langevin_occupation_time(
    drift_func: Py<PyAny>,
    diffusion_func: Py<PyAny>,
    start_position: f64,
    alpha: f64,
    domain: (f64, f64),
    duration: f64,
    time_step: f64,
) -> XPyResult<f64> {
    let langevin = {
        let drift = |x: f64, t: f64| -> f64 { call_py_func(&drift_func, (x, t)) };

        let diffusion = |x: f64, t: f64| -> f64 { call_py_func(&diffusion_func, (x, t)) };

        GeneralizedLangevin::new(drift, diffusion, start_position, alpha)?
    };
    let result = langevin.occupation_time(domain, duration, time_step)?;
    Ok(result)
}

/// Get the raw moment of the occupation time of GeneralizedLangevin process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn generalized_langevin_occupation_time_raw_moment(
    drift_func: Py<PyAny>,
    diffusion_func: Py<PyAny>,
    start_position: f64,
    alpha: f64,
    domain: (f64, f64),
    duration: f64,
    order: i32,
    particles: usize,
    time_step: f64,
) -> XPyResult<f64> {
    let langevin = {
        let drift = |x: f64, t: f64| -> f64 { call_py_func(&drift_func, (x, t)) };

        let diffusion = |x: f64, t: f64| -> f64 { call_py_func(&diffusion_func, (x, t)) };

        GeneralizedLangevin::new(drift, diffusion, start_position, alpha)?
    };
    let oc = OccupationTime::new(&langevin, domain, duration)?;
    let result = oc.raw_moment(order, particles, time_step)?;
    Ok(result)
}

/// Get the central moment of the occupation time of GeneralizedLangevin process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn generalized_langevin_occupation_time_central_moment(
    drift_func: Py<PyAny>,
    diffusion_func: Py<PyAny>,
    start_position: f64,
    alpha: f64,
    domain: (f64, f64),
    duration: f64,
    order: i32,
    particles: usize,
    time_step: f64,
) -> XPyResult<f64> {
    let langevin = {
        let drift = |x: f64, t: f64| -> f64 { call_py_func(&drift_func, (x, t)) };

        let diffusion = |x: f64, t: f64| -> f64 { call_py_func(&diffusion_func, (x, t)) };

        GeneralizedLangevin::new(drift, diffusion, start_position, alpha)?
    };
    let oc = OccupationTime::new(&langevin, domain, duration)?;
    let result = oc.central_moment(order, particles, time_step)?;
    Ok(result)
}

/// Get the time-averaged mean squared displacement of GeneralizedLangevin process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn generalized_langevin_tamsd(
    drift_func: Py<PyAny>,
    diffusion_func: Py<PyAny>,
    start_position: f64,
    alpha: f64,
    duration: f64,
    delta: f64,
    time_step: f64,
    quad_order: usize,
) -> XPyResult<f64> {
    let langevin = {
        let drift = |x: f64, t: f64| -> f64 { call_py_func(&drift_func, (x, t)) };

        let diffusion = |x: f64, t: f64| -> f64 { call_py_func(&diffusion_func, (x, t)) };

        GeneralizedLangevin::new(drift, diffusion, start_position, alpha)?
    };
    let result = langevin.tamsd(duration, delta, time_step, quad_order)?;
    Ok(result)
}

/// Get the effective time-averaged mean squared displacement of GeneralizedLangevin process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn generalized_langevin_eatamsd(
    drift_func: Py<PyAny>,
    diffusion_func: Py<PyAny>,
    start_position: f64,
    alpha: f64,
    duration: f64,
    delta: f64,
    particles: usize,
    time_step: f64,
    quad_order: usize,
) -> XPyResult<f64> {
    let langevin = {
        let drift = |x: f64, t: f64| -> f64 { call_py_func(&drift_func, (x, t)) };

        let diffusion = |x: f64, t: f64| -> f64 { call_py_func(&diffusion_func, (x, t)) };

        GeneralizedLangevin::new(drift, diffusion, start_position, alpha)?
    };
    let result = langevin.eatamsd(duration, delta, particles, time_step, quad_order)?;
    Ok(result)
}

/// Get the mean of GeneralizedLangevin process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn generalized_langevin_mean(
    drift_func: Py<PyAny>,
    diffusion_func: Py<PyAny>,
    start_position: f64,
    alpha: f64,
    duration: f64,
    particles: usize,
    time_step: f64,
) -> XPyResult<f64> {
    let langevin = {
        let drift = |x: f64, t: f64| -> f64 { call_py_func(&drift_func, (x, t)) };

        let diffusion = |x: f64, t: f64| -> f64 { call_py_func(&diffusion_func, (x, t)) };

        GeneralizedLangevin::new(drift, diffusion, start_position, alpha)?
    };
    let result = langevin.mean(duration, particles, time_step)?;
    Ok(result)
}

/// Get the msd of GeneralizedLangevin process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn generalized_langevin_msd(
    drift_func: Py<PyAny>,
    diffusion_func: Py<PyAny>,
    start_position: f64,
    alpha: f64,
    duration: f64,
    particles: usize,
    time_step: f64,
) -> XPyResult<f64> {
    let langevin = {
        let drift = |x: f64, t: f64| -> f64 { call_py_func(&drift_func, (x, t)) };

        let diffusion = |x: f64, t: f64| -> f64 { call_py_func(&diffusion_func, (x, t)) };

        GeneralizedLangevin::new(drift, diffusion, start_position, alpha)?
    };
    let result = langevin.msd(duration, particles, time_step)?;
    Ok(result)
}

/// Simulate SubordinatedLangevin process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn subordinated_langevin_simulate(
    py: Python<'_>,
    drift_func: Py<PyAny>,
    diffusion_func: Py<PyAny>,
    start_position: f64,
    alpha: f64,
    duration: f64,
    time_step: f64,
) -> XPyResult<PyArrayPair<'_>> {
    let langevin = {
        let drift = |x: f64, t: f64| -> f64 { call_py_func(&drift_func, (x, t)) };

        let diffusion = |x: f64, t: f64| -> f64 { call_py_func(&diffusion_func, (x, t)) };

        SubordinatedLangevin::new(drift, diffusion, start_position, alpha)?
    };

    let (times, positions) = langevin.simulate(duration, time_step)?;

    Ok(vec_to_pyarray(py, times, positions))
}

/// Get the raw moment of SubordinatedLangevin process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn subordinated_langevin_raw_moment(
    drift_func: Py<PyAny>,
    diffusion_func: Py<PyAny>,
    start_position: f64,
    alpha: f64,
    duration: f64,
    order: i32,
    particles: usize,
    time_step: f64,
) -> XPyResult<f64> {
    let langevin = {
        let drift = |x: f64, t: f64| -> f64 { call_py_func(&drift_func, (x, t)) };

        let diffusion = |x: f64, t: f64| -> f64 { call_py_func(&diffusion_func, (x, t)) };

        SubordinatedLangevin::new(drift, diffusion, start_position, alpha)?
    };

    let result = langevin.raw_moment(duration, order, particles, time_step)?;
    Ok(result)
}

/// Get the central moment of SubordinatedLangevin process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn subordinated_langevin_central_moment(
    drift_func: Py<PyAny>,
    diffusion_func: Py<PyAny>,
    start_position: f64,
    alpha: f64,
    duration: f64,
    order: i32,
    particles: usize,
    time_step: f64,
) -> XPyResult<f64> {
    let langevin = {
        let drift = |x: f64, t: f64| -> f64 { call_py_func(&drift_func, (x, t)) };

        let diffusion = |x: f64, t: f64| -> f64 { call_py_func(&diffusion_func, (x, t)) };

        SubordinatedLangevin::new(drift, diffusion, start_position, alpha)?
    };

    let result = langevin.central_moment(duration, order, particles, time_step)?;
    Ok(result)
}

/// Get the fractional raw moment of SubordinatedLangevin process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn subordinated_langevin_frac_raw_moment(
    drift_func: Py<PyAny>,
    diffusion_func: Py<PyAny>,
    start_position: f64,
    alpha: f64,
    duration: f64,
    order: f64,
    particles: usize,
    time_step: f64,
) -> XPyResult<f64> {
    let langevin = {
        let drift = |x: f64, t: f64| -> f64 { call_py_func(&drift_func, (x, t)) };

        let diffusion = |x: f64, t: f64| -> f64 { call_py_func(&diffusion_func, (x, t)) };

        SubordinatedLangevin::new(drift, diffusion, start_position, alpha)?
    };

    let result = langevin.frac_raw_moment(duration, order, particles, time_step)?;
    Ok(result)
}

/// Get the fractional central moment of SubordinatedLangevin process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn subordinated_langevin_frac_central_moment(
    drift_func: Py<PyAny>,
    diffusion_func: Py<PyAny>,
    start_position: f64,
    alpha: f64,
    duration: f64,
    order: f64,
    particles: usize,
    time_step: f64,
) -> XPyResult<f64> {
    let langevin = {
        let drift = |x: f64, t: f64| -> f64 { call_py_func(&drift_func, (x, t)) };

        let diffusion = |x: f64, t: f64| -> f64 { call_py_func(&diffusion_func, (x, t)) };

        SubordinatedLangevin::new(drift, diffusion, start_position, alpha)?
    };

    let result = langevin.frac_central_moment(duration, order, particles, time_step)?;
    Ok(result)
}

/// Get the first passage time of SubordinatedLangevin process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn subordinated_langevin_fpt(
    drift_func: Py<PyAny>,
    diffusion_func: Py<PyAny>,
    start_position: f64,
    alpha: f64,
    domain: (f64, f64),
    max_duration: f64,
    time_step: f64,
) -> XPyResult<Option<f64>> {
    let langevin = {
        let drift = |x: f64, t: f64| -> f64 { call_py_func(&drift_func, (x, t)) };

        let diffusion = |x: f64, t: f64| -> f64 { call_py_func(&diffusion_func, (x, t)) };

        SubordinatedLangevin::new(drift, diffusion, start_position, alpha)?
    };

    let result = langevin.fpt(domain, max_duration, time_step)?;
    Ok(result)
}

/// Get the raw moment of the first passage time of SubordinatedLangevin process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn subordinated_langevin_fpt_raw_moment(
    drift_func: Py<PyAny>,
    diffusion_func: Py<PyAny>,
    start_position: f64,
    alpha: f64,
    domain: (f64, f64),
    max_duration: f64,
    order: i32,
    particles: usize,
    time_step: f64,
) -> XPyResult<Option<f64>> {
    let langevin = {
        let drift = |x: f64, t: f64| -> f64 { call_py_func(&drift_func, (x, t)) };

        let diffusion = |x: f64, t: f64| -> f64 { call_py_func(&diffusion_func, (x, t)) };

        SubordinatedLangevin::new(drift, diffusion, start_position, alpha)?
    };
    let fpt = FirstPassageTime::new(&langevin, domain)?;
    let result = fpt.raw_moment(order, particles, max_duration, time_step)?;
    Ok(result)
}

/// Get the central moment of the first passage time of SubordinatedLangevin process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn subordinated_langevin_fpt_central_moment(
    drift_func: Py<PyAny>,
    diffusion_func: Py<PyAny>,
    start_position: f64,
    alpha: f64,
    domain: (f64, f64),
    max_duration: f64,
    order: i32,
    particles: usize,
    time_step: f64,
) -> XPyResult<Option<f64>> {
    let langevin = {
        let drift = |x: f64, t: f64| -> f64 { call_py_func(&drift_func, (x, t)) };

        let diffusion = |x: f64, t: f64| -> f64 { call_py_func(&diffusion_func, (x, t)) };

        SubordinatedLangevin::new(drift, diffusion, start_position, alpha)?
    };
    let fpt = FirstPassageTime::new(&langevin, domain)?;
    let result = fpt.central_moment(order, particles, max_duration, time_step)?;
    Ok(result)
}

/// Get the occupation time of SubordinatedLangevin process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn subordinated_langevin_occupation_time(
    drift_func: Py<PyAny>,
    diffusion_func: Py<PyAny>,
    start_position: f64,
    alpha: f64,
    domain: (f64, f64),
    duration: f64,
    time_step: f64,
) -> XPyResult<f64> {
    let langevin = {
        let drift = |x: f64, t: f64| -> f64 { call_py_func(&drift_func, (x, t)) };

        let diffusion = |x: f64, t: f64| -> f64 { call_py_func(&diffusion_func, (x, t)) };

        SubordinatedLangevin::new(drift, diffusion, start_position, alpha)?
    };
    let result = langevin.occupation_time(domain, duration, time_step)?;
    Ok(result)
}

/// Get the raw moment of the occupation time of SubordinatedLangevin process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn subordinated_langevin_occupation_time_raw_moment(
    drift_func: Py<PyAny>,
    diffusion_func: Py<PyAny>,
    start_position: f64,
    alpha: f64,
    domain: (f64, f64),
    duration: f64,
    order: i32,
    particles: usize,
    time_step: f64,
) -> XPyResult<f64> {
    let langevin = {
        let drift = |x: f64, t: f64| -> f64 { call_py_func(&drift_func, (x, t)) };

        let diffusion = |x: f64, t: f64| -> f64 { call_py_func(&diffusion_func, (x, t)) };

        SubordinatedLangevin::new(drift, diffusion, start_position, alpha)?
    };
    let oc = OccupationTime::new(&langevin, domain, duration)?;
    let result = oc.raw_moment(order, particles, time_step)?;
    Ok(result)
}

/// Get the central moment of the occupation time of SubordinatedLangevin process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn subordinated_langevin_occupation_time_central_moment(
    drift_func: Py<PyAny>,
    diffusion_func: Py<PyAny>,
    start_position: f64,
    alpha: f64,
    domain: (f64, f64),
    duration: f64,
    order: i32,
    particles: usize,
    time_step: f64,
) -> XPyResult<f64> {
    let langevin = {
        let drift = |x: f64, t: f64| -> f64 { call_py_func(&drift_func, (x, t)) };

        let diffusion = |x: f64, t: f64| -> f64 { call_py_func(&diffusion_func, (x, t)) };

        SubordinatedLangevin::new(drift, diffusion, start_position, alpha)?
    };
    let oc = OccupationTime::new(&langevin, domain, duration)?;
    let result = oc.central_moment(order, particles, time_step)?;
    Ok(result)
}

/// Get the time-averaged mean squared displacement of SubordinatedLangevin process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn subordinated_langevin_tamsd(
    drift_func: Py<PyAny>,
    diffusion_func: Py<PyAny>,
    start_position: f64,
    alpha: f64,
    duration: f64,
    delta: f64,
    time_step: f64,
    quad_order: usize,
) -> XPyResult<f64> {
    let langevin = {
        let drift = |x: f64, t: f64| -> f64 { call_py_func(&drift_func, (x, t)) };

        let diffusion = |x: f64, t: f64| -> f64 { call_py_func(&diffusion_func, (x, t)) };

        SubordinatedLangevin::new(drift, diffusion, start_position, alpha)?
    };
    let result = langevin.tamsd(duration, delta, time_step, quad_order)?;
    Ok(result)
}

/// Get the effective time-averaged mean squared displacement of SubordinatedLangevin process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn subordinated_langevin_eatamsd(
    drift_func: Py<PyAny>,
    diffusion_func: Py<PyAny>,
    start_position: f64,
    alpha: f64,
    duration: f64,
    delta: f64,
    particles: usize,
    time_step: f64,
    quad_order: usize,
) -> XPyResult<f64> {
    let langevin = {
        let drift = |x: f64, t: f64| -> f64 { call_py_func(&drift_func, (x, t)) };

        let diffusion = |x: f64, t: f64| -> f64 { call_py_func(&diffusion_func, (x, t)) };

        SubordinatedLangevin::new(drift, diffusion, start_position, alpha)?
    };
    let result = langevin.eatamsd(duration, delta, particles, time_step, quad_order)?;
    Ok(result)
}

/// Get the mean of SubordinatedLangevin process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn subordinated_langevin_mean(
    drift_func: Py<PyAny>,
    diffusion_func: Py<PyAny>,
    start_position: f64,
    alpha: f64,
    duration: f64,
    particles: usize,
    time_step: f64,
) -> XPyResult<f64> {
    let langevin = {
        let drift = |x: f64, t: f64| -> f64 { call_py_func(&drift_func, (x, t)) };

        let diffusion = |x: f64, t: f64| -> f64 { call_py_func(&diffusion_func, (x, t)) };

        SubordinatedLangevin::new(drift, diffusion, start_position, alpha)?
    };
    let result = langevin.mean(duration, particles, time_step)?;
    Ok(result)
}

/// Get the msd of SubordinatedLangevin process.
#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn subordinated_langevin_msd(
    drift_func: Py<PyAny>,
    diffusion_func: Py<PyAny>,
    start_position: f64,
    alpha: f64,
    duration: f64,
    particles: usize,
    time_step: f64,
) -> XPyResult<f64> {
    let langevin = {
        let drift = |x: f64, t: f64| -> f64 { call_py_func(&drift_func, (x, t)) };

        let diffusion = |x: f64, t: f64| -> f64 { call_py_func(&diffusion_func, (x, t)) };

        SubordinatedLangevin::new(drift, diffusion, start_position, alpha)?
    };
    let result = langevin.msd(duration, particles, time_step)?;
    Ok(result)
}
