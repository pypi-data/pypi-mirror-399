use crate::common::{BufferPool, TokenAcquirer};
use crate::list_stream::ListStream;
use crate::read_stream::ReadStream;
use crate::tos_model::TosObject;
use crate::write_stream::WriteStream;
use async_trait::async_trait;
use futures_util::future::BoxFuture;
use std::future::Future;
use std::sync::atomic::{AtomicIsize, Ordering};
use std::sync::Arc;
use std::thread;
use std::time::Duration;
use tokio::runtime::{Builder, Handle, Runtime};
use ve_tos_rust_sdk::asynchronous::bucket::BucketAPI;
use ve_tos_rust_sdk::asynchronous::object::ObjectAPI;
use ve_tos_rust_sdk::asynchronous::tos;
use ve_tos_rust_sdk::asynchronous::tos::{AsyncRuntime, TosClientImpl};
use ve_tos_rust_sdk::bucket::{CreateBucketInput, CreateBucketOutput};
use ve_tos_rust_sdk::credential::{CommonCredentials, CommonCredentialsProvider};
use ve_tos_rust_sdk::error::{GenericError, TosError};
use ve_tos_rust_sdk::object::HeadObjectInput;

#[derive(Debug, Default)]
pub struct TokioRuntime {
    pub(crate) runtime: Option<Arc<Runtime>>,
}

#[async_trait]
impl AsyncRuntime for TokioRuntime {
    type JoinError = tokio::task::JoinError;
    async fn sleep(&self, duration: Duration) {
        tokio::time::sleep(duration).await;
    }

    fn spawn<'a, F>(&self, future: F) -> BoxFuture<'a, Result<F::Output, Self::JoinError>>
    where
        F: Future + Send + 'static,
        F::Output: Send + 'static,
    {
        match self.runtime.as_ref() {
            None => Box::pin(Handle::current().spawn(future)),
            Some(r) => Box::pin(r.spawn(future)),
        }
    }

    fn block_on<F: Future>(&self, future: F) -> F::Output {
        match self.runtime.as_ref() {
            None => Handle::current().block_on(future),
            Some(r) => r.block_on(future),
        }
    }
}

pub(crate) type InnerTosClient =
    TosClientImpl<CommonCredentialsProvider<CommonCredentials>, CommonCredentials, TokioRuntime>;

pub struct TosClient {
    rclient: Arc<InnerTosClient>,
    wclient: Arc<InnerTosClient>,
    runtime: Arc<Runtime>,
    pcontext: Arc<SharedPrefetchContext>,
    sta: Arc<Option<TokenAcquirer>>,
    buffer_pool: BufferPool,

    region: String,
    endpoint: String,
    ak: String,
    sk: String,
    part_size: isize,
    max_retry_count: isize,
    max_prefetch_tasks: isize,
    shared_prefetch_tasks: isize,
    max_upload_part_tasks: isize,
    shared_upload_part_tasks: isize,
    enable_crc: bool,
}

