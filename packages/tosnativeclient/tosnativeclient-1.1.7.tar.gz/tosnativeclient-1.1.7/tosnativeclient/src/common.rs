use pyo3::{pyfunction, PyResult, Python};

#[pyfunction]
#[pyo3(signature = (seconds, file_path, image_width=1200))]
pub fn async_write_profile(
    py: Python<'_>,
    seconds: i64,
    file_path: String,
    image_width: usize,
) -> PyResult<()> {
    tosnativeclient_core::common::async_write_profile(seconds, file_path.as_str(), image_width);
    Ok(())
}

#[pyfunction]
#[pyo3(signature = (directives, directory, file_name_prefix))]
pub fn init_tracing_log(
    py: Python<'_>,
    directives: String,
    directory: String,
    file_name_prefix: String,
) -> PyResult<()> {
    tosnativeclient_core::common::init_tracing_log(directives, directory, file_name_prefix);
    Ok(())
}
