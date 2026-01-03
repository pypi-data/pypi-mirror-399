# MemAlloy

> "The High-Performance Memory Kernel for AI Agents."

**MemAlloy** is an open-source "Memory Kernel" designed to solve the data ingestion and retrieval bottleneck in Python AI applications. By offloading heavy tasks to a high-performance Rust core, it provides Python developers with a "Second Brain" that is **100x faster**, **memory-efficient**, and **privacy-first**.

## The Problem

Python is the language of AI, but it is ill-suited for the infrastructure of AI Memory:

*   **Latency**: Watching thousands of files and chunking text introduces massive lag (GIL issues).
*   **Complexity**: Glueing together `watchdog`, `pypdf`, `sentence-transformers`, `chromadb`, etc. is fragile.
*   **Resource Heaviness**: Docker containers for vector DBs consume GBs of RAM.

## The Solution

MemAlloy consolidates the entire RAG pipeline into a single, installable binary that exposes a clean Python API.

---

### Key Features

*   ⚡ **Zero-Latency Ingestion**: Detects file changes instantly.
*   🧠 **Local Intelligence**: Runs ONNX embedding models locally on CPU.
*   💾 **Embedded Storage**: Uses **LanceDB** for serverless, persistent vector storage.
*   🐍 **Python Native**: Simple `pip install` experience.
