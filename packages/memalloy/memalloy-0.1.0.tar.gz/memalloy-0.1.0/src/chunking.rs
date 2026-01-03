use pyo3::prelude::*;
use regex::Regex;
use unicode_segmentation::UnicodeSegmentation;

#[derive(Debug, Clone)]
pub enum ChunkingStrategy {
    Sentence { chunk_size: usize, overlap: usize },
    Token { chunk_size: usize, overlap: usize },
    Fixed { chunk_size: usize, overlap: usize },
}

impl ChunkingStrategy {
    pub fn chunk(&self, text: &str) -> Vec<String> {
        match self {
            ChunkingStrategy::Sentence { chunk_size, overlap } => {
                self.chunk_by_sentence(text, *chunk_size, *overlap)
            }
            ChunkingStrategy::Token { chunk_size, overlap } => {
                self.chunk_by_tokens(text, *chunk_size, *overlap)
            }
            ChunkingStrategy::Fixed { chunk_size, overlap } => {
                self.chunk_fixed(text, *chunk_size, *overlap)
            }
        }
    }

    fn chunk_by_sentence(&self, text: &str, chunk_size: usize, overlap: usize) -> Vec<String> {
        let sentence_re = Regex::new(r"[.!?]+\s+").unwrap();
        let sentences: Vec<&str> = sentence_re.split(text).collect();
        
        let mut chunks = Vec::new();
        let mut current_chunk = String::new();
        
        for sentence in sentences {
            if current_chunk.len() + sentence.len() > chunk_size && !current_chunk.is_empty() {
                chunks.push(current_chunk.trim().to_string());
                // Handle overlap
                if overlap > 0 {
                    let words: Vec<&str> = current_chunk.split_whitespace().collect();
                    let overlap_start = words.len().saturating_sub(overlap);
                    current_chunk = words[overlap_start..].join(" ");
                } else {
                    current_chunk = String::new();
                }
            }
            current_chunk.push_str(sentence);
            current_chunk.push(' ');
        }
        
        if !current_chunk.trim().is_empty() {
            chunks.push(current_chunk.trim().to_string());
        }
        
        chunks
    }

    fn chunk_by_tokens(&self, text: &str, chunk_size: usize, overlap: usize) -> Vec<String> {
        let words: Vec<&str> = text.split_whitespace().collect();
        let mut chunks = Vec::new();
        
        let mut i = 0;
        while i < words.len() {
            let end = (i + chunk_size).min(words.len());
            let chunk = words[i..end].join(" ");
            chunks.push(chunk);
            
            if end >= words.len() {
                break;
            }
            
            i = end.saturating_sub(overlap);
        }
        
        chunks
    }

    fn chunk_fixed(&self, text: &str, chunk_size: usize, overlap: usize) -> Vec<String> {
        let mut chunks = Vec::new();
        let mut i = 0;
        
        while i < text.len() {
            let end = (i + chunk_size).min(text.len());
            chunks.push(text[i..end].to_string());
            
            if end >= text.len() {
                break;
            }
            
            i = end.saturating_sub(overlap);
        }
        
        chunks
    }
}

#[pyclass]
pub struct PyChunkingStrategy {
    strategy: ChunkingStrategy,
}

#[pymethods]
impl PyChunkingStrategy {
    #[staticmethod]
    fn sentence(chunk_size: usize, overlap: usize) -> Self {
        Self {
            strategy: ChunkingStrategy::Sentence { chunk_size, overlap },
        }
    }

    #[staticmethod]
    fn token(chunk_size: usize, overlap: usize) -> Self {
        Self {
            strategy: ChunkingStrategy::Token { chunk_size, overlap },
        }
    }

    #[staticmethod]
    fn fixed(chunk_size: usize, overlap: usize) -> Self {
        Self {
            strategy: ChunkingStrategy::Fixed { chunk_size, overlap },
        }
    }

    fn chunk(&self, text: &str) -> Vec<String> {
        self.strategy.chunk(text)
    }
}
