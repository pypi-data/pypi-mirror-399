use crate::common::TokenAcquirer;
use crate::read_stream::ReadStream;
use crate::tos_client::{InnerTosClient, TosClient};
use crate::tos_model::TosObject;
use arc_swap::ArcSwap;
use async_channel::{Receiver, Sender};
use std::collections::{LinkedList, VecDeque};
use std::sync::atomic::{AtomicI8, AtomicIsize, AtomicU64, AtomicUsize, Ordering};
use std::sync::Arc;
use tokio::runtime::Runtime;
use tokio::sync::{OwnedSemaphorePermit, RwLock, TryAcquireError};
use tokio::task::JoinHandle;
use tracing::log::warn;
use ve_tos_rust_sdk::asynchronous::object::ObjectAPI;
use ve_tos_rust_sdk::error::TosError;
use ve_tos_rust_sdk::object::{ListObjectsType2Input, ListObjectsType2Output};

const DEFAULT_BUFFER_COUNT: usize = 3;
pub struct ListStream {
    client: Arc<InnerTosClient>,
    runtime: Arc<Runtime>,
    tos_client: Arc<TosClient>,
    paginator: RwLock<Option<Paginator>>,
    closed: AtomicI8,
    bucket: String,
    prefix: String,
    delimiter: String,
    max_keys: isize,
    continuation_token: String,
    start_after: String,
    list_background_buffer_count: isize,
    prefetch_concurrency: isize,
    distributed_info: Option<(isize, isize, isize, isize)>,
}

impl ListStream {
    pub fn next(
        &self,
    ) -> Result<
        Option<(
            VecDeque<TosObject>,
            Option<Vec<String>>,
            Option<Vec<ReadStream>>,
        )>,
        TosError,
    > {
        self.runtime.block_on(async {
            {
                let pg = self.paginator.read().await;
                if pg.is_some() {
                    return self.next_page(pg.as_ref()).await;
                }
            }

            if self.closed.load(Ordering::Acquire) == 1 {
                return Err(TosError::TosClientError {
                    message: "ListStream is closed".to_string(),
                    cause: None,
                    request_url: "".to_string(),
                });
            }

            let mut pg = self.paginator.write().await;
            if pg.is_none() {
                *pg = self.list_background(self.prefetch_concurrency);
            }
            self.next_page(pg.as_ref()).await
        })
    }

    pub fn close(&self) {
        if let Ok(_) = self
            .closed
            .compare_exchange(0, 1, Ordering::AcqRel, Ordering::Relaxed)
        {
            self.runtime.block_on(async {
                if let Some(pg) = self.paginator.write().await.as_mut() {
                    pg.receiver.close();
                    pg.close().await;
                }
            })
        }
    }

    pub fn current_prefix(&self) -> Result<Option<String>, TosError> {
        self.runtime.block_on(async {
            match self.paginator.read().await.as_ref() {
                None => Ok(None),
                Some(pg) => Ok(Some(pg.current_prefix())),
            }
        })
    }

    pub fn current_continuation_token(&self) -> Result<Option<String>, TosError> {
        self.runtime.block_on(async {
            match self.paginator.read().await.as_ref() {
                None => Ok(None),
                Some(pg) => Ok(Some(pg.current_continuation_token())),
            }
        })
    }

    pub fn bucket(&self) -> &str {
        &self.bucket
    }

    pub fn prefix(&self) -> &str {
        &self.prefix
    }

    pub fn delimiter(&self) -> &str {
        &self.delimiter
    }

    pub fn max_keys(&self) -> isize {
        self.max_keys
    }

    pub fn continuation_token(&self) -> &str {
        &self.continuation_token
    }

    pub fn start_after(&self) -> &str {
        &self.start_after
    }

    pub fn list_background_buffer_count(&self) -> isize {
        self.list_background_buffer_count
    }

    pub(crate) fn new(
        client: Arc<InnerTosClient>,
        runtime: Arc<Runtime>,
        tos_client: Arc<TosClient>,
        bucket: String,
        prefix: String,
        delimiter: String,
        max_keys: isize,
        continuation_token: String,
        start_after: String,
        list_background_buffer_count: isize,
        prefetch_concurrency: isize,
        distributed_info: Option<(isize, isize, isize, isize)>,
    ) -> Self {
        Self {
            client,
            runtime,
            tos_client,
            paginator: RwLock::new(None),
            closed: AtomicI8::new(0),
            bucket,
            prefix,
            delimiter,
            max_keys,
            continuation_token,
            start_after,
            list_background_buffer_count,
            prefetch_concurrency,
            distributed_info,
        }
    }