impl TosClient {
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
        max_worker_threads: isize,
        dns_cache_async_refresh: bool,
    ) -> Result<Arc<Self>, TosError> {
        let mut builder = Builder::new_multi_thread();
        if max_worker_threads > 0 {
            builder.worker_threads(max_worker_threads as usize);
        } else if let Ok(max_worker_threads) = thread::available_parallelism() {
            builder.worker_threads(max_worker_threads.get());
        } else {
            builder.worker_threads(16);
        }
        match builder.enable_all().build() {
            Err(ex) => Err(TosError::TosClientError {
                message: "build runtime error".to_string(),
                cause: Some(GenericError::DefaultError(ex.to_string())),
                request_url: "".to_string(),
            }),
            Ok(runtime) => {
                let runtime = Arc::new(runtime);
                let mut clients = Vec::with_capacity(2);
                for _ in 0..2 {
                    match tos::builder()
                        .connection_timeout(3000)
                        .request_timeout(120000)
                        .max_connections(10000)
                        .max_retry_count(max_retry_count)
                        .ak(ak.clone())
                        .sk(sk.clone())
                        .region(region.clone())
                        .dns_cache_async_refresh(dns_cache_async_refresh)
                        .endpoint(endpoint.clone())
                        .enable_crc(enable_crc)
                        .async_runtime(TokioRuntime {
                            runtime: Some(runtime.clone()),
                        })
                        .build()
                    {
                        Err(ex) => return Err(ex),
                        Ok(client) => {
                            clients.push(client);
                        }
                    }
                }

                let sta;
                if shared_upload_part_tasks > 0 {
                    sta = Some(TokenAcquirer::new(shared_upload_part_tasks));
                } else {
                    sta = None;
                }

                Ok(Arc::new(Self {
                    rclient: Arc::new(clients.pop().unwrap()),
                    wclient: Arc::new(clients.pop().unwrap()),
                    runtime,
                    pcontext: Arc::new(SharedPrefetchContext::new(shared_prefetch_tasks)),
                    sta: Arc::new(sta),
                    buffer_pool: BufferPool::new(0, 0),
                    region,
                    endpoint,
                    ak,
                    sk,
                    part_size,
                    max_retry_count,
                    max_prefetch_tasks,
                    shared_prefetch_tasks,
                    max_upload_part_tasks,
                    shared_upload_part_tasks,
                    enable_crc,
                }))
            }
        }
    }

    pub fn list_objects(
        self: &Arc<Self>,
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
        ListStream::new(
            self.rclient.clone(),
            self.runtime.clone(),
            self.clone(),
            bucket,
            prefix,
            delimiter,
            max_keys,
            continuation_token,
            start_after,
            list_background_buffer_count,
            prefetch_concurrency,
            distributed_info,
        )
    }

    pub fn head_object(&self, bucket: String, key: String) -> Result<TosObject, TosError> {
        let input = HeadObjectInput::new(bucket, key);
        self.runtime.block_on(async {
            match self.rclient.head_object(&input).await {
                Err(ex) => Err(ex),
                Ok(output) => Ok(TosObject::inner_new(input.bucket(), input.key(), output)),
            }
        })
    }

    pub async fn async_head_object(
        &self,
        bucket: String,
        key: String,
    ) -> Result<TosObject, TosError> {
        let input = HeadObjectInput::new(bucket, key);
        match self.rclient.head_object(&input).await {
            Err(ex) => Err(ex),
            Ok(output) => Ok(TosObject::inner_new(input.bucket(), input.key(), output)),
        }
    }

    pub fn batch_get_objects(
        &self,
        objects: Vec<(String, String, Option<String>, Option<isize>)>,
        prefetch_concurrency: isize,
        fetch_etag_size: bool,
    ) -> Result<Vec<ReadStream>, TosError> {
        self.runtime.block_on(async {
            self.async_batch_get_objects(objects, prefetch_concurrency, fetch_etag_size)
                .await
        })
    }

    pub async fn async_batch_get_objects(
        &self,
        objects: Vec<(String, String, Option<String>, Option<isize>)>,
        prefetch_concurrency: isize,
        fetch_etag_size: bool,
    ) -> Result<Vec<ReadStream>, TosError> {
        let client = self.rclient.clone();
        let runtime = self.runtime.clone();
        let pcontext = self.pcontext.clone();
        let part_size = self.part_size;
        let max_prefetch_tasks = self.max_prefetch_tasks;
        let mut ta = None;
        if prefetch_concurrency > 0 {
            ta = Some(Arc::new(TokenAcquirer::new(prefetch_concurrency)));
        }
        let mut read_streams = Vec::with_capacity(objects.len());
        for object in objects {
            let mut etag = object.2;
            let mut size = object.3;
            if fetch_etag_size {
                if etag.is_none() || size.is_none() {
                    let output = client
                        .head_object(&HeadObjectInput::new(object.0.clone(), object.1.clone()))
                        .await?;
                    etag = Some(output.etag().to_string());
                    size = Some(output.content_length() as isize);
                }
            }
            let read_stream = ReadStream::new(
                client.clone(),
                runtime.clone(),
                pcontext.clone(),
                object.0,
                object.1,
                etag,
                size,
                part_size,
                max_prefetch_tasks,
            );
            if let Some(_ta) = ta.as_ref() {
                read_stream
                    .trigger_first_fetch_task(Some((Some(_ta.clone()), None)))
                    .await;
            }
            read_streams.push(read_stream);
        }
        Ok(read_streams)
    }

    pub fn get_object(
        &self,
        bucket: String,
        key: String,
        etag: Option<String>,
        size: Option<isize>,
        preload: bool,
    ) -> ReadStream {
        self.runtime.block_on(async {
            self.async_get_object(bucket, key, etag, size, preload)
                .await
        })
    }

    pub async fn async_get_object(
        &self,
        bucket: String,
        key: String,
        etag: Option<String>,
        size: Option<isize>,
        preload: bool,
    ) -> ReadStream {
        let client = self.rclient.clone();
        let runtime = self.runtime.clone();
        let pcontext = self.pcontext.clone();
        let part_size = self.part_size;
        let max_prefetch_tasks = self.max_prefetch_tasks;
        let read_stream = ReadStream::new(
            client,
            runtime,
            pcontext,
            bucket,
            key,
            etag,
            size,
            part_size,
            max_prefetch_tasks,
        );
        if preload {
            read_stream.trigger_first_fetch_task(None).await;
        }

        read_stream
    }

    pub fn put_object(
        &self,
        bucket: String,
        key: String,
        storage_class: Option<String>,
    ) -> Result<WriteStream, TosError> {
        self.runtime
            .block_on(async { self.async_put_object(bucket, key, storage_class).await })
    }

    pub async fn async_put_object(
        &self,
        bucket: String,
        key: String,
        storage_class: Option<String>,
    ) -> Result<WriteStream, TosError> {
        let client = self.wclient.clone();
        let runtime = self.runtime.clone();
        let part_size = self.part_size;
        let max_upload_part_tasks = self.max_upload_part_tasks;
        let sta = self.sta.clone();
        let buffer_pool = self.buffer_pool.clone();
        WriteStream::new(
            client,
            runtime,
            bucket,
            key,
            storage_class,
            part_size,
            max_upload_part_tasks,
            sta,
            buffer_pool,
        )
        .await
    }

    pub fn create_bucket(&self, bucket: String) -> Result<CreateBucketOutput, TosError> {
        let client = self.wclient.clone();
        self.runtime
            .block_on(async { client.create_bucket(&CreateBucketInput::new(bucket)).await })
    }

    pub fn get_async_runtime(&self) -> Arc<Runtime> {
        self.runtime.clone()
    }

    pub async fn async_close(&self) {
        self.rclient.shutdown().await;
        self.wclient.shutdown().await;
    }

    pub fn close(&self) {
        self.runtime.block_on(async {
            self.async_close().await;
        })
    }

    pub(crate) fn wclient(&self) -> Arc<InnerTosClient> {
        self.wclient.clone()
    }

    pub(crate) fn rclient(&self) -> Arc<InnerTosClient> {
        self.rclient.clone()
    }
}

