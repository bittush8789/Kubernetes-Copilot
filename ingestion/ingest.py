import sys
import os
import logging

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.rag.chroma import chroma_manager
from ingestion.loader import KubernetesDocLoader
from ingestion.chunker import KubernetesChunker

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("kubernetes-copilot.ingest")

def run_ingestion(reset: bool = False):
    """
    Executes the official Kubernetes documentation ingestion pipeline:
    Loader -> Chunker -> Embeddings -> ChromaDB
    """
    logger.info("Starting Kubernetes documentation ingestion pipeline...")
    
    if reset:
        logger.info("Resetting existing ChromaDB collection...")
        chroma_manager.reset_collection()

    current_count = chroma_manager.count()
    if current_count > 0 and not reset:
        logger.info(f"ChromaDB already contains {current_count} documents. Skipping duplicate ingestion.")
        return current_count

    # 1. Load Documents
    loader = KubernetesDocLoader()
    docs = loader.load_curated_docs()
    logger.info(f"Loaded {len(docs)} official Kubernetes documentation items.")

    # 2. Chunk Documents
    chunker = KubernetesChunker(chunk_size=550, chunk_overlap=80)
    chunk_objects = chunker.chunk_documents(docs)
    logger.info(f"Generated {len(chunk_objects)} document chunks.")

    # 3. Prepare for ChromaDB
    texts = [c["text"] for c in chunk_objects]
    metadatas = [c["metadata"] for c in chunk_objects]
    ids = [c["chunk_id"] for c in chunk_objects]

    # 4. Embed & Upsert
    logger.info("Generating embeddings and indexing into ChromaDB...")
    chroma_manager.add_documents(documents=texts, metadatas=metadatas, ids=ids)

    final_count = chroma_manager.count()
    logger.info(f"Ingestion complete! Total documents in ChromaDB collection: {final_count}")
    return final_count

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Ingest Kubernetes Official Documentation into ChromaDB")
    parser.add_argument("--reset", action="store_true", help="Reset ChromaDB collection before ingestion")
    args = parser.parse_args()

    run_ingestion(reset=args.reset)
