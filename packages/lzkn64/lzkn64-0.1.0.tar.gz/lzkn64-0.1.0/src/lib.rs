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

#[pymodule]
fn lzkn64(_py: Python, m: &PyModule) -> PyResult<()> {
    #[pyfn(m)]
    #[pyo3(name = "compress")]
    fn compress_py(py: Python, input: &[u8]) -> PyResult<PyObject> {
        let compressed = compress(input).map_err(PyErr::from)?;
        Ok(PyBytes::new(py, &compressed).into())
    }

    #[pyfn(m)]
    #[pyo3(name = "decompress")]
    fn decompress_py(py: Python, input: &[u8]) -> PyResult<PyObject> {
        let decompressed = decompress(input).map_err(PyErr::from)?;
        Ok(PyBytes::new(py, &decompressed).into())
    }

    Ok(())
}