pub(crate) struct SharedPrefetchContext {
    stolen_shared_prefetch_tasks: AtomicIsize,
    shared_prefetch_tasks: isize,
}

impl SharedPrefetchContext {
    pub(crate) fn new(shared_prefetch_tasks: isize) -> Self {
        Self {
            stolen_shared_prefetch_tasks: AtomicIsize::new(0),
            shared_prefetch_tasks,
        }
    }

    pub(crate) fn try_steal_shared_prefetch_task(&self) -> bool {
        loop {
            let current = self.stolen_shared_prefetch_tasks.load(Ordering::Acquire);
            if current >= self.shared_prefetch_tasks {
                return false;
            }
            if let Ok(_) = self.stolen_shared_prefetch_tasks.compare_exchange(
                current,
                current + 1,
                Ordering::AcqRel,
                Ordering::Relaxed,
            ) {
                return true;
            }
        }
    }

    pub(crate) fn release_shared_prefetch_task(&self) {
        self.stolen_shared_prefetch_tasks
            .fetch_add(-1, Ordering::Release);
    }
}

#[cfg(test)]
mod tests {
    use crate::tos_client::TosClient;
    use rand::Rng;
    use scopeguard::defer;
    use std::env;
    use std::sync::Arc;
    use ve_tos_rust_sdk::asynchronous::bucket::BucketAPI;
    use ve_tos_rust_sdk::asynchronous::multipart::MultipartAPI;
    use ve_tos_rust_sdk::asynchronous::object::ObjectAPI;
    use ve_tos_rust_sdk::bucket::DeleteBucketInput;
    use ve_tos_rust_sdk::multipart::{AbortMultipartUploadInput, ListMultipartUploadsInput};
    use ve_tos_rust_sdk::object::{DeleteObjectInput, ListObjectsType2Input};

