import json
import logging
from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, HumanMessage

from backend.agent.state import AgentState, SourceItem
from backend.agent.prompts import (
    INTENT_ROUTING_PROMPT,
    SYSTEM_GROUNDING_PROMPT,
    SYNTHESIS_USER_PROMPT,
    FALLBACK_RESPONSE,
)
from backend.rag.retriever import k8s_retriever
from backend.mcp.client import mcp_client
from backend.llm.grok import grok_service

logger = logging.getLogger("kubernetes-copilot.agent")

def understand_query_node(state: AgentState) -> Dict[str, Any]:
    """
    Node 1: Query Understanding & Autonomous Tool Selection.
    Analyzes user query and conversation context to select RAG, MCP, RAG+MCP, or direct.
    """
    query = state.get("user_query", "").strip()
    history = state.get("chat_history", [])
    
    # Format recent history for intent context
    history_snippet = "\n".join([f"{m.get('role', 'user')}: {m.get('content', '')}" for m in history[-4:]])
    
    routing_user_msg = f"User Query: {query}\nRecent History:\n{history_snippet}"
    
    routing_output = grok_service.invoke([
        SystemMessage(content=INTENT_ROUTING_PROMPT),
        HumanMessage(content=routing_user_msg)
    ])
    
    intent = "k8s_concept"
    selected_tool = "rag"
    
    try:
        clean_text = routing_output.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]
        parsed = json.loads(clean_text)
        intent = parsed.get("intent", "k8s_concept")
        selected_tool = parsed.get("selected_tool", "rag")
    except Exception as e:
        logger.warning(f"Could not parse routing JSON ({e}); using heuristic classification.")
        lower_q = query.lower()
        if any(term in lower_q for term in ["find", "official", "url", "link", "doc", "where is", "reference"]):
            intent = "doc_retrieval"
            selected_tool = "mcp"
        elif any(term in lower_q for term in ["crashloopbackoff", "imagepullbackoff", "troubleshoot", "debug", "oomkilled", "error"]):
            intent = "troubleshooting"
            selected_tool = "rag+mcp"
        elif any(term in lower_q for term in ["hi", "hello", "hey"]):
            intent = "greeting"
            selected_tool = "direct"
        else:
            intent = "k8s_concept"
            selected_tool = "rag"

    logger.info(f"Intent classified: '{intent}', Selected tool: '{selected_tool}'")
    return {
        "intent": intent,
        "selected_tool": selected_tool,
        "tools_used": []
    }

def rag_node(state: AgentState) -> Dict[str, Any]:
    """
    Node: RAG Retrieval from ChromaDB.
    """
    query = state.get("user_query", "")
    retrieved_chunks = k8s_retriever.search_knowledge_base(query=query, top_k=4)
    
    sources: List[SourceItem] = []
    seen_urls = set()
    for chunk in retrieved_chunks:
        meta = chunk.get("metadata", {})
        url = meta.get("url", "https://kubernetes.io/docs/")
        title = meta.get("title", "Official Documentation")
        if url not in seen_urls:
            seen_urls.add(url)
            sources.append({
                "title": title,
                "url": url,
                "section": meta.get("section")
            })

    context_str = k8s_retriever.format_context(retrieved_chunks)
    
    return {
        "rag_context": retrieved_chunks,
        "combined_context": context_str,
        "sources": sources,
        "tools_used": ["rag"]
    }

def mcp_node(state: AgentState) -> Dict[str, Any]:
    """
    Node: MCP Retrieval from official Kubernetes Documentation registry.
    """
    query = state.get("user_query", "")
    mcp_docs = mcp_client.search_docs(query=query, limit=3)
    
    sources: List[SourceItem] = []
    seen_urls = set()
    mcp_text_blocks = []
    
    for i, doc in enumerate(mcp_docs, 1):
        url = doc.get("url", "https://kubernetes.io/docs/")
        title = doc.get("title", "Official Documentation")
        if url not in seen_urls:
            seen_urls.add(url)
            sources.append({
                "title": title,
                "url": url,
                "section": doc.get("section")
            })
            
        mcp_text_blocks.append(
            f"### [MCP Doc {i}] {title} ({doc.get('section', '')})\n"
            f"Source: {doc.get('source', 'Kubernetes Official Documentation')}\n"
            f"URL: {url}\n"
            f"Summary: {doc.get('summary', '')}\n"
            f"Content:\n{doc.get('content', '')}\n"
        )
        
    combined_str = "\n----------------------------------------\n".join(mcp_text_blocks)
    if not combined_str:
        combined_str = "No matching documentation found via Kubernetes Documentation MCP."
        
    return {
        "mcp_context": mcp_docs,
        "combined_context": combined_str,
        "sources": sources,
        "tools_used": ["mcp"]
    }

