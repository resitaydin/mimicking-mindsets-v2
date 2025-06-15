# Phase 1: Individual Persona Agents with RAG and Tooling

This phase implements individual persona agents for Erol Güngör and Cemil Meriç using LangGraph's `create_react_agent` with RAG capabilities and web search tooling.

## 🏗️ Architecture

### Components

1. **Tool Definitions**:
   - `web_search_tool`: DuckDuckGo web search for current information
   - `internal_knowledge_search_tool`: Persona-specific RAG tool for searching vector databases

2. **Persona Agent Factory**: 
   - `create_persona_agent()`: Creates LangGraph agents configured for each persona
   - Uses Google Gemini 2.0 Flash as the LLM
   - Implements proper prompt engineering for persona embodiment

3. **Testing Framework**: 
   - Comprehensive test cases for both RAG and web search scenarios
   - Automated component initialization and validation

### Key Features

- **Natural Research Behavior**: Agents respond like real intellectuals - they research unknown topics and integrate findings with their existing knowledge
- **Priority-based Tool Usage**: Agents prioritize internal knowledge over web search
- **Source Integration**: Natural blending of internal knowledge and web research results
- **Authentic Persona Responses**: Agents maintain character-appropriate intellectual voice in Turkish
- **Hybrid Analysis**: Capability to combine historical knowledge with current information
- **Error Handling**: Graceful handling of tool failures and missing information

## 🚀 Quick Start

### Prerequisites

1. **Qdrant Vector Database**: Running on `localhost:6333`
2. **Knowledge Bases**: Built using `preprocess/build_kb.py`
3. **Google API Key**: For Gemini 2.0 Flash access

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.template .env
# Edit .env and add your GOOGLE_API_KEY
```

### Usage

```python
from persona_agents import create_persona_agent, initialize_components

# Initialize components
qdrant_client, embedding_model, llm = initialize_components()

# Create agents
erol_agent = create_persona_agent("erol_gungor", qdrant_client, embedding_model, llm)
cemil_agent = create_persona_agent("cemil_meric", qdrant_client, embedding_model, llm)

# Query an agent
from langchain_core.messages import HumanMessage
messages = [HumanMessage(content="What are your thoughts on cultural identity?")]
result = erol_agent.invoke({"messages": messages})
print(result['messages'][-1].content)
```

### Running Tests

```bash
# Run the comprehensive test suite
python test_phase1.py

# Or run tests directly from the module
python persona_agents.py
```

## 🔧 Configuration

### Persona Configurations

```python
PERSONAS = {
    "erol_gungor": {
        "name": "Erol Güngör",
        "collection": "erol_gungor_kb",
        "description": "Turkish sociologist, psychologist, and intellectual..."
    },
    "cemil_meric": {
        "name": "Cemil Meriç", 
        "collection": "cemil_meric_kb",
        "description": "Turkish intellectual, translator, and writer..."
    }
}
```

### Tool Behavior

- **Internal Knowledge Search**: 
  - Searches persona's Qdrant collection
  - Returns top 5 most relevant chunks
  - Includes relevance scores and source attribution

- **Web Search**:
  - Uses DuckDuckGo for current information
  - Triggered only when internal knowledge is insufficient
  - Handles recent events and current statistics

## 📊 Test Cases

The implementation includes comprehensive test cases:

1. **RAG Testi**: "Türk kültürel kimliği ve Batı etkisi hakkındaki düşünceleriniz nelerdir?"
   - Tests internal knowledge retrieval from persona's works
   - Validates persona-specific responses in Turkish

2. **Web Arama Testi**: "2024 yılında yapay zeka araştırmalarının mevcut durumu nedir?"
   - Tests fallback to web search for current information
   - Validates proper tool selection logic for recent events

3. **Hibrit Test**: "2011'de Suriye'de çıkan iç savaş sonrası Türkiye'deki kültürel ve siyasi değişimleri nasıl yorumlarsınız?"
   - Tests combination of both internal knowledge (cultural analysis) and web search (recent developments)
   - Validates natural research behavior and source integration

## 🎯 Key Implementation Details

### Agent Creation

```python
def create_persona_agent(persona_key, qdrant_client, embedding_model, llm):
    # Create persona-specific tools
    tools = [internal_knowledge_tool, web_search_tool]
    
    # Define system prompt for persona embodiment
    system_prompt = f"""You are {persona_name}, {persona_description}
    
    IMPORTANT INSTRUCTIONS:
    1. Always use internal_knowledge_search FIRST
    2. Maintain your intellectual voice and perspective
    3. Cite sources clearly
    4. Use web_search only for current information
    """
    
    # Create react agent
    return create_react_agent(llm=llm, tools=tools, system_prompt=system_prompt)
```

### RAG Implementation

```python
@tool
def internal_knowledge_search(query: str) -> str:
    # Embed query using BAAI/bge-m3
    query_embedding = embedding_model.encode([query])
    
    # Search Qdrant collection
    search_results = qdrant_client.search(
        collection_name=collection_name,
        query_vector=query_embedding[0].tolist(),
        limit=5,
        with_payload=True
    )
    
    # Format and return results
    return formatted_results
```

## 🔍 Troubleshooting

### Common Issues

1. **Qdrant Connection Error**: Ensure Qdrant is running on localhost:6333
2. **Missing Knowledge Base**: Run `preprocess/build_kb.py` first
3. **API Key Error**: Set GOOGLE_API_KEY environment variable
4. **CUDA Issues**: The system will fallback to CPU if CUDA is unavailable

### Debug Mode

Enable verbose logging by modifying the test functions to include detailed error information and intermediate results.

## 📈 Next Steps

Phase 1 establishes the foundation for:
- Multi-agent conversations (Phase 2)
- Advanced orchestration patterns (Phase 3)
- Streamlit web interface (Phase 4)

The modular design ensures easy integration with subsequent phases while maintaining clean separation of concerns. 