    #[test]
    fn test_single_object() {
        let ak = env::var("TOS_ACCESS_KEY").unwrap_or("".to_string());
        let sk = env::var("TOS_SECRET_KEY").unwrap_or("".to_string());
        let ep = env::var("TOS_ENDPOINT").unwrap_or("".to_string());
        let mut client = TosClient::new(
            "test-region".to_string(),
            ep,
            ak,
            sk,
            5 * 1024 * 1024,
            3,
            1,
            32,
            true,
            1,
            32,
            0,
            true,
        )
        .unwrap();
        let bucket = create_bucket(client.clone());
        defer! {
           clean_bucket(client.clone(), &bucket);
        }

        let key = gen_random_string(8);
        let ws = client
            .put_object(bucket.clone(), key.clone(), None)
            .unwrap();
        for i in 0..3 {
            let size = ws.write("helloworld".as_bytes()).unwrap();
            assert_eq!(size, "helloworld".len() as isize);
        }
        ws.close().unwrap();

        let om = client.head_object(bucket.clone(), key.clone()).unwrap();
        assert_eq!(om.size, ("helloworld".len() * 3) as isize);

        let rs = client.get_object(
            bucket.clone(),
            key.clone(),
            Some(om.etag),
            Some(om.size),
            false,
        );
        let mut content = Vec::with_capacity(om.size as usize);
        let mut offset = 0;
        loop {
            let data = rs.read(offset, 3, true).unwrap();
            if data.is_none() {
                break;
            }
            let data = data.unwrap();
            content.extend_from_slice(&data);
            offset += data.len() as isize;
        }
        assert_eq!(offset, om.size);
        assert_eq!(content, "helloworld".repeat(3).as_bytes());

        client.close();
    }

    #[test]
    fn test_multi_objects() {}

    fn create_bucket(client: Arc<TosClient>) -> String {
        let mut fixed_bucket;
        loop {
            fixed_bucket = gen_random_string(10);
            match client.create_bucket(fixed_bucket.clone()) {
                Ok(_) => {
                    return fixed_bucket;
                }
                Err(e) => {
                    if !e.is_server_error() {
                        panic!("{}", e.to_string());
                    }

                    let ex = e.as_server_error().unwrap();
                    if ex.status_code() != 409 {
                        panic!("unexpected status code, {}", ex.code());
                    }
                }
            }
        }
    }

    fn gen_random_string(len: usize) -> String {
        let mut result = String::with_capacity(len);
        let characters = "0123456789abcdefghijklmnopqrstuvwxyz".as_bytes();
        let mut ra = rand::thread_rng();
        for _ in 0..len {
            let a = ra.gen_range(0..characters.len());
            result.push(characters[a] as char);
        }

        result
    }

    fn clean_bucket(client: Arc<TosClient>, bucket: &str) {
        let runtime = client.get_async_runtime();
        let client = client.wclient();
        runtime.block_on(async {
            let mut can_delete_bucket = true;
            let mut input = ListObjectsType2Input::new(bucket);
            input.set_max_keys(1000);
            'outer: loop {
                match client.list_objects_type2(&input).await {
                    Ok(o) => {
                        for content in o.contents() {
                            if let Err(_) = client
                                .delete_object(&DeleteObjectInput::new(bucket, content.key()))
                                .await
                            {
                                can_delete_bucket = false;
                                break 'outer;
                            }
                        }

                        if !o.is_truncated() {
                            break;
                        }

                        input.set_continuation_token(o.next_continuation_token());
                    }
                    Err(_) => {
                        can_delete_bucket = false;
                        break;
                    }
                }
            }

            let mut input = ListMultipartUploadsInput::new(bucket);
            input.set_max_uploads(1000);
            'outer: loop {
                match client.list_multipart_uploads(&input).await {
                    Ok(o) => {
                        for upload in o.uploads() {
                            if let Err(_) = client
                                .abort_multipart_upload(&AbortMultipartUploadInput::new(
                                    bucket,
                                    upload.key(),
                                    upload.upload_id(),
                                ))
                                .await
                            {
                                can_delete_bucket = false;
                                break 'outer;
                            }
                        }

                        if !o.is_truncated() {
                            break;
                        }

                        input.set_upload_id_marker(o.next_upload_id_marker());
                        input.set_key_marker(o.next_key_marker());
                    }
                    Err(_) => {
                        can_delete_bucket = false;
                        break;
                    }
                }
            }

            if can_delete_bucket {
                let _ = client.delete_bucket(&DeleteBucketInput::new(bucket)).await;
            }
        });
    }
}
