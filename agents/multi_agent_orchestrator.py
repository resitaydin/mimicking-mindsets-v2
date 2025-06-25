"""
Phase 2: Multi-Agent Orchestration with LangGraph

Bu modül, iki persona ajanının (Erol Güngör ve Cemil Meriç) paralel çalışmasını koordine eden
çok-ajanli orkestrasyon sistemini içerir. LangGraph kullanarak tool node'ları ve conditional
edge'leri destekler.

Bu system şu bileşenleri içerir:
- Graph State: Tüm ajanların durumunu takip eden TypedDict
- Persona Agent Nodes: Her persona için ayrı node'lar
- Tool Nodes: Her ajanın tool çağrılarını yöneten node'lar
- Synthesizer Node: Ajanların çıktılarını birleştiren node
- Memory Node: Sohbet geçmişini güncelleyen node
- LangSmith Tracing: Comprehensive agent execution tracing
"""

import asyncio
from typing import Any, Dict, List, Optional, TypedDict, Annotated, Literal
from dataclasses import dataclass

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

# Import Phase 1 components
from .persona_agents import initialize_components, create_persona_agent
from .persona_prompts import get_persona_info, list_available_personas

# Import logging
from utils.logging_config import get_orchestrator_logger

# Import LangSmith tracing - using lazy imports to avoid circular dependency
# Note: evaluation imports moved to functions to avoid circular dependency

# Initialize logger
logger = get_orchestrator_logger()

# --- Graph State Definition ---

class GraphState(TypedDict):
    """LangGraph için durum yönetimi."""
    user_query: str
    erol_gungor_agent_output: Optional[Dict[str, Any]]
    cemil_meric_agent_output: Optional[Dict[str, Any]]
    synthesized_answer: Optional[str]
    agent_responses: Optional[Dict[str, str]]
    sources: Optional[List[Dict[str, str]]]
    chat_history: Annotated[List[BaseMessage], add_messages]
    # Agent-specific memory tracking
    erol_gungor_history: Annotated[List[BaseMessage], add_messages]
    cemil_meric_history: Annotated[List[BaseMessage], add_messages]
    # Tracing fields
    session_id: Optional[str]
    erol_trace_id: Optional[str]
    cemil_trace_id: Optional[str]

# LangGraph handles memory automatically with MemorySaver and add_messages
# No need for custom memory management

# --- Node Functions ---

def erol_gungor_agent_node(state: GraphState, config: RunnableConfig) -> Dict[str, Any]:
    """Erol Güngör ajanını çalıştıran node."""
    
    # Lazy import to avoid circular dependency
    from evaluation.langsmith_tracing import trace_agent_execution, update_agent_trace, complete_agent_trace, get_realtime_callback
    
    # Start tracing
    trace_id = trace_agent_execution("Erol Güngör", state['user_query'])
    
    # Get the agent from config
    erol_agent = config.get("configurable", {}).get("erol_agent")
    if not erol_agent:
        logger.error("Erol Güngör agent not found in config")
        complete_agent_trace(trace_id, "", "Erol Güngör ajanı yapılandırılmamış")
        return {
            "erol_gungor_agent_output": {"error": "Erol Güngör ajanı yapılandırılmamış"},
            "erol_trace_id": trace_id
        }
    
    try:
        # Update trace status
        update_agent_trace(trace_id, "Sorgu analiz ediliyor...")
        
        # Use agent-specific history but LIMIT IT to prevent context dilution
        erol_specific_history = state.get("erol_gungor_history", [])
        
        # Keep only the last 2 exchanges (4 messages max) to prevent tool instruction dilution
        if len(erol_specific_history) > 4:
            erol_specific_history = erol_specific_history[-4:]
        
        # Add tool usage reminder to the current query to ensure it's always visible
        enhanced_query = f"""🔧 ARAÇ KULLANIM HATIRLATMASI 🔧
Bu soruya yanıt vermeden önce MUTLAKA:
1. internal_knowledge_search_erol_gungor aracını kullan
2. Gerekirse web_search aracını da kullan

Kullanıcı Sorusu: {state["user_query"]}"""
        
        current_message = HumanMessage(content=enhanced_query)
        messages = erol_specific_history + [current_message]
        
        # Update trace for agent invocation
        update_agent_trace(trace_id, "Ajan çalıştırılıyor...")
        
        # Get real-time callback for this agent
        callback = get_realtime_callback("Erol Güngör", trace_id)
        
        # Invoke the agent with real-time callback (if available)
        if callback:
            result = erol_agent.invoke({"messages": messages}, config={"callbacks": [callback]})
        else:
            result = erol_agent.invoke({"messages": messages})
        
        # Extract response for tracing and history update
        response_text = ""
        if result and "messages" in result and result["messages"]:
            last_message = result["messages"][-1]
            response_text = last_message.content if hasattr(last_message, 'content') else str(last_message)
        
        # Complete trace
        complete_agent_trace(trace_id, response_text)
        
        # Update agent-specific history with ORIGINAL user query (not enhanced) and agent response
        original_message = HumanMessage(content=state["user_query"])
        agent_response = AIMessage(content=response_text) if response_text else AIMessage(content="Yanıt alınamadı")
        
        return {
            "erol_gungor_agent_output": result,
            "erol_trace_id": trace_id,
            "erol_gungor_history": [original_message, agent_response]  # Store original query in history
        }
        
    except Exception as e:
        logger.error(f"Error in Erol Güngör agent node: {str(e)}")
        complete_agent_trace(trace_id, "", str(e))
        
        # Update history even on error
        original_message = HumanMessage(content=state["user_query"])
        error_response = AIMessage(content=f"Erol Güngör ajanı hatası: {str(e)}")
        
        return {
            "erol_gungor_agent_output": {"error": f"Erol Güngör ajanı hatası: {str(e)}"},
            "erol_trace_id": trace_id,
            "erol_gungor_history": [original_message, error_response]
        }

