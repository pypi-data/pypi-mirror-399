"""
memalloy - A high-performance Python package wrapping a Rust-based local RAG kernel.

Memalloy provides a fast, local RAG (Retrieval-Augmented Generation) system that runs
entirely on your machine. It's built with Rust for performance and exposed through
a clean Python API.

Example:
    >>> from memalloy import RAGKernel
    >>> 
    >>> # Initialize the RAG kernel
    >>> rag = RAGKernel(embedding_dimension=384, chunk_size=500, overlap=50)
    >>> 
    >>> # Add documents
    >>> doc_id = rag.add_document(
    ...     "Python is a high-level programming language.",
    ...     metadata={"source": "wikipedia"}
    ... )
    >>> 
    >>> # Search for similar content
    >>> results = rag.search("programming languages", top_k=5)
    >>> for doc, score in results:
    ...     print(f"Score: {score:.3f} - {doc.content[:50]}...")
"""

try:
    from memalloy._memalloy import RAGKernel, PyDocument, PyChunkingStrategy, PyFileWatcher

    __all__ = ["RAGKernel", "PyDocument", "PyChunkingStrategy", "PyFileWatcher"]
except ImportError:
    # Fallback for when the Rust extension isn't built yet
    __all__ = []

__version__ = "0.1.0"
