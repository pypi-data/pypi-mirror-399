# API Reference

This reference documents the Python API exposed by the `memalloy` package.

---

## Class `RAGKernel`

The main entry point for the MemAlloy system. It manages the vector database connection, embedding generation, and document retrieval.

### Constructor

```python
def __init__(self, db_path: Optional[str] = None, chunk_size: int = 500, overlap: int = 50)
```

**Parameters:**
*   `db_path` *(str, optional)*:
    *   FileSystem path to store the LanceDB database.
    *   **Default**: `"./.memalloy_data"` in the current working directory.
*   `chunk_size` *(int, optional)*:
    *   Maximum number of characters per text chunk. Smaller chunks are better for pinpointing specific facts; larger chunks preserve more context.
    *   **Default**: `500`.
*   `overlap` *(int, optional)*:
    *   Number of characters to overlap between adjacent chunks to prevent context loss at boundaries.
    *   **Default**: `50`.

**Example:**
```python
rag = RAGKernel(db_path="/tmp/my_knowledge_base", chunk_size=1000)
```

### Methods

#### `add_document`

```python
def add_document(self, content: str, metadata: Optional[Dict[str, str]] = None) -> str
```

Ingests a single document into the system. The document is immediately chunked, embedded, and saved to disk.

*   **Parameters:**
    *   `content` *(str)*: The raw text content of the document.
    *   `metadata` *(dict, optional)*: A simple key-value dictionary for storing extra info (e.g., source filename, author, date).
*   **Returns**:
    *   *(str)*: A unique UUID generated for this document.

**Example:**
```python
doc_id = rag.add_document(
    "The mitochondria is the powerhouse of the cell.",
    metadata={"subject": "biology"}
)
```

#### `search`

```python
def search(self, query: str, top_k: int = 5) -> List[Tuple[Document, float]]
```

Performs a semantic similarity search against the knowledge base.

*   **Parameters:**
    *   `query` *(str)*: The natural language query.
    *   `top_k` *(int, optional)*: Number of results to return. Default is 5.
*   **Returns**:
    *   A list of tuples, where each tuple is `(Document, score)`.
    *   `score` is a float between 0.0 and 1.0 (approximate), where higher is better.

**Example:**
```python
results = rag.search("energy source cell")
```

#### `count`

```python
def count(self) -> int
```

*   **Returns**: The total number of *chunks* (vectors) currently stored in the database.

---

## Class `FileWatcher`

A utility class that wraps a `RAGKernel` and monitors a filesystem directory for changes.

### Constructor

```python
def __init__(self, rag_kernel: RAGKernel, watch_path: str, extensions: Optional[List[str]] = None, recursive: bool = True)
```

**Parameters:**
*   `rag_kernel`: An initialized `RAGKernel` instance.
*   `watch_path`: Path to the directory to monitor.
*   `extensions`: List of file extensions to include (e.g., `["txt", "md"]`). If None, watches all files.
*   `recursive`: Whether to watch subdirectories. Default `True`.

### Methods

#### `sync`

```python
def sync(self) -> None
```

Performs a one-time scan of the directory and adds any matching files that aren't already in the index (based on path/hash).

#### `start_watching`

```python
def start_watching(self) -> None
```

Spawns a background thread that listens for OS-level file system events (`Create`, `Modify`, `Delete`). Changes are reflected in the RAG Kernel instantly.

#### `stop_watching`

```python
def stop_watching(self) -> None
```

Stops the background monitoring thread.

---

## Class `Document`

A simple data class representing a retrieved result.

**Properties:**
*   `id` *(str)*: The unique ID of the document (or chunk).
*   `content` *(str)*: The text content.
*   `metadata` *(dict)*: The associated metadata.