def cemil_meric_agent_node(state: GraphState, config: RunnableConfig) -> Dict[str, Any]:
    """Cemil Meriç ajanını çalıştıran node."""
    
    # Lazy import to avoid circular dependency
    from evaluation.langsmith_tracing import trace_agent_execution, update_agent_trace, complete_agent_trace, get_realtime_callback
    
    # Start tracing
    trace_id = trace_agent_execution("Cemil Meriç", state['user_query'])
    
    # Get the agent from config
    cemil_agent = config.get("configurable", {}).get("cemil_agent")
    if not cemil_agent:
        logger.error("Cemil Meriç agent not found in config")
        complete_agent_trace(trace_id, "", "Cemil Meriç ajanı yapılandırılmamış")
        return {
            "cemil_meric_agent_output": {"error": "Cemil Meriç ajanı yapılandırılmamış"},
            "cemil_trace_id": trace_id
        }
    
    try:
        # Update trace status
        update_agent_trace(trace_id, "Felsefi çerçeve oluşturuluyor...")
        
        # Use agent-specific history but LIMIT IT to prevent context dilution
        cemil_specific_history = state.get("cemil_meric_history", [])
        
        # Keep only the last 2 exchanges (4 messages max) to prevent tool instruction dilution
        if len(cemil_specific_history) > 4:
            cemil_specific_history = cemil_specific_history[-4:]
        
        # Add tool usage reminder to the current query to ensure it's always visible
        enhanced_query = f"""🔧 ARAÇ KULLANIM HATIRLATMASI 🔧
Bu soruya yanıt vermeden önce MUTLAKA:
1. internal_knowledge_search_cemil_meric aracını kullan
2. Gerekirse web_search aracını da kullan

Kullanıcı Sorusu: {state["user_query"]}"""
        
        current_message = HumanMessage(content=enhanced_query)
        messages = cemil_specific_history + [current_message]
        
        # Update trace for agent invocation
        update_agent_trace(trace_id, "Ajan çalıştırılıyor...")
        
        # Get real-time callback for this agent
        callback = get_realtime_callback("Cemil Meriç", trace_id)
        
        # Invoke the agent with real-time callback (if available)
        if callback:
            result = cemil_agent.invoke({"messages": messages}, config={"callbacks": [callback]})
        else:
            result = cemil_agent.invoke({"messages": messages})
        
        # Extract response for tracing and history update
        response_text = ""
        if result and "messages" in result and result["messages"]:
            last_message = result["messages"][-1]
            response_text = last_message.content if hasattr(last_message, 'content') else str(last_message)
        
        # Complete trace
        complete_agent_trace(trace_id, response_text)
        
        # Update agent-specific history with ORIGINAL user query (not enhanced) and agent response
        original_message = HumanMessage(content=state["user_query"])
        agent_response = AIMessage(content=response_text) if response_text else AIMessage(content="Yanıt alınamadı")
        
        return {
            "cemil_meric_agent_output": result,
            "cemil_trace_id": trace_id,
            "cemil_meric_history": [original_message, agent_response]  # Store original query in history
        }
        
    except Exception as e:
        logger.error(f"Error in Cemil Meriç agent node: {str(e)}")
        complete_agent_trace(trace_id, "", str(e))
        
        # Update history even on error
        original_message = HumanMessage(content=state["user_query"])
        error_response = AIMessage(content=f"Cemil Meriç ajanı hatası: {str(e)}")
        
        return {
            "cemil_meric_agent_output": {"error": f"Cemil Meriç ajanı hatası: {str(e)}"},
            "cemil_trace_id": trace_id,
            "cemil_meric_history": [original_message, error_response]
        }

