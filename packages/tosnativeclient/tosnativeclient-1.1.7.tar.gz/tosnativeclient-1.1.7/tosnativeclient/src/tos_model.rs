use pyo3::types::PyTuple;
use pyo3::{pyclass, pymethods, Bound, IntoPyObject, PyRef, PyResult};
use std::collections::VecDeque;

#[pyclass(name = "ListObjectsResult", module = "tosnativeclient")]
pub struct ListObjectsResult {
    #[pyo3(get)]
    pub(crate) contents: Vec<TosObject>,
    #[pyo3(get)]
    pub(crate) common_prefixes: Vec<String>,
}

impl ListObjectsResult {
    pub(crate) fn new(
        objects: VecDeque<tosnativeclient_core::tos_model::TosObject>,
        common_prefixes: Option<Vec<String>>,
    ) -> Self {
        let mut contents = Vec::with_capacity(objects.len());
        for object in objects {
            contents.push(TosObject {
                bucket: object.bucket().to_string(),
                key: object.key().to_string(),
                size: object.size(),
                etag: object.etag().to_string(),
            });
        }

        match common_prefixes {
            None => Self {
                contents,
                common_prefixes: vec![],
            },
            Some(common_prefixes) => Self {
                contents,
                common_prefixes,
            },
        }
    }
}

#[derive(Clone)]
#[pyclass(name = "TosObject", module = "tosnativeclient")]
pub struct TosObject {
    #[pyo3(get)]
    pub(crate) bucket: String,
    #[pyo3(get)]
    pub(crate) key: String,
    #[pyo3(get)]
    pub(crate) size: isize,
    #[pyo3(get)]
    pub(crate) etag: String,
}

#[pymethods]
impl TosObject {
    #[new]
    #[pyo3(signature = (bucket, key, size, etag))]
    pub fn new(bucket: String, key: String, size: isize, etag: String) -> Self {
        Self {
            bucket,
            key,
            size,
            etag,
        }
    }
    pub fn __getnewargs__(slf: PyRef<'_, Self>) -> PyResult<Bound<'_, PyTuple>> {
        let py = slf.py();
        let state = [
            slf.bucket.clone().into_pyobject(py)?.into_any(),
            slf.key.clone().into_pyobject(py)?.into_any(),
            slf.size.into_pyobject(py)?.into_any(),
            slf.etag.clone().into_pyobject(py)?.into_any(),
        ];
        PyTuple::new(py, state)
    }
}
