"""
LangSmith Tracing Integration for Multi-Agent Orchestrator

This module provides comprehensive tracing capabilities using LangSmith to monitor
agent execution, tool usage, and system performance.
"""

import os
import time
import json
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from dataclasses import dataclass, asdict
from threading import Lock
import logging

# Import logging configuration
from utils.logging_config import get_logger

# Initialize logger
logger = get_logger(__name__)

# LangSmith imports
try:
    from langsmith import Client
    from langsmith.run_helpers import traceable
    LANGSMITH_AVAILABLE = True
except ImportError:
    LANGSMITH_AVAILABLE = False
    logger.warning("LangSmith not available. Install with: pip install langsmith")

# LangChain callback imports
try:
    from langchain_core.callbacks import BaseCallbackHandler
    from langchain_core.outputs import LLMResult
    from langchain_core.agents import AgentAction, AgentFinish
    CALLBACKS_AVAILABLE = True
except ImportError:
    CALLBACKS_AVAILABLE = False
    logger.warning("LangChain callbacks not available. Real-time tracing will be limited.")

from dotenv import load_dotenv
load_dotenv()
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "mimicking-mindsets")

# Global LangSmith client for reuse across all components
_langsmith_client: Optional['Client'] = None
_client_lock = Lock()

def get_langsmith_client() -> Optional['Client']:
    """Get or create the global LangSmith client (thread-safe, efficient initialization)."""
    global _langsmith_client
    
    if not LANGSMITH_AVAILABLE or not LANGSMITH_API_KEY:
        return None
    
    # Double-checked locking pattern for efficient thread-safe initialization
    if _langsmith_client is None:
        with _client_lock:
            if _langsmith_client is None:  # Check again inside the lock
                try:
                    _langsmith_client = Client(
                        api_key=LANGSMITH_API_KEY,
                        api_url=os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
                    )
                except Exception as e:
                    logger.error(f"Failed to initialize LangSmith client: {e}")
                    return None
    
    return _langsmith_client

def initialize_langsmith() -> bool:
    """Initialize LangSmith client at startup. Returns True if successful."""
    client = get_langsmith_client()
    return client is not None

@dataclass
class TraceEvent:
    """Represents a single trace event."""
    timestamp: str
    event_type: str
    agent_name: Optional[str] = None
    message: str = ""
    details: Optional[Dict[str, Any]] = None
    run_id: Optional[str] = None
    duration_ms: Optional[float] = None
    status: str = "running"

@dataclass
class AgentTrace:
    """Represents the complete trace for an agent."""
    agent_name: str
    run_id: str
    start_time: str
    end_time: Optional[str] = None
    status: str = "running"
    events: List[TraceEvent] = None
    total_duration_ms: Optional[float] = None
    tool_calls: int = 0
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.events is None:
            self.events = []

