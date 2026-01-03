use crate::document::Document;
use crate::embedding::EmbeddingEngine;
use crate::vector_store::{Vector, VectorStore};
use crate::chunking::ChunkingStrategy;
use crate::rag::RAGKernel;
use anyhow::{Context, Result};
use notify::{Event, EventKind, RecommendedWatcher, RecursiveMode, Watcher};
use pyo3::prelude::*;
use std::collections::HashMap;
use std::path::{Path, PathBuf};
use std::sync::Arc;
use tokio::sync::RwLock;
use uuid::Uuid;
use walkdir::WalkDir;

#[derive(Debug, Clone)]
pub struct FileInfo {
    pub path: PathBuf,
    pub content: String,
    pub metadata: HashMap<String, String>,
}

impl FileInfo {
    pub fn new(path: PathBuf, content: String) -> Self {
        let mut metadata = HashMap::new();
        metadata.insert("source".to_string(), "file".to_string());
        metadata.insert(
            "file_path".to_string(),
            path.to_string_lossy().to_string(),
        );
        metadata.insert(
            "file_name".to_string(),
            path.file_name()
                .map(|n| n.to_string_lossy().to_string())
                .unwrap_or_default(),
        );
        if let Some(ext) = path.extension() {
            metadata.insert(
                "file_extension".to_string(),
                ext.to_string_lossy().to_string(),
            );
        }

        Self {
            path,
            content,
            metadata,
        }
    }
}

pub struct FileWatcher {
    watch_path: PathBuf,
    embedding_engine: Arc<EmbeddingEngine>,
    vector_store: Arc<VectorStore>,
    chunking_strategy: Arc<tokio::sync::RwLock<ChunkingStrategy>>,
    file_map: Arc<RwLock<HashMap<PathBuf, String>>>, // path -> document_id
    extensions: Vec<String>,
    recursive: bool,
}

impl FileWatcher {
    pub fn new(
        watch_path: PathBuf,
        embedding_engine: Arc<EmbeddingEngine>,
        vector_store: Arc<VectorStore>,
        chunking_strategy: Arc<tokio::sync::RwLock<ChunkingStrategy>>,
        extensions: Option<Vec<String>>,
        recursive: bool,
    ) -> Self {
        let default_extensions = vec![
            "txt".to_string(),
            "md".to_string(),
            "py".to_string(),
            "rs".to_string(),
            "js".to_string(),
            "ts".to_string(),
            "json".to_string(),
            "yaml".to_string(),
            "yml".to_string(),
        ];

        Self {
            watch_path,
            embedding_engine,
            vector_store,
            chunking_strategy,
            file_map: Arc::new(RwLock::new(HashMap::new())),
            extensions: extensions.unwrap_or(default_extensions),
            recursive,
        }
    }

    pub async fn sync_folder(&self) -> Result<usize> {
        let mut count = 0;
        let walker = if self.recursive {
            WalkDir::new(&self.watch_path)
        } else {
            WalkDir::new(&self.watch_path).max_depth(1)
        };

        for entry in walker.into_iter().filter_map(|e| e.ok()) {
            let path = entry.path();
            if path.is_file() {
                if let Some(ext) = path.extension() {
                    let ext_str = ext.to_string_lossy().to_lowercase();
                    if self.extensions.iter().any(|e| e.to_lowercase() == ext_str) {
                        match self.process_file(path).await {
                            Ok(_) => count += 1,
                            Err(e) => eprintln!("Error processing {}: {}", path.display(), e),
                        }
                    }
                }
            }
        }

        Ok(count)
    }

    async fn process_file(&self, path: &Path) -> Result<()> {
        let content = std::fs::read_to_string(path)
            .with_context(|| format!("Failed to read file: {}", path.display()))?;

        let file_info = FileInfo::new(path.to_path_buf(), content);
        let doc = Document::new(file_info.content.clone(), Some(file_info.metadata.clone()));

        // Check if file already exists
        let mut file_map = self.file_map.write().await;
        if let Some(old_doc_id) = file_map.get(path) {
            // Remove old document
            self.vector_store.remove_document(old_doc_id).await;
        }

        // Add new document
        let doc_id = doc.id.clone();
        file_map.insert(path.to_path_buf(), doc_id.clone());

        // Get chunking strategy
        let chunking_strategy = self.chunking_strategy.read().await;

        // Add document
        self.vector_store.add_document(doc.clone()).await;

        // Chunk the document
        let chunks = chunking_strategy.chunk(&doc.content);

        // Generate embeddings for chunks
        let embeddings = self.embedding_engine.embed_batch(&chunks)?;

        // Create vectors
        let mut vectors = Vec::new();
        for (idx, (_chunk, embedding)) in chunks.iter().zip(embeddings.iter()).enumerate() {
            let vector = Vector::new(
                Uuid::new_v4().to_string(),
                embedding.clone(),
                doc.id.clone(),
                idx,
                doc.metadata.clone(),
            );
            vectors.push(vector);
        }

        // Add vectors to store
        self.vector_store.add_vectors(vectors).await;

        Ok(())
    }

