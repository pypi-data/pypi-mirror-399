pub mod document;
pub mod embedding;
pub mod vector_store;
pub mod rag;
pub mod chunking;
pub mod file_watcher;

use pyo3::prelude::*;

/// Python bindings for memalloy RAG kernel
#[pymodule]
fn _memalloy(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<rag::RAGKernel>()?;
    m.add_class::<document::PyDocument>()?;
    m.add_class::<chunking::PyChunkingStrategy>()?;
    m.add_class::<file_watcher::PyFileWatcher>()?;
    Ok(())
}
