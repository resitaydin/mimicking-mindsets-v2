# Mimicking Mindsets v2

AI-Generated Insights from Influential Turkish Minds

## Overview

This multi-agent system allows you to interact with AI representations of prominent Turkish intellectuals. The system provides synthesized insights from multiple perspectives using a sophisticated RAG (Retrieval-Augmented Generation) architecture.

### Available Personas
- **Cemil Meriç** (1916-1987): Intellectual, translator, essayist. Expert in Eastern/Western philosophy, French literature, cultural synthesis.
- **Erol Güngör** (1938-1983): Psychologist, sociologist. Expert in social psychology, Turkish cultural psychology, social change.

## Architecture

### Phase 1: Knowledge Base Construction (`build_kb.py`)
- PDF text extraction and preprocessing
- Text chunking and embedding generation
- Vector storage in Qdrant collections

### Phase 2: Runtime Interaction
- **Memory Module**: Conversation history management
- **Persona Agents**: Individual intellectual perspectives with knowledge retrieval
- **Orchestrator Agent**: Central coordination and response synthesis
- **Web Search Tool**: For current information not in historical knowledge base

## Prerequisites

1. **Python 3.12+**
2. **Qdrant** vector database
3. **Gemini API key** from Google AI Studio

## Quick Start

### 1. Install Dependencies
```bash
uv sync
```

### 2. Start Qdrant
```bash
# Using Docker (recommended)
docker run -p 6333:6333 qdrant/qdrant
```

### 3. Set Environment Variables
Create a `.env` file:
```env
GEMINI_API_KEY=your_actual_api_key_here
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

### 4. Build Knowledge Base
```bash
python build_kb.py
```

### 5. Run the System
```bash
python main.py
```

## Usage

### Interactive Commands
- Type questions naturally for synthesized responses
- `/help` - Show help information  
- `/summary` - View conversation summary
- `/clear` - Clear conversation history
- `/export <filename>` - Export conversation to JSON
- `/quit` - Exit system

### Example Questions
- "What is the relationship between culture and civilization?"
- "How does modernization affect traditional values?"
- "What role does psychology play in understanding society?"

## System Flow

1. **Query Analysis**: Orchestrator determines relevant persona agents
2. **Parallel Processing**: Multiple agents process query concurrently
3. **Knowledge Retrieval**: Each agent searches its Qdrant collection
4. **Web Search**: Additional context if needed for current topics
5. **Response Generation**: Gemini LLM generates persona-specific responses
6. **Synthesis**: Orchestrator combines perspectives into coherent answer
7. **Memory Storage**: Conversation history is maintained

## Technical Features

- **Hybrid Search**: Semantic similarity + keyword matching
- **Concurrent Processing**: Parallel agent execution for efficiency
- **Context Management**: Conversation continuity across turns
- **Source Attribution**: References to original works when available
- **Adaptive Querying**: Query enhancement for better retrieval
- **Error Resilience**: Graceful handling of failures

## Development

### File Structure
```
├── build_kb.py          # Knowledge base construction
├── main.py              # Entry point
├── runtime.py           # Main runtime system
├── orchestrator.py      # Central coordination agent
├── persona_agents.py    # Individual persona agents
├── memory.py            # Conversation memory management
├── pyproject.toml       # Dependencies
└── README.md           # This file
```

### Adding New Personas
1. Add persona configuration to `runtime.py`
2. Create new agent class in `persona_agents.py`
3. Add PDF files to appropriate directory
4. Update `build_kb.py` configuration
5. Rebuild knowledge base

## Performance Notes

- First run downloads embedding model (~500MB)
- GPU acceleration available for embeddings
- Qdrant collections are created automatically
- Web search is used sparingly for current topics

## Troubleshooting

**Qdrant Connection Issues**
- Verify Qdrant is running and accessible
- Check host/port configuration

**Missing Collections**
- Run `build_kb.py` to create knowledge base
- Ensure PDF files exist in correct directories

**API Errors**
- Verify Gemini API key is valid
- Check API quota and billing status

## License

This project is part of the Mimicking Mindsets research initiative.