    pub(crate) fn list_background(&self, prefetch_concurrency: isize) -> Option<Paginator> {
        let mut buffer_count = self.list_background_buffer_count as usize;
        if buffer_count <= 0 {
            buffer_count = DEFAULT_BUFFER_COUNT;
        }
        let (sender, receiver) = async_channel::bounded(buffer_count);
        let client = self.client.clone();
        let mut input = ListObjectsType2Input::new(self.bucket.as_str());
        input.set_prefix(self.prefix.as_str());
        input.set_max_keys(self.max_keys);
        input.set_delimiter(self.delimiter.as_str());
        input.set_list_only_once(true);
        if self.continuation_token != "" {
            input.set_continuation_token(self.continuation_token.as_str());
        }
        if self.start_after != "" {
            input.set_start_after(self.start_after.as_str());
        }
        let tos_client = self.tos_client.clone();
        let mut ta = None;
        if prefetch_concurrency > 0 {
            ta = Some(Arc::new(TokenAcquirer::new(prefetch_concurrency)));
        }
        let distributed_info = self.distributed_info;
        let bucket = self.bucket.clone();
        let is_end = ArcSwap::new(Arc::new(false));
        let wait_list_background = self.runtime.spawn(async move {
            // global_idx, worker_idx, pglobal_idx, pworker_idx
            let mut idxs = (0, 0, 0, 0);
            let mut need_break = false;
            if input.delimiter() == "" {
                loop {
                    match client.list_objects_type2(&input).await {
                        Ok(o) => {
                            if o.is_truncated() {
                                input.set_continuation_token(o.next_continuation_token());
                            } else {
                                need_break = true;
                            }

                            let (mut objects, _, prefix, continuation_token) =
                                pick_objects_by_distributed_info(
                                    bucket.as_str(),
                                    o,
                                    distributed_info,
                                    &mut idxs,
                                );
                            if let Some(ta) = ta.as_ref() {
                                let mut is_end = false;
                                while objects.len() > 0 {
                                    let permit = ta.acquire().await.unwrap();
                                    let (splited_objects, read_stream_list) = split_objects(
                                        &input,
                                        &mut objects,
                                        tos_client.clone(),
                                        ta.clone(),
                                        permit,
                                    )
                                    .await;
                                    if objects.is_empty() {
                                        is_end = need_break;
                                    }
                                    if let Err(_) = sender
                                        .send((
                                            is_end,
                                            Ok((
                                                splited_objects,
                                                None,
                                                prefix.clone(),
                                                continuation_token.clone(),
                                                Some(read_stream_list),
                                            )),
                                        ))
                                        .await
                                    {
                                        warn!("send on closed channel!");
                                        is_end = true;
                                        need_break = true;
                                    }
                                }
                            } else {
                                if objects.len() > 0 {
                                    if let Err(_) = sender
                                        .send((
                                            need_break,
                                            Ok((objects, None, prefix, continuation_token, None)),
                                        ))
                                        .await
                                    {
                                        warn!("send on closed channel!");
                                        need_break = true;
                                    }
                                }
                            }
                        }
                        Err(e) => {
                            need_break = true;
                            let _ = sender.send((need_break, Err(e))).await;
                        }
                    }
                    if need_break {
                        break;
                    }
                }
            } else {
                let mut prefixes = LinkedList::<String>::new();
                let mut last_page_end = false;
                loop {
                    if last_page_end {
                        let prefix = prefixes.pop_front().unwrap();
                        input.set_prefix(prefix);
                        input.set_start_after("");
                        input.set_continuation_token("");
                        last_page_end = false;
                    }
                    match client.list_objects_type2(&input).await {
                        Ok(o) => {
                            if o.is_truncated() {
                                input.set_continuation_token(o.next_continuation_token());
                            } else {
                                last_page_end = true;
                            }

                            for cp in o.common_prefixes() {
                                prefixes.push_back(cp.prefix().to_string());
                            }
                            need_break = last_page_end && prefixes.is_empty();
                            let (mut objects, mut common_prefixes, prefix, continuation_token) =
                                pick_objects_by_distributed_info(
                                    bucket.as_str(),
                                    o,
                                    distributed_info,
                                    &mut idxs,
                                );
                            if let Some(ta) = ta.as_ref() {
                                let mut is_end = false;
                                let mut _common_prefixes = None;
                                while objects.len() > 0 {
                                    let permit = ta.acquire().await.unwrap();
                                    let (splited_objects, read_stream_list) = split_objects(
                                        &input,
                                        &mut objects,
                                        tos_client.clone(),
                                        ta.clone(),
                                        permit,
                                    )
                                    .await;
                                    if objects.is_empty() {
                                        is_end = need_break;
                                        _common_prefixes = common_prefixes.take();
                                    }
                                    if let Err(_) = sender
                                        .send((
                                            is_end,
                                            Ok((
                                                splited_objects,
                                                _common_prefixes.take(),
                                                prefix.clone(),
                                                continuation_token.clone(),
                                                Some(read_stream_list),
                                            )),
                                        ))
                                        .await
                                    {
                                        warn!("send on closed channel!");
                                        is_end = true;
                                        need_break = true;
                                    }
                                }
                            } else {
                                if objects.len() > 0 || common_prefixes.is_some() {
                                    if let Err(_) = sender
                                        .send((
                                            need_break,
                                            Ok((
                                                objects,
                                                common_prefixes,
                                                prefix,
                                                continuation_token,
                                                None,
                                            )),
                                        ))
                                        .await
                                    {
                                        warn!("send on closed channel!");
                                        need_break = true;
                                    }
                                }
                            }
                        }
                        Err(e) => {
                            need_break = true;
                            let _ = sender.send((need_break, Err(e))).await;
                        }
                    }
                    if need_break {
                        break;
                    }
                }
            }
        });
        Some(Paginator {
            is_end,
            last_err: ArcSwap::new(Arc::new(None)),
            current_prefix: ArcSwap::new(Arc::new(self.prefix.clone())),
            current_continuation_token: ArcSwap::new(Arc::new(self.continuation_token.clone())),
            receiver,
            wait_list_background: Some(wait_list_background),
        })
    }

