import os
import uuid
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from backend.config import settings
from backend.agent.graph import copilot_app
from backend.rag.chroma import chroma_manager
from backend.llm.grok import grok_service
from ingestion.ingest import run_ingestion

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("kubernetes-copilot.api")

app = FastAPI(
    title="Kubernetes Copilot API",
    description="Agentic RAG AI Chatbot grounded in official Kubernetes documentation",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session stores for MVP
conversations_store: Dict[str, List[Dict[str, Any]]] = {}
feedback_store: List[Dict[str, Any]] = []

# Pydantic Schemas
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User's query")
    conversation_id: Optional[str] = Field(None, description="Active conversation ID")

class SourceResponse(BaseModel):
    title: str
    url: str
    section: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceResponse]
    tools_used: List[str]
    conversation_id: str
    timestamp: str

class FeedbackRequest(BaseModel):
    conversation_id: str
    thumb: str = Field(..., pattern="^(up|down)$")
    message_index: Optional[int] = None
    reason: Optional[str] = None
    comment: Optional[str] = None

class ConversationCreateResponse(BaseModel):
    conversation_id: str
    created_at: str

@app.on_event("startup")
def startup_event():
    """
    Ensure ChromaDB contains official Kubernetes documentation on startup.
    """
    try:
        count = chroma_manager.count()
        if count == 0:
            logger.info("ChromaDB is empty. Triggering automated documentation ingestion...")
            run_ingestion()
        else:
            logger.info(f"ChromaDB ready with {count} indexed documentation chunks.")
    except Exception as e:
        logger.error(f"Error checking/initializing vector store: {e}")

# API Endpoints
@app.get("/api/health")
def health_check():
    """
    Health check endpoint returning system status and knowledge base statistics.
    """
    try:
        docs_count = chroma_manager.count()
    except Exception:
        docs_count = 0

    active_model = settings.GROQ_MODEL if settings.LLM_PROVIDER == "groq" else settings.GROK_MODEL
    return {
        "status": "healthy",
        "service": "Kubernetes Copilot",
        "version": "1.0.0",
        "docs_count": docs_count,
        "llm_provider": settings.LLM_PROVIDER,
        "llm_configured": grok_service.is_configured,
        "llm_model": active_model,
        "reasoning_effort": settings.GROQ_REASONING_EFFORT if settings.LLM_PROVIDER == "groq" else None
    }

@app.post("/api/conversations", response_model=ConversationCreateResponse)
def create_conversation():
    """
    Creates a new conversation session.
    """
    conv_id = f"conv-{uuid.uuid4().hex[:12]}"
    conversations_store[conv_id] = []
    logger.info(f"Created new conversation: {conv_id}")
    return ConversationCreateResponse(
        conversation_id=conv_id,
        created_at=datetime.utcnow().isoformat()
    )

@app.get("/api/conversations/{conversation_id}")
def get_conversation(conversation_id: str):
    """
    Retrieves message history for a conversation.
    """
    if conversation_id not in conversations_store:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {
        "conversation_id": conversation_id,
        "messages": conversations_store[conversation_id]
    }

@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    """
    Main Chatbot endpoint. Runs the LangGraph agent workflow:
    Query Understanding -> Tool Selection (RAG / MCP / RAG+MCP) -> Retrieval -> Grok Reasoning -> Grounded Answer.
    """
    conv_id = request.conversation_id or f"conv-{uuid.uuid4().hex[:12]}"
    if conv_id not in conversations_store:
        conversations_store[conv_id] = []

    history = conversations_store[conv_id]

    # Initialize Agent State
    initial_state = {
        "conversation_id": conv_id,
        "user_query": request.message,
        "chat_history": history,
        "intent": None,
        "selected_tool": None,
        "rag_context": [],
        "mcp_context": [],
        "combined_context": "",
        "sources": [],
        "tools_used": [],
        "final_answer": "",
        "error": None
    }

    try:
        # Execute LangGraph workflow
        final_state = copilot_app.invoke(initial_state)
        
        answer = final_state.get("final_answer", "")
        raw_sources = final_state.get("sources", [])
        tools_used = final_state.get("tools_used", [])

        # Deduplicate and format sources
        formatted_sources: List[SourceResponse] = []
        seen_urls = set()
        for s in raw_sources:
            url = s.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                formatted_sources.append(SourceResponse(
                    title=s.get("title", "Kubernetes Documentation"),
                    url=url,
                    section=s.get("section")
                ))

        timestamp = datetime.utcnow().isoformat()

        # Update conversation history
        conversations_store[conv_id].append({
            "role": "user",
            "content": request.message,
            "timestamp": timestamp
        })
        conversations_store[conv_id].append({
            "role": "assistant",
            "content": answer,
            "sources": [s.dict() for s in formatted_sources],
            "tools_used": tools_used,
            "timestamp": timestamp
        })

        return ChatResponse(
            answer=answer,
            sources=formatted_sources,
            tools_used=tools_used,
            conversation_id=conv_id,
            timestamp=timestamp
        )

    except Exception as e:
        logger.error(f"Error processing chat request: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="I couldn't generate a response right now. Please try again."
        )

@app.post("/api/feedback")
def submit_feedback(feedback: FeedbackRequest):
    """
    Submits user feedback (thumbs up / thumbs down with optional reason and comments).
    """
    entry = {
        "id": f"fb-{uuid.uuid4().hex[:8]}",
        "conversation_id": feedback.conversation_id,
        "thumb": feedback.thumb,
        "message_index": feedback.message_index,
        "reason": feedback.reason,
        "comment": feedback.comment,
        "timestamp": datetime.utcnow().isoformat()
    }
    feedback_store.append(entry)
    logger.info(f"Recorded feedback: {entry}")
    return {"status": "success", "message": "Feedback recorded successfully", "feedback_id": entry["id"]}

# Static Files & Frontend UI Mount
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/")
    def serve_index():
        return FileResponse(FRONTEND_DIR / "index.html")
