# Mimicking Mindsets

A multi-agent AI system that simulates Turkish intellectuals **Erol Güngör** and **Cemil Meriç** using advanced RAG (Retrieval-Augmented Generation) capabilities, web search integration, and intelligent response synthesis.

## 🎯 Overview

This project creates authentic AI personas of two prominent Turkish intellectuals who can engage in meaningful conversations about culture, philosophy, and society. The system combines their historical knowledge with current information through web search, providing thoughtful responses that reflect their unique perspectives.

### Key Features

- **Dual Persona Agents**: Erol Güngör (sociologist/psychologist) and Cemil Meriç (intellectual/translator)
- **RAG Integration**: Persona-specific knowledge bases built from their works
- **Web Search Capability**: DuckDuckGo integration for current information
- **Multi-Agent Orchestration**: Parallel processing and intelligent response synthesis
- **Comprehensive Evaluation**: RAGAS-based faithfulness and coherence metrics
- **Web Interface**: React frontend with FastAPI backend
- **Tracing & Monitoring**: LangSmith integration for debugging

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐
│   Erol Güngör   │    │   Cemil Meriç   │
│     Agent       │    │     Agent       │
└─────────┬───────┘    └─────────┬───────┘
          │                      │
          ├──────────┬────────────┤
                     │
          ┌─────────────────┐
          │   Orchestrator  │
          │   (LangGraph)   │
          └─────────┬───────┘
                    │
          ┌─────────────────┐
          │   Web Interface │
          │ (React + FastAPI)│
          └─────────────────┘
```

## 📁 Project Structure

```
├── agents/                    # Persona agents and orchestration
│   ├── persona_agents.py      # Individual agent implementations
│   ├── persona_prompts.py     # Persona-specific prompts
│   └── multi_agent_orchestrator.py  # Multi-agent coordination
├── tests/                     # Test suite
│   ├── test_phase1.py         # Individual agent tests
│   └── test_phase2.py         # Multi-agent tests
├── evaluation/                # Evaluation and monitoring
│   ├── evaluation_pipeline.py # RAGAS-based evaluation
│   ├── langsmith_tracing.py   # LangSmith integration
│   ├── run_evaluation.py      # Interactive evaluation runner
│   ├── demo_evaluation.py     # Simple evaluation demo
│   └── demo_evaluation_results/ # Sample evaluation results
├── web-interface/             # Web application
│   ├── frontend/              # React frontend
│   ├── api_server.py          # FastAPI backend
│   └── start_backend.py       # Backend startup script
├── knowledge-base/            # Knowledge base management
│   └── preprocess/            # Knowledge base building tools
├── scripts/                   # Utility scripts
│   └── main.py               # Main entry point
├── config/                    # Configuration files
└── docs/                     # Documentation
```

## 🚀 Quick Start

### Prerequisites

1. **Python 3.12+**
2. **Qdrant Vector Database** running on `localhost:6333`
3. **Google API Key** for Gemini 2.0 Flash

### Installation

```bash
# Clone and navigate to project
cd mimicking-mindsets

# Install dependencies using uv (faster)
pip install uv
uv pip install -r requirements.txt

# Set up environment variables
export GOOGLE_API_KEY="your-gemini-api-key"
```

### Build Knowledge Base

```bash
# Build persona knowledge bases
uv run python knowledge-base/preprocess/build_kb.py
```

### Run the System

#### Option 1: Web Interface

```bash
# Start backend server
uv run python web-interface/start_backend.py

# In another terminal, start frontend
cd web-interface/frontend
npm install
npm run dev
```

Access the application at `http://localhost:5173`

#### Option 2: Direct Python Usage

```python
from agents.multi_agent_orchestrator import run_multi_agent_query

# Ask a question
result = run_multi_agent_query("Türk kültürel kimliği hakkında ne düşünüyorsunuz?")
print(result["synthesized_answer"])
```

## 🧪 Testing & Evaluation

### Run Agent Tests

```bash
# Test individual agents (Phase 1)
uv run python tests/test_phase1.py

# Test multi-agent orchestration (Phase 2)
uv run python tests/test_phase2.py

# Or run all tests using pytest (if installed)
pytest tests/
```

### Comprehensive Evaluation

```bash
# Interactive evaluation menu
uv run python evaluation/run_evaluation.py

# Quick demo evaluation
uv run python evaluation/demo_evaluation.py
```

The evaluation system uses:
- **RAGAS metrics**: Faithfulness, relevancy, context precision/recall
- **LangChain evaluators**: Coherence and reasoning integrity
- **Comprehensive reporting**: JSON, CSV, and console outputs

## 📊 Evaluation Metrics

| Metric | Purpose | Score Range |
|--------|---------|-------------|
| **Faithfulness** | Groundedness in source texts | 0-1 |
| **Answer Relevancy** | Relevance to user query | 0-1 |
| **Context Precision** | Quality of retrieved context | 0-1 |
| **Context Recall** | Completeness of context | 0-1 |
| **Coherence** | Logical consistency | 0-1 |

## 🔧 Configuration

### Environment Variables

```bash
# Required
export GOOGLE_API_KEY="your-gemini-api-key"

# Optional
export QDRANT_HOST="localhost"
export QDRANT_PORT="6333"
export LANGSMITH_API_KEY="your-langsmith-key"  # For tracing
```

### Persona Configuration

The system supports configurable personas through `agents/persona_prompts.py`:

```python
PERSONAS = {
    "erol_gungor": {
        "name": "Erol Güngör",
        "collection": "erol_gungor_kb",
        "description": "Turkish sociologist and psychologist..."
    },
    "cemil_meric": {
        "name": "Cemil Meriç",
        "collection": "cemil_meric_kb",
        "description": "Turkish intellectual and translator..."
    }
}
```

## 🛠️ Advanced Features

### Multi-Agent Orchestration

The system uses LangGraph for sophisticated multi-agent coordination:

```python
# Parallel agent execution
START → erol_agent ──┐
     → cemil_agent ──┴→ synthesis → memory → END
```

### RAG Integration

- **Embedding Model**: BAAI/bge-m3 for multilingual support
- **Vector Database**: Qdrant for efficient similarity search
- **Knowledge Sources**: Persona-specific document collections

### Web Search Integration

- **Search Engine**: DuckDuckGo for current information
- **Fallback Logic**: Internal knowledge → Web search if needed
- **Source Integration**: Natural blending of historical and current knowledge

## 🔍 Troubleshooting

### Common Issues

1. **Qdrant Connection Error**
   ```bash
   # Start Qdrant
   docker run -p 6333:6333 qdrant/qdrant
   ```

2. **Missing Knowledge Base**
   ```bash
   uv run python knowledge-base/preprocess/build_kb.py
   ```

3. **API Key Error**
   ```bash
   export GOOGLE_API_KEY="your-api-key"
   ```

4. **Frontend Issues**
   ```bash
   cd web-interface/frontend
   npm install
   npm run dev
   ```

## 📈 Performance

- **Parallel Processing**: Agents run simultaneously for faster responses
- **Connection Pooling**: Optimized Qdrant connections
- **Caching**: Intelligent caching for repeated queries
- **Streaming**: Real-time response streaming in web interface

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Run the evaluation pipeline
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **Erol Güngör** and **Cemil Meriç** for their invaluable intellectual contributions
- **LangChain/LangGraph** for the multi-agent framework
- **RAGAS** for evaluation metrics
- **Qdrant** for vector database capabilities

---

*Built with ❤️ to preserve and share Turkish intellectual heritage*
