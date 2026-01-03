use crate::common::TokenAcquirer;
use crate::tos_client::{InnerTosClient, SharedPrefetchContext};
use crate::tos_model::TosObject;
use async_channel::{Receiver, Sender};
use bytes::Bytes;
use futures_util::StreamExt;
use std::collections::LinkedList;
use std::num::ParseIntError;
use std::sync::atomic::{AtomicI8, AtomicIsize, Ordering};
use std::sync::Arc;
use tokio::runtime::Runtime;
use tokio::sync::{Mutex, MutexGuard, Notify, OwnedSemaphorePermit, RwLock};
use tokio::task::JoinHandle;
use tracing::log::{error, warn};
use ve_tos_rust_sdk::asynchronous::object::ObjectAPI;
use ve_tos_rust_sdk::error::TosError;
use ve_tos_rust_sdk::object::GetObjectInput;

const DEFAULT_PREFERRED_CHUNK_SIZE: isize = 128 * 1024;
const COMMON_IO_SIZE: isize = 1 * 1024 * 1024;
const DEFAULT_SEQUENTIAL_READ_THRESHOLD: isize = 3;
const DEFAULT_ONE_REQUEST_READ_BUFFER_LIMIT: isize = 100 * 1024 * 1024;
const DEFAULT_PART_SIZE: isize = 8 * 1024 * 1024;
const DEFAULT_FETCH_RETRY_COUNT: isize = 3;
const DEFAULT_SHARED_PREFETCH_TASK_LIMIT: isize = 100;
const DEFAULT_PREFETCH_TASKS: isize = 3;
pub struct ReadStream {
    object_fetcher: ObjectFetcher,
    runtime: Arc<Runtime>,
    object_info: Arc<ObjectInfo>,
}

impl ReadStream {
    pub fn read(
        &self,
        offset: isize,
        length: isize,
        read_once: bool,
    ) -> Result<Option<Bytes>, TosError> {
        match self
            .runtime
            .block_on(async { self.object_fetcher.read(offset, length, read_once).await })
        {
            Err(ex) => Err(ex),
            Ok(result) => match result {
                None => Ok(None),
                Some(mut data) => match data.take() {
                    Err(ex) => Err(ex),
                    Ok(data) => match data {
                        None => Ok(None),
                        Some(data) => Ok(Some(data)),
                    },
                },
            },
        }
    }

    pub async fn async_read(
        &self,
        offset: isize,
        length: isize,
        read_once: bool,
    ) -> Result<Option<Bytes>, TosError> {
        match self.object_fetcher.read(offset, length, read_once).await {
            Err(ex) => Err(ex),
            Ok(result) => match result {
                None => Ok(None),
                Some(mut data) => match data.take() {
                    Err(ex) => Err(ex),
                    Ok(data) => match data {
                        None => Ok(None),
                        Some(data) => Ok(Some(data)),
                    },
                },
            },
        }
    }

    pub fn close(&self) {
        self.runtime
            .block_on(async { self.object_fetcher.close().await })
    }

    pub fn is_closed(&self) -> bool {
        self.object_fetcher.is_closed()
    }

    pub async fn async_close(&self) {
        self.object_fetcher.close().await
    }

    pub fn bucket(&self) -> &str {
        self.object_info.bucket()
    }

    pub fn key(&self) -> &str {
        self.object_info.key()
    }

    pub fn etag(&self) -> String {
        self.runtime
            .block_on(async { self.object_info.etag().await })
    }

    pub fn size(&self) -> isize {
        self.runtime
            .block_on(async { self.object_info.size().await })
    }

    pub fn try_get_size(&self) -> Option<isize> {
        self.runtime
            .block_on(async { self.object_info.try_get_size().await })
    }

    pub fn try_get_etag(&self) -> Option<String> {
        self.runtime
            .block_on(async { self.object_info.try_get_etag().await })
    }

    pub(crate) async fn trigger_first_fetch_task(
        &self,
        ta: Option<(Option<Arc<TokenAcquirer>>, Option<OwnedSemaphorePermit>)>,
    ) {
        self.object_fetcher.trigger_first_fetch_task(ta).await;
    }

    pub(crate) fn new(
        client: Arc<InnerTosClient>,
        runtime: Arc<Runtime>,
        pcontext: Arc<SharedPrefetchContext>,
        bucket: String,
        key: String,
        etag: Option<String>,
        size: Option<isize>,
        part_size: isize,
        max_prefetch_tasks: isize,
    ) -> Self {
        let mut part_size = part_size;
        if part_size <= 0 {
            part_size = DEFAULT_PART_SIZE;
        }

        let mut max_prefetch_tasks = max_prefetch_tasks;
        if max_prefetch_tasks <= 0 {
            max_prefetch_tasks = DEFAULT_PREFETCH_TASKS;
        }

        let pc = PrefetchConfig {
            first_request_size: COMMON_IO_SIZE,
            max_request_size: part_size,
            sequential_prefetch_multiplier: 8,
            max_forward_seek_wait_distance: 16 * COMMON_IO_SIZE,
            max_backward_seek_distance: 1 * COMMON_IO_SIZE,
            max_prefetch_tasks,
            shared_prefetch_task_limit: DEFAULT_SHARED_PREFETCH_TASK_LIMIT,
        };

        let mut fc = FetchContext {
            preferred_chunk_size: DEFAULT_PREFERRED_CHUNK_SIZE,
            next_sequential_read_offset: 0,
            next_request_size: 0,
            next_request_offset: 0,
            current: None,
            tasks: LinkedList::new(),
            bsw: ChunkList::new(pc.max_backward_seek_distance),
            shared_prefetch_task: Arc::new(AtomicIsize::new(0)),
            sequential_read_hint: 0,
            pcontext,
        };
        fc.next_request_size = pc.first_request_size;
        let object_info = Arc::new(ObjectInfo::new(bucket, key, etag, size));
        Self {
            object_fetcher: ObjectFetcher {
                client,
                runtime: runtime.clone(),
                closed: Arc::new(AtomicI8::new(0)),
                pc,
                fc: Mutex::new(fc),
                om: object_info.clone(),
            },
            runtime,
            object_info,
        }
    }
}

