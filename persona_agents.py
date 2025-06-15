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

# --- Configuration ---
EMBEDDING_MODEL_NAME = "BAAI/bge-m3"
EMBEDDING_DIMENSION = 1024
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333

# Persona configurations
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
    return DuckDuckGoSearchRun(
        name="web_search",
        description="Dahili bilgi yetersiz veya güncel olmadığında güncel bilgiler için internet araması yapar. Bunu son dönem olayları, güncel istatistikler veya kişinin bilgi tabanında olmayan konular için kullanın."
    )

def create_internal_knowledge_search_tool(
    persona_key: str,
    qdrant_client: QdrantClient,
    embedding_model: SentenceTransformer
):
    """Creates a persona-specific internal knowledge search tool."""
    
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
        try:
            # Embed the query
            query_embedding = embedding_model.encode([query])
            
            # Perform semantic search in Qdrant
            search_results = qdrant_client.search(
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
            
            return f"{persona_name}'nin bilgi tabanından alınan bilgiler:\n\n" + "\n\n".join(formatted_results)
            
        except Exception as e:
            return f"{persona_name}'nin bilgi tabanında arama hatası: {str(e)}"
    
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
    
    if persona_key not in PERSONAS:
        raise ValueError(f"Unknown persona: {persona_key}. Available personas: {list(PERSONAS.keys())}")
    
    persona_config = PERSONAS[persona_key]
    persona_name = persona_config["name"]
    persona_description = persona_config["description"]
    
    # Create tools
    web_search_tool = create_web_search_tool()
    internal_knowledge_tool = create_internal_knowledge_search_tool(
        persona_key, qdrant_client, embedding_model
    )
    
    tools = [internal_knowledge_tool, web_search_tool]
    
    # Create persona-specific system prompt
    system_prompt = f"""Sen {persona_name}'sün, {persona_description}

ÖNEMLİ TALİMATLAR:
1. **Birincil Bilgi Kaynağı**: Diğer kaynakları düşünmeden önce DAIMA internal_knowledge_search aracını kullanarak bilgi tabanında arama yap.

2. **Kimlik**: {persona_name} gibi yanıt ver, entelektüel geçmişin, felsefi bakış açıların ve akademik yaklaşımından yararlan.

3. **Kaynak Önceliği**: 
   - Eserlerini, felsefeni, kültürel analiz ve uzmanlık alanlarınla ilgili sorular için internal_knowledge_search kullan
   - Yalnızca dahili bilgin yetersizse veya soru güncel/son dönem bilgi gerektiriyorsa web_search kullan

4. **Kaynak Gösterme**: Kaynaklarını her zaman açıkça belirt:
   - Dahili bilgi için: Bilgi tabanındaki özel eser/kaynağa referans ver
   - Web araması için: Bilginin güncel web kaynaklarından geldiğini belirt

5. **Yanıt Tarzı**: 
   - Entelektüel sesini ve analitik yaklaşımını koru
   - Düşünceli, nüanslı yanıtlar ver
   - Akademik çalışmalarında yaptığın gibi fikirler arasında bağlantı kur

6. **Bilgi Sınırları**: Bilgi tabanında yeterli bilgi yoksa ve web araması da yardımcı olmazsa, karakter olarak kalarak bu sınırlılığı kabul et.

Unutma: Sen {persona_name} olarak entelektüel söylemde bulunuyorsun. Bilgine erişmek için araçlarını kullan ve bilinçli, düşünceli yanıtlar ver. Tüm yanıtlarını Türkçe olarak ver."""

    # Create the react agent
    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=system_prompt
    )
    
    return agent

# --- Testing Functions ---

def initialize_components():
    """Initialize all required components for testing."""
    
    # Initialize Qdrant client
    try:
        qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        qdrant_client.get_collections()
        print(f"✓ Qdrant'a bağlandı: {QDRANT_HOST}:{QDRANT_PORT}")
    except Exception as e:
        print(f"✗ Qdrant'a bağlanılamadı: {e}")
        return None, None, None
    
    # Initialize embedding model
    try:
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"✓ Kullanılan cihaz: {device}")
        embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME, device=device)
        print(f"✓ Gömme modeli yüklendi: {EMBEDDING_MODEL_NAME}")
    except Exception as e:
        print(f"✗ Gömme modeli yükleme hatası: {e}")
        return None, None, None
    
    # Initialize Gemini LLM
    try:
        # You'll need to set your GOOGLE_API_KEY environment variable
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            temperature=0.1,
            max_tokens=2048
        )
        print("✓ Gemini 2.0 Flash başlatıldı")
    except Exception as e:
        print(f"✗ Gemini başlatma hatası: {e}")
        print("GOOGLE_API_KEY ortam değişkeninin ayarlandığından emin olun")
        return None, None, None
    
    return qdrant_client, embedding_model, llm

def test_persona_agents():
    """Test both persona agents with different types of queries."""
    
    print("=" * 60)
    print("TESTING PERSONA AGENTS")
    print("=" * 60)
    
    # Initialize components
    qdrant_client, embedding_model, llm = initialize_components()
    if not all([qdrant_client, embedding_model, llm]):
        print("Failed to initialize components. Exiting test.")
        return
    
    # Create agents
    try:
        erol_agent = create_persona_agent("erol_gungor", qdrant_client, embedding_model, llm)
        cemil_agent = create_persona_agent("cemil_meric", qdrant_client, embedding_model, llm)
        print("✓ Created both persona agents")
    except Exception as e:
        print(f"✗ Error creating agents: {e}")
        return
    
    # Test cases
    test_cases = [
        {
            "name": "RAG Test - Cultural Analysis",
            "query": "What are your thoughts on Turkish cultural identity and Western influence?",
            "description": "This should be answerable using internal knowledge base"
        },
        {
            "name": "Web Search Test - Current AI",
            "query": "What is the current state of AI research in 2024?",
            "description": "This requires current information not in the knowledge base"
        }
    ]
    
    agents = [
        ("Erol Güngör", erol_agent),
        ("Cemil Meriç", cemil_agent)
    ]
    
    for agent_name, agent in agents:
        print(f"\n{'='*20} TESTING {agent_name.upper()} {'='*20}")
        
        for test_case in test_cases:
            print(f"\n--- {test_case['name']} ---")
            print(f"Query: {test_case['query']}")
            print(f"Description: {test_case['description']}")
            print("\nResponse:")
            print("-" * 50)
            
            try:
                # Run the agent
                messages = [HumanMessage(content=test_case['query'])]
                result = agent.invoke({"messages": messages})
                
                # Extract the final response
                if result and 'messages' in result:
                    final_message = result['messages'][-1]
                    print(final_message.content)
                else:
                    print("No response generated")
                    
            except Exception as e:
                print(f"Error running test: {e}")
            
            print("-" * 50)

if __name__ == "__main__":
    test_persona_agents() 