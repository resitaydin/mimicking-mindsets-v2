# Mimicking Mindsets: A Multi-Agent AI System for Simulating Intellectual Personas

A high-performance multi-agent AI system that simulates conversations with Turkish intellectuals **Erol Güngör** and **Cemil Meriç**. The system leverages a sophisticated Retrieval-Augmented Generation (RAG) pipeline, real-time web search, and GPU-accelerated inference to create authentic, interactive AI personas.

## Project Overview

This project aims to bridge the gap between historical intellectual heritage and contemporary dialogue. By creating dynamic AI personas of Erol Güngör and Cemil Meriç, users can explore complex ideas on culture, philosophy, and society in an interactive format. The system moves beyond static text by combining a deep knowledge base, derived from the complete works of both thinkers, with the ability to access current information via web search. This dual capability allows the agents to provide thoughtful, nuanced responses that are grounded in their original perspectives yet relevant to modern-day issues.

The core of the system is a multi-agent architecture where each intellectual is represented by a distinct AI agent. These agents process queries in parallel and collaborate to produce a synthesized, dialogical answer, simulating a rich intellectual exchange.

## 🏗System Architecture

The system is designed as a modular, multi-agent pipeline that ensures efficient and high-quality response generation.

```
┌─────────────────┐      ┌─────────────────┐
│   Erol Güngör   │      │   Cemil Meriç   │
│   Agent (RAG)   │      │   Agent (RAG)   │
└─────────┬───────┘      └─────────┬───────┘
          │                        │
          ├──────────┬─────────────┤
                     │
          ┌─────────────────┐
          │  Orchestrator   │
          │  (LangGraph)    │
          └─────────┬───────┘
                    │
          ┌─────────────────┐
          │    Synthesizer  │
          │ (Gemini 2.0 Flash)│
          └─────────┬───────┘
                    │
          ┌─────────────────┐
          │ Web Interface   │
          │(React + FastAPI)│
          └─────────────────┘
```
**Data Flow:**
1.  A user query is submitted through the **React** frontend.
2.  The **FastAPI** backend receives the request and passes it to the **LangGraph Orchestrator**.
3.  The orchestrator dispatches the query to both the **Erol Güngör** and **Cemil Meriç** agents to be processed **in parallel**.
4.  Each agent uses its dedicated knowledge base and web search tools to formulate a perspective.
5.  The individual responses are sent to a final **Synthesizer** LLM, which combines them into a single, coherent, and conversational answer.
6.  The final response is streamed back to the user interface.

## 🔬 Methodology & Implementation

The project was developed in two main phases: building the knowledge foundation and implementing the intelligent agent system.

### 1. The Knowledge Foundation (Persona-Specific RAG)

Creating authentic personas required building a deep, structured knowledge base for each intellectual.

-   **Data Collection & Preprocessing**: The complete works of Erol Güngör and Cemil Meriç were digitized, cleaned, and normalized to create a high-quality text corpus.
-   **Text Chunking**: The corpus was divided into smaller, semantically meaningful chunks with overlap to ensure contextual integrity during retrieval.
-   **Vector Embeddings**: Each text chunk was converted into a numerical vector using the powerful, multilingual **BAAI/bge-m3** embedding model, running with CUDA acceleration.
-   **Vector Database**: These embeddings are stored in two separate **Qdrant** collections, one for each persona. This separation allows for highly targeted and efficient semantic searches.

### 2. The Multi-Agent System

The core logic is handled by a sophisticated multi-agent system designed for collaboration and intelligent decision-making.

-   **Multi-Agent Orchestration**: **LangGraph** is used to define and execute the conversational flow. It enables parallel processing of queries by both agents, drastically reducing latency and facilitating a final synthesis step.
-   **Intelligent Tool Use**: Each agent operates using the **ReAct (Reason and Act)** framework. This allows an agent to autonomously decide which tool to use:
    -   **Search Internal Knowledge Base**: The primary action to find relevant passages from the thinker's works.
    -   **Search the Web**: A fallback action using the **DuckDuckGo Search API** if the internal knowledge is insufficient or if the query requires contemporary information.
    -   **Generate Response**: The final action once sufficient context has been gathered.

## 📊 Evaluation & Results

The system's performance was rigorously evaluated using a combination of quantitative metrics and qualitative expert review.

### Quantitative Metrics (RAGAS Framework)

We established an evaluation pipeline using the **RAGAS** framework to measure the quality of the generated responses. The key metrics, averaged over a diverse set of test queries, are:

| Metric | Description | Average Score |
| :--- | :--- | :--- |
| **Faithfulness** | Measures how factually consistent the answer is with the retrieved context. | **0.88 / 1.0** |
| **Answer Relevancy** | Measures how relevant the answer is to the original query. | **0.70 / 1.0** |
| **Coherence** | Measures the logical flow and readability of the answer. | **1.00 / 1.0** |

These results indicate that the system generates highly coherent responses that are strongly grounded in the source material.

### Qualitative Validation

A collaborating history expert, **Doç. Dr. Yasemin Hoca**, reviewed the system's outputs for persona accuracy and intellectual style. Her feedback confirmed that the system successfully captures the distinct tones, vocabularies, and philosophical stances of both Erol Güngör and Cemil Meriç.

### Monitoring

**LangSmith** was integrated for real-time tracing of every step in the agent and RAG pipelines, which was invaluable for debugging, optimization, and ensuring quality.

## 🛠️ Technical Stack

-   **Backend**: FastAPI, LangChain, LangGraph
-   **Frontend**: React, Nginx
-   **AI/ML**: PyTorch (CUDA), Gemini 2.0 Flash, BAAI/bge-m3
-   **Database**: Qdrant (Vector DB)
-   **Evaluation**: RAGAS, LangSmith
-   **DevOps**: Docker, Docker Compose, `uv`

## 🚀 Running the Project

The simplest way to run the entire application stack is with Docker Compose.

```bash
# Ensure Docker and NVIDIA Container Toolkit are installed
# Set your GOOGLE_API_KEY in a .env file

# Build and run all services in production mode
docker-compose --profile production up
```
*For detailed local setup and development instructions, please refer to the `docs/` directory.*

## 📄 License

This project is licensed under the **MIT License**.

## Acknowledgments

This project is indebted to the intellectual legacies of **Erol Güngör** and **Cemil Meriç**.

Our work was made possible by the incredible open-source community. We gratefully acknowledge the teams behind **LangChain/LangGraph**, **RAGAS**, **Qdrant**, **FastAPI**, and the **Hugging Face** ecosystem. We also thank **Google** for providing access to the Gemini API.

---

*Preserving Turkish intellectual heritage through AI* 🇹🇷
- **R.A. 25/06/2025 GTU**