struct ObjectFetcher {
    client: Arc<InnerTosClient>,
    runtime: Arc<Runtime>,
    closed: Arc<AtomicI8>,
    pc: PrefetchConfig,
    fc: Mutex<FetchContext>,
    om: Arc<ObjectInfo>,
}

impl ObjectFetcher {
    async fn read(
        &self,
        offset: isize,
        length: isize,
        read_once: bool,
    ) -> Result<Option<BytesResult>, TosError> {
        if self.closed.load(Ordering::Acquire) == 1 {
            warn!("read on closed object fetcher");
            return Err(TosError::TosClientError {
                message: "read on closed object fetcher".to_string(),
                cause: None,
                request_url: "".to_string(),
            });
        }

        let mut fc = self.fc.lock().await;
        self.revise_preferred_chunk_size(&mut fc, length);

        let mut to_read = self.get_to_read(offset, length).await;
        if to_read == 0 {
            return Ok(None);
        }

        if offset == 0
            && to_read == DEFAULT_PREFERRED_CHUNK_SIZE
            && fc.bsw.chunks.is_empty()
            && fc.tasks.is_empty()
        {
            fc.next_request_size = self.pc.first_request_size + DEFAULT_PREFERRED_CHUNK_SIZE;
        }

        // try to seek if this read is not sequential
        if offset != fc.next_sequential_read_offset {
            match self.try_seek(&mut fc, offset).await {
                Err(ex) => {
                    error!("try seek to start {} failed", offset);
                    self.reset(&mut fc, offset).await;
                    return Err(ex);
                }
                Ok((succ, add_hint)) => {
                    if !succ {
                        self.reset(&mut fc, offset).await;
                        fc.sequential_read_hint = 0
                    } else if add_hint {
                        fc.sequential_read_hint += 1;
                    }
                }
            }
        } else {
            fc.sequential_read_hint += 1;
        }

        self.do_trigger_fetch_tasks(&mut fc, None).await;
        let mut result = None;
        while to_read > 0 {
            match fc.current.as_mut() {
                None => {
                    break;
                }
                Some(current) => match current.read(to_read).await {
                    None => {
                        self.reset(&mut fc, offset).await;
                        error!("read chunk error, get none");
                        return Err(TosError::TosClientError {
                            message: "read chunk error, get none".to_string(),
                            cause: None,
                            request_url: "".to_string(),
                        });
                    }
                    Some(mut chk) => {
                        if let Some(ex) = chk.err.take() {
                            self.reset(&mut fc, offset).await;
                            error!("read chunk error, {}", ex.to_string());
                            chk.release();
                            return Err(ex);
                        }

                        if chk.key_offset != fc.next_sequential_read_offset {
                            error!(
                                "mismatch startOffset, expected [{}], actual [{}]",
                                fc.next_sequential_read_offset, chk.key_offset
                            );
                            chk.release();
                            return Err(TosError::TosClientError {
                                message: format!(
                                    "mismatch startOffset, expected [{}], actual [{}]",
                                    fc.next_sequential_read_offset, chk.key_offset
                                ),
                                cause: None,
                                request_url: "".to_string(),
                            });
                        }

                        fc.bsw.push(chk.clone());
                        let chk_size = chk.size();
                        fc.next_sequential_read_offset += chk_size;
                        if read_once {
                            return Ok(Some(BytesResult::new_with_chunk(chk, chk_size)));
                        }

                        if result.is_none() && chk_size == to_read {
                            return Ok(Some(BytesResult::new_with_chunk(chk, chk_size)));
                        }
                        self.do_trigger_fetch_tasks(&mut fc, None).await;
                        if result.is_none() {
                            result = Some(BytesResult::new());
                        }

                        result.as_mut().unwrap().concat(chk, chk_size);
                        to_read -= chk_size;
                    }
                },
            }
        }
        Ok(result)
    }

    async fn close(&self) {
        if let Ok(_) = self
            .closed
            .compare_exchange(0, 1, Ordering::AcqRel, Ordering::Relaxed)
        {
            self.reset_with_lock(0).await;
        }
    }

    fn is_closed(&self) -> bool {
        self.closed.load(Ordering::Acquire) == 1
    }

    async fn reset_with_lock(&self, offset: isize) {
        let mut fc = self.fc.lock().await;
        self.reset(&mut fc, offset).await;
    }

    async fn reset(&self, fc: &mut MutexGuard<'_, FetchContext>, offset: isize) {
        if let Some(mut current) = fc.current.take() {
            current.drain().await;
        }
        fc.bsw.drain();
        while fc.has_tasks() {
            if let Some(mut task) = fc.pop_task() {
                task.drain().await;
            }
        }
        fc.next_sequential_read_offset = offset;
        fc.next_request_offset = offset;
        fc.next_request_size = self.pc.first_request_size;
        fc.sequential_read_hint = 0;
    }