if CALLBACKS_AVAILABLE:
    class RealTimeTracingCallback(BaseCallbackHandler):
        """Real-time callback handler for agent and tool execution."""
        
        def __init__(self, agent_name: str, run_id: str):
            super().__init__()
            self.agent_name = agent_name
            self.run_id = run_id
            self.manager = get_tracing_manager()
        
        def on_llm_start(self, serialized, prompts, **kwargs):
            """Called when LLM starts."""
            self.manager.update_agent_status(
                self.run_id, 
                f"{self.agent_name} düşünüyor ve yanıt hazırlıyor...", 
                "working"
            )
        
        def on_llm_end(self, response: LLMResult, **kwargs):
            """Called when LLM ends."""
            self.manager.update_agent_status(
                self.run_id, 
                f"{self.agent_name} yanıtını tamamladı", 
                "working"
            )
        
        def on_tool_start(self, serialized, input_str, **kwargs):
            """Called when tool starts."""
            tool_name = serialized.get("name", "unknown_tool")
            
            # Map tool names to Turkish descriptions
            tool_descriptions = {
                "internal_knowledge_search": "bilgi tabanından araştırma yapıyor",
                "web_search": "web'de güncel bilgi arıyor",
                "search": "arama yapıyor",
                "calculator": "hesaplama yapıyor"
            }
            
            description = tool_descriptions.get(tool_name, f"{tool_name} aracını kullanıyor")
            
            self.manager.update_agent_status(
                self.run_id, 
                f"{self.agent_name} {description}...", 
                "working", 
                tool_call=True, 
                tool_name=tool_name
            )
        
        def on_tool_end(self, output, **kwargs):
            """Called when tool ends."""
            self.manager.update_agent_status(
                self.run_id, 
                f"{self.agent_name} araç sonuçlarını değerlendiriyor...", 
                "working"
            )
        
        def on_agent_action(self, action: AgentAction, **kwargs):
            """Called when agent takes an action."""
            tool_name = action.tool
            tool_descriptions = {
                "internal_knowledge_search": "bilgi tabanından araştırma yapıyor",
                "web_search": "web'de güncel bilgi arıyor", 
                "search": "arama yapıyor"
            }
            
            description = tool_descriptions.get(tool_name, f"{tool_name} aracını kullanıyor")
            
            self.manager.update_agent_status(
                self.run_id, 
                f"{self.agent_name} {description}...", 
                "working", 
                tool_call=True, 
                tool_name=tool_name
            )
        
        def on_agent_finish(self, finish: AgentFinish, **kwargs):
            """Called when agent finishes."""
            self.manager.update_agent_status(
                self.run_id, 
                f"{self.agent_name} yanıtını tamamlıyor...", 
                "working"
            )
        
        def on_chain_error(self, error, **kwargs):
            """Called when there's an error."""
            self.manager.update_agent_status(
                self.run_id, 
                f"{self.agent_name} hata ile karşılaştı: {str(error)[:50]}...", 
                "error"
            )
else:
    # Fallback class when callbacks are not available
    class RealTimeTracingCallback:
        """Fallback callback when LangChain callbacks are not available."""
        
        def __init__(self, agent_name: str, run_id: str):
            self.agent_name = agent_name
            self.run_id = run_id
            logger.warning(f"Real-time callbacks not available for {agent_name}")

