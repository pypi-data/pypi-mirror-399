use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum Lzkn64Error {
    #[error("Input buffer is empty or invalid size")]
    InvalidSize,

    #[error("Output buffer overflow")]
    OutputOverflow,

    #[error("Unexpected end of input data")]
    InputOverflow,

    #[error("Corrupt or invalid compressed data: {0}")]
    CorruptData(String),

    #[error("Invalid header in compressed data")]
    InvalidHeader,

    #[error("Interleaved/planar data (plane_count > 1) is not supported")]
    UnsupportedInterleaved,

    #[error("Compression error: {0}")]
    CompressionError(String),
}

// Map Rust errors to Python exceptions
impl From<Lzkn64Error> for PyErr {
    fn from(err: Lzkn64Error) -> PyErr {
        PyValueError::new_err(err.to_string())
    }
}