    async fn trigger_first_fetch_task(
        &self,
        ta: Option<(Option<Arc<TokenAcquirer>>, Option<OwnedSemaphorePermit>)>,
    ) {
        let mut fc = self.fc.lock().await;
        if fc.current.is_some() || fc.has_tasks() {
            return;
        }
        fc.current = self
            .start_first_fetch_task(&mut fc, self.runtime.clone(), ta)
            .await;
    }

    async fn do_trigger_fetch_tasks(
        &self,
        fc: &mut MutexGuard<'_, FetchContext>,
        ta: Option<(Option<Arc<TokenAcquirer>>, Option<OwnedSemaphorePermit>)>,
    ) {
        match fc.current.as_mut() {
            None => {
                if fc.has_tasks() {
                    fc.current = fc.pop_task()
                } else {
                    fc.current = self.start_fetch_task(fc, self.runtime.clone(), ta).await;
                }
            }
            Some(current) => {
                let remaining = current.remaining_total.remaining().await;
                if remaining <= 0 {
                    current.drain().await;
                    if fc.has_tasks() {
                        fc.current = fc.pop_task()
                    } else {
                        fc.current = self.start_fetch_task(fc, self.runtime.clone(), ta).await;
                    }
                } else if fc.exceed_sequential_read_threshold() {
                    if fc.can_add_task(self.pc.max_prefetch_tasks) {
                        if let Some(next) =
                            self.start_fetch_task(fc, self.runtime.clone(), ta).await
                        {
                            fc.push_task(next, false);
                        }
                    } else if fc.can_steal_shared_task(self.pc.shared_prefetch_task_limit)
                        && fc.pcontext.try_steal_shared_prefetch_task()
                    {
                        match self.start_fetch_task(fc, self.runtime.clone(), ta).await {
                            Some(mut next) => {
                                next.is_shared = true;
                                fc.steal_shared_task();
                                fc.push_task(next, false);
                            }
                            None => {
                                fc.pcontext.release_shared_prefetch_task();
                            }
                        }
                    }
                }
            }
        }
    }

    async fn start_fetch_task(
        &self,
        fc: &mut MutexGuard<'_, FetchContext>,
        runtime: Arc<Runtime>,
        ta: Option<(Option<Arc<TokenAcquirer>>, Option<OwnedSemaphorePermit>)>,
    ) -> Option<FetchTask> {
        let size = self.om.size().await;
        if fc.next_request_offset >= size {
            return None;
        }
        let (mut task, size, _) = self.new_fetch_task(fc, Some(size));
        self.revise_next_request_offset_and_size(fc, size);
        task.wait_async_fetch = Some(
            task.async_fetch(self.client.clone(), runtime, ta, size, None)
                .await,
        );
        Some(task)
    }

    async fn start_first_fetch_task(
        &self,
        fc: &mut MutexGuard<'_, FetchContext>,
        runtime: Arc<Runtime>,
        ta: Option<(Option<Arc<TokenAcquirer>>, Option<OwnedSemaphorePermit>)>,
    ) -> Option<FetchTask> {
        let size = self.om.try_get_size().await;
        if let Some(size) = size {
            if fc.next_request_offset >= size {
                return None;
            }
        }
        let (mut task, size, first_remaining_total) = self.new_fetch_task(fc, size);
        self.revise_next_request_offset_and_size(fc, size);
        task.wait_async_fetch = Some(
            task.async_fetch(
                self.client.clone(),
                runtime,
                ta,
                size,
                Some(first_remaining_total),
            )
            .await,
        );
        Some(task)
    }

    async fn try_seek(
        &self,
        fc: &mut MutexGuard<'_, FetchContext>,
        offset: isize,
    ) -> Result<(bool, bool), TosError> {
        // seek backward
        if offset < fc.next_sequential_read_offset {
            let backward_length = fc.next_sequential_read_offset - offset;
            return match fc.bsw.read_back(backward_length) {
                None => Ok((false, false)),
                Some(chunks) => {
                    if chunks.is_empty() {
                        return Ok((false, false));
                    }

                    if let Some(mut current) = fc.current.take() {
                        if current.remaining_total.remaining().await <= 0 {
                            current.drain().await;
                        } else {
                            fc.push_task(current, true);
                        }
                    }

                    fc.current = Some(
                        self.new_fetch_task_by_chunks(
                            chunks,
                            offset,
                            fc.preferred_chunk_size,
                            fc.shared_prefetch_task.clone(),
                            fc.pcontext.clone(),
                        )
                        .await,
                    );
                    fc.next_sequential_read_offset = offset;
                    Ok((true, backward_length < COMMON_IO_SIZE))
                }
            };
        }

        let mut temp_current = None;
        match fc.current.take() {
            // no requests in flight
            None => return Ok((false, false)),
            Some(mut current) => {
                // seek forward
                let end_offset = current.end_offset().await;
                if offset >= end_offset {
                    fc.next_sequential_read_offset = end_offset;
                    current.drain().await;
                }

                while fc.has_tasks() {
                    if let Some(mut task) = fc.pop_task() {
                        let end_offset = task.end_offset().await;
                        if end_offset > offset {
                            temp_current = Some(task);
                            break;
                        }

                        fc.next_sequential_read_offset = end_offset;
                        task.drain().await;
                    }
                }

                if temp_current.is_none() {
                    return Ok((false, false));
                }

                fc.bsw.drain();
            }
        }

        let mut temp_current = temp_current.unwrap();
        // too long to wait
        if offset >= temp_current.available_offset() + self.pc.max_forward_seek_wait_distance {
            temp_current.drain().await;
            return Ok((false, false));
        }

        let mut to_skip = offset - fc.next_sequential_read_offset;
        while to_skip > 0 {
            match temp_current.read(to_skip).await {
                None => {
                    temp_current.drain().await;
                    return Ok((false, false));
                }
                Some(mut chk) => {
                    if let Some(ex) = chk.err.take() {
                        chk.release();
                        temp_current.drain().await;
                        return Err(ex);
                    }

                    let chk_size = chk.size();
                    to_skip -= chk_size;
                    fc.next_sequential_read_offset += chk_size;
                    fc.bsw.push(chk);
                }
            }
        }

        fc.current = Some(temp_current);
        Ok((true, true))
    }

