use anyhow::{Result, Error};
use std::sync::{Arc, Mutex};
use fastembed::{TextEmbedding, InitOptions, EmbeddingModel as FastEmbedModelEnum};

/// Embedding model interface
pub trait EmbeddingModel: Send + Sync {
    fn embed(&self, text: &str) -> Result<Vec<f32>>;
    fn embed_batch(&self, texts: &[String]) -> Result<Vec<Vec<f32>>>;
    fn dimension(&self) -> usize;
}

/// FastEmbed model wrapper
pub struct FastEmbedModel {
    model: Mutex<TextEmbedding>,
}

impl FastEmbedModel {
    pub fn new() -> Result<Self> {
        let mut options = InitOptions::default();
        options.model_name = FastEmbedModelEnum::AllMiniLML6V2;
        options.show_download_progress = false;
        
        let model = TextEmbedding::try_new(options)?;
        Ok(Self { model: Mutex::new(model) })
    }
}

impl EmbeddingModel for FastEmbedModel {
    fn embed(&self, text: &str) -> Result<Vec<f32>> {
        let mut model = self.model.lock().map_err(|_| Error::msg("Mutex poisoned"))?;
        let embeddings = model.embed(vec![text], None)?;
        embeddings
            .into_iter()
            .next()
            .ok_or_else(|| Error::msg("No embedding generated"))
    }

    fn embed_batch(&self, texts: &[String]) -> Result<Vec<Vec<f32>>> {
        let mut model = self.model.lock().map_err(|_| Error::msg("Mutex poisoned"))?;
        let embeddings = model.embed(texts.to_vec(), None)?;
        Ok(embeddings)
    }

    fn dimension(&self) -> usize {
        384
    }
}

pub struct EmbeddingEngine {
    model: Arc<dyn EmbeddingModel>,
}

impl EmbeddingEngine {
    pub fn new(model: Arc<dyn EmbeddingModel>) -> Self {
        Self { model }
    }

    pub fn embed(&self, text: &str) -> Result<Vec<f32>> {
        self.model.embed(text)
    }

    pub fn embed_batch(&self, texts: &[String]) -> Result<Vec<Vec<f32>>> {
        self.model.embed_batch(texts)
    }

    pub fn dimension(&self) -> usize {
        self.model.dimension()
    }
}
