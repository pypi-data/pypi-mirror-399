use pyo3::prelude::*;
use pyo3::types::PyBytes;

mod commands;
mod compress;
mod constants;
mod decompress;
mod error;
mod io;

pub use compress::compress;
pub use decompress::decompress;
pub use error::Lzkn64Error;

#[pyfunction]
#[pyo3(name = "compress")]
fn compress_py<'py>(py: Python<'py>, input: &[u8]) -> PyResult<Bound<'py, PyBytes>> {
    let compressed = compress(input)?;   
    Ok(PyBytes::new(py, &compressed))
}

#[pyfunction]
#[pyo3(name = "decompress")]
fn decompress_py<'py>(py: Python<'py>, input: &[u8]) -> PyResult<Bound<'py, PyBytes>> {
    let decompressed = decompress(input)?;
    Ok(PyBytes::new(py, &decompressed))
}

#[pymodule]
fn lzkn64(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(compress_py, m)?)?;
    m.add_function(wrap_pyfunction!(decompress_py, m)?)?;

    Ok(())
}