use crate::read_stream::ReadStream;
use crate::tos_error::map_tos_error;
use crate::tos_model::ListObjectsResult;
use pyo3::{pyclass, pymethods, PyRef, PyResult};
use std::collections::VecDeque;
use std::sync::Arc;

#[pyclass(name = "ListStream", module = "tosnativeclient")]
pub struct ListStream {
    pub(crate) list_stream: Arc<tosnativeclient_core::list_stream::ListStream>,
    #[pyo3(get)]
    pub(crate) bucket: String,
    #[pyo3(get)]
    pub(crate) prefix: String,
    #[pyo3(get)]
    pub(crate) delimiter: String,
    #[pyo3(get)]
    pub(crate) max_keys: isize,
    #[pyo3(get)]
    pub(crate) continuation_token: String,
    #[pyo3(get)]
    pub(crate) start_after: String,
    #[pyo3(get)]
    pub(crate) list_background_buffer_count: isize,
    #[pyo3(get)]
    pub(crate) prefetch_concurrency: isize,
}

#[pymethods]
impl ListStream {
    pub fn __iter__(slf: PyRef<'_, Self>) -> PyRef<'_, Self> {
        slf
    }

    pub fn __next__(
        slf: PyRef<'_, Self>,
    ) -> PyResult<Option<(ListObjectsResult, Option<Vec<ReadStream>>)>> {
        let list_stream = slf.list_stream.clone();
        slf.py().allow_threads(|| match list_stream.next() {
            Ok(data) => match data {
                None => Ok(None),
                Some(output) => Ok(Some(trans_list_objects_result(output))),
            },
            Err(ex) => Err(map_tos_error(ex)),
        })
    }

    pub fn close(slf: PyRef<'_, Self>) {
        let list_stream = slf.list_stream.clone();
        slf.py().allow_threads(|| {
            list_stream.close();
        });
    }

    pub fn current_prefix(slf: PyRef<'_, Self>) -> PyResult<Option<String>> {
        let list_stream = slf.list_stream.clone();
        slf.py()
            .allow_threads(|| match list_stream.current_prefix() {
                Ok(prefix) => Ok(prefix),
                Err(ex) => Err(map_tos_error(ex)),
            })
    }

    pub fn current_continuation_token(slf: PyRef<'_, Self>) -> PyResult<Option<String>> {
        let list_stream = slf.list_stream.clone();
        slf.py()
            .allow_threads(|| match list_stream.current_continuation_token() {
                Ok(prefix) => Ok(prefix),
                Err(ex) => Err(map_tos_error(ex)),
            })
    }
}

fn trans_list_objects_result(
    output: (
        VecDeque<tosnativeclient_core::tos_model::TosObject>,
        Option<Vec<String>>,
        Option<Vec<tosnativeclient_core::read_stream::ReadStream>>,
    ),
) -> (ListObjectsResult, Option<Vec<ReadStream>>) {
    match output.2 {
        None => (ListObjectsResult::new(output.0, output.1), None),
        Some(streams) => {
            let mut read_streams = Vec::with_capacity(streams.len());
            for stream in streams {
                let bucket = stream.bucket().to_string();
                let key = stream.key().to_string();
                read_streams.push(ReadStream {
                    read_stream: Arc::new(stream),
                    bucket,
                    key,
                });
            }
            (
                ListObjectsResult::new(output.0, output.1),
                Some(read_streams),
            )
        }
    }
}
