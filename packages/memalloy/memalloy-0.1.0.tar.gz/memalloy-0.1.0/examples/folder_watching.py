"""Example of using memalloy to watch a folder and automatically create embeddings."""

import os
import time
from pathlib import Path
from memalloy import RAGKernel, PyFileWatcher


def create_test_files(test_dir: Path):
    """Create some test files in the directory."""
    test_dir.mkdir(exist_ok=True)
    
    files = {
        "python_intro.txt": "Python is a high-level programming language known for its simplicity and readability.",
        "rust_intro.txt": "Rust is a systems programming language focused on safety, speed, and concurrency.",
        "machine_learning.md": "# Machine Learning\n\nMachine learning is a subset of artificial intelligence that enables computers to learn from data.",
        "data_science.md": "# Data Science\n\nData science combines statistics, programming, and domain expertise to extract insights from data.",
    }
    
    for filename, content in files.items():
        filepath = test_dir / filename
        filepath.write_text(content)
        print(f"Created: {filepath}")


def main():
    # Create a test directory
    test_dir = Path("test_documents")
    
    # Clean up if it exists
    if test_dir.exists():
        import shutil
        shutil.rmtree(test_dir)
    
    # Create test files
    print("Creating test files...")
    create_test_files(test_dir)
    
    # Initialize RAG kernel
    print("\nInitializing RAG kernel...")
    rag = RAGKernel(embedding_dimension=384, chunk_size=500, overlap=50)
    
    # Create file watcher
    print(f"Setting up file watcher for: {test_dir.absolute()}")
    watcher = PyFileWatcher(
        rag_kernel=rag,
        watch_path=str(test_dir.absolute()),
        extensions=["txt", "md"],  # Only watch .txt and .md files
        recursive=True
    )
    
    # Initial sync - process all existing files
    print("\nPerforming initial sync...")
    count = watcher.sync()
    print(f"Processed {count} files")
    
    # Show current documents
    print(f"\nDocuments in store: {len(rag.list_documents())}")
    print(f"Total chunks: {rag.count()}")
    
    # Start watching for changes
    print("\nStarting file watcher...")
    watcher.start_watching()
    print("File watcher is now active. Try modifying files in the test_documents folder!")
    
    # Demonstrate search
    print("\n" + "=" * 60)
    print("Testing search functionality...")
    print("=" * 60)
    results = rag.search("programming languages", top_k=3)
    for i, (doc, score) in enumerate(results, 1):
        print(f"\nResult {i} (Score: {score:.4f}):")
        print(f"  Content: {doc.content[:80]}...")
        print(f"  Source: {doc.metadata.get('file_name', 'unknown')}")
    
    # Wait a bit and then add a new file to demonstrate watching
    print("\n" + "=" * 60)
    print("Adding a new file to demonstrate auto-detection...")
    print("=" * 60)
    time.sleep(2)
    
    new_file = test_dir / "new_document.txt"
    new_file.write_text("This is a new document about artificial intelligence and neural networks.")
    print(f"Created new file: {new_file}")
    
    # Wait for watcher to process
    time.sleep(1)
    
    # Check if new document was added
    print(f"\nDocuments after new file: {len(rag.list_documents())}")
    print(f"Total chunks: {rag.count()}")
    
    # Search for the new content
    results = rag.search("neural networks", top_k=2)
    print("\nSearch results for 'neural networks':")
    for i, (doc, score) in enumerate(results, 1):
        print(f"  {i}. Score: {score:.4f} - {doc.metadata.get('file_name', 'unknown')}")
    
    # Modify an existing file
    print("\n" + "=" * 60)
    print("Modifying an existing file...")
    print("=" * 60)
    time.sleep(1)
    
    python_file = test_dir / "python_intro.txt"
    python_file.write_text(
        "Python is a high-level programming language known for its simplicity and readability. "
        "It supports multiple programming paradigms including object-oriented, functional, and procedural programming."
    )
    print(f"Modified: {python_file}")
    
    # Wait for watcher to process
    time.sleep(1)
    
    # Search again
    results = rag.search("programming paradigms", top_k=2)
    print("\nSearch results for 'programming paradigms':")
    for i, (doc, score) in enumerate(results, 1):
        print(f"  {i}. Score: {score:.4f} - {doc.metadata.get('file_name', 'unknown')}")
    
    # Stop watching
    print("\nStopping file watcher...")
    watcher.stop_watching()
    print("Done!")
    
    # Cleanup
    print(f"\nCleaning up test directory: {test_dir}")
    import shutil
    shutil.rmtree(test_dir)


if __name__ == "__main__":
    main()