    pub(crate) async fn next_page(
        &self,
        paginator: Option<&Paginator>,
    ) -> Result<
        Option<(
            VecDeque<TosObject>,
            Option<Vec<String>>,
            Option<Vec<ReadStream>>,
        )>,
        TosError,
    > {
        match paginator {
            None => Ok(None),
            Some(pg) => {
                match pg.has_next() {
                    Err(ex) => {
                        return Err(ex);
                    }
                    Ok(has_next) => {
                        if !has_next {
                            return Ok(None);
                        }
                    }
                }
                pg.next_page().await
            }
        }
    }
}

fn pick_objects_by_distributed_info(
    bucket: &str,
    o: ListObjectsType2Output,
    distributed_info: Option<(isize, isize, isize, isize)>,
    idxs: &mut (isize, isize, isize, isize),
) -> (VecDeque<TosObject>, Option<Vec<String>>, String, String) {
    let mut objects = VecDeque::with_capacity(o.contents().len());
    let mut common_prefixes = None;
    if let Some((world_size, rank, worker_size, worker_id)) = distributed_info {
        for content in o.contents() {
            if idxs.0 % world_size == rank {
                if idxs.1 % worker_size == worker_id {
                    objects.push_back(TosObject::new(
                        bucket,
                        content.key(),
                        content.size() as isize,
                        content.etag(),
                    ));
                }
                idxs.1 += 1;
            }
            idxs.0 += 1;
        }

        if o.common_prefixes().len() > 0 {
            let mut _common_prefixes = Vec::with_capacity(o.common_prefixes().len());
            for common_prefix in o.common_prefixes() {
                if idxs.2 % world_size == rank {
                    if idxs.3 % worker_size == worker_id {
                        _common_prefixes.push(common_prefix.prefix().to_string());
                    }
                    idxs.3 += 1;
                }
                idxs.2 += 1;
            }
            common_prefixes = Some(_common_prefixes);
        }

        return (
            objects,
            common_prefixes,
            o.prefix().to_string(),
            o.continuation_token().to_string(),
        );
    }
    idxs.0 += o.contents().len() as isize;
    idxs.1 += o.contents().len() as isize;
    idxs.2 += o.common_prefixes().len() as isize;
    idxs.3 += o.common_prefixes().len() as isize;
    for content in o.contents() {
        objects.push_back(TosObject::new(
            bucket,
            content.key(),
            content.size() as isize,
            content.etag(),
        ));
    }

    if o.common_prefixes().len() > 0 {
        let mut _common_prefixes = Vec::with_capacity(o.common_prefixes().len());
        for common_prefix in o.common_prefixes() {
            _common_prefixes.push(common_prefix.prefix().to_string());
        }
        common_prefixes = Some(_common_prefixes);
    }
    (
        objects,
        common_prefixes,
        o.prefix().to_string(),
        o.continuation_token().to_string(),
    )
}