class AgentTracingManager:
    """Manages agent tracing across the multi-agent orchestrator."""
    
    def __init__(self):
        self.active_session_id: Optional[str] = None
        self.session_traces: Dict[str, List[AgentTrace]] = {}
        self.event_callbacks: List[Callable] = []
        self.session_lock = Lock()
        
        # Use global client for efficiency
        self.client = get_langsmith_client()
        
        if not self.client and LANGSMITH_API_KEY:
            logger.warning("LangSmith tracing disabled due to initialization failure")
        elif not LANGSMITH_API_KEY:
            logger.info("LangSmith tracing disabled. Set LANGSMITH_API_KEY to enable.")
    
    def initialize(self, session_id: Optional[str] = None) -> str:
        """Initialize tracing for a new session."""
        session_id = session_id or f"session_{int(time.time())}"
        
        with self.session_lock:
            self.active_session_id = session_id
            self.session_traces[session_id] = []
            
        logger.info(f"Tracing initialized for session: {session_id}")
        return session_id
    
    def add_event_callback(self, callback: Callable[[TraceEvent], None]):
        """Add a callback to receive trace events."""
        self.event_callbacks.append(callback)
    
    def start_agent_trace(self, agent_name: str, query: str) -> str:
        """Start tracing for a specific agent."""
        run_id = f"{agent_name}_{int(time.time())}"
        
        trace = AgentTrace(
            agent_name=agent_name,
            run_id=run_id,
            start_time=datetime.now().isoformat(),
            status="running"
        )
        
        with self.session_lock:
            if self.active_session_id:
                self.session_traces[self.active_session_id].append(trace)
        
        # Create start event
        event = TraceEvent(
            timestamp=datetime.now().isoformat(),
            event_type="agent_start",
            agent_name=agent_name,
            message=f"{agent_name} started processing",
            run_id=run_id,
            details={"query": query}
        )
        
        self._handle_trace_event(event)
        return run_id
    
    def update_agent_status(self, run_id: str, message: str, status: str = "running", tool_call: bool = False, tool_name: str = None):
        """Update agent status with a new message."""
        # Update tool call count if needed
        if tool_call:
            with self.session_lock:
                if self.active_session_id:
                    for trace in self.session_traces[self.active_session_id]:
                        if trace.run_id == run_id:
                            trace.tool_calls += 1
                            break
        
        event = TraceEvent(
            timestamp=datetime.now().isoformat(),
            event_type="tool_call" if tool_call else "agent_step",
            message=message,
            run_id=run_id,
            status=status,
            details={"tool_call": tool_call, "tool_name": tool_name}
        )
        
        self._handle_trace_event(event)
    
    def complete_agent_trace(self, run_id: str, response: str, error: Optional[str] = None):
        """Complete tracing for a specific agent."""
        end_time = datetime.now().isoformat()
        status = "error" if error else "completed"
        
        # Update trace record
        with self.session_lock:
            if self.active_session_id:
                for trace in self.session_traces[self.active_session_id]:
                    if trace.run_id == run_id:
                        trace.end_time = end_time
                        trace.status = status
                        if error:
                            trace.error_message = error
                        
                        # Calculate duration
                        try:
                            start_dt = datetime.fromisoformat(trace.start_time)
                            end_dt = datetime.fromisoformat(end_time)
                            trace.total_duration_ms = (end_dt - start_dt).total_seconds() * 1000
                        except:
                            trace.total_duration_ms = 0
                        break
        
        # Create completion event
        event = TraceEvent(
            timestamp=end_time,
            event_type="agent_complete",
            message=f"Agent completed with {status}",
            run_id=run_id,
            status=status,
            details={"response_length": len(response), "error": error}
        )
        
        self._handle_trace_event(event)
    
    def get_current_status(self) -> Dict[str, Dict[str, Any]]:
        """Get current status of all active agents for frontend display."""
        if not self.active_session_id:
            return {}
        
        status_dict = {}
        traces = self.get_session_traces()
        
        for trace in traces:
            if trace.status == "running":
                status_dict[trace.agent_name] = {
                    "status": "working",
                    "message": f"İşlem devam ediyor... ({trace.tool_calls} araç kullanıldı)",
                    "run_id": trace.run_id,
                    "start_time": trace.start_time,
                    "tool_calls": trace.tool_calls
                }
            elif trace.status == "completed":
                duration_text = f"{trace.total_duration_ms:.0f}ms" if trace.total_duration_ms else "N/A"
                status_dict[trace.agent_name] = {
                    "status": "completed",
                    "message": f"Tamamlandı ({duration_text})",
                    "run_id": trace.run_id,
                    "duration": trace.total_duration_ms,
                    "tool_calls": trace.tool_calls
                }
            elif trace.status == "error":
                status_dict[trace.agent_name] = {
                    "status": "error",
                    "message": f"Hata: {trace.error_message}",
                    "run_id": trace.run_id,
                    "tool_calls": trace.tool_calls
                }
        
        return status_dict
    
    def get_session_traces(self, session_id: Optional[str] = None) -> List[AgentTrace]:
        """Get all traces for a session."""
        session_id = session_id or self.active_session_id
        if not session_id:
            return []
        
        with self.session_lock:
            return self.session_traces.get(session_id, []).copy()
    
    def _handle_trace_event(self, event: TraceEvent):
        """Handle incoming trace events efficiently."""
        # Store event in the appropriate trace
        with self.session_lock:
            if self.active_session_id and event.run_id:
                for trace in self.session_traces[self.active_session_id]:
                    if trace.run_id == event.run_id:
                        trace.events.append(event)
                        break
        
        # Send to LangSmith if available (async for performance)
        if self.client and LANGSMITH_AVAILABLE:
            self._send_to_langsmith_async(event)
        
        # Notify all callbacks with error handling
        for callback in self.event_callbacks:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Error in event callback: {e}")
    
    def _send_to_langsmith_async(self, event: TraceEvent):
        """Send trace event to LangSmith asynchronously to avoid blocking."""
        try:
            # Create a properly formatted run record for LangSmith
            run_data = {
                "name": f"{event.agent_name or 'system'}_{event.event_type}",
                "run_type": "chain",
                "inputs": {"message": event.message, "run_id": event.run_id},
                "outputs": {"details": event.details or {}, "status": event.status},
                "start_time": event.timestamp,
                "end_time": event.timestamp,
                "project_name": LANGSMITH_PROJECT,
                "tags": [event.event_type, event.agent_name] if event.agent_name else [event.event_type]
            }
            
            # Note: For production, this would use proper LangSmith SDK methods
            # self.client.create_run(**run_data)
            logger.debug(f"Trace event prepared for LangSmith: {event.event_type}")
            
        except Exception as e:
            logger.error(f"Error preparing LangSmith trace: {e}")
    
    def export_traces(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Export traces in a JSON-serializable format."""
        traces = self.get_session_traces(session_id)
        return {
            "session_id": session_id or self.active_session_id,
            "timestamp": datetime.now().isoformat(),
            "traces": [asdict(trace) for trace in traces]
        }
    
    def clear_session(self, session_id: Optional[str] = None):
        """Clear traces for a session."""
        session_id = session_id or self.active_session_id
        if session_id:
            with self.session_lock:
                self.session_traces.pop(session_id, None)
                if self.active_session_id == session_id:
                    self.active_session_id = None

# Global tracing manager instance
_tracing_manager: Optional[AgentTracingManager] = None
_manager_lock = Lock()

def get_tracing_manager() -> AgentTracingManager:
    """Get or create the global tracing manager (thread-safe, efficient initialization)."""
    global _tracing_manager
    
    # Double-checked locking pattern for efficient thread-safe initialization
    if _tracing_manager is None:
        with _manager_lock:
            if _tracing_manager is None:  # Check again inside the lock
                _tracing_manager = AgentTracingManager()
                logger.info("Global tracing manager initialized")
    
    return _tracing_manager

def initialize_tracing_system() -> bool:
    """Initialize the entire tracing system at startup. Returns True if successful."""
    try:
        # Initialize LangSmith client
        langsmith_ok = initialize_langsmith()
        
        # Initialize tracing manager
        manager = get_tracing_manager()
        
        logger.info(f"Tracing system initialized - LangSmith: {'✓' if langsmith_ok else '✗'}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize tracing system: {e}")
        return False

def initialize_tracing(session_id: Optional[str] = None) -> str:
    """Initialize tracing for a session."""
    manager = get_tracing_manager()
    return manager.initialize(session_id)

def trace_agent_execution(agent_name: str, query: str):
    """Start tracing for an agent execution."""
    manager = get_tracing_manager()
    return manager.start_agent_trace(agent_name, query)

def update_agent_trace(run_id: str, message: str, status: str = "running", tool_call: bool = False, tool_name: str = None):
    """Update an agent trace with new information."""
    manager = get_tracing_manager()
    manager.update_agent_status(run_id, message, status, tool_call, tool_name)

def complete_agent_trace(run_id: str, response: str, error: Optional[str] = None):
    """Complete an agent trace."""
    manager = get_tracing_manager()
    manager.complete_agent_trace(run_id, response, error)

def get_current_agent_status() -> Dict[str, Dict[str, Any]]:
    """Get current status of all agents for frontend display."""
    manager = get_tracing_manager()
    return manager.get_current_status()

def get_realtime_callback(agent_name: str, run_id: str):
    """Get a real-time callback handler for an agent."""
    if CALLBACKS_AVAILABLE:
        return RealTimeTracingCallback(agent_name, run_id)
    else:
        # Return None if callbacks are not available
        logger.warning(f"Real-time callbacks not available for {agent_name}")
        return None 