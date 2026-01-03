use pyo3::prelude::*;

/// A Python module implemented in Rust. The name of this module must match
/// the `lib.name` setting in the `Cargo.toml`, else Python will not be able to
/// import the module.
#[pymodule]
mod _core {
    use pyo3::prelude::*;

    #[pyfunction]
    fn hello_from_bin(py: Python) -> PyResult<String> {
        let version = py
            .import("importlib.metadata")?
            .call_method1("version", ("acu",))?
            .extract::<String>()?;
        Ok(format!("Hello from acu:{}", version))
    }
}
