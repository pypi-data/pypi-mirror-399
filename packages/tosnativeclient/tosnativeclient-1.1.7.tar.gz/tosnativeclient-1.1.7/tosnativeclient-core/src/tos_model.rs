use ve_tos_rust_sdk::object::HeadObjectOutput;

#[derive(Clone)]
pub struct TosObject {
    pub(crate) bucket: String,
    pub(crate) key: String,
    pub(crate) etag: String,
    pub(crate) size: isize,
}

impl TosObject {
    pub fn new(
        bucket: impl Into<String>,
        key: impl Into<String>,
        size: isize,
        etag: impl Into<String>,
    ) -> Self {
        Self {
            bucket: bucket.into(),
            key: key.into(),
            etag: etag.into(),
            size,
        }
    }
    pub(crate) fn inner_new(
        bucket: impl Into<String>,
        key: impl Into<String>,
        output: HeadObjectOutput,
    ) -> Self {
        Self {
            bucket: bucket.into(),
            key: key.into(),
            etag: output.etag().to_string(),
            size: output.content_length() as isize,
        }
    }

    pub fn bucket(&self) -> &str {
        &self.bucket
    }

    pub fn key(&self) -> &str {
        &self.key
    }

    pub fn size(&self) -> isize {
        self.size
    }

    pub fn etag(&self) -> &str {
        &self.etag
    }
}