    async fn get_to_read(&self, offset: isize, length: isize) -> isize {
        let size = self.om.size().await;
        if size < offset {
            return 0;
        }

        let mut remaining = size - offset;
        if remaining > length {
            remaining = length;
        }
        remaining
    }
    fn revise_preferred_chunk_size(&self, fc: &mut MutexGuard<FetchContext>, length: isize) {
        if fc.preferred_chunk_size < length {
            fc.preferred_chunk_size = length;
        }

        if fc.preferred_chunk_size > COMMON_IO_SIZE {
            fc.preferred_chunk_size = COMMON_IO_SIZE;
        }
    }

    fn revise_next_request_offset_and_size(
        &self,
        fc: &mut MutexGuard<FetchContext>,
        last_request_size: isize,
    ) {
        fc.next_request_offset += last_request_size;
        let mut next_request_size = last_request_size * self.pc.sequential_prefetch_multiplier;
        if next_request_size > self.pc.max_request_size {
            next_request_size = self.pc.max_request_size;
        }
        fc.next_request_size = next_request_size;
    }

    fn calc_chunk_queue_size(&self) -> isize {
        let mut queue_size = DEFAULT_ONE_REQUEST_READ_BUFFER_LIMIT / COMMON_IO_SIZE;
        if DEFAULT_ONE_REQUEST_READ_BUFFER_LIMIT % COMMON_IO_SIZE != 0 {
            queue_size += 1;
        }
        queue_size
    }

    fn new_fetch_task(
        &self,
        fc: &mut MutexGuard<'_, FetchContext>,
        object_size: Option<isize>,
    ) -> (FetchTask, isize, Arc<FetchTaskSize>) {
        let mut size = fc.next_request_size;
        let remaining_total = Arc::new(match object_size {
            None => FetchTaskSize::new(None),
            Some(object_size) => {
                if fc.next_request_offset + size > object_size {
                    size = object_size - fc.next_request_offset;
                }
                FetchTaskSize::new(Some(size))
            }
        });
        (
            FetchTask {
                remaining_total: remaining_total.clone(),
                is_streaming: true,
                is_shared: false,
                shared_prefetch_task: fc.shared_prefetch_task.clone(),
                pcontext: fc.pcontext.clone(),
                om: self.om.clone(),
                start_offset: fc.next_request_offset,
                fetched_size: Arc::new(AtomicIsize::new(0)),
                preferred_chunk_size: fc.preferred_chunk_size,
                chunk_queue: Arc::new(ChunkQueue::new(self.calc_chunk_queue_size() as usize)),
                last_chunk: ChunkHolder::new(None),
                closed: self.closed.clone(),
                wait_async_fetch: None,
                client: self.client.clone(),
            },
            size,
            remaining_total,
        )
    }

    async fn new_fetch_task_by_chunks(
        &self,
        chunks: LinkedList<Chunk>,
        offset: isize,
        preferred_chunk_size: isize,
        shared_prefetch_task: Arc<AtomicIsize>,
        pcontext: Arc<SharedPrefetchContext>,
    ) -> FetchTask {
        let mut chunk_queue = ChunkQueue::new(chunks.len());
        let mut size = 0;
        for chunk in chunks {
            let chk_size = chunk.size();
            size += chk_size;
            chunk_queue.push(chunk).await;
        }
        let remaining_total = Arc::new(FetchTaskSize::new(Some(size)));
        let mut task = FetchTask {
            remaining_total,
            is_streaming: false,
            is_shared: false,
            shared_prefetch_task,
            pcontext,
            om: self.om.clone(),
            start_offset: offset,
            fetched_size: Arc::new(AtomicIsize::new(0)),
            preferred_chunk_size,
            chunk_queue: Arc::new(chunk_queue),
            last_chunk: ChunkHolder { inner: None },
            closed: self.closed.clone(),
            wait_async_fetch: None,
            client: self.client.clone(),
        };
        task.fetched_size.fetch_add(size, Ordering::Release);
        task.chunk_queue.close();
        task
    }
}

struct BytesResult {
    inner: Vec<Chunk>,
    size: isize,
}

impl BytesResult {
    fn new() -> Self {
        Self {
            inner: Vec::with_capacity(3),
            size: 0,
        }
    }
    fn new_with_chunk(chk: Chunk, chk_size: isize) -> Self {
        Self {
            inner: vec![chk],
            size: chk_size,
        }
    }
    fn concat(&mut self, chk: Chunk, chk_size: isize) -> bool {
        if chk.data.is_some() {
            self.inner.push(chk);
            self.size += chk_size;
            return true;
        }
        false
    }

    fn as_ref(&self) -> Result<&[u8], TosError> {
        if self.inner.is_empty() {
            return Ok(&[]);
        }

        if self.inner.len() == 1 {
            return match &self.inner[0].data {
                None => Ok(&[]),
                Some(data) => Ok(data.as_ref()),
            };
        }

        Err(TosError::TosClientError {
            message: "cannot trans to &[u8]".to_string(),
            cause: None,
            request_url: "".to_string(),
        })
    }

