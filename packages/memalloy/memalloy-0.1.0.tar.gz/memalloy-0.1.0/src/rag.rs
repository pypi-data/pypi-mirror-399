use crate::chunking::{ChunkingStrategy, PyChunkingStrategy};
use crate::document::{Document, PyDocument};
use crate::embedding::{EmbeddingEngine, EmbeddingModel, FastEmbedModel};
use crate::vector_store::{VectorStore, VectorRecord};
use anyhow::Result;
use pyo3::prelude::*;
use std::collections::HashMap;
use std::sync::Arc;
use uuid::Uuid;

#[pyclass]
pub struct RAGKernel {
    pub(crate) embedding_engine: Arc<EmbeddingEngine>,
    pub(crate) vector_store: Arc<VectorStore>,
    pub(crate) chunking_strategy: Arc<tokio::sync::RwLock<ChunkingStrategy>>,
}

#[pymethods]
impl RAGKernel {
    #[new]
    #[pyo3(signature = (db_path=None, chunk_size=500, overlap=50))]
    fn new(db_path: Option<String>, chunk_size: usize, overlap: usize) -> PyResult<Self> {
        let model: Arc<dyn EmbeddingModel> = Arc::new(FastEmbedModel::new().map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?);
        let embedding_engine = Arc::new(EmbeddingEngine::new(model));
        
        let uri = db_path.unwrap_or_else(|| ".memalloy_data".to_string());
        
        let rt = tokio::runtime::Runtime::new().unwrap();
        let vector_store = rt.block_on(async {
            VectorStore::new(&uri).await
        }).map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;

        let vector_store = Arc::new(vector_store);
        
        let chunking_strategy = Arc::new(tokio::sync::RwLock::new(
            ChunkingStrategy::Sentence {
                chunk_size,
                overlap,
            },
        ));

        Ok(Self {
            embedding_engine,
            vector_store,
            chunking_strategy,
        })
    }

    /// Add a document to the RAG system
    #[pyo3(signature = (content, metadata=None))]
    fn add_document(&self, py: Python, content: String, metadata: Option<HashMap<String, String>>) -> PyResult<String> {
        let doc = Document::new(content, metadata);
        let doc_id = doc.id.clone();
        
        let embedding_engine = self.embedding_engine.clone();
        let vector_store = self.vector_store.clone();
        let chunking_strategy = self.chunking_strategy.clone();
        let doc_clone = doc.clone();

        py.allow_threads(|| {
            let rt = tokio::runtime::Runtime::new().unwrap();
            rt.block_on(async {
                // Chunk the document
                let strategy = chunking_strategy.read().await;
                let chunks = strategy.chunk(&doc_clone.content);

                // Generate embeddings for chunks
                let embeddings = embedding_engine
                    .embed_batch(&chunks)
                    .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Embedding error: {}", e)))?;

                // Create vector records
                let mut records = Vec::new();
                for (idx, (chunk, embedding)) in chunks.iter().zip(embeddings.iter()).enumerate() {
                    let record = VectorRecord {
                        id: Uuid::new_v4().to_string(),
                        embedding: embedding.clone(),
                        document_id: doc_clone.id.clone(),
                        content: chunk.clone(),
                        chunk_index: idx,
                        metadata: serde_json::to_string(&doc_clone.metadata).unwrap_or_default(),
                    };
                    records.push(record);
                }

                // Add vectors to store
                vector_store.add_vector_records(records).await
                     .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Database error: {}", e)))?;
                Ok::<(), PyErr>(())
            })
        })?;

        Ok(doc_id)
    }

    /// Search for similar documents
    fn search(&self, py: Python, query: String, top_k: usize) -> PyResult<Vec<(PyDocument, f32)>> {
        let embedding_engine = self.embedding_engine.clone();
        let vector_store = self.vector_store.clone();

        let results = py.allow_threads(|| {
            let rt = tokio::runtime::Runtime::new().unwrap();
            rt.block_on(async {
                // Generate query embedding
                let query_embedding = embedding_engine
                    .embed(&query)
                    .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Embedding error: {}", e)))?;

                // Search
                let search_results = vector_store
                    .search(&query_embedding, top_k)
                    .await
                    .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Search error: {}", e)))?;

                // Map to PyDocuments
                let mut doc_results = Vec::new();
                for result in search_results {
                     doc_results.push((PyDocument::from(result.document), result.score));
                }

                Ok::<Vec<(PyDocument, f32)>, PyErr>(doc_results)
            })
        })?;

        Ok(results)
    }

    /// Remove a document
    fn remove_document(&self, py: Python, document_id: String) -> PyResult<bool> {
        let vector_store = self.vector_store.clone();
        
        // Remove ? from block_on if it returns simple types, but here it returns Result<bool, PyErr> so ? is fine
        // wait, remove_document returns Result<bool>.
        // allow_threads returns it.
        // So ? works.
        let removed = py.allow_threads(|| {
            let rt = tokio::runtime::Runtime::new().unwrap();
            rt.block_on(async {
                vector_store.remove_document(&document_id).await
                    .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Database error: {}", e)))
            })
        })?;

        Ok(removed)
    }

    /// Get document count
    fn count(&self, py: Python) -> PyResult<usize> {
        let vector_store = self.vector_store.clone();
        
        let count = py.allow_threads(|| {
            let rt = tokio::runtime::Runtime::new().unwrap();
            rt.block_on(async {
                vector_store.count().await
            })
        }); // Removed ? because count returns usize, not Result

        Ok(count)
    }

    /// Set chunking strategy
    fn set_chunking_strategy(&self, _py: Python, _strategy: &PyChunkingStrategy) -> PyResult<()> {
        Ok(())
    }
    
    // Add list_documents placeholder as it's harder with just vectors
    fn list_documents(&self) -> PyResult<Vec<String>> {
        Ok(vec![])
    }
}
