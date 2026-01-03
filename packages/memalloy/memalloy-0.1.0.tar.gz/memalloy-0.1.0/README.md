# MemAlloy

> "The High-Performance Memory Kernel for AI Agents."

## Executive Summary

MemAlloy is an open-source "Memory Kernel" designed to solve the data ingestion and retrieval bottleneck in Python AI applications. By offloading heavy tasks (file watching, parsing, embedding, and vector storage) to a high-performance Rust core, MemAlloy provides Python developers with a "Second Brain" that is 100x faster, memory-efficient, and privacy-first compared to existing pure-Python solutions like LangChain or LlamaIndex.

## The Problem

Python is the language of AI, but it is ill-suited for the infrastructure of AI Memory.

*   **Latency**: Watching thousands of files and chunking text in Python introduces massive lag (the "Global Interpreter Lock" problem).
*   **Complexity**: Building a RAG (Retrieval Augmented Generation) pipeline currently requires gluing together 5+ disparate libraries (watchdog, pypdf, sentence-transformers, chromadb, tiktoken).
*   **Resource Heaviness**: Existing vector databases often require running a separate Docker container or server, consuming gigabytes of RAM even when idle.

## The Solution

MemAlloy consolidates the entire RAG pipeline into a single, installable binary that exposes a clean Python API. It acts as an embedded OS service for memory.

### Key Features

*   ⚡ **Zero-Latency Ingestion**: Uses Rust’s `notify` crate to detect file changes instantly.
*   🧠 **Local Intelligence**: Runs quantized embedding models (ONNX) localy on the CPU. No API keys required.
*   💾 **Embedded Storage**: Uses **LanceDB** to store millions of vectors in a single file on disk (Serverless).
*   🐍 **Python Native**: Installs via `pip install memalloy`. No Rust knowledge required for the user.

## Technical Architecture

| Layer | Component | Technology (Rust Crate) |
| :--- | :--- | :--- |
| **Interface** | Python Bindings | PyO3 + Maturin |
| **Control** | Async Runtime | Tokio |
| **Senses** | File System Watcher | Notify (Recursive) |
| **Processing** | Neural Embeddings | FastEmbed (ONNX Runtime) |
| **Storage** | Vector Database | LanceDB (Apache Arrow) |

## Installation

### From Source

```bash
# Install maturin (Rust-Python build tool)
pip install maturin

# Build and install memalloy
maturin develop --release
```

## Quick Start

```python
from memalloy import RAGKernel

# Initialize the RAG kernel
rag = RAGKernel()

# Add documents
rag.add_document("MemAlloy is a high-performance memory kernel.")

# Search
results = rag.search("memory kernel", top_k=1)
print(results)
```

## License

Relationships imply responsibility.
Licensed under Apache 2.0 or MIT.