    fn take(&mut self) -> Result<Option<Bytes>, TosError> {
        if self.inner.is_empty() {
            return Ok(None);
        }

        if self.inner.len() == 1 {
            return match self.inner.remove(0).data {
                None => Ok(None),
                Some(data) => Ok(Some(data)),
            };
        }

        Err(TosError::TosClientError {
            message: "cannot trans to &[u8]".to_string(),
            cause: None,
            request_url: "".to_string(),
        })
    }

    fn to_vec(&self) -> Vec<u8> {
        if self.inner.is_empty() {
            return Vec::new();
        }

        let mut buf = Vec::with_capacity(self.size as usize);
        for chk in self.inner.iter() {
            if let Some(data) = &chk.data {
                buf.extend_from_slice(data.as_ref());
            }
        }
        buf
    }
}

struct PrefetchConfig {
    first_request_size: isize,
    max_request_size: isize,
    sequential_prefetch_multiplier: isize,
    max_forward_seek_wait_distance: isize,
    max_backward_seek_distance: isize,
    max_prefetch_tasks: isize,
    shared_prefetch_task_limit: isize,
}

struct FetchContext {
    preferred_chunk_size: isize,
    next_sequential_read_offset: isize,
    next_request_size: isize,
    next_request_offset: isize,

    current: Option<FetchTask>,
    tasks: LinkedList<FetchTask>,
    bsw: ChunkList,
    shared_prefetch_task: Arc<AtomicIsize>,
    sequential_read_hint: isize,
    pcontext: Arc<SharedPrefetchContext>,
}

impl FetchContext {
    fn exceed_sequential_read_threshold(&self) -> bool {
        self.sequential_read_hint >= DEFAULT_SEQUENTIAL_READ_THRESHOLD
    }
    fn can_add_task(&self, max_prefetch_tasks: isize) -> bool {
        self.tasks.len() < max_prefetch_tasks as usize
    }

    fn can_steal_shared_task(&self, shared_prefetch_task_limit: isize) -> bool {
        self.shared_prefetch_task.load(Ordering::Acquire) < shared_prefetch_task_limit
    }

    fn steal_shared_task(&self) {
        self.shared_prefetch_task.fetch_add(1, Ordering::Release);
    }

    fn has_tasks(&self) -> bool {
        !self.tasks.is_empty()
    }

    fn pop_task(&mut self) -> Option<FetchTask> {
        self.tasks.pop_front()
    }

    fn push_task(&mut self, task: FetchTask, push_to_front: bool) {
        if push_to_front {
            self.tasks.push_front(task);
        } else {
            self.tasks.push_back(task);
        }
    }
}

struct FetchTaskSize {
    remaining_total: RwLock<Option<(AtomicIsize, isize)>>,
    remaining_total_notify: Notify,
}

impl FetchTaskSize {
    fn new(size: Option<isize>) -> Self {
        match size {
            None => Self {
                remaining_total: RwLock::new(None),
                remaining_total_notify: Notify::new(),
            },
            Some(size) => Self {
                remaining_total: RwLock::new(Some((AtomicIsize::new(size), size))),
                remaining_total_notify: Notify::new(),
            },
        }
    }

    async fn set_remaining_total(&self, size: isize) {
        let mut remaining_total = self.remaining_total.write().await;
        if remaining_total.is_none() {
            *remaining_total = Some((AtomicIsize::new(size), size));
        }
        self.remaining_total_notify.notify_waiters();
    }

    async fn add_remaining(&self, size: isize) {
        loop {
            {
                let remaining_total = self.remaining_total.read().await;
                if let Some((remaining, _)) = remaining_total.as_ref() {
                    let _ = remaining.fetch_add(size, Ordering::Release);
                    return;
                }
            }
            self.remaining_total_notify.notified().await;
        }
    }

    async fn remaining(&self) -> isize {
        loop {
            {
                let remaining_total = self.remaining_total.read().await;
                if let Some((remaining, _)) = remaining_total.as_ref() {
                    return remaining.load(Ordering::Acquire);
                }
            }
            self.remaining_total_notify.notified().await;
        }
    }

    async fn total(&self) -> isize {
        loop {
            {
                let remaining_total = self.remaining_total.read().await;
                if let Some((_, total)) = remaining_total.as_ref() {
                    return *total;
                }
            }
            self.remaining_total_notify.notified().await;
        }
    }

    async fn remaining_and_total(&self) -> (isize, isize) {
        loop {
            {
                let remaining_total = self.remaining_total.read().await;
                if let Some((remaining, total)) = remaining_total.as_ref() {
                    return (remaining.load(Ordering::Acquire), *total);
                }
            }
            self.remaining_total_notify.notified().await;
        }
    }
}

struct FetchTask {
    remaining_total: Arc<FetchTaskSize>,
    is_streaming: bool,
    is_shared: bool,
    shared_prefetch_task: Arc<AtomicIsize>,
    pcontext: Arc<SharedPrefetchContext>,
    om: Arc<ObjectInfo>,
    start_offset: isize,
    fetched_size: Arc<AtomicIsize>,
    preferred_chunk_size: isize,
    chunk_queue: Arc<ChunkQueue>,
    last_chunk: ChunkHolder,
    closed: Arc<AtomicI8>,
    wait_async_fetch: Option<JoinHandle<()>>,
    client: Arc<InnerTosClient>,
}

impl FetchTask {
    async fn start_next_hint(&self) -> bool {
        let (remaining, total) = self.remaining_total.remaining_and_total().await;
        self.is_streaming && remaining <= total / 2
    }
    async fn end_offset(&self) -> isize {
        self.start_offset + self.remaining_total.total().await
    }
    fn available_offset(&self) -> isize {
        self.start_offset + self.fetched_size.load(Ordering::Acquire)
    }