    async fn handle_file_event(&self, event: Event) -> Result<()> {
        for path in event.paths {
            if path.is_file() {
                if let Some(ext) = path.extension() {
                    let ext_str = ext.to_string_lossy().to_lowercase();
                    if self.extensions.iter().any(|e| e.to_lowercase() == ext_str) {
                        match event.kind {
                            EventKind::Create(_) | EventKind::Modify(_) => {
                                self.process_file(&path).await?;
                            }
                            EventKind::Remove(_) => {
                                let mut file_map = self.file_map.write().await;
                                if let Some(doc_id) = file_map.remove(&path) {
                                    self.vector_store.remove_document(&doc_id).await;
                                }
                            }
                            _ => {}
                        }
                    }
                }
            }
        }
        Ok(())
    }
}

#[pyclass]
pub struct PyFileWatcher {
    watcher: Arc<RwLock<Option<RecommendedWatcher>>>,
    file_watcher: Arc<FileWatcher>,
    watch_path: PathBuf,
}

#[pymethods]
impl PyFileWatcher {
    #[new]
    #[pyo3(signature = (rag_kernel, watch_path, extensions=None, recursive=true))]
    fn new(
        rag_kernel: PyRef<RAGKernel>,
        watch_path: String,
        extensions: Option<Vec<String>>,
        recursive: bool,
    ) -> PyResult<Self> {
        let path = PathBuf::from(watch_path.clone());
        if !path.exists() {
            return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                format!("Path does not exist: {}", watch_path),
            ));
        }

        let file_watcher = Arc::new(FileWatcher::new(
            path.clone(),
            rag_kernel.embedding_engine.clone(),
            rag_kernel.vector_store.clone(),
            rag_kernel.chunking_strategy.clone(),
            extensions,
            recursive,
        ));

        Ok(Self {
            watcher: Arc::new(RwLock::new(None)),
            file_watcher,
            watch_path: path,
        })
    }

    /// Sync all files in the folder (initial sync)
    fn sync(&self, py: Python) -> PyResult<usize> {
        let file_watcher = self.file_watcher.clone();
        py.allow_threads(|| {
            let rt = tokio::runtime::Runtime::new().unwrap();
            rt.block_on(async {
                file_watcher
                    .sync_folder()
                    .await
                    .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Sync error: {}", e)))
            })
        })
    }

    /// Start watching for file changes
    fn start_watching(&self, py: Python) -> PyResult<()> {
        let file_watcher = self.file_watcher.clone();
        let watch_path = self.watch_path.clone();
        let watcher_arc = self.watcher.clone();

        py.allow_threads(|| {
            let rt = tokio::runtime::Runtime::new().unwrap();
            rt.block_on(async {
                let (tx, mut rx) = tokio::sync::mpsc::unbounded_channel();

                let mut watcher = notify::recommended_watcher(move |res| {
                    if let Ok(event) = res {
                        let _ = tx.send(event);
                    }
                })
                .map_err(|e| {
                    PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                        "Watcher creation error: {}",
                        e
                    ))
                })?;

                watcher
                    .watch(&watch_path, RecursiveMode::Recursive)
                    .map_err(|e| {
                        PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                            "Watch error: {}",
                            e
                        ))
                    })?;

                // Store watcher
                {
                    let mut w = watcher_arc.write().await;
                    *w = Some(watcher);
                }

                // Spawn task to handle events
                tokio::spawn(async move {
                    while let Some(event) = rx.recv().await {
                        if let Err(e) = file_watcher.handle_file_event(event).await {
                            eprintln!("Error handling file event: {}", e);
                        }
                    }
                });

                Ok::<(), PyErr>(())
            })
        })
    }

    /// Stop watching for file changes
    fn stop_watching(&self, py: Python) -> PyResult<()> {
        let watcher_arc = self.watcher.clone();
        py.allow_threads(|| {
            let rt = tokio::runtime::Runtime::new().unwrap();
            rt.block_on(async {
                let mut w = watcher_arc.write().await;
                *w = None;
                Ok::<(), PyErr>(())
            })
        })
    }

    fn __repr__(&self) -> String {
        format!("FileWatcher(path={})", self.watch_path.display())
    }
}
