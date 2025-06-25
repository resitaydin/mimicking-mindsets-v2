# Mimicking Mindsets

A high-performance multi-agent AI system that simulates Turkish intellectuals **Erol Güngör** and **Cemil Meriç** using advanced RAG (Retrieval-Augmented Generation), web search integration, and GPU-accelerated inference.

## 🎯 Overview

This project creates authentic AI personas of two prominent Turkish intellectuals who can engage in meaningful conversations about culture, philosophy, and society. The system combines their historical knowledge with current information through web search, providing thoughtful responses that reflect their unique perspectives.

### Key Features

- **🤖 Dual Persona Agents**: Erol Güngör (sociologist/psychologist) and Cemil Meriç (intellectual/translator)
- **🔍 RAG Integration**: Persona-specific knowledge bases built from their works
- **🌐 Web Search**: DuckDuckGo integration for current information
- **⚡ GPU Acceleration**: CUDA-enabled PyTorch for fast inference
- **🔀 Multi-Agent Orchestration**: Parallel processing with LangGraph
- **📊 Comprehensive Evaluation**: RAGAS-based metrics with LangSmith tracing
- **🖥️ Modern Web Interface**: React frontend with FastAPI backend
- **🐳 Docker Support**: Full containerization with GPU support

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
├── evaluation/                # RAGAS evaluation and LangSmith tracing
├── knowledge-base/            # Knowledge base building tools
├── web-interface/             # React frontend + FastAPI backend
├── tests/                     # Comprehensive test suite
├── utils/                     # Logging and utilities
├── docs/                      # Technical documentation
├── docker-compose.yml         # Multi-service Docker setup
└── pyproject.toml            # Modern Python project configuration
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.12+**
- **NVIDIA GPU** (optional but recommended for performance)
- **Docker & Docker Compose** (for containerized deployment)
- **Google API Key** for Gemini 2.0 Flash

### Installation

#### Option 1: Local Development (Recommended)

```bash
# Clone repository
git clone <repository-url>
cd mimicking-mindsets

# Install uv (fast Python package manager)
pip install uv

# Install dependencies with GPU support
uv sync
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 --reinstall

# Set environment variables
export GOOGLE_API_KEY="your-gemini-api-key"
export QDRANT_HOST="localhost"
export QDRANT_PORT="6333"
```

#### Option 2: Docker Deployment

```bash
# Create external network
docker network create mimicking-mindsets-network

# Set environment variables
export GOOGLE_API_KEY="your-gemini-api-key"

# Development mode
docker-compose --profile development up

# Production mode
docker-compose --profile production up
```

### Setup

```bash
# Start Qdrant vector database
docker run -d -p 6333:6333 qdrant/qdrant

# Build knowledge bases
uv run python knowledge-base/preprocess/build_kb.py

# Or with Docker
docker-compose --profile setup up kb-builder
```

## 🧪 Testing & Evaluation

### Run Tests

```bash
# Individual agent tests
uv run python tests/test_phase1.py

# Multi-agent orchestration tests  
uv run python tests/test_phase2.py

# All tests
pytest tests/
```

### Evaluation Pipeline

```bash
# Interactive evaluation
uv run python evaluation/run_evaluation.py

# Docker evaluation
docker-compose --profile evaluation up evaluator
```

### Metrics

| Metric | Purpose | Range |
|--------|---------|-------|
| **Faithfulness** | Groundedness in sources | 0-1 |
| **Answer Relevancy** | Query relevance | 0-1 |
| **Coherence** | Response consistency | 0-1 |

## ⚙️ Configuration

### Environment Variables

```bash
# Required
GOOGLE_API_KEY="your-gemini-api-key"

# Optional
QDRANT_HOST="localhost"          # Qdrant host
QDRANT_PORT="6333"              # Qdrant port
LANGSMITH_API_KEY="your-key"    # LangSmith tracing
HF_HOME="./hf_cache"            # Hugging Face cache
```

### GPU Support

The system automatically detects and uses NVIDIA GPUs when available:

- **Embedding Model**: BAAI/bge-m3 with CUDA acceleration
- **Docker**: GPU support configured in docker-compose.yml
- **Fallback**: Graceful CPU fallback if GPU unavailable

### Performance Optimizations

- **Optimized Logging**: Minimal overhead with WARNING-level default
- **Connection Pooling**: Efficient Qdrant connections
- **Parallel Processing**: Concurrent agent execution
- **Caching**: Intelligent response and embedding caching

## 🐳 Docker Deployment

### Development

```bash
docker-compose --profile development up
```

Includes:
- Hot reloading
- Volume mounts for code changes
- Development-friendly logging

### Production

```bash
docker-compose --profile production up
```

Features:
- Optimized builds
- Health checks
- Automatic restarts
- GPU acceleration

### Services

- **backend**: FastAPI server with GPU support
- **frontend**: React app with Nginx
- **kb-builder**: Knowledge base construction
- **evaluator**: Evaluation pipeline runner

## 🔧 Advanced Features

### Multi-Agent Orchestration

```python
# Parallel execution flow
START → erol_agent ──┐
     → cemil_agent ──┴→ synthesis → memory → END
```

### RAG Pipeline

- **Embedding**: BAAI/bge-m3 multilingual model
- **Vector DB**: Qdrant with optimized indexing
- **Retrieval**: Hybrid search with reranking
- **Generation**: Gemini 2.0 Flash with persona prompts

### Web Search Integration

- **Engine**: DuckDuckGo Search API
- **Strategy**: Knowledge base first, web search as fallback
- **Integration**: Seamless blending of historical and current knowledge

**Knowledge Base Missing**
```bash
# Rebuild knowledge base
uv run python knowledge-base/preprocess/build_kb.py
```

## 📈 Performance

- **GPU Acceleration**: 3-5x faster inference with CUDA
- **Parallel Agents**: Simultaneous processing reduces latency
- **Optimized Logging**: Minimal performance overhead
- **Connection Pooling**: Efficient database connections
- **Smart Caching**: Reduces redundant computations

## 📄 License

MIT License

## Acknowledgments

- **Erol Güngör** and **Cemil Meriç** for their intellectual legacy
- **LangChain/LangGraph** for multi-agent frameworks
- **RAGAS** for evaluation metrics
- **Qdrant** for vector database capabilities
- **Google** for Gemini API access

---

*Preserving Turkish intellectual heritage through AI* 🇹🇷
- **R.A. 25/06/2025 GTU**