    async fn async_fetch(
        &self,
        client: Arc<InnerTosClient>,
        runtime: Arc<Runtime>,
        ta: Option<(Option<Arc<TokenAcquirer>>, Option<OwnedSemaphorePermit>)>,
        size: isize,
        first_remaining_total: Option<Arc<FetchTaskSize>>,
    ) -> JoinHandle<()> {
        let fetch_task_context = FetchTaskContext::new(self, client, size);
        runtime.spawn(async move {
            let _permit;
            if let Some(ta) = ta {
                if let Some(permit) = ta.1 {
                    _permit = Some(permit);
                } else if let Some(ta) = ta.0 {
                    _permit = Some(ta.acquire().await.unwrap());
                } else {
                    _permit = None;
                }
            } else {
                _permit = None;
            }
            fetch_task_context
                .fetch_from_server(first_remaining_total)
                .await;
            fetch_task_context.chunk_queue.close();
        })
    }

    async fn read(&mut self, length: isize) -> Option<Chunk> {
        let mut chk = self.last_chunk.take();
        if chk.is_none() {
            chk = self.chunk_queue.pop().await;
        }

        match chk {
            None => None,
            Some(mut chk) => {
                if chk.size() <= length {
                    self.remaining_total.add_remaining(-chk.size()).await;
                    return Some(chk);
                }

                let front = chk.split(length);
                if chk.size() > 0 {
                    self.last_chunk.set(chk);
                }
                if let Some(ref front) = front {
                    self.remaining_total.add_remaining(-front.size()).await;
                }
                front
            }
        }
    }

    async fn drain(&mut self) {
        self.chunk_queue.close();
        self.chunk_queue
            .drain(|mut chk| {
                chk.release();
            })
            .await;

        if let Some(mut chk) = self.last_chunk.take() {
            chk.release()
        }

        if self.is_shared {
            self.shared_prefetch_task.fetch_add(-1, Ordering::Release);
            self.pcontext.release_shared_prefetch_task();
        }
        if let Some(wait_execute) = self.wait_async_fetch.take() {
            let _ = wait_execute.await;
        }
    }
}

struct FetchTaskContext {
    client: Arc<InnerTosClient>,
    om: Arc<ObjectInfo>,
    start_offset: isize,
    remaining_total: Arc<FetchTaskSize>,
    size: isize,
    fetched_size: Arc<AtomicIsize>,
    preferred_chunk_size: isize,
    chunk_queue: Arc<ChunkQueue>,
    closed: Arc<AtomicI8>,
}

impl FetchTaskContext {
    fn new(task: &FetchTask, client: Arc<InnerTosClient>, size: isize) -> Self {
        Self {
            client,
            om: task.om.clone(),
            start_offset: task.start_offset,
            remaining_total: task.remaining_total.clone(),
            size,
            fetched_size: task.fetched_size.clone(),
            preferred_chunk_size: task.preferred_chunk_size,
            chunk_queue: task.chunk_queue.clone(),
            closed: task.closed.clone(),
        }
    }