async fn split_objects(
    input: &ListObjectsType2Input,
    objects: &mut VecDeque<TosObject>,
    tos_client: Arc<TosClient>,
    ta: Arc<TokenAcquirer>,
    permit: OwnedSemaphorePermit,
) -> (VecDeque<TosObject>, Vec<ReadStream>) {
    let mut permits = LinkedList::new();
    permits.push_back(permit);
    loop {
        if permits.len() >= objects.len() {
            break;
        }

        match ta.try_acquire() {
            Ok(permit) => {
                permits.push_back(permit);
            }
            Err(_) => {
                break;
            }
        }
    }

    let mut splited_objects = VecDeque::with_capacity(permits.len());
    let mut read_stream_list = Vec::with_capacity(permits.len());
    loop {
        if permits.is_empty() || objects.is_empty() {
            break;
        }
        let object = objects.pop_front().unwrap();
        let permit = permits.pop_front().unwrap();
        let read_stream = tos_client
            .async_get_object(
                input.bucket().to_string(),
                object.key().to_string(),
                Some(object.etag().to_string()),
                Some(object.size()),
                false,
            )
            .await;
        read_stream
            .trigger_first_fetch_task(Some((None, Some(permit))))
            .await;
        read_stream_list.push(read_stream);
        splited_objects.push_back(object);
    }

    (splited_objects, read_stream_list)
}

pub(crate) struct Paginator {
    is_end: ArcSwap<bool>,
    last_err: ArcSwap<Option<TosError>>,
    current_prefix: ArcSwap<String>,
    current_continuation_token: ArcSwap<String>,
    receiver: Receiver<(
        bool,
        Result<
            (
                VecDeque<TosObject>,
                Option<Vec<String>>,
                String,
                String,
                Option<Vec<ReadStream>>,
            ),
            TosError,
        >,
    )>,
    wait_list_background: Option<JoinHandle<()>>,
}

impl Paginator {
    fn has_next(&self) -> Result<bool, TosError> {
        if let Some(err) = self.last_err.load().as_ref() {
            return Err(err.clone());
        }
        Ok(!*self.is_end.load().as_ref())
    }

    fn current_prefix(&self) -> String {
        self.current_prefix.load().to_string()
    }
    fn current_continuation_token(&self) -> String {
        self.current_continuation_token.load().to_string()
    }

    async fn close(&mut self) {
        if let Some(wait_list_background) = self.wait_list_background.take() {
            let _ = wait_list_background.await;
        }
    }

    async fn next_page(
        &self,
    ) -> Result<
        Option<(
            VecDeque<TosObject>,
            Option<Vec<String>>,
            Option<Vec<ReadStream>>,
        )>,
        TosError,
    > {
        if let Some(e) = self.last_err.load().as_ref() {
            return Err(e.clone());
        }
        if *self.is_end.load().as_ref() {
            return Ok(None);
        }

        match self.receiver.recv().await {
            Err(_) => {
                self.is_end.store(Arc::new(true));
                Ok(None)
            }
            Ok((is_end, result)) => match result {
                Err(e) => {
                    self.last_err.store(Arc::new(Some(e.clone())));
                    Err(e)
                }
                Ok(output) => {
                    self.current_prefix.store(Arc::new(output.2));
                    self.current_continuation_token.store(Arc::new(output.3));
                    if is_end {
                        self.is_end.store(Arc::new(true));
                    }
                    Ok(Some((output.0, output.1, output.4)))
                }
            },
        }
    }
}
