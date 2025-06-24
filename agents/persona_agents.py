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

# Import logging
from utils.logging_config import get_agent_logger

# Initialize logger
logger = get_agent_logger()

# --- Configuration ---
EMBEDDING_MODEL_NAME = "BAAI/bge-m3"
EMBEDDING_DIMENSION = 1024
QDRANT_HOST = "my-qdrant-instance"
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
        logger.info(f"Initializing Qdrant connection pool (size: {self.pool_size})")
        
        for i in range(self.pool_size):
            try:
                client = QdrantClient(host=self.host, port=self.port)
                # Test connection
                client.get_collections()
                self.pool.put(client)
            except Exception as e:
                logger.error(f"Failed to create connection {i+1}: {e}")
                raise
        
        logger.info("Qdrant connection pool initialized successfully")
    
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
        
        try:
            results = base_search.run(query)
            logger.info(f"Web search completed for query: '{query[:50]}...'")
            return results
            
        except Exception as e:
            logger.error(f"Error during web search: {str(e)}")
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
        # Get connection pool and client
        pool = get_qdrant_pool()
        client = pool.get_client()
        
        try:
            # Embed the query
            query_embedding = embedding_model.encode([query])
            
            # Perform semantic search in Qdrant using pooled connection
            search_results = client.search(
                collection_name=collection_name,
                query_vector=query_embedding[0].tolist(),
                limit=5,  # Top 5 most relevant chunks
                with_payload=True
            )
            
            if not search_results:
                return f"{persona_name}'nin bilgi tabanında '{query}' sorgusu için ilgili bilgi bulunamadı."
            
            # Format results
            formatted_results = []
            for i, result in enumerate(search_results, 1):
                payload = result.payload
                text = payload.get('text', 'Metin mevcut değil')
                source = payload.get('source', 'Bilinmeyen kaynak')
                score = result.score
                
                formatted_results.append(
                    f"Sonuç {i} (İlgililik: {score:.3f}):\n"
                    f"Kaynak: {source}\n"
                    f"İçerik: {text}\n"
                    f"{'='*50}"
                )
            
            logger.info(f"Internal knowledge search completed for {persona_name}")
            return f"{persona_name}'nin bilgi tabanından alınan bilgiler:\n\n" + "\n\n".join(formatted_results)
            
        except Exception as e:
            logger.error(f"Error during internal knowledge search: {str(e)}")
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
    
    # Validate persona key using the new module
    available_personas = list_available_personas()
    if persona_key not in available_personas:
        raise ValueError(f"Unknown persona: {persona_key}. Available personas: {available_personas}")
    
    # Get persona information from the new module
    persona_info = get_persona_info(persona_key)
    persona_name = persona_info["name"]
    
    # Create tools
    web_search_tool = create_web_search_tool()
    internal_knowledge_tool = create_internal_knowledge_search_tool(
        persona_key, qdrant_client, embedding_model
    )
    
    tools = [internal_knowledge_tool, web_search_tool]
    
    # Get the complete system prompt from the new module
    system_prompt = get_persona_system_prompt(persona_key)
    
    # Create the react agent
    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=system_prompt
    )
    
    logger.info(f"Successfully created {persona_name} agent")
    return agent

# --- Testing Functions ---

def initialize_components():
    """Initialize all required components with connection pooling."""
    
    logger.info("Starting component initialization")
    
    # Initialize Qdrant connection pool
    try:
        pool = get_qdrant_pool()
        
        # Test pool by getting a client and checking collections
        test_client = pool.get_client()
        try:
            collections = test_client.get_collections()
            logger.info(f"Found {len(collections.collections)} collections in Qdrant")
            
            # Return a client for backward compatibility (though pool will be used internally)
            qdrant_client = test_client
        finally:
            pool.return_client(test_client)
            
    except Exception as e:
        logger.error(f"Failed to initialize Qdrant connection pool: {e}")
        return None, None, None
    
    # Initialize embedding model
    try:
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        logger.info(f"Using device: {device}")
        if device == 'cuda':
            logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
        
        embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME, device=device)
        logger.info(f"Embedding model loaded: {EMBEDDING_MODEL_NAME}")
    except Exception as e:
        logger.error(f"Failed to load embedding model: {e}")
        return None, None, None
    
    # Initialize Gemini LLM
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.1,
            max_tokens=2048
        )
        logger.info("Gemini 2.0 Flash initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Gemini: {e}")
        logger.error("Make sure GOOGLE_API_KEY environment variable is set")
        return None, None, None
    
    logger.info("All components initialized successfully")
    return qdrant_client, embedding_model, llm