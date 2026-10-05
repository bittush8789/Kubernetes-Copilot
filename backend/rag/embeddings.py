import logging
import hashlib
import math
from typing import List
from backend.config import settings

logger = logging.getLogger("kubernetes-copilot.embeddings")

STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can't", "cannot", "could", "did",
    "do", "does", "doing", "don't", "down", "during", "each", "few", "for", "from",
    "further", "had", "has", "have", "having", "he", "her", "here", "hers", "herself",
    "him", "himself", "his", "how", "i", "if", "in", "into", "is", "isn't", "it",
    "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself",
    "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought",
    "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she",
    "should", "so", "some", "such", "than", "that", "the", "their", "theirs",
    "them", "themselves", "then", "there", "these", "they", "this", "those",
    "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we",
    "were", "weren't", "what", "when", "where", "which", "while", "who", "whom",
    "why", "with", "won't", "would", "you", "your", "yours", "yourself"
}

K8S_KEYWORDS = {
    "pod": 6.0, "pods": 6.0,
    "deployment": 6.0, "deployments": 6.0,
    "service": 6.0, "services": 6.0,
    "ingress": 6.0,
    "crashloopbackoff": 8.0,
    "imagepullbackoff": 8.0,
    "statefulset": 6.0, "statefulsets": 6.0,
    "daemonset": 6.0, "daemonsets": 6.0,
    "configmap": 6.0, "configmaps": 6.0,
    "secret": 6.0, "secrets": 6.0,
    "replicaset": 6.0, "replicasets": 6.0,
    "kubectl": 5.0, "namespace": 5.0,
    "kubelet": 5.0, "control plane": 5.0,
    "troubleshooting": 5.0, "debug": 5.0
}

class EmbeddingService:
    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.EMBEDDING_MODEL_NAME
        self._model = None
        self._use_chroma_default = True

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        for text in texts:
            vec = [0.0] * 384
            tokens = text.lower().replace("-", " ").replace("/", " ").replace("(", " ").replace(")", " ").split()
            for token in tokens:
                if token in STOP_WORDS or len(token) < 2:
                    continue
                weight = K8S_KEYWORDS.get(token, 1.0)
                idx = int(hashlib.md5(token.encode()).hexdigest(), 16) % 384
                vec[idx] += weight
            norm = math.sqrt(sum(x * x for x in vec)) or 1.0
            embeddings.append([x / norm for x in vec])
        return embeddings

    def embed_query(self, text: str) -> List[float]:
        return self.embed_documents([text])[0]

embedding_service = EmbeddingService()