    async fn fetch_from_server(&self, first_remaining_total: Option<Arc<FetchTaskSize>>) {
        let range_start = self.start_offset;
        let range_end = self.start_offset + self.size - 1;
        let mut fetch_retry_count = DEFAULT_FETCH_RETRY_COUNT;
        'outer: loop {
            if self.chunk_queue.is_closed() {
                if let Some(first_remaining_total) = first_remaining_total.as_ref() {
                    self.om.set_etag_size("".to_string(), -1).await;
                    first_remaining_total.set_remaining_total(-1).await;
                }
                break;
            }
            let mut input = GetObjectInput::new(self.om.bucket.as_str(), self.om.key.as_str());
            if let Some(etag) = self.om.try_get_etag().await {
                input.set_if_match(etag);
            }
            input.set_range(format!("bytes={}-{}", range_start, range_end));
            let output = self.client.get_object(&input).await;
            match output {
                Err(ex) => {
                    if let Some(first_remaining_total) = first_remaining_total.as_ref() {
                        self.om.set_etag_size("".to_string(), -1).await;
                        first_remaining_total.set_remaining_total(-1).await;
                    }
                    error!(
                        "get object [{}] in bucket [{}] failed, {}",
                        self.om.bucket,
                        self.om.key,
                        ex.to_string()
                    );
                    self.chunk_queue.push(Chunk::err(ex)).await;
                    return;
                }

                Ok(mut output) => {
                    let total;
                    if let Some(first_remaining_total) = first_remaining_total.as_ref() {
                        if output.content_range() != "" {
                            // eg. bytes 0-1/11
                            let splited =
                                output.content_range().splitn(2, "/").collect::<Vec<&str>>();
                            if splited.len() != 2 {
                                self.om.set_etag_size("".to_string(), -1).await;
                                first_remaining_total.set_remaining_total(-1).await;
                                error!(
                                    "parse content range for object [{}] in bucket [{}] failed",
                                    self.om.bucket, self.om.key,
                                );
                                self.chunk_queue.push(Chunk::err(TosError::TosClientError {
                                    message: format!("parse content range for object [{}] in bucket [{}] failed",
                                                     self.om.bucket, self.om.key),
                                    cause: None,
                                    request_url: "".to_string(),
                                })).await;
                                return;
                            }
                            match splited[1].parse::<isize>() {
                                Ok(size) => {
                                    total = size;
                                }
                                Err(e) => {
                                    self.om.set_etag_size("".to_string(), -1).await;
                                    first_remaining_total.set_remaining_total(-1).await;
                                    error!(
                                        "parse content range for object [{}] in bucket [{}] failed",
                                        self.om.bucket, self.om.key,
                                    );
                                    self.chunk_queue.push(Chunk::err(TosError::TosClientError {
                                        message: format!("parse content range for object [{}] in bucket [{}] failed",
                                                         self.om.bucket, self.om.key),
                                        cause: None,
                                        request_url: "".to_string(),
                                    })).await;
                                    return;
                                }
                            }
                        } else {
                            total = output.content_length() as isize;
                        }

                        self.om
                            .set_etag_size(output.etag().to_string(), total)
                            .await;
                        first_remaining_total.set_remaining_total(total).await;
                    } else {
                        total = self.remaining_total.total().await;
                    }
                    let mut total_read = 0isize;
                    let key_offset = AtomicIsize::new(self.start_offset);
                    let mut can_re_fetch = true;
                    loop {
                        match output.next().await {
                            None => {
                                // read eof
                                return;
                            }
                            Some(result) => match result {
                                Err(ex) => {
                                    error!(
                                        "read object [{}] in bucket [{}] failed, {}",
                                        self.om.bucket,
                                        self.om.key,
                                        ex.to_string()
                                    );

                                    if fetch_retry_count > 0 && can_re_fetch {
                                        fetch_retry_count -= 1;
                                        continue 'outer;
                                    }
                                    self.chunk_queue
                                        .push(Chunk::err(TosError::TosClientError {
                                            message: format!(
                                                "read object [{}] in bucket [{}] failed, {}",
                                                self.om.bucket,
                                                self.om.key,
                                                ex.to_string()
                                            ),
                                            cause: None,
                                            request_url: "".to_string(),
                                        }))
                                        .await;
                                    return;
                                }
                                Ok(data) => {
                                    can_re_fetch = false;
                                    total_read += data.len() as isize;
                                    if !self.consume_data(data, &key_offset).await {
                                        return;
                                    }
                                    if total_read >= total {
                                        return;
                                    }
                                }
                            },
                        }
                    }
                }
            }
        }
    }

    async fn consume_data(&self, mut data: Bytes, key_offset: &AtomicIsize) -> bool {
        let mut chunk_size = self.preferred_chunk_size;
        let mut remaining = data.len() as isize;
        // consume one
        if chunk_size >= remaining {
            chunk_size = remaining;
            let chk = Chunk::new(
                self.om.key.to_string(),
                key_offset.load(Ordering::Acquire),
                data,
            );
            key_offset.fetch_add(chunk_size, Ordering::Release);
            let (send_result, succeed) = self.chunk_queue.push(chk).await;
            if succeed {
                self.fetched_size.fetch_add(chunk_size, Ordering::Release);
            } else if let Some(mut chk) = send_result {
                chk.release();
            }
            return self.closed.load(Ordering::Acquire) == 0;
        }

        // consume many
        loop {
            if chunk_size > remaining {
                chunk_size = remaining;
            }

            if chunk_size == 0 {
                break;
            }

            let chk = Chunk::new(
                self.om.key.to_string(),
                key_offset.load(Ordering::Acquire),
                data.split_to(chunk_size as usize),
            );
            key_offset.fetch_add(chunk_size, Ordering::Release);
            remaining -= chunk_size;
            let (send_result, succeed) = self.chunk_queue.push(chk).await;
            if succeed {
                self.fetched_size.fetch_add(chunk_size, Ordering::Release);
            } else if let Some(mut chk) = send_result {
                chk.release();
            }
        }

        self.closed.load(Ordering::Acquire) == 0
    }
}

struct ChunkQueue {
    sender: Sender<Chunk>,
    receiver: Receiver<Chunk>,
    chunk_in_queue: AtomicIsize,
}

impl ChunkQueue {
    fn new(cap: usize) -> Self {
        let (sender, receiver) = async_channel::bounded(cap);
        Self {
            sender,
            receiver,
            chunk_in_queue: AtomicIsize::new(0),
        }
    }

    fn is_empty(&self) -> bool {
        self.chunk_in_queue.load(Ordering::Acquire) == 0
    }
    fn close(&self) {
        self.sender.close();
    }

    fn is_closed(&self) -> bool {
        self.sender.is_closed()
    }

    async fn push(&self, chk: Chunk) -> (Option<Chunk>, bool) {
        match self.sender.send(chk).await {
            Ok(_) => {
                self.chunk_in_queue.fetch_add(1, Ordering::Release);
                (None, true)
            }
            Err(ex) => (Some(ex.0), false),
        }
    }
    async fn pop(&self) -> Option<Chunk> {
        match self.receiver.recv().await {
            Ok(chk) => Some(chk),
            Err(_) => None,
        }
    }
    async fn drain(&self, f: impl Fn(Chunk)) {
        while let Ok(chk) = self.receiver.recv().await {
            self.chunk_in_queue.fetch_sub(1, Ordering::Release);
            f(chk);
        }
    }
}

struct ChunkHolder {
    inner: Option<Chunk>,
}
impl ChunkHolder {
    fn new(inner: Option<Chunk>) -> Self {
        Self { inner }
    }

    fn take(&mut self) -> Option<Chunk> {
        self.inner.take()
    }

    fn set(&mut self, chunk: Chunk) {
        self.inner = Some(chunk);
    }
}

struct ChunkList {
    chunks: LinkedList<Chunk>,
    max_size: isize,
    current_size: isize,
}

impl ChunkList {
    fn new(max_size: isize) -> Self {
        Self {
            chunks: LinkedList::new(),
            max_size,
            current_size: 0,
        }
    }

