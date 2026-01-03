use crate::list_stream::ListStream;
use crate::read_stream::ReadStream;
use crate::tos_error::map_tos_error;
use crate::tos_model::TosObject;
use crate::write_stream::WriteStream;
use pyo3::types::PyTuple;
use pyo3::{pyclass, pymethods, Bound, IntoPyObject, IntoPyObjectExt, PyRef, PyResult};
use std::sync::{Arc, RwLock};
use ve_tos_rust_sdk::error::TosError;

#[pyclass(name = "TosClient", module = "tosnativeclient")]
pub struct TosClient {
    pub(crate) client: Arc<tosnativeclient_core::tos_client::TosClient>,
    #[pyo3(get)]
    pub(crate) region: String,
    #[pyo3(get)]
    pub(crate) endpoint: String,
    #[pyo3(get)]
    pub(crate) ak: String,
    #[pyo3(get)]
    pub(crate) sk: String,
    #[pyo3(get)]
    pub(crate) part_size: isize,
    #[pyo3(get)]
    pub(crate) max_retry_count: isize,
    #[pyo3(get)]
    pub(crate) max_prefetch_tasks: isize,
    #[pyo3(get)]
    pub(crate) shared_prefetch_tasks: isize,
    #[pyo3(get)]
    pub(crate) enable_crc: bool,
    #[pyo3(get)]
    pub(crate) max_upload_part_tasks: isize,
    #[pyo3(get)]
    pub(crate) shared_upload_part_tasks: isize,
    #[pyo3(get)]
    pub(crate) dns_cache_async_refresh: bool,
}

