use crate::{XPyResult, simulation::PyArrayPair};
use gauss_quad::GaussLegendre;
use numpy::PyArrayMethods;
use pyo3::prelude::*;
#[cfg(feature = "stub_gen")]
use pyo3_stub_gen::derive::gen_stub_pyfunction;
use rayon::prelude::*;
use std::sync::Arc;

#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn moment(
    py: Python<'_>,
    simulate_fn: Py<PyAny>,
    central: bool,
    order: i32,
    duration: f64,
    time_step: f64,
    particles: usize,
) -> f64 {
    if central {
        central_moment(py, simulate_fn, order, duration, time_step, particles)
    } else {
        raw_moment(py, simulate_fn, order, duration, time_step, particles)
    }
}

#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn mean(
    py: Python<'_>,
    simulate_fn: Py<PyAny>,
    duration: f64,
    time_step: f64,
    particles: usize,
) -> f64 {
    let simulate = Arc::new(simulate_fn.clone_ref(py));

    let value = (0..particles)
        .into_par_iter()
        .map(|_| {
            Python::attach(|py| {
                let (_, x) = simulate
                    .call_method1(py, "simulate", (duration, time_step))
                    .expect("Failed to call simulate method")
                    .extract::<PyArrayPair<'_>>(py)
                    .expect("Failed to extract simulate result");

                *x.to_vec()
                    .expect("Failed to convert position array to Vec")
                    .last()
                    .ok_or("Failed to get last element")
                    .unwrap()
            })
        })
        .sum::<f64>();

    value / particles as f64
}

#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn msd(
    py: Python<'_>,
    simulate_fn: Py<PyAny>,
    duration: f64,
    time_step: f64,
    particles: usize,
) -> f64 {
    let simulate = Arc::new(simulate_fn.clone_ref(py));

    let value = (0..particles)
        .into_par_iter()
        .map(|_| {
            Python::attach(|py| {
                let (_, x) = simulate
                    .call_method1(py, "simulate", (duration, time_step))
                    .expect("Failed to call simulate method")
                    .extract::<PyArrayPair<'_>>(py)
                    .expect("Failed to extract simulate result");

                let x_vec = x.to_vec().expect("Failed to convert position array to Vec");

                let end = *x_vec.last().ok_or("Failed to get last element").unwrap();
                let start = *x_vec.first().ok_or("Failed to get first element").unwrap();
                (end - start) * (end - start)
            })
        })
        .sum::<f64>();

    value / particles as f64
}

#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn tamsd(
    py: Python<'_>,
    simulate_fn: Py<PyAny>,
    duration: f64,
    delta: f64,
    time_step: f64,
    quad_order: usize,
) -> XPyResult<f64> {
    let simulate = Arc::new(simulate_fn.clone_ref(py));

    let legendre_quad = GaussLegendre::new(quad_order)?;
    let nodes_weights_pairs = legendre_quad.into_node_weight_pairs();
    let nodes_weights = nodes_weights_transform(0.0, duration - delta, &nodes_weights_pairs);
    let result = nodes_weights
        .into_par_iter()
        .map(|(node, weight)| -> f64 {
            Python::attach(|py| {
                let (_, x) = simulate
                    .call_method1(py, "simulate", (node + delta, time_step))
                    .expect("Failed to call simulate method")
                    .extract::<PyArrayPair<'_>>(py)
                    .expect("Failed to extract simulate result");

                let x_vec = x.to_vec().expect("Failed to convert position array to Vec");

                let slag_length = (delta / time_step).ceil() as usize;

                let len = x_vec.len();
                let end_position = x_vec.last();
                let slag_position = x_vec.get(len - slag_length - 1);
                if end_position.is_none() || slag_position.is_none() {
                    panic!("Failed to get last element or slag position");
                }
                let end_position = *end_position.unwrap();
                let slag_position = *slag_position.unwrap();

                (end_position - slag_position) * (end_position - slag_position) * weight
            })
        })
        .sum::<f64>()
        / (duration - delta);
    Ok(result)
}

