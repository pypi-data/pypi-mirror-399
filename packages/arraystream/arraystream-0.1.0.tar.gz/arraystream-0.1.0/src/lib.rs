use pyo3::prelude::*;

mod numeric;
mod grouping;

use numeric::{scan, diff, pairwise, clip};
use grouping::{run_length_encode, groupby_runs};

/// Python module for array stream transformations
#[pymodule]
fn _arraystream(_py: Python, m: &PyModule) -> PyResult<()> {
    // Numeric operations
    m.add_function(wrap_pyfunction!(scan, m)?)?;
    m.add_function(wrap_pyfunction!(diff, m)?)?;
    m.add_function(wrap_pyfunction!(pairwise, m)?)?;
    m.add_function(wrap_pyfunction!(clip, m)?)?;

    // Grouping operations
    m.add_function(wrap_pyfunction!(run_length_encode, m)?)?;
    m.add_function(wrap_pyfunction!(groupby_runs, m)?)?;

    Ok(())
}