#[pymethods]
impl TosClient {
    #[new]
    #[pyo3(signature = (region, endpoint, ak=String::from(""), sk=String::from(""), part_size=8388608, max_retry_count=3, max_prefetch_tasks=3,
    shared_prefetch_tasks=32, enable_crc=true, max_upload_part_tasks=3, shared_upload_part_tasks=32, dns_cache_async_refresh=false))]
    pub fn new(
        region: String,
        endpoint: String,
        ak: String,
        sk: String,
        part_size: isize,
        max_retry_count: isize,
        max_prefetch_tasks: isize,
        shared_prefetch_tasks: isize,
        enable_crc: bool,
        max_upload_part_tasks: isize,
        shared_upload_part_tasks: isize,
        dns_cache_async_refresh: bool,
    ) -> PyResult<Self> {
        match tosnativeclient_core::tos_client::TosClient::new(
            region.clone(),
            endpoint.clone(),
            ak.clone(),
            sk.clone(),
            part_size,
            max_retry_count,
            max_prefetch_tasks,
            shared_prefetch_tasks,
            enable_crc,
            max_upload_part_tasks,
            shared_upload_part_tasks,
            0,
            dns_cache_async_refresh,
        ) {
            Err(ex) => Err(map_tos_error(ex)),
            Ok(client) => Ok(Self {
                client,
                region,
                endpoint,
                ak,
                sk,
                part_size,
                max_retry_count,
                max_prefetch_tasks,
                shared_prefetch_tasks,
                enable_crc,
                max_upload_part_tasks,
                shared_upload_part_tasks,
                dns_cache_async_refresh,
            }),
        }
    }

    #[pyo3(signature = (bucket, prefix=String::from(""), max_keys=1000, delimiter=String::from(""),
    continuation_token=String::from(""), start_after=String::from(""), list_background_buffer_count=1, prefetch_concurrency=0, distributed_info=None))]
    pub fn list_objects(
        slf: PyRef<'_, Self>,
        bucket: String,
        prefix: String,
        max_keys: isize,
        delimiter: String,
        continuation_token: String,
        start_after: String,
        list_background_buffer_count: isize,
        prefetch_concurrency: isize,
        distributed_info: Option<(isize, isize, isize, isize)>,
    ) -> ListStream {
        let client = slf.client.clone();
        slf.py().allow_threads(|| {
            let list_stream = client.list_objects(
                bucket.to_string(),
                prefix.to_string(),
                max_keys,
                delimiter.to_string(),
                continuation_token.to_string(),
                start_after.to_string(),
                list_background_buffer_count,
                prefetch_concurrency,
                distributed_info,
            );

            ListStream {
                list_stream: Arc::new(list_stream),
                bucket,
                prefix,
                delimiter,
                max_keys,
                continuation_token,
                start_after,
                list_background_buffer_count,
                prefetch_concurrency,
            }
        })
    }
    #[pyo3(signature = (bucket, key))]
    pub fn head_object(slf: PyRef<'_, Self>, bucket: String, key: String) -> PyResult<TosObject> {
        let client = slf.client.clone();
        slf.py()
            .allow_threads(|| match client.head_object(bucket, key) {
                Err(ex) => Err(map_tos_error(ex)),
                Ok(output) => Ok(TosObject::new(
                    output.bucket().to_string(),
                    output.key().to_string(),
                    output.size(),
                    output.etag().to_string(),
                )),
            })
    }
    #[pyo3(signature = (objects, prefetch_concurrency=0, fetch_etag_size=false))]
    pub fn batch_get_objects(
        slf: PyRef<'_, Self>,
        objects: Vec<(String, String, Option<String>, Option<isize>)>,
        prefetch_concurrency: isize,
        fetch_etag_size: bool,
    ) -> PyResult<Vec<ReadStream>> {
        let client = slf.client.clone();
        slf.py().allow_threads(|| {
            match client.batch_get_objects(objects, prefetch_concurrency, fetch_etag_size) {
                Err(ex) => Err(map_tos_error(ex)),
                Ok(result) => {
                    let mut read_streams = Vec::with_capacity(result.len());
                    for read_stream in result {
                        let bucket = read_stream.bucket().to_string();
                        let key = read_stream.key().to_string();
                        read_streams.push(ReadStream {
                            read_stream: Arc::new(read_stream),
                            bucket,
                            key,
                        });
                    }
                    Ok(read_streams)
                }
            }
        })
    }

    #[pyo3(signature = (bucket, key, etag=None, size=None, preload=false))]
    pub fn get_object(
        slf: PyRef<'_, Self>,
        bucket: String,
        key: String,
        etag: Option<String>,
        size: Option<isize>,
        preload: bool,
    ) -> ReadStream {
        let client = slf.client.clone();
        slf.py().allow_threads(|| {
            let read_stream = client.get_object(bucket.clone(), key.clone(), etag, size, preload);
            ReadStream {
                read_stream: Arc::new(read_stream),
                bucket,
                key,
            }
        })
    }

    #[pyo3(signature = (bucket, key, storage_class=None))]
    pub fn put_object(
        slf: PyRef<'_, Self>,
        bucket: String,
        key: String,
        storage_class: Option<String>,
    ) -> PyResult<WriteStream> {
        let client = slf.client.clone();
        slf.py().allow_threads(|| {
            match client.put_object(bucket.clone(), key.clone(), storage_class.clone()) {
                Err(ex) => Err(map_tos_error(ex)),
                Ok(write_stream) => Ok(WriteStream {
                    write_stream: Arc::new(write_stream),
                    bucket,
                    key,
                    storage_class,
                }),
            }
        })
    }

    pub fn close(slf: PyRef<'_, Self>) {
        let client = slf.client.clone();
        slf.py().allow_threads(|| client.close());
    }

    pub fn __getnewargs__(slf: PyRef<'_, Self>) -> PyResult<Bound<'_, PyTuple>> {
        let py = slf.py();
        let state = [
            slf.region.clone().into_pyobject(py)?.into_any(),
            slf.endpoint.clone().into_pyobject(py)?.into_any(),
            slf.ak.clone().into_pyobject(py)?.into_any(),
            slf.sk.clone().into_pyobject(py)?.into_any(),
            slf.part_size.into_pyobject(py)?.into_any(),
            slf.max_retry_count.into_pyobject(py)?.into_any(),
            slf.max_prefetch_tasks.into_pyobject(py)?.into_any(),
            slf.shared_prefetch_tasks.into_pyobject(py)?.into_any(),
            slf.enable_crc.into_py_any(py)?.bind(py).to_owned(),
            slf.max_upload_part_tasks.into_pyobject(py)?.into_any(),
            slf.shared_upload_part_tasks.into_pyobject(py)?.into_any(),
            slf.dns_cache_async_refresh
                .into_py_any(py)?
                .bind(py)
                .to_owned(),
        ];
        PyTuple::new(py, state)
    }
}
