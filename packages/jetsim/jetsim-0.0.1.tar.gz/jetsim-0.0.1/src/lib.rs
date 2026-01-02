//! JetSim - Fast Air Traffic Simulator
//!
//! A high-performance air traffic simulator written in Rust.
//!
//! Full implementation coming soon. See <https://github.com/open-aviation/jetsim>

/// Placeholder - full implementation coming soon
pub fn version() -> &'static str {
    "0.0.1"
}

#[cfg(feature = "python")]
mod python {
    use pyo3::prelude::*;

    #[pyfunction]
    fn version() -> &'static str {
        "0.0.1"
    }

    #[pymodule]
    fn jetsim(m: &Bound<'_, PyModule>) -> PyResult<()> {
        m.add_function(wrap_pyfunction!(version, m)?)?;
        Ok(())
    }
}
