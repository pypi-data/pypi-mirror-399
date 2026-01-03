"""Basic usage example for memalloy."""

from memalloy import RAGKernel


def main():
    # Initialize the RAG kernel
    print("Initializing RAG kernel...")
    rag = RAGKernel(embedding_dimension=384, chunk_size=500, overlap=50)

    # Add some documents
    print("\nAdding documents...")
    documents = [
        (
            "Python is a high-level, interpreted programming language with dynamic semantics. "
            "Its high-level built-in data structures, combined with dynamic typing and dynamic binding, "
            "make it very attractive for Rapid Application Development.",
            {"source": "wikipedia", "topic": "programming", "language": "python"},
        ),
        (
            "Rust is a multi-paradigm, general-purpose programming language that emphasizes performance, "
            "type safety, and concurrency. Rust enforces memory safety without requiring garbage collection.",
            {"source": "wikipedia", "topic": "programming", "language": "rust"},
        ),
        (
            "Machine learning is a method of data analysis that automates analytical model building. "
            "It is a branch of artificial intelligence based on the idea that systems can learn from data.",
            {"source": "wikipedia", "topic": "ai", "field": "machine learning"},
        ),
        (
            "Natural language processing (NLP) is a subfield of linguistics, computer science, "
            "and artificial intelligence concerned with the interactions between computers and human language.",
            {"source": "wikipedia", "topic": "ai", "field": "nlp"},
        ),
    ]

    doc_ids = []
    for content, metadata in documents:
        doc_id = rag.add_document(content, metadata)
        doc_ids.append(doc_id)
        print(f"  Added document: {doc_id[:8]}...")

    # Search for similar content
    print("\n" + "=" * 60)
    print("Searching for 'programming languages'...")
    print("=" * 60)
    results = rag.search("programming languages", top_k=3)

    for i, (doc, score) in enumerate(results, 1):
        print(f"\nResult {i} (Score: {score:.4f}):")
        print(f"  Content: {doc.content[:100]}...")
        print(f"  Metadata: {doc.metadata}")

    # Another search
    print("\n" + "=" * 60)
    print("Searching for 'artificial intelligence'...")
    print("=" * 60)
    results = rag.search("artificial intelligence", top_k=2)

    for i, (doc, score) in enumerate(results, 1):
        print(f"\nResult {i} (Score: {score:.4f}):")
        print(f"  Content: {doc.content[:100]}...")
        print(f"  Metadata: {doc.metadata}")

    # List all documents
    print("\n" + "=" * 60)
    print("Document Management")
    print("=" * 60)
    all_docs = rag.list_documents()
    print(f"Total documents: {len(all_docs)}")
    print(f"Total chunks: {rag.count()}")

    # Remove a document
    if doc_ids:
        print(f"\nRemoving document: {doc_ids[0][:8]}...")
        removed = rag.remove_document(doc_ids[0])
        print(f"Removed: {removed}")
        print(f"Remaining documents: {len(rag.list_documents())}")


if __name__ == "__main__":
    main()