def rag_plus_mcp_node(state: AgentState) -> Dict[str, Any]:
    """
    Node: Combined RAG + MCP Retrieval.
    Used for complex troubleshooting or questions needing both deep semantic context and exact documentation references.
    """
    query = state.get("user_query", "")
    
    # 1. RAG retrieval from ChromaDB
    retrieved_chunks = k8s_retriever.search_knowledge_base(query=query, top_k=3)
    rag_str = k8s_retriever.format_context(retrieved_chunks)
    
    # 2. MCP lookup
    mcp_docs = mcp_client.search_docs(query=query, limit=3)
    mcp_text_blocks = []
    
    sources: List[SourceItem] = []
    seen_urls = set()
    
    for chunk in retrieved_chunks:
        meta = chunk.get("metadata", {})
        url = meta.get("url", "https://kubernetes.io/docs/")
        title = meta.get("title", "Official Documentation")
        if url not in seen_urls:
            seen_urls.add(url)
            sources.append({
                "title": title,
                "url": url,
                "section": meta.get("section")
            })

    for i, doc in enumerate(mcp_docs, 1):
        url = doc.get("url", "https://kubernetes.io/docs/")
        title = doc.get("title", "Official Documentation")
        if url not in seen_urls:
            seen_urls.add(url)
            sources.append({
                "title": title,
                "url": url,
                "section": doc.get("section")
            })
            
        mcp_text_blocks.append(
            f"### [MCP Doc {i}] {title} ({doc.get('section', '')})\n"
            f"Source: {doc.get('source', 'Kubernetes Official Documentation')}\n"
            f"URL: {url}\n"
            f"Summary: {doc.get('summary', '')}\n"
            f"Content:\n{doc.get('content', '')}\n"
        )
        
    mcp_str = "\n----------------------------------------\n".join(mcp_text_blocks)
    combined = (
        f"--- RAG RETRIEVAL (ChromaDB) ---\n{rag_str}\n\n"
        f"--- KUBERNETES DOCUMENTATION MCP ---\n{mcp_str}"
    )
    
    return {
        "rag_context": retrieved_chunks,
        "mcp_context": mcp_docs,
        "combined_context": combined,
        "sources": sources,
        "tools_used": ["rag", "mcp"]
    }

def generate_answer_node(state: AgentState) -> Dict[str, Any]:
    """
    Node: Grok Reasoning & Answer Synthesis.
    Applies strict grounding rules and produces final Markdown answer.
    """
    query = state.get("user_query", "")
    context = state.get("combined_context", "")
    history = state.get("chat_history", [])
    selected_tool = state.get("selected_tool", "rag")
    
    # Handle direct greetings or general conversational intent
    if selected_tool == "direct":
        return {
            "final_answer": (
                "Hello! I am **Kubernetes Copilot**, your Agentic RAG assistant. "
                "I can help you understand Kubernetes architecture, workloads (Pods, Deployments, StatefulSets), "
                "networking (Services, Ingress), configuration, and troubleshoot issues like CrashLoopBackOff. "
                "What would you like to explore?"
            ),
            "sources": [],
            "tools_used": []
        }

    # Grounding check: If context is empty or no documents retrieved
    if not context or "no matching documentation found" in context.lower():
        return {
            "final_answer": FALLBACK_RESPONSE,
            "sources": [],
            "tools_used": state.get("tools_used", [])
        }

    # Prepare chat history context
    history_str = "\n".join([f"{m.get('role', 'user')}: {m.get('content', '')}" for m in history[-6:]])
    if not history_str:
        history_str = "None (Initial turn)"

    user_prompt = SYNTHESIS_USER_PROMPT.format(
        context=context,
        chat_history=history_str,
        user_query=query
    )

    llm_answer = grok_service.invoke([
        SystemMessage(content=SYSTEM_GROUNDING_PROMPT),
        HumanMessage(content=user_prompt)
    ])

    return {
        "final_answer": llm_answer
    }

def route_decision(state: AgentState) -> str:
    """
    Branching condition based on autonomous tool selection.
    """
    tool = state.get("selected_tool", "rag")
    if tool == "rag":
        return "rag_node"
    elif tool == "mcp":
        return "mcp_node"
    elif tool == "rag+mcp":
        return "rag_plus_mcp_node"
    else:
        return "generate_answer_node"

def build_kubernetes_copilot_graph():
    """
    Builds and compiles the LangGraph StateGraph.
    """
    workflow = StateGraph(AgentState)

    # Add Nodes
    workflow.add_node("understand_query", understand_query_node)
    workflow.add_node("rag_node", rag_node)
    workflow.add_node("mcp_node", mcp_node)
    workflow.add_node("rag_plus_mcp_node", rag_plus_mcp_node)
    workflow.add_node("generate_answer", generate_answer_node)

    # Set Entry Point
    workflow.set_entry_point("understand_query")

    # Add Conditional Edges from understand_query
    workflow.add_conditional_edges(
        "understand_query",
        route_decision,
        {
            "rag_node": "rag_node",
            "mcp_node": "mcp_node",
            "rag_plus_mcp_node": "rag_plus_mcp_node",
            "generate_answer_node": "generate_answer"
        }
    )

    # Connect tool nodes to answer generation
    workflow.add_edge("rag_node", "generate_answer")
    workflow.add_edge("mcp_node", "generate_answer")
    workflow.add_edge("rag_plus_mcp_node", "generate_answer")
    workflow.add_edge("generate_answer", END)

    return workflow.compile()

# Global compiled LangGraph workflow
copilot_app = build_kubernetes_copilot_graph()
