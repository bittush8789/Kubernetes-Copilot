import os
import logging
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from backend.config import settings
from backend.rag.embeddings import embedding_service

logger = logging.getLogger("kubernetes-copilot.chroma")

class ChromaManager:
    def __init__(
        self,
        persist_directory: Optional[str] = None,
        collection_name: Optional[str] = None
    ):
        self.persist_directory = persist_directory or settings.CHROMA_PERSIST_DIRECTORY
        self.collection_name = collection_name or settings.COLLECTION_NAME
        os.makedirs(self.persist_directory, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Kubernetes Official Documentation Vector Store"}
        )
        logger.info(
            f"ChromaDB initialized at '{self.persist_directory}' "
            f"with collection '{self.collection_name}'. Document count: {self.collection.count()}"
        )

    def add_documents(
        self,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str]
    ) -> None:
        """
        Embeds and upserts documents into ChromaDB.
        """
        if not documents:
            return
        
        embeddings = embedding_service.embed_documents(documents)
        self.collection.upsert(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        logger.info(f"Upserted {len(documents)} document chunks into ChromaDB.")

    def query(
        self,
        query_text: str,
        n_results: int = 4,
        where_filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Queries ChromaDB using semantic embeddings.
        """
        count = self.collection.count()
        if count == 0:
            logger.warning("ChromaDB collection is empty. Returning empty results.")
            return []

        limit = min(n_results, count)
        query_embedding = embedding_service.embed_query(query_text)
        
        kwargs = {
            "query_embeddings": [query_embedding],
            "n_results": limit,
        }
        if where_filter:
            kwargs["where"] = where_filter

        results = self.collection.query(**kwargs)
        
        retrieved_docs = []
        if results and "documents" in results and results["documents"]:
            docs = results["documents"][0]
            metas = results["metadatas"][0] if "metadatas" in results and results["metadatas"] else [{}] * len(docs)
            distances = results.get("distances", [[]])[0]
            
            for i, doc_text in enumerate(docs):
                meta = metas[i] if i < len(metas) else {}
                dist = distances[i] if i < len(distances) else None
                retrieved_docs.append({
                    "content": doc_text,
                    "metadata": meta,
                    "distance": dist
                })

        return retrieved_docs

    def count(self) -> int:
        return self.collection.count()

    def reset_collection(self) -> None:
        self.client.delete_collection(name=self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Kubernetes Official Documentation Vector Store"}
        )
        logger.info(f"Reset ChromaDB collection '{self.collection_name}'.")

# Global ChromaDB Manager singleton
chroma_manager = ChromaManager()
