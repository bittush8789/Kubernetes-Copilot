import logging
from typing import List, Dict, Any, Optional
import httpx
from bs4 import BeautifulSoup
from backend.mcp.client import K8S_DOCS_REGISTRY

logger = logging.getLogger("kubernetes-copilot.ingestion.loader")

class KubernetesDocLoader:
    """
    Loader for official Kubernetes documentation.
    Can load from pre-curated official documentation registry or live web pages.
    """
    def __init__(self, registry: Optional[List[Dict[str, Any]]] = None):
        self.registry = registry or K8S_DOCS_REGISTRY

    def load_curated_docs(self) -> List[Dict[str, Any]]:
        """
        Loads the pre-structured official Kubernetes documentation pages.
        """
        logger.info(f"Loading {len(self.registry)} official Kubernetes documentation documents.")
        return self.registry

    def load_from_url(self, url: str, section: str = "Live Web Doc") -> Optional[Dict[str, Any]]:
        """
        Loads and parses a live Kubernetes documentation web page.
        """
        try:
            logger.info(f"Fetching documentation from {url}...")
            response = httpx.get(url, timeout=10.0, follow_redirects=True)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Remove scripts, styles, navbars
            for element in soup(["script", "style", "nav", "footer", "header"]):
                element.extract()
                
            title_tag = soup.find("h1") or soup.find("title")
            title = title_tag.get_text(strip=True) if title_tag else "Kubernetes Documentation"
            
            # Content body
            main_content = soup.find("main") or soup.find("article") or soup.body
            text = main_content.get_text(separator="\n", strip=True) if main_content else ""
            
            # Generate doc id
            doc_id = "k8s-" + url.rstrip("/").split("/")[-1].replace(".html", "")
            
            return {
                "document_id": doc_id,
                "title": title,
                "section": section,
                "source": "Kubernetes Official Documentation",
                "url": url,
                "content": text,
                "summary": text[:200]
            }
        except Exception as e:
            logger.error(f"Failed to load URL {url}: {e}")
            return None
