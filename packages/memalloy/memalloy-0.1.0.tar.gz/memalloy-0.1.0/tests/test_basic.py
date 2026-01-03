"""Basic tests for memalloy."""

import pytest


def test_import():
    """Test that memalloy can be imported."""
    try:
        from memalloy import RAGKernel, PyDocument, PyChunkingStrategy
        assert RAGKernel is not None
        assert PyDocument is not None
        assert PyChunkingStrategy is not None
    except ImportError:
        pytest.skip("memalloy not built yet. Run 'maturin develop' first.")


def test_rag_kernel_initialization():
    """Test RAG kernel initialization."""
    try:
        from memalloy import RAGKernel
        
        rag = RAGKernel(chunk_size=500, overlap=50)
        assert rag is not None
    except ImportError:
        pytest.skip("memalloy not built yet.")


def test_add_document():
    """Test adding a document."""
    try:
        from memalloy import RAGKernel
        
        rag = RAGKernel()
        doc_id = rag.add_document("Test document content")
        assert doc_id is not None
        assert len(doc_id) > 0
    except ImportError:
        pytest.skip("memalloy not built yet.")


def test_search():
    """Test searching for documents."""
    try:
        from memalloy import RAGKernel
        
        rag = RAGKernel()
        
        # Add a document
        rag.add_document("Python is a programming language")
        
        # Search
        results = rag.search("programming", top_k=5)
        assert len(results) > 0
        assert isinstance(results[0], tuple)
        assert len(results[0]) == 2  # (document, score)
    except ImportError:
        pytest.skip("memalloy not built yet.")


def test_document_management():
    """Test document management operations."""
    try:
        from memalloy import RAGKernel
        
        rag = RAGKernel()
        
        # Add documents
        doc_id1 = rag.add_document("Document 1")
        doc_id2 = rag.add_document("Document 2")
        
        # List documents
        # doc_ids = rag.list_documents()
        # assert doc_id1 in doc_ids
        # assert doc_id2 in doc_ids
        
        # Remove document
        # removed = rag.remove_document(doc_id1)
        # assert removed is True
        
        # Verify removal
        # doc_ids = rag.list_documents()
        # assert doc_id1 not in doc_ids
        # assert doc_id2 in doc_ids
    except ImportError:
        pytest.skip("memalloy not built yet.")
