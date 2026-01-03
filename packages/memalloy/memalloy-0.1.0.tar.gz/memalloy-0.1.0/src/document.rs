use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use chrono::{DateTime, Utc};
use uuid::Uuid;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Document {
    pub id: String,
    pub content: String,
    pub metadata: HashMap<String, String>,
    pub created_at: DateTime<Utc>,
}

impl Document {
    pub fn new(content: String, metadata: Option<HashMap<String, String>>) -> Self {
        Self {
            id: Uuid::new_v4().to_string(),
            content,
            metadata: metadata.unwrap_or_default(),
            created_at: Utc::now(),
        }
    }
}

#[pyclass]
#[derive(Clone)]
pub struct PyDocument {
    #[pyo3(get, set)]
    pub id: String,
    #[pyo3(get, set)]
    pub content: String,
    #[pyo3(get, set)]
    pub metadata: HashMap<String, String>,
}

#[pymethods]
impl PyDocument {
    #[new]
    fn new(content: String, metadata: Option<HashMap<String, String>>) -> Self {
        let doc = Document::new(content, metadata);
        Self {
            id: doc.id,
            content: doc.content,
            metadata: doc.metadata,
        }
    }

    fn __repr__(&self) -> String {
        format!("Document(id={}, content_len={})", self.id, self.content.len())
    }
}

impl From<Document> for PyDocument {
    fn from(doc: Document) -> Self {
        Self {
            id: doc.id,
            content: doc.content,
            metadata: doc.metadata,
        }
    }
}

impl From<PyDocument> for Document {
    fn from(py_doc: PyDocument) -> Self {
        Self {
            id: py_doc.id,
            content: py_doc.content,
            metadata: py_doc.metadata,
            created_at: Utc::now(),
        }
    }
}
