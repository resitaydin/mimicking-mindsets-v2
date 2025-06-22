import asyncio
from typing import Any, Dict, List, Optional, Tuple
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun
from langgraph.prebuilt import create_react_agent
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
import torch
import os

# Import persona prompts
from .persona_prompts import get_persona_system_prompt, get_persona_info, list_available_personas

# --- Configuration ---
EMBEDDING_MODEL_NAME = "BAAI/bge-m3"
EMBEDDING_DIMENSION = 1024
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333

# Connection pool configuration
QDRANT_POOL_SIZE = 3  # Small pool for efficiency

# --- Global Connection Pool ---
import threading
from queue import Queue

class QdrantConnectionPool:
    """Simple connection pool for Qdrant clients to improve performance."""
    
    def __init__(self, host: str, port: int, pool_size: int = 3):
        self.host = host
        self.port = port
        self.pool_size = pool_size
        self.pool = Queue(maxsize=pool_size)
        self.lock = threading.Lock()
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Initialize the connection pool with Qdrant clients."""
        print(f"🔗 DEBUG: Initializing Qdrant connection pool (size: {self.pool_size})")
        
        for i in range(self.pool_size):
            try:
                client = QdrantClient(host=self.host, port=self.port)
                # Test connection
                client.get_collections()
                self.pool.put(client)
                print(f"✓ DEBUG: Connection {i+1}/{self.pool_size} added to pool")
            except Exception as e:
                print(f"❌ DEBUG: Failed to create connection {i+1}: {e}")
                raise
        
        print(f"✅ DEBUG: Qdrant connection pool initialized successfully")
    
    def get_client(self) -> QdrantClient:
        """Get a client from the pool (blocking if pool is empty)."""
        return self.pool.get()
    
    def return_client(self, client: QdrantClient):
        """Return a client to the pool."""
        self.pool.put(client)
    
    def get_pool_size(self) -> int:
        """Get current pool size."""
        return self.pool.qsize()

# Global connection pool instance
_qdrant_pool = None
_pool_lock = threading.Lock()

def get_qdrant_pool() -> QdrantConnectionPool:
    """Get or create the global Qdrant connection pool."""
    global _qdrant_pool
    
    with _pool_lock:
        if _qdrant_pool is None:
            _qdrant_pool = QdrantConnectionPool(QDRANT_HOST, QDRANT_PORT, QDRANT_POOL_SIZE)
    
    return _qdrant_pool

# Persona configurations (updated to use persona_prompts module)
PERSONAS = {
    "erol_gungor": {
        "name": "Erol Güngör",
        "collection": "erol_gungor_kb",
        "description": "Turkish sociologist, psychologist, and intellectual known for his works on cultural psychology and social analysis."
    },
    "cemil_meric": {
        "name": "Cemil Meriç",
        "collection": "cemil_meric_kb", 
        "description": "Turkish intellectual, translator, and writer known for his profound philosophical and cultural analyses."
    }
}

# --- Tool Definitions ---

def create_web_search_tool():
    """Creates a web search tool using DuckDuckGo."""
    
    # Create the base DuckDuckGo search tool
    base_search = DuckDuckGoSearchRun()
    
    # Wrap it with debug functionality
    @tool
    def web_search(query: str) -> str:
        """Dahili bilgi yetersiz veya güncel olmadığında güncel bilgiler için internet araması yapar. Bunu son dönem olayları, güncel istatistikler veya kişinin bilgi tabanında olmayan konular için kullanın."""
        
        print(f"\n🌐 DEBUG: Starting web search for query: '{query}'")
        
        try:
            print(f"🔍 DEBUG: Using DuckDuckGo to search the web...")
            results = base_search.run(query)
            
            print(f"📊 DEBUG: Web search completed successfully")
            print(f"📄 DEBUG: Search results length: {len(results)} characters")
            
            # Show a preview of the results (first 200 chars)
            preview = results[:200] + "..." if len(results) > 200 else results
            print(f"👀 DEBUG: Search results preview: {preview}")
            
            print(f"✅ DEBUG: Web search completed successfully")
            return results
            
        except Exception as e:
            print(f"❌ DEBUG: Error during web search: {str(e)}")
            return f"Web araması hatası: {str(e)}"
    
    return web_search

def create_internal_knowledge_search_tool(
    persona_key: str,
    qdrant_client: QdrantClient,  # Keep for backward compatibility
    embedding_model: SentenceTransformer
):
    """Creates a persona-specific internal knowledge search tool with connection pooling."""
    
    persona_config = PERSONAS[persona_key]
    collection_name = persona_config["collection"]
    persona_name = persona_config["name"]
    
    @tool
    def internal_knowledge_search(query: str) -> str:
        """Belirtilen sorgu için kişinin dahili bilgi tabanından ilgili bilgileri arar.
        
        Args:
            query: Kişinin eserlerinden ve bilgisinden ilgili bilgi bulmak için arama sorgusu.
            
        Returns:
            Kişinin bilgi tabanından kaynak bilgileri ile birlikte alınan metin parçaları.
        """
        print(f"\n🔍 DEBUG: {persona_name} is searching internal knowledge base for: '{query}'")
        
        # Get connection pool and client
        pool = get_qdrant_pool()
        client = pool.get_client()
        
        try:
            # Embed the query
            print(f"📊 DEBUG: Embedding query using {EMBEDDING_MODEL_NAME}...")
            query_embedding = embedding_model.encode([query])
            print(f"✅ DEBUG: Query embedded successfully (dimension: {len(query_embedding[0])})")
            
            # Perform semantic search in Qdrant using pooled connection
            print(f"🔎 DEBUG: Performing semantic search in Qdrant collection: {collection_name} (pooled connection)")
            search_results = client.search(
                collection_name=collection_name,
                query_vector=query_embedding[0].tolist(),
                limit=5,  # Top 5 most relevant chunks
                with_payload=True
            )
            
            print(f"📋 DEBUG: Found {len(search_results)} results from internal knowledge base")
            
            if not search_results:
                print(f"❌ DEBUG: No relevant information found in {persona_name}'s knowledge base")
                return f"{persona_name}'nin bilgi tabanında '{query}' sorgusu için ilgili bilgi bulunamadı."
            
            # Format results
            formatted_results = []
            for i, result in enumerate(search_results, 1):
                payload = result.payload
                text = payload.get('text', 'Metin mevcut değil')
                source = payload.get('source', 'Bilinmeyen kaynak')
                score = result.score
                
                print(f"📄 DEBUG: Result {i} - Source: {source}, Relevance: {score:.3f}, Text length: {len(text)} chars")
                
                formatted_results.append(
                    f"Sonuç {i} (İlgililik: {score:.3f}):\n"
                    f"Kaynak: {source}\n"
                    f"İçerik: {text}\n"
                    f"{'='*50}"
                )
            
            print(f"✅ DEBUG: Internal knowledge search completed successfully for {persona_name}")
            return f"{persona_name}'nin bilgi tabanından alınan bilgiler:\n\n" + "\n\n".join(formatted_results)
            
        except Exception as e:
            print(f"❌ DEBUG: Error during internal knowledge search: {str(e)}")
            return f"{persona_name}'nin bilgi tabanında arama hatası: {str(e)}"
        finally:
            # Always return the client to the pool
            pool.return_client(client)
    
    # Set the tool name to be persona-specific
    internal_knowledge_search.name = f"internal_knowledge_search_{persona_key}"
    internal_knowledge_search.description = f"{persona_name}'nin dahili bilgi tabanında sorguya uygun bilgileri arar. {persona_name} olarak yanıt verirken bu sizin birincil bilgi kaynağınız olmalıdır."
    
    return internal_knowledge_search

# --- Persona Agent Factory ---

def create_persona_agent(
    persona_key: str,
    qdrant_client: QdrantClient,
    embedding_model: SentenceTransformer,
    llm: ChatGoogleGenerativeAI
):
    """
    Creates a persona agent using LangGraph's create_react_agent.
    
    Args:
        persona_key: Key identifying the persona ('erol_gungor' or 'cemil_meric')
        qdrant_client: Qdrant client for vector database access
        embedding_model: SentenceTransformer model for embeddings
        llm: Language model (Gemini 2.0 Flash)
        
    Returns:
        LangGraph agent configured for the specified persona
    """
    
    print(f"\n🤖 DEBUG: Creating persona agent for: {persona_key}")
    
    # Validate persona key using the new module
    available_personas = list_available_personas()
    if persona_key not in available_personas:
        raise ValueError(f"Unknown persona: {persona_key}. Available personas: {available_personas}")
    
    # Get persona information from the new module
    persona_info = get_persona_info(persona_key)
    persona_name = persona_info["name"]
    
    print(f"👤 DEBUG: Persona name: {persona_name}")
    print(f"📅 DEBUG: Persona years: {persona_info['years']}")
    print(f"🎯 DEBUG: Expertise areas: {', '.join(persona_info['expertise_areas'])}")
    
    # Create tools
    print(f"🔧 DEBUG: Creating web search tool...")
    web_search_tool = create_web_search_tool()
    
    print(f"🔧 DEBUG: Creating internal knowledge search tool...")
    internal_knowledge_tool = create_internal_knowledge_search_tool(
        persona_key, qdrant_client, embedding_model
    )
    
    tools = [internal_knowledge_tool, web_search_tool]
    print(f"🛠️ DEBUG: Created {len(tools)} tools for {persona_name}")
    
    # Get the complete system prompt from the new module
    print(f"📝 DEBUG: Generating system prompt for {persona_name}...")
    system_prompt = get_persona_system_prompt(persona_key)
    print(f"📏 DEBUG: System prompt length: {len(system_prompt)} characters")
    
    # Create the react agent
    print(f"🏗️ DEBUG: Creating LangGraph ReAct agent with Gemini 2.0 Flash...")
    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=system_prompt
    )
    
    print(f"✅ DEBUG: Successfully created {persona_name} agent")
    return agent

# --- Testing Functions ---

def initialize_components():
    """Initialize all required components with connection pooling."""
    
    print(f"\n🚀 DEBUG: Starting component initialization...")
    
    # Initialize Qdrant connection pool
    print(f"🔌 DEBUG: Initializing Qdrant connection pool at {QDRANT_HOST}:{QDRANT_PORT}...")
    try:
        pool = get_qdrant_pool()
        
        # Test pool by getting a client and checking collections
        test_client = pool.get_client()
        try:
            collections = test_client.get_collections()
            print(f"📊 DEBUG: Found {len(collections.collections)} collections in Qdrant")
            for collection in collections.collections:
                print(f"   📁 DEBUG: Collection: {collection.name}")
            print(f"✓ Qdrant connection pool initialized: {QDRANT_HOST}:{QDRANT_PORT}")
            
            # Return a client for backward compatibility (though pool will be used internally)
            qdrant_client = test_client
        finally:
            pool.return_client(test_client)
            
    except Exception as e:
        print(f"❌ DEBUG: Failed to initialize Qdrant connection pool: {e}")
        print(f"✗ Qdrant connection pool initialization failed: {e}")
        return None, None, None
    
    # Initialize embedding model
    print(f"🧠 DEBUG: Loading embedding model: {EMBEDDING_MODEL_NAME}...")
    try:
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"💻 DEBUG: Using device: {device}")
        if device == 'cuda':
            print(f"🎮 DEBUG: GPU: {torch.cuda.get_device_name(0)}")
        
        embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME, device=device)
        print(f"📏 DEBUG: Model embedding dimension: {embedding_model.get_sentence_embedding_dimension()}")
        print(f"✓ Kullanılan cihaz: {device}")
        print(f"✓ Gömme modeli yüklendi: {EMBEDDING_MODEL_NAME}")
    except Exception as e:
        print(f"❌ DEBUG: Failed to load embedding model: {e}")
        print(f"✗ Gömme modeli yükleme hatası: {e}")
        return None, None, None
    
    # Initialize Gemini LLM
    print(f"🤖 DEBUG: Initializing Gemini 2.0 Flash LLM...")
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            temperature=0.1,
            max_tokens=2048
        )
        print(f"🔧 DEBUG: LLM configuration - Model: gemini-2.0-flash-exp, Temperature: 0.1, Max tokens: 2048")
        print("✓ Gemini 2.0 Flash başlatıldı")
    except Exception as e:
        print(f"❌ DEBUG: Failed to initialize Gemini: {e}")
        print(f"✗ Gemini başlatma hatası: {e}")
        print("GOOGLE_API_KEY ortam değişkeninin ayarlandığından emin olun")
        return None, None, None
    
    print(f"✅ DEBUG: All components initialized successfully!")
    return qdrant_client, embedding_model, llm