    fn push(&mut self, mut chk: Chunk) {
        let size = chk.size();
        if size == 0 {
            return;
        }

        if size > self.max_size {
            self.drain();
            chk.release();
            return;
        }

        loop {
            if self.chunks.is_empty() || self.max_size - self.current_size >= size {
                break;
            }

            // drop front
            if let Some(mut chk) = self.poll_first() {
                chk.release();
            }
        }

        self.push_last(chk);
    }

    fn poll_first(&mut self) -> Option<Chunk> {
        match self.chunks.pop_front() {
            None => None,
            Some(chk) => {
                self.current_size -= chk.size();
                Some(chk)
            }
        }
    }

    fn push_last(&mut self, chk: Chunk) {
        self.current_size += chk.size();
        self.chunks.push_back(chk);
    }

    fn poll_last(&mut self) -> Option<Chunk> {
        match self.chunks.pop_back() {
            None => None,
            Some(chk) => {
                self.current_size -= chk.size();
                Some(chk)
            }
        }
    }

    fn read_back(&mut self, length: isize) -> Option<LinkedList<Chunk>> {
        if length > self.current_size {
            return None;
        }
        let mut result = LinkedList::new();
        let mut length = length;
        loop {
            if length <= 0 {
                break;
            }

            let chk = self.poll_last();
            if chk.is_none() {
                break;
            }

            let mut chk = chk.unwrap();
            let size = chk.size();
            if size > length {
                if let Some(front_chk) = chk.split(size - length) {
                    self.push_last(front_chk);
                }
            }

            length -= chk.size();
            result.push_front(chk);
        }
        Some(result)
    }

    fn drain(&mut self) {
        while self.chunks.len() > 0 {
            if let Some(mut chk) = self.chunks.pop_front() {
                chk.release();
            }
        }
        self.current_size = 0;
    }
}

struct Chunk {
    err: Option<TosError>,
    key: String,
    key_offset: isize,
    data: Option<Bytes>,
}

impl Chunk {
    fn new(key: String, key_offset: isize, data: Bytes) -> Self {
        Self {
            err: None,
            key,
            key_offset,
            data: Some(data),
        }
    }

    fn err(err: TosError) -> Self {
        Self {
            err: Some(err),
            key: "".to_string(),
            key_offset: -1,
            data: None,
        }
    }

    fn split(&mut self, front_length: isize) -> Option<Self> {
        if front_length == 0 || self.err.is_some() {
            return None;
        }

        if self.data.as_ref()?.len() <= front_length as usize {
            return Some(Self {
                err: None,
                key: self.key.to_string(),
                key_offset: self.key_offset,
                data: self.data.take(),
            });
        }

        let front = Chunk {
            err: None,
            key: self.key.to_string(),
            key_offset: self.key_offset,
            data: Some(self.data.as_mut()?.split_to(front_length as usize)),
        };

        self.key_offset += front_length;
        Some(front)
    }

    fn data(&self) -> Option<&[u8]> {
        if self.err.is_some() {
            return None;
        }

        self.data.as_ref().map(|data| &data[..])
    }

    fn size(&self) -> isize {
        if self.err.is_some() {
            return 0;
        }

        match self.data.as_ref() {
            None => 0,
            Some(data) => data.len() as isize,
        }
    }

    fn clone(&self) -> Self {
        Self {
            err: self.err.clone(),
            key: self.key.to_string(),
            key_offset: self.key_offset,
            data: self.data.clone(),
        }
    }

    fn release(&mut self) {
        // do nothing
    }
}

pub(crate) struct ObjectInfo {
    pub(crate) bucket: String,
    pub(crate) key: String,
    pub(crate) etag_size: RwLock<Option<(String, isize)>>,
    pub(crate) etag_size_notify: Notify,
}

impl ObjectInfo {
    pub(crate) fn new(
        bucket: String,
        key: String,
        etag: Option<String>,
        size: Option<isize>,
    ) -> Self {
        let etag_size;
        if etag.is_none() || size.is_none() {
            etag_size = None;
        } else {
            etag_size = Some((etag.unwrap(), size.unwrap()));
        }

        Self {
            bucket,
            key,
            etag_size: RwLock::new(etag_size),
            etag_size_notify: Notify::new(),
        }
    }

    pub(crate) async fn set_etag_size(&self, etag: String, size: isize) {
        let mut etag_size = self.etag_size.write().await;
        if etag_size.is_none() {
            *etag_size = Some((etag, size));
        }
        self.etag_size_notify.notify_waiters();
    }

    pub(crate) fn bucket(&self) -> &str {
        &self.bucket
    }
    pub(crate) fn key(&self) -> &str {
        &self.key
    }

    pub(crate) async fn etag(&self) -> String {
        loop {
            {
                let etag_size = self.etag_size.read().await;
                if let Some((etag, _)) = etag_size.as_ref() {
                    return etag.to_string();
                }
            }
            self.etag_size_notify.notified().await;
        }
    }

    pub(crate) async fn size(&self) -> isize {
        loop {
            {
                let etag_size = self.etag_size.read().await;
                if let Some((_, size)) = etag_size.as_ref() {
                    return *size;
                }
            }
            self.etag_size_notify.notified().await;
        }
    }

    pub(crate) async fn try_get_size(&self) -> Option<isize> {
        let etag_size = self.etag_size.read().await;
        if let Some((_, size)) = etag_size.as_ref() {
            return Some(*size);
        }
        None
    }

    pub(crate) async fn try_get_etag(&self) -> Option<String> {
        let etag_size = self.etag_size.read().await;
        if let Some((etag, _)) = etag_size.as_ref() {
            return Some(etag.to_string());
        }
        None
    }
}
