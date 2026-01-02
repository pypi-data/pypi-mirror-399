use numpy::PyReadonlyArray1;
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

/// Perform linear regression on the provided data points.
///
/// # Arguments
///
/// * `data` - An array of f64 numbers. It must be non-empty, have an even number of elements,
///   and contain NaN or infinite.
///
/// # Returns
///
/// A vector (mapped to a list in Python) of tuples. The first element of a tuple is the name
/// of the output quantity, and the second element is the value.
#[pyfunction]
fn do_linear_regression(data: PyReadonlyArray1<f64>) -> PyResult<Vec<(&'static str, f64)>> {
    let slice = data
        .as_slice()
        .map_err(|_| PyValueError::new_err("Input array must be contiguous"))?;
    if slice.is_empty() {
        return Err(PyValueError::new_err("Input array must be non-empty"));
    }
    if slice.len() % 2 != 0 {
        return Err(PyValueError::new_err("Input array must have an even number of elements"));
    }
    if slice.iter().any(|x| x.is_nan() || x.is_infinite()) {
        return Err(PyValueError::new_err("Input array must not contain NaN or infinite values"));
    }
    let r = linear_regression::do_linear_regression(slice);
    Ok(r.iter().map(|(k, v)| (k, v)).collect())
}

#[pymodule]
fn linear_regression_python_bindings(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(do_linear_regression, m)?)?;
    Ok(())
}
