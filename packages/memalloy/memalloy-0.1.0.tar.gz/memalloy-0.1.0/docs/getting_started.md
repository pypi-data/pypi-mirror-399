# Getting Started

## Installation

### Prerequisites
*   **Python**: Version 3.8 or higher.
*   **Operating System**: macOS, Linux, or Windows (WSL2 recommended).
*   **Rust Toolchain**: Required only if building from source.

### Option 1: Install from Source (Recommended)
Since MemAlloy is currently in active development, building from source is the best way to get the latest performance improvements.

```bash
# 1. Install Maturin (The Rust-Python bridge builder)
pip install maturin

# 2. Clone the repository
git clone https://github.com/your-username/memalloy
cd memalloy

# 3. Build and install into your current Python environment
# --release flag is CRITICAL for performance (10-100x speed difference)
maturin develop --release
```

---

## Basic Usage

The core of MemAlloy is the `RAGKernel`. It handles the entire lifecycle of your data: chunking, embedding, and storage.

### 1. Initialize the Kernel
```python
from memalloy import RAGKernel

# Initialize with default settings
# - Creates .memalloy_data folder in current directory
# - Uses 'AllMiniLML6V2' model (downloads automatically on first run)
rag = RAGKernel()
```

### 2. Ingest Data manually
You can add raw text strings directly. This is useful for chat logs, API responses, or data you've already parsed.

```python
# Returns a unique Document ID
doc_id = rag.add_document(
    content="Rust's ownership model guarantees memory safety without garbage collection.",
    metadata={"source": "The Rust Book", "chapter": 4}
)
print(f"Ingested Document: {doc_id}")
```

### 3. Semantic Search
Search your knowledge base using natural language queries.

```python
results = rag.search(query="Why is Rust safe?", top_k=3)

for doc, score in results:
    print(f"--- Score: {score:.4f} ---")
    print(f"Content: {doc.content}")
    print(f"Metadata: {doc.metadata}")
```

---

## Advanced: Automated File Watching

MemAlloy includes a `FileWatcher` that can monitor a directory and automatically ingest changes in real-time. This is useful for building "Chat with your Docs" applications.

```python
import time
from memalloy import RAGKernel, FileWatcher

# 1. Setup Kernel
rag = RAGKernel()

# 2. Setup Watcher
# Monitors './my_docs' for .md and .txt files
watcher = FileWatcher(
    rag_kernel=rag,
    watch_path="./my_docs",
    extensions=["md", "txt", "py"]
)

# 3. Initial Sync (Ingest files already there)
print("Syncing existing files...")
watcher.sync()

# 4. Start Real-time Monitoring (Background Thread)
print("Watching for changes...")
watcher.start_watching()

try:
    # Keep main thread alive
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    watcher.stop_watching()
    print("Stopped.")
```

## Configuration

| Parameter | Default | Description |
| :--- | :--- | :--- |
| `db_path` | `.memalloy_data` | Directory where LanceDB stores vectors. |
| `chunk_size` | `500` | Maximum number of characters per chunk. |
| `overlap` | `50` | Number of overlapping characters between chunks. |

*(Note: Embedding model is currently fixed to `AllMiniLM-L6-v2` for optimal local performance).*
