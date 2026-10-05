import logging
from typing import List, Dict, Any

logger = logging.getLogger("kubernetes-copilot.ingestion.chunker")

class KubernetesChunker:
    """
    Chunks Kubernetes documentation into semantically coherent segments
    while preserving document metadata.
    """
    def __init__(self, chunk_size: int = 600, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(self, doc: Dict[str, Any]) -> List[Dict[str, Any]]:
        content = doc.get("content", "")
        if not content:
            return []

        # Split by double newlines (paragraphs) first, or fixed character windows
        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
        chunks: List[str] = []
        current_chunk = ""

        for para in paragraphs:
            if len(current_chunk) + len(para) + 2 <= self.chunk_size:
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                
                # If paragraph itself is larger than chunk_size, slice it
                if len(para) > self.chunk_size:
                    start = 0
                    while start < len(para):
                        end = start + self.chunk_size
                        chunks.append(para[start:end])
                        start += self.chunk_size - self.chunk_overlap
                    current_chunk = ""
                else:
                    current_chunk = para

        if current_chunk:
            chunks.append(current_chunk)

        # Assemble chunk objects with complete metadata
        chunk_objects = []
        for idx, chunk_text in enumerate(chunks):
            chunk_id = f"{doc.get('document_id', 'doc')}_chunk_{idx}"
            chunk_objects.append({
                "chunk_id": chunk_id,
                "text": chunk_text,
                "metadata": {
                    "document_id": doc.get("document_id", ""),
                    "title": doc.get("title", ""),
                    "section": doc.get("section", ""),
                    "source": doc.get("source", "Kubernetes Official Documentation"),
                    "url": doc.get("url", "https://kubernetes.io/docs/"),
                    "chunk_index": idx
                }
            })

        logger.debug(f"Document '{doc.get('title')}' split into {len(chunk_objects)} chunks.")
        return chunk_objects

    def chunk_documents(self, docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        all_chunks = []
        for doc in docs:
            all_chunks.extend(self.chunk_document(doc))
        logger.info(f"Chunked {len(docs)} documents into a total of {len(all_chunks)} chunks.")
        return all_chunks