#[cfg_attr(feature = "stub_gen", gen_stub_pyfunction)]
#[pyfunction]
pub fn eatamsd(
    py: Python<'_>,
    simulate_fn: Py<PyAny>,
    duration: f64,
    delta: f64,
    particles: usize,
    time_step: f64,
    quad_order: usize,
) -> f64 {
    let simulate = Arc::new(simulate_fn.clone_ref(py));

    (0..particles)
        .into_par_iter()
        .map(|_| {
            let legendre_quad =
                GaussLegendre::new(quad_order).expect("Failed to create legendre quad");
            let nodes_weights_pairs = legendre_quad.into_node_weight_pairs();
            let nodes_weights =
                nodes_weights_transform(0.0, duration - delta, &nodes_weights_pairs);
            nodes_weights
                .into_par_iter()
                .map(|(node, weight)| -> f64 {
                    Python::attach(|py| {
                        let (_, x) = simulate
                            .call_method1(py, "simulate", (node + delta, time_step))
                            .expect("Failed to call simulate method")
                            .extract::<PyArrayPair<'_>>(py)
                            .expect("Failed to extract simulate result");

                        let x_vec = x.to_vec().expect("Failed to convert position array to Vec");

                        let slag_length = (delta / time_step).ceil() as usize;

                        let len = x_vec.len();
                        let end_position = x_vec.last();
                        let slag_position = x_vec.get(len - slag_length - 1);
                        if end_position.is_none() || slag_position.is_none() {
                            panic!("Failed to get last element or slag position");
                        }
                        let end_position = *end_position.unwrap();
                        let slag_position = *slag_position.unwrap();

                        (end_position - slag_position) * (end_position - slag_position) * weight
                    })
                })
                .sum::<f64>()
                / (duration - delta)
        })
        .sum::<f64>()
        / particles as f64
}

fn raw_moment(
    py: Python<'_>,
    simulate_fn: Py<PyAny>,
    order: i32,
    duration: f64,
    time_step: f64,
    particles: usize,
) -> f64 {
    let simulate = Arc::new(simulate_fn.clone_ref(py));

    let value = (0..particles)
        .into_par_iter()
        .map(|_| {
            Python::attach(|py| {
                let (_, x) = simulate
                    .call_method1(py, "simulate", (duration, time_step))
                    .expect("Failed to call simulate method")
                    .extract::<PyArrayPair<'_>>(py)
                    .expect("Failed to extract simulate result");

                let end = *x
                    .to_vec()
                    .expect("Failed to convert position array to Vec")
                    .last()
                    .ok_or("Failed to get last element")
                    .unwrap();
                if order == 1 { end } else { end.powi(order) }
            })
        })
        .sum::<f64>();

    value / particles as f64
}

fn central_moment(
    py: Python<'_>,
    simulate_fn: Py<PyAny>,
    order: i32,
    duration: f64,
    time_step: f64,
    particles: usize,
) -> f64 {
    let mean = raw_moment(
        py,
        simulate_fn.clone_ref(py),
        1,
        duration,
        time_step,
        particles,
    );

    let simulate = Arc::new(simulate_fn.clone_ref(py));

    let value = (0..particles)
        .into_par_iter()
        .map(|_| {
            Python::attach(|py| {
                let (_, x) = simulate
                    .call_method1(py, "simulate", (duration, time_step))
                    .expect("Failed to call simulate method")
                    .extract::<PyArrayPair<'_>>(py)
                    .expect("Failed to extract simulate result");

                let end = *x
                    .to_vec()
                    .expect("Failed to convert position array to Vec")
                    .last()
                    .ok_or("Failed to get last element")
                    .unwrap();
                if order == 1 {
                    end - mean
                } else {
                    (end - mean).powi(order)
                }
            })
        })
        .sum::<f64>();

    value / particles as f64
}

fn nodes_weights_transform(
    a: impl Into<f64>,
    b: impl Into<f64>,
    pairs: &[(f64, f64)],
) -> Vec<(f64, f64)> {
    let a: f64 = a.into();
    let b: f64 = b.into();
    pairs
        .iter()
        .map(|(node, weight)| {
            let new_weight = weight * (b - a) / 2.0;
            let new_node = (b - a) * node / 2.0 + (b + a) / 2.0;
            (new_node, new_weight)
        })
        .collect()
}
