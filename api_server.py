"""
FastAPI Backend Server for Mimicking Mindsets Chatbot
Provides REST API endpoints for the React frontend to communicate with the multi-agent system.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import asyncio
import logging
from datetime import datetime

# Import our multi-agent orchestrator
from multi_agent_orchestrator import run_multi_agent_query

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Mimicking Mindsets API",
    description="Backend API for chatting with Erol Güngör and Cemil Meriç AI personas",
    version="1.0.0"
)

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request logging middleware
@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"DEBUG: Incoming request: {request.method} {request.url}")
    logger.info(f"DEBUG: Request headers: {dict(request.headers)}")
    
    response = await call_next(request)
    
    logger.info(f"DEBUG: Response status: {response.status_code}")
    return response

# Pydantic models for request/response
class ChatMessage(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str

class ChatRequest(BaseModel):
    user_query: str
    chat_history: Optional[List[ChatMessage]] = []
    thread_id: Optional[str] = None

class ChatResponse(BaseModel):
    synthesized_answer: str
    agent_responses: Dict[str, str]
    chat_history: List[ChatMessage]
    thread_id: str
    timestamp: str

class HealthResponse(BaseModel):
    status: str
    message: str
    timestamp: str

# Global thread storage (in production, use Redis or database)
active_threads: Dict[str, List[ChatMessage]] = {}

@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Mimicking Mindsets API",
        "description": "Backend for chatting with Turkish intellectual AI personas",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/chat",
            "health": "/health",
            "docs": "/docs"
        }
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        message="Mimicking Mindsets API is running",
        timestamp=datetime.now().isoformat()
    )

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Main chat endpoint that processes user queries through the multi-agent system.
    """
    try:
        logger.info(f"DEBUG: Received chat request - Query: {request.user_query}")
        
        # Generate thread ID if not provided
        thread_id = request.thread_id or f"thread_{datetime.now().timestamp()}"
        
        # Get or initialize chat history for this thread
        if thread_id not in active_threads:
            active_threads[thread_id] = []
        
        # Add existing chat history if provided
        if request.chat_history:
            active_threads[thread_id].extend(request.chat_history)
        
        # Add user message to history
        user_message = ChatMessage(role="user", content=request.user_query)
        active_threads[thread_id].append(user_message)
        
        # Call the multi-agent orchestrator
        logger.info(f"DEBUG: Calling multi-agent orchestrator")
        result = await asyncio.to_thread(
            run_multi_agent_query, 
            request.user_query, 
            thread_id
        )
        
        logger.info(f"DEBUG: Multi-agent result: {result}")
        
        if not result or "synthesized_answer" not in result:
            raise HTTPException(
                status_code=500, 
                detail="Multi-agent system failed to generate response"
            )
        
        # Extract synthesized answer and agent responses
        synthesized_answer = result.get("synthesized_answer", "Yanıt oluşturulamadı.")
        agent_responses = result.get("agent_responses", {})
        
        # Add assistant response to history
        assistant_message = ChatMessage(role="assistant", content=synthesized_answer)
        active_threads[thread_id].append(assistant_message)
        
        # Create response object
        response = ChatResponse(
            synthesized_answer=synthesized_answer,
            agent_responses=agent_responses,
            chat_history=active_threads[thread_id],
            thread_id=thread_id,
            timestamp=datetime.now().isoformat()
        )
        
        logger.info(f"DEBUG: Sending response back to frontend")
        return response
        
    except Exception as e:
        logger.error(f"DEBUG: Error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/threads/{thread_id}", response_model=List[ChatMessage])
async def get_thread_history(thread_id: str):
    """Get chat history for a specific thread."""
    if thread_id not in active_threads:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    return active_threads[thread_id]

@app.delete("/threads/{thread_id}")
async def clear_thread_history(thread_id: str):
    """Clear chat history for a specific thread."""
    if thread_id in active_threads:
        del active_threads[thread_id]
        return {"message": f"Thread {thread_id} cleared successfully"}
    else:
        raise HTTPException(status_code=404, detail="Thread not found")

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    logger.error(f"DEBUG: HTTP exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": f"HTTP {exc.status_code}", "detail": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"DEBUG: Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting Mimicking Mindsets API Server...")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🌐 Frontend should connect to: http://localhost:8000")
    
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 