def join_agents_node(state: GraphState, config: RunnableConfig) -> Dict[str, Any]:
    """İki ajanın tamamlanmasını bekleyen ara node."""
    
    erol_output = state.get("erol_gungor_agent_output")
    cemil_output = state.get("cemil_meric_agent_output")
    
    # This node doesn't modify state, just serves as a junction
    return {}

def extract_sources_from_messages(messages, agent_name=None):
    """Extract sources from agent messages with agent attribution."""
    sources = []
    
    if not messages:
        return sources
    
    for message in messages:
        content = message.content if hasattr(message, 'content') else str(message)
        
        # Extract vector database sources
        if "Kaynak:" in content:
            lines = content.split('\n')
            for line in lines:
                if line.strip().startswith("Kaynak:"):
                    source_name = line.replace("Kaynak:", "").strip()
                    if source_name and source_name not in [s["name"] for s in sources]:
                        sources.append({
                            "type": "vector_db",
                            "name": source_name,
                            "description": f"Kaynak: {source_name}",
                            "agent": agent_name
                        })
        
        # Extract web search indication
        if any(keyword in content.lower() for keyword in ["web araması", "internet", "güncel", "duckduckgo"]):
            web_search_exists = any(s["type"] == "web_search" and s.get("agent") == agent_name for s in sources)
            if not web_search_exists:
                sources.append({
                    "type": "web_search", 
                    "name": "Web Araması",
                    "description": "İnternet araması yapıldı",
                    "agent": agent_name
                })
    
    return sources

def synthesize_response_node(state: GraphState, config: RunnableConfig) -> Dict[str, Any]:
    """İki ajanın yanıtlarını birleştiren node."""
    
    logger.info("Starting synthesis node")
    
    # Get the LLM from config
    llm = config.get("configurable", {}).get("llm")
    if not llm:
        logger.error("LLM not found in config for synthesis")
        return {"synthesized_answer": "Sentez için dil modeli yapılandırılmamış."}
    
    # Extract responses from agent outputs
    erol_response = ""
    cemil_response = ""
    
    # Process Erol Güngör's output
    erol_output = state.get("erol_gungor_agent_output", {})
    if erol_output and "messages" in erol_output:
        erol_messages = erol_output["messages"]
        if erol_messages:
            last_message = erol_messages[-1]
            erol_response = last_message.content if hasattr(last_message, 'content') else str(last_message)
    elif erol_output and "error" in erol_output:
        erol_response = f"Erol Güngör yanıtı alınamadı: {erol_output['error']}"
    
    # Process Cemil Meriç's output
    cemil_output = state.get("cemil_meric_agent_output", {})
    if cemil_output and "messages" in cemil_output:
        cemil_messages = cemil_output["messages"]
        if cemil_messages:
            last_message = cemil_messages[-1]
            cemil_response = last_message.content if hasattr(last_message, 'content') else str(last_message)
    elif cemil_output and "error" in cemil_output:
        cemil_response = f"Cemil Meriç yanıtı alınamadı: {cemil_output['error']}"
    
    # Extract sources from both agents
    all_sources = []
    
    # Extract sources from Erol Güngör's messages
    if erol_output and "messages" in erol_output:
        erol_sources = extract_sources_from_messages(erol_output["messages"], "Erol Güngör")
        all_sources.extend(erol_sources)
    
    # Extract sources from Cemil Meriç's messages  
    if cemil_output and "messages" in cemil_output:
        cemil_sources = extract_sources_from_messages(cemil_output["messages"], "Cemil Meriç")
        all_sources.extend(cemil_sources)
    
    # Create synthesis prompt with chat history context if available
    chat_history = state.get("chat_history", [])
    history_context = ""
    
    if len(chat_history) > 2:  # If there's meaningful chat history
        history_context = "\n\nÖnceki Sohbet Bağlamı:\n"
        for i, msg in enumerate(chat_history[-4:]):  # Last 2 exchanges
            role = "Kullanıcı" if isinstance(msg, HumanMessage) else "Asistan"
            content = msg.content[:200] + "..." if len(msg.content) > 200 else msg.content
            history_context += f"{role}: {content}\n"
        history_context += "\nBu bağlamı göz önünde bulundurarak yanıt ver.\n"
    
    synthesis_prompt = f"""Sen, Türk entelektüel geleneğini anlayan ve farklı bakış açılarını sentezleyebilen bir asistansın.
{history_context}
Kullanıcı Sorusu: {state['user_query']}

Erol Güngör'ün Yanıtı:
{erol_response}

Cemil Meriç'in Yanıtı:
{cemil_response}

Görevin: Bu iki entelektüelin yanıtlarını birleştirerek tek bir tutarlı, kapsamlı yanıt oluşturmak. 

Sentez yaparken:
1. Her iki perspektifi de saygıyla dahil et
2. Ortak noktaları vurgula
3. Farklı görüşleri de belirt ve bunları tamamlayıcı olarak sun
4. Tekrarları önle
5. Akıcı, tutarlı bir metin oluştur
6. Her iki entelektüelin katkısını acknowledge et
7. Eğer önceki sohbet bağlamı varsa, ona uygun şekilde yanıt ver

Başlıklar kullanma, doğrudan kapsamlı bir yanıt ver."""
    
    try:
        synthesis_result = llm.invoke(synthesis_prompt)
        
        synthesized_text = synthesis_result.content if hasattr(synthesis_result, 'content') else str(synthesis_result)
        logger.info("Synthesis completed successfully")
        
        # Prepare individual agent responses for frontend
        agent_responses = {
            "Erol Güngör": erol_response,
            "Cemil Meriç": cemil_response
        }
        
        # Update chat history with user query and AI response using LangGraph's add_messages
        user_message = HumanMessage(content=state['user_query'])
        ai_message = AIMessage(content=synthesized_text)
        
        return {
            "synthesized_answer": synthesized_text,
            "agent_responses": agent_responses,
            "sources": all_sources,
            "chat_history": [user_message, ai_message]  # LangGraph will add these to existing history
        }
        
    except Exception as e:
        logger.error(f"Error during synthesis: {str(e)}")
        # Even on error, update chat history
        error_response = f"Sentez hatası: {str(e)}"
        user_message = HumanMessage(content=state['user_query'])
        ai_message = AIMessage(content=error_response)
        
        return {
            "synthesized_answer": error_response,
            "agent_responses": {
                "Erol Güngör": erol_response if erol_response else "Yanıt alınamadı",
                "Cemil Meriç": cemil_response if cemil_response else "Yanıt alınamadı"
            },
            "sources": all_sources,
            "chat_history": [user_message, ai_message]  # LangGraph will add these to existing history
        }

# LangGraph's add_messages annotation automatically handles chat history updates
# No need for manual memory update node

# --- Graph Builder ---

class MultiAgentOrchestrator:
    """Multi-agent orchestration system using LangGraph."""
    
    def __init__(self):
        """Orchestrator'ı başlatır."""
        self.graph = None
        self.qdrant_client = None
        self.embedding_model = None
        self.llm = None
        self.agents = {}
        
    def initialize(self):
        """Tüm bileşenleri başlatır."""
        
        logger.info("Initializing Multi-Agent Orchestrator")
        
        # Initialize Phase 1 components
        self.qdrant_client, self.embedding_model, self.llm = initialize_components()
        
        if not all([self.qdrant_client, self.embedding_model, self.llm]):
            raise Exception("Phase 1 bileşenleri başlatılamadı")
        
        logger.info("Phase 1 components initialized successfully")
        
        # Create persona agents
        available_personas = list_available_personas()
        
        for persona_key in available_personas:
            try:
                agent = create_persona_agent(
                    persona_key, 
                    self.qdrant_client, 
                    self.embedding_model, 
                    self.llm
                )
                self.agents[persona_key] = agent
                persona_info = get_persona_info(persona_key)
                logger.info(f"Created agent for {persona_info['name']}")
            except Exception as e:
                logger.error(f"Failed to create agent for {persona_key}: {e}")
                raise
        
        logger.info("All persona agents created successfully")
        
        # Build the graph
        self._build_graph()
        logger.info("Multi-Agent Orchestrator initialized successfully")
    
    def _build_graph(self):
        """LangGraph workflow'unu oluşturur."""
        
        # Create the state graph
        workflow = StateGraph(GraphState)
        
        # Add nodes
        workflow.add_node("erol_gungor_agent", erol_gungor_agent_node)
        workflow.add_node("cemil_meric_agent", cemil_meric_agent_node)
        workflow.add_node("join_agents", join_agents_node)
        workflow.add_node("synthesize_response", synthesize_response_node)
        
        # Add edges
        # Entry point: Start with both agents in parallel
        workflow.add_edge(START, "erol_gungor_agent")
        workflow.add_edge(START, "cemil_meric_agent")
        
        # Both agents feed into join node
        workflow.add_edge("erol_gungor_agent", "join_agents")
        workflow.add_edge("cemil_meric_agent", "join_agents")
        
        # Sequential flow after joining
        workflow.add_edge("join_agents", "synthesize_response")
        workflow.add_edge("synthesize_response", END)  # End directly after synthesis
        
        # Compile the graph
        checkpointer = MemorySaver()
        self.graph = workflow.compile(checkpointer=checkpointer)
        
        logger.info("Graph compiled successfully")
    
    def invoke(self, user_query: str, thread_id: str = "default") -> Dict[str, Any]:
        """Orchestrator'ı çalıştırır using LangGraph's built-in memory management."""
        
        logger.info(f"Invoking Multi-Agent Orchestrator for thread: {thread_id}")
        
        # Initialize tracing for this session
        from evaluation.langsmith_tracing import initialize_tracing
        session_id = initialize_tracing(thread_id)
        
        # Prepare initial state - LangGraph's MemorySaver will handle chat history persistence
        initial_state = {
            "user_query": user_query,
            "erol_gungor_agent_output": None,
            "cemil_meric_agent_output": None,
            "synthesized_answer": None,
            "agent_responses": None,
            "session_id": session_id,
            "erol_trace_id": None,
            "cemil_trace_id": None
        }
        
        # Prepare config with agents for runtime
        runtime_config = {
            "configurable": {
                "erol_agent": self.agents.get("erol_gungor"),
                "cemil_agent": self.agents.get("cemil_meric"),
                "llm": self.llm,
                "thread_id": thread_id
            }
        }
        
        try:
            # LangGraph's MemorySaver automatically loads and saves chat history based on thread_id
            # The thread_id is passed in the config for the checkpointer
            result = self.graph.invoke(
                initial_state, 
                config={"configurable": {"thread_id": thread_id}, **runtime_config}
            )
            logger.info("Graph execution completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error during graph execution: {str(e)}")
            return {
                "error": f"Orchestration hatası: {str(e)}",
                "user_query": user_query,
                "synthesized_answer": "Sistem hatası nedeniyle yanıt oluşturulamadı."
            }

# --- Convenience Functions ---

# Global orchestrator instance for reuse across requests
_global_orchestrator = None
import threading
_orchestrator_lock = threading.Lock()

def get_global_orchestrator() -> MultiAgentOrchestrator:
    """Get or create the global orchestrator instance (thread-safe)."""
    global _global_orchestrator
    
    with _orchestrator_lock:
        if _global_orchestrator is None:
            logger.info("Creating global orchestrator instance")
            _global_orchestrator = MultiAgentOrchestrator()
            _global_orchestrator.initialize()
            logger.info("Global orchestrator created and initialized successfully")
    
    return _global_orchestrator

def create_orchestrator() -> MultiAgentOrchestrator:
    """Yeni bir Multi-Agent Orchestrator oluşturur ve başlatır."""
    
    orchestrator = MultiAgentOrchestrator()
    orchestrator.initialize()
    return orchestrator

def run_multi_agent_query(query: str, thread_id: str = "default") -> Dict[str, Any]:
    """Tek seferlik multi-agent sorgu çalıştırır - uses LangGraph's built-in memory management."""
    
    # Use the global orchestrator instead of creating a new one each time
    # This dramatically improves performance by avoiding model reloading
    orchestrator = get_global_orchestrator()
    
    return orchestrator.invoke(query, thread_id) 