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
from persona_agents import initialize_components, create_persona_agent
from persona_prompts import get_persona_info, list_available_personas

# --- Graph State Definition ---

class GraphState(TypedDict):
    """LangGraph için durum yönetimi."""
    user_query: str
    erol_gungor_agent_output: Optional[Dict[str, Any]]
    cemil_meric_agent_output: Optional[Dict[str, Any]]
    synthesized_answer: Optional[str]
    agent_responses: Optional[Dict[str, str]]
    chat_history: Annotated[List[BaseMessage], add_messages]

# --- Node Functions ---

def erol_gungor_agent_node(state: GraphState, config: RunnableConfig) -> Dict[str, Any]:
    """Erol Güngör ajanını çalıştıran node."""
    
    print(f"\n🎯 DEBUG: Starting Erol Güngör agent node")
    print(f"🔍 DEBUG: User query: {state['user_query']}")
    
    # Get the agent from config
    erol_agent = config.get("configurable", {}).get("erol_agent")
    if not erol_agent:
        print(f"❌ DEBUG: Erol Güngör agent not found in config")
        return {
            "erol_gungor_agent_output": {"error": "Erol Güngör ajanı yapılandırılmamış"}
        }
    
    try:
        # Create message for the agent
        messages = [HumanMessage(content=state["user_query"])]
        print(f"💬 DEBUG: Invoking Erol Güngör agent")
        
        # Invoke the agent
        result = erol_agent.invoke({"messages": messages})
        print(f"✅ DEBUG: Erol Güngör agent completed successfully")
        print(f"📊 DEBUG: Agent returned {len(result.get('messages', []))} messages")
        
        return {
            "erol_gungor_agent_output": result
        }
        
    except Exception as e:
        print(f"❌ DEBUG: Error in Erol Güngör agent node: {str(e)}")
        return {
            "erol_gungor_agent_output": {"error": f"Erol Güngör ajanı hatası: {str(e)}"}
        }

def cemil_meric_agent_node(state: GraphState, config: RunnableConfig) -> Dict[str, Any]:
    """Cemil Meriç ajanını çalıştıran node."""
    
    print(f"\n🎯 DEBUG: Starting Cemil Meriç agent node")
    print(f"🔍 DEBUG: User query: {state['user_query']}")
    
    # Get the agent from config
    cemil_agent = config.get("configurable", {}).get("cemil_agent")
    if not cemil_agent:
        print(f"❌ DEBUG: Cemil Meriç agent not found in config")
        return {
            "cemil_meric_agent_output": {"error": "Cemil Meriç ajanı yapılandırılmamış"}
        }
    
    try:
        # Create message for the agent
        messages = [HumanMessage(content=state["user_query"])]
        print(f"💬 DEBUG: Invoking Cemil Meriç agent")
        
        # Invoke the agent
        result = cemil_agent.invoke({"messages": messages})
        print(f"✅ DEBUG: Cemil Meriç agent completed successfully")
        print(f"📊 DEBUG: Agent returned {len(result.get('messages', []))} messages")
        
        return {
            "cemil_meric_agent_output": result
        }
        
    except Exception as e:
        print(f"❌ DEBUG: Error in Cemil Meriç agent node: {str(e)}")
        return {
            "cemil_meric_agent_output": {"error": f"Cemil Meriç ajanı hatası: {str(e)}"}
        }

def join_agents_node(state: GraphState, config: RunnableConfig) -> Dict[str, Any]:
    """İki ajanın tamamlanmasını bekleyen ara node."""
    
    print(f"\n🔄 DEBUG: Join node - checking if both agents completed")
    
    erol_output = state.get("erol_gungor_agent_output")
    cemil_output = state.get("cemil_meric_agent_output")
    
    print(f"✓ DEBUG: Erol Güngör output available: {erol_output is not None}")
    print(f"✓ DEBUG: Cemil Meriç output available: {cemil_output is not None}")
    
    # This node doesn't modify state, just serves as a junction
    return {}

def synthesize_response_node(state: GraphState, config: RunnableConfig) -> Dict[str, Any]:
    """İki ajanın yanıtlarını birleştiren node."""
    
    print(f"\n🔄 DEBUG: Starting synthesis node")
    
    # Get the LLM from config
    llm = config.get("configurable", {}).get("llm")
    if not llm:
        print(f"❌ DEBUG: LLM not found in config for synthesis")
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
    
    print(f"📝 DEBUG: Erol Güngör response length: {len(erol_response)} characters")
    print(f"📝 DEBUG: Cemil Meriç response length: {len(cemil_response)} characters")
    
    # Create synthesis prompt
    synthesis_prompt = f"""Sen, Türk entelektüel geleneğini anlayan ve farklı bakış açılarını sentezleyebilen bir asistansın.

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

Başlıklar kullanma, doğrudan kapsamlı bir yanıt ver."""
    
    try:
        print(f"🧠 DEBUG: Sending synthesis request to Gemini...")
        synthesis_result = llm.invoke(synthesis_prompt)
        
        synthesized_text = synthesis_result.content if hasattr(synthesis_result, 'content') else str(synthesis_result)
        print(f"✅ DEBUG: Synthesis completed successfully")
        print(f"📏 DEBUG: Synthesized response length: {len(synthesized_text)} characters")
        
        # Prepare individual agent responses for frontend
        agent_responses = {
            "Erol Güngör": erol_response,
            "Cemil Meriç": cemil_response
        }
        
        print(f"🎯 DEBUG: Agent responses prepared for frontend: {list(agent_responses.keys())}")
        
        return {
            "synthesized_answer": synthesized_text,
            "agent_responses": agent_responses
        }
        
    except Exception as e:
        print(f"❌ DEBUG: Error during synthesis: {str(e)}")
        return {
            "synthesized_answer": f"Sentez hatası: {str(e)}",
            "agent_responses": {
                "Erol Güngör": erol_response if erol_response else "Yanıt alınamadı",
                "Cemil Meriç": cemil_response if cemil_response else "Yanıt alınamadı"
            }
        }

def update_history_node(state: GraphState, config: RunnableConfig) -> Dict[str, Any]:
    """Sohbet geçmişini güncelleyen node."""
    
    print(f"\n📚 DEBUG: Updating chat history")
    
    # Create messages for history
    user_message = HumanMessage(content=state["user_query"])
    ai_message = AIMessage(content=state.get("synthesized_answer", "Yanıt oluşturulamadı"))
    
    print(f"💬 DEBUG: Adding user message and AI response to history")
    print(f"📊 DEBUG: Current history length: {len(state.get('chat_history', []))}")
    
    new_messages = [user_message, ai_message]
    
    print(f"✅ DEBUG: Chat history updated with {len(new_messages)} new messages")
    
    return {"chat_history": new_messages}

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
        
        print(f"\n🚀 DEBUG: Initializing Multi-Agent Orchestrator")
        
        # Initialize Phase 1 components
        print(f"🔧 DEBUG: Initializing Phase 1 components...")
        self.qdrant_client, self.embedding_model, self.llm = initialize_components()
        
        if not all([self.qdrant_client, self.embedding_model, self.llm]):
            raise Exception("Phase 1 bileşenleri başlatılamadı")
        
        print(f"✅ DEBUG: Phase 1 components initialized successfully")
        
        # Create persona agents
        print(f"👥 DEBUG: Creating persona agents...")
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
                print(f"✓ DEBUG: Created agent for {persona_info['name']}")
            except Exception as e:
                print(f"❌ DEBUG: Failed to create agent for {persona_key}: {e}")
                raise
        
        print(f"✅ DEBUG: All persona agents created successfully")
        
        # Build the graph
        print(f"🏗️ DEBUG: Building LangGraph workflow...")
        self._build_graph()
        print(f"✅ DEBUG: Multi-Agent Orchestrator initialized successfully")
    
    def _build_graph(self):
        """LangGraph workflow'unu oluşturur."""
        
        print(f"\n🏗️ DEBUG: Building state graph...")
        
        # Create the state graph
        workflow = StateGraph(GraphState)
        
        # Add nodes
        print(f"➕ DEBUG: Adding nodes to graph...")
        workflow.add_node("erol_gungor_agent", erol_gungor_agent_node)
        workflow.add_node("cemil_meric_agent", cemil_meric_agent_node)
        workflow.add_node("join_agents", join_agents_node)
        workflow.add_node("synthesize_response", synthesize_response_node)
        workflow.add_node("update_history", update_history_node)
        
        # Add edges
        print(f"🔗 DEBUG: Adding edges to graph...")
        
        # Entry point: Start with both agents in parallel
        workflow.add_edge(START, "erol_gungor_agent")
        workflow.add_edge(START, "cemil_meric_agent")
        
        # Both agents feed into join node
        workflow.add_edge("erol_gungor_agent", "join_agents")
        workflow.add_edge("cemil_meric_agent", "join_agents")
        
        # Sequential flow after joining
        workflow.add_edge("join_agents", "synthesize_response")
        workflow.add_edge("synthesize_response", "update_history")
        workflow.add_edge("update_history", END)
        
        # Compile the graph
        print(f"⚙️ DEBUG: Compiling graph...")
        checkpointer = MemorySaver()
        self.graph = workflow.compile(checkpointer=checkpointer)
        
        print(f"✅ DEBUG: Graph compiled successfully")
    
    def invoke(self, user_query: str, thread_id: str = "default") -> Dict[str, Any]:
        """Orchestrator'ı çalıştırır."""
        
        print(f"\n🎯 DEBUG: Invoking Multi-Agent Orchestrator")
        print(f"💬 DEBUG: User query: {user_query}")
        print(f"🧵 DEBUG: Thread ID: {thread_id}")
        
        # Prepare initial state
        initial_state = {
            "user_query": user_query,
            "erol_gungor_agent_output": None,
            "cemil_meric_agent_output": None,
            "synthesized_answer": None,
            "agent_responses": None,
            "chat_history": []
        }
        
        # Prepare config with agents
        config = {
            "configurable": {
                "erol_agent": self.agents.get("erol_gungor"),
                "cemil_agent": self.agents.get("cemil_meric"),
                "llm": self.llm,
                "thread_id": thread_id
            }
        }
        
        try:
            print(f"🚀 DEBUG: Starting graph execution...")
            result = self.graph.invoke(initial_state, config)
            
            print(f"✅ DEBUG: Graph execution completed successfully")
            print(f"📊 DEBUG: Final state keys: {list(result.keys())}")
            
            return result
            
        except Exception as e:
            print(f"❌ DEBUG: Error during graph execution: {str(e)}")
            return {
                "error": f"Orchestration hatası: {str(e)}",
                "user_query": user_query,
                "synthesized_answer": "Sistem hatası nedeniyle yanıt oluşturulamadı."
            }

# --- Convenience Functions ---

def create_orchestrator() -> MultiAgentOrchestrator:
    """Yeni bir Multi-Agent Orchestrator oluşturur ve başlatır."""
    
    orchestrator = MultiAgentOrchestrator()
    orchestrator.initialize()
    return orchestrator

def run_multi_agent_query(query: str, thread_id: str = "default") -> Dict[str, Any]:
    """Tek seferlik multi-agent sorgu çalıştırır."""
    
    orchestrator = create_orchestrator()
    return orchestrator.invoke(query, thread_id) 