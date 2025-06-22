"""
FastAPI Backend Server for Mimicking Mindsets Chatbot
Provides REST API endpoints for the React frontend to communicate with the multi-agent system.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import asyncio
import logging
import json
from datetime import datetime

# Import our multi-agent orchestrator
from agents.multi_agent_orchestrator import run_multi_agent_query, get_global_orchestrator

# Import LangSmith tracing
from evaluation.langsmith_tracing import (
    initialize_tracing,
    get_current_agent_status,
    get_tracing_manager
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Mimicking Mindsets API",
    description="Backend API for chatting with Erol Güngör and Cemil Meriç AI personas",
    version="1.0.0"
)

# Startup event to initialize components
@app.on_event("startup")
async def startup_event():
    """Initialize the multi-agent orchestrator on server startup for optimal performance."""
    logger.info("🚀 Starting Mimicking Mindsets API Server...")
    logger.info("🔧 Initializing multi-agent orchestrator components...")
    
    try:
        # Initialize the global orchestrator during startup
        # This will load models, connect to databases, etc.
        orchestrator = get_global_orchestrator()
        logger.info("✅ Multi-agent orchestrator initialized successfully!")
        logger.info("🎯 All models loaded and ready for fast responses")
    except Exception as e:
        logger.error(f"❌ Failed to initialize orchestrator during startup: {str(e)}")
        logger.error("⚠️ Server will still start, but first request may be slow")

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
    sources: Optional[List[Dict[str, str]]] = []
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
        sources = result.get("sources", [])
        
        # Add assistant response to history
        assistant_message = ChatMessage(role="assistant", content=synthesized_answer)
        active_threads[thread_id].append(assistant_message)
        
        # Create response object
        response = ChatResponse(
            synthesized_answer=synthesized_answer,
            agent_responses=agent_responses,
            sources=sources,
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

@app.post("/chat/stream")
async def chat_stream_endpoint(request: ChatRequest):
    """
    Streaming chat endpoint that processes user queries and streams responses.
    """
    async def generate_stream():
        try:
            logger.info(f"DEBUG: Received streaming chat request - Query: {request.user_query}")
            
            # Generate thread ID if not provided
            thread_id = request.thread_id or f"thread_{datetime.now().timestamp()}"
            
            # Initialize tracing for this session
            session_id = initialize_tracing(thread_id)
            
            # Get or initialize chat history for this thread
            if thread_id not in active_threads:
                active_threads[thread_id] = []
            
            # Add existing chat history if provided
            if request.chat_history:
                active_threads[thread_id].extend(request.chat_history)
            
            # Add user message to history
            user_message = ChatMessage(role="user", content=request.user_query)
            active_threads[thread_id].append(user_message)
            
            # Send initial status
            yield f"data: {json.dumps({'type': 'status', 'message': 'Ajanlar çalışmaya başladı...', 'thread_id': thread_id})}\n\n"
            
            # Set up real-time tracing callback
            tracing_manager = get_tracing_manager()
            
            def trace_callback(event):
                """Callback to send trace events to frontend."""
                try:
                    if event.agent_name:
                        status_map = {
                            "running": "working",
                            "completed": "completed", 
                            "error": "error"
                        }
                        
                        event_data = {
                            'type': 'agent_trace',
                            'agent': event.agent_name,
                            'message': event.message,
                            'status': status_map.get(event.status, "working"),
                            'timestamp': event.timestamp
                        }
                        
                        # This would be sent in a real streaming implementation
                        # For now, we'll let the orchestrator handle the updates
                        pass
                except Exception as e:
                    logger.error(f"Error in trace callback: {e}")
            
            tracing_manager.add_event_callback(trace_callback)
            
            # Send agent start notifications based on real tracing
            yield f"data: {json.dumps({'type': 'agent_start', 'agent': 'Erol Güngör', 'message': 'Erol Güngör hazırlanıyor...'})}\n\n"
            yield f"data: {json.dumps({'type': 'agent_start', 'agent': 'Cemil Meriç', 'message': 'Cemil Meriç hazırlanıyor...'})}\n\n"
            
            # Start the orchestrator in background and send periodic updates
            logger.info(f"DEBUG: Calling multi-agent orchestrator for streaming")
            
            # Start orchestrator task
            orchestrator_task = asyncio.create_task(
                asyncio.to_thread(run_multi_agent_query, request.user_query, thread_id)
            )
            
            # Send real-time status updates while orchestrator is running
            last_status = {}
            while not orchestrator_task.done():
                await asyncio.sleep(0.5)  # Update every 0.5 seconds for responsiveness
                
                # Get current tracing status
                try:
                    current_status = get_current_agent_status()
                    
                    # Only send updates if status has changed
                    for agent_name, status in current_status.items():
                        if agent_name not in last_status or last_status[agent_name]['message'] != status['message']:
                            yield f"data: {json.dumps({'type': 'agent_working', 'agent': agent_name, 'message': status['message']})}\n\n"
                            last_status[agent_name] = status
                            
                except Exception as e:
                    logger.error(f"Error getting tracing status: {e}")
                    # No fallback messages - rely only on real tracing data
            
            # Get the final result
            result = await orchestrator_task
            
            logger.info(f"DEBUG: Multi-agent streaming result: {result}")
            
            if not result or "synthesized_answer" not in result:
                yield f"data: {json.dumps({'type': 'error', 'message': 'Multi-agent system failed to generate response'})}\n\n"
                return
            
            # Extract responses
            synthesized_answer = result.get("synthesized_answer", "Yanıt oluşturulamadı.")
            agent_responses = result.get("agent_responses", {})
            sources = result.get("sources", [])
            
            # Send individual agent responses
            for agent_name, agent_response in agent_responses.items():
                yield f"data: {json.dumps({'type': 'agent_response', 'agent': agent_name, 'response': agent_response})}\n\n"
            
            # Send synthesis start message
            yield f"data: {json.dumps({'type': 'synthesis_start', 'message': 'Yanıtlar birleştiriliyor...'})}\n\n"
            
            # Simulate streaming by sending chunks of the synthesized answer
            words = synthesized_answer.split(' ')
            chunk_size = 20  # Send 5 words at a time
            
            for i in range(0, len(words), chunk_size):
                chunk = ' '.join(words[i:i + chunk_size])
                if i + chunk_size < len(words):
                    chunk += ' '
                
                yield f"data: {json.dumps({'type': 'synthesis_chunk', 'chunk': chunk})}\n\n"
                await asyncio.sleep(0.1)  # Small delay for streaming effect
            
            # Add assistant response to history
            assistant_message = ChatMessage(role="assistant", content=synthesized_answer)
            active_threads[thread_id].append(assistant_message)
            
            # Send completion
            yield f"data: {json.dumps({'type': 'complete', 'synthesized_answer': synthesized_answer, 'agent_responses': agent_responses, 'sources': sources, 'thread_id': thread_id, 'timestamp': datetime.now().isoformat()})}\n\n"
            
        except Exception as e:
            logger.error(f"DEBUG: Error in streaming endpoint: {str(e)}")
            yield f"data: {json.dumps({'type': 'error', 'message': f'Streaming error: {str(e)}'})}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
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

@app.get("/tracing/status")
async def get_tracing_status():
    """Get current agent tracing status."""
    try:
        current_status = get_current_agent_status()
        return {
            "success": True,
            "agent_status": current_status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"DEBUG: Error getting tracing status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tracing/export/{session_id}")
async def export_traces(session_id: str):
    """Export all traces for a session."""
    try:
        tracing_manager = get_tracing_manager()
        traces = tracing_manager.export_traces(session_id)
        return {
            "success": True,
            "traces": traces
        }
    except Exception as e:
        logger.error(f"DEBUG: Error exporting traces: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

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
    print("🔧 Components will be initialized during startup for optimal performance")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🌐 Frontend should connect to: http://localhost:8000")
    print("⏳ Please wait for initialization to complete...")
    
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 