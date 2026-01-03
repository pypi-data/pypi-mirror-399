# Architecture

MemAlloy is a **hybrid system** that bridges the ease of Python with the raw performance of Rust. It avoids the common "Python Glue" antipattern where Python orchestrates heavy loops, instead pushing the entire data pipeline down into native code.

## System Diagram

![MemAlloy Architecture](assets/architecture_diagram.png)

## Component Deep Dive

### 1. The Interface Layer (`src/lib.rs`)
*   **Technology**: [PyO3](https://pyo3.rs/)
*   **Role**: Converts Python objects into Rust structs and vice-versa.
*   **Optimization**: We use `PyString` and zero-copy references where possible to avoid memory duplication when passing large documents from Python to Rust.

### 2. The Async Runtime (`src/rag.rs`)
*   **Technology**: [Tokio](https://tokio.rs/)
*   **Role**: Although the Python API is synchronous (blocking for simplicity), the Rust core runs an internal Tokio runtime.
*   **Why?**: Database I/O (LanceDB) and file system events are inherently asynchronous. We bridge this gap by spawning a temporary runtime for each operation or properly managing a background thread for the `FileWatcher`.

### 3. The Embedding Engine (`src/embedding.rs`)
*   **Technology**: [FastEmbed-rs](https://github.com/Anush008/fastembed-rs) + `ort` (ONNX Runtime)
*   **Model**: `All-MiniLM-L6-v2` (Quantized).
*   **Performance**:
    *   Typical Python implementations use valid PyTorch which is heavy (2GB+ RAM).
    *   MemAlloy uses the ONNX runtime which is extremely lightweight (<500MB RAM) and optimized for CPU inference (AVX2/AVX512 instructions).

### 4. Storage Engine (`src/vector_store.rs`)
*   **Technology**: [LanceDB](https://lancedb.com/)
*   **Format**: Apache Arrow (Columnar).
*   **Schema**:
    *   `id`: UUID (String)
    *   `vector`: FixedSizeList<Float32> (384 dimensions)
    *   `document_id`: The parent document UUID
    *   `content`: The literal text chunk (String)
    *   `metadata`: JSON String (for flexible filtering)
*   **Benefit**: LanceDB allows us to perform Approximate Nearest Neighbor (ANN) search directly on disk without loading the entire index into RAM, making it "Serverless" and scalable.

## Concurrency Model

When you call `rag.add_document()`, Python releases the **GIL (Global Interpreter Lock)** immediately. This allows your Python application (e.g., a FastAPI server or Streamlit app) to remain responsive while Rust crunches the numbers on background threads.

1.  **Python call** enters Rust.
2.  **Rust** releases GIL.
3.  **Rust** spawns work on rayon/tokio threads.
4.  **Result** computed.
5.  **Rust** re-acquires GIL to return result.
