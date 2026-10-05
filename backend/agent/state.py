from typing import Annotated, Dict, List, Optional, Any
from typing_extensions import TypedDict
import operator

class SourceItem(TypedDict):
    title: str
    url: str
    section: Optional[str]

class RetrievedDoc(TypedDict):
    content: str
    metadata: Dict[str, Any]

class AgentState(TypedDict):
    conversation_id: str
    user_query: str
    chat_history: List[Dict[str, str]]
    intent: Optional[str]
    selected_tool: Optional[str]  # 'rag', 'mcp', 'rag+mcp', 'direct'
    rag_context: List[RetrievedDoc]
    mcp_context: List[Dict[str, Any]]
    combined_context: str
    sources: List[SourceItem]
    tools_used: List[str]
    final_answer: str
    error: Optional[str]
