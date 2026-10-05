import logging
from typing import List, Dict, Any, Optional
from backend.rag.chroma import chroma_manager

logger = logging.getLogger("kubernetes-copilot.retriever")

class KubernetesRetriever:
    """
    RAG Retriever for Kubernetes Official Documentation.
    Performs semantic search over ChromaDB and constructs grounded context.
    """
    def __init__(self, top_k: int = 4):
        self.top_k = top_k

    def search_knowledge_base(
        self,
        query: str,
        top_k: Optional[int] = None,
        filter_section: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Executes semantic retrieval against ChromaDB.
        Returns top-k chunks with metadata and source tracking.
        """
        k = top_k or self.top_k
        where_clause = {"section": filter_section} if filter_section else None
        
        try:
            results = chroma_manager.query(query_text=query, n_results=k, where_filter=where_clause)
            logger.info(f"Retrieved {len(results)} chunks for query: '{query[:50]}...'")
            return results
        except Exception as e:
            logger.error(f"Error querying knowledge base: {e}")
            return []

    def format_context(self, docs: List[Dict[str, Any]]) -> str:
        """
        Formats retrieved documentation chunks into clean context for LLM synthesis.
        """
        if not docs:
            return "No matching documentation found in Kubernetes knowledge base."

        formatted_chunks = []
        for i, doc in enumerate(docs, 1):
            meta = doc.get("metadata", {})
            title = meta.get("title", "Official Documentation")
            section = meta.get("section", "Kubernetes Docs")
            url = meta.get("url", "https://kubernetes.io/docs/")
            content = doc.get("content", "").strip()

            chunk_str = (
                f"### [Document {i}] {title} ({section})\n"
                f"Source: Kubernetes Official Documentation\n"
                f"URL: {url}\n"
                f"Content:\n{content}\n"
            )
            formatted_chunks.append(chunk_str)

        return "\n----------------------------------------\n".join(formatted_chunks)

k8s_retriever = KubernetesRetriever()
