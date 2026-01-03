import logging
import time
from memalloy import RAGKernel

# Set up logging to clear any internal noise if needed
logging.basicConfig(level=logging.INFO)

def main():
    print("🚀 Initializing MemAlloy 'Second Brain'...")
    # This might take a few seconds on first run to download the ONNX model (~100MB)
    start_time = time.time()
    rag = RAGKernel()
    print(f"✅ Kernel initialized in {time.time() - start_time:.2f}s")

    print("\n📚 Ingesting knowledge...")
    # Add some sample documents
    rag.add_document(
        "MemAlloy is a high-performance memory kernel for AI agents built with Rust.",
        metadata={"category": "tech", "lang": "rust"}
    )
    rag.add_document(
        "Python is great for high-level logic but slow for heavy data processing due to the GIL.",
        metadata={"category": "tech", "lang": "python"}
    )
    rag.add_document(
        "The mitochondria is the powerhouse of the cell.",
        metadata={"category": "biology"}
    )

    print("\n🔍 Running Semantic Search...")
    query = "Why is python slow?"
    print(f"Query: '{query}'")
    
    # Perform search
    results = rag.search(query, top_k=1)
    
    for doc, score in results:
        print(f"\nResult (Score: {score:.4f}):")
        print(f"Content: {doc.content}")
        print(f"Metadata: {doc.metadata}")

    print("\n💾 Vector Store Persistence Check...")
    print(f"Total chunks in DB: {rag.count()}")
    print("Data is saved to './.memalloy_data' and will persist across runs.")

if __name__ == "__main__":
    main()
