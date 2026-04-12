# System Architecture

Technical architecture of the RepoMind: GitHub Repository Intelligence System.

## Overview

3-tier architecture with frontend, backend, and data layers for analyzing GitHub repositories through AI-powered semantic search and agentic reasoning.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           CLIENT LAYER                                  │
│                                                                          │
│              ┌────────────────────────────────┐                         │
│              │   JavaScript Frontend          │                         │
│              │   HTML + CSS + Vanilla JS      │                         │
│              │   (Obsidian-style UI)          │                         │
│              └────────────────────────────────┘                         │
│                            │                                             │
│                    HTTP/SSE (REST API)                                   │
│                            │                                             │
└──────────────────────────────┼───────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           SERVER LAYER                                  │
│                                                                          │
│    ┌──────────────────────────────────────────────────────────────┐    │
│    │              FastAPI Backend                                  │    │
│    │              Python 3.10+                                     │    │
│    │                                                               │    │
│    │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐ │    │
│    │  │ Repository      │  │ Parser         │  │ Embedder       │ │    │
│    │  │ Cloner          │  │                │  │                │ │    │
│    │  │ (GitPython)     │  │ Multi-language │  │ Semantic       │ │    │
│    │  │                 │  │ Code Parser    │  │ Embeddings     │ │    │
│    │  └────────────────┘  └────────────────┘  └────────────────┘ │    │
│    │                                                               │    │
│    │           ┌──────────────────────────────┐                   │    │
│    │           │ Agent (ReAct-style)          │                   │    │
│    │           │ Multi-step Reasoning         │                   │    │
│    │           │ LangChain Integration        │                   │    │
│    │           └──────────────────────────────┘                   │    │
│    │                                                               │    │
│    └──────────────────────────────────────────────────────────────┘    │
│                  │                              │                       │
│              Query API                     Streaming (SSE)              │
│                                                                          │
└──────────────────┼──────────────────────────────┼────────────────────────┘
                   │                              │
                   ▼                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           DATA LAYER                                    │
│                                                                          │
│  ┌──────────────────────┐    ┌──────────────────────┐                  │
│  │      ChromaDB        │    │   Ollama LLM         │                  │
│  │                      │    │                      │                  │
│  │ Vector Database      │    │ Local LLM Inference  │                  │
│  │ Semantic Search      │    │ Privacy-respecting   │                  │
│  │ (Embeddings Store)   │    │ Multi-model Support  │                  │
│  └──────────────────────┘    └──────────────────────┘                  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## Components

### Client Layer
- **JavaScript Frontend**: Vanilla JavaScript with HTML/CSS
- **UI Pattern**: Obsidian-style interface for repository exploration
- **Communication**: HTTP/REST API + Server-Sent Events (SSE) for real-time streaming

### Server Layer
The FastAPI backend orchestrates the core functionality:

- **Repository Cloner**: 
  - GitPython integration for cloning public GitHub repositories
  - Handles repository download and storage
  
- **Parser**: 
  - Multi-language code parser supporting Python, JavaScript, TypeScript, Java, Go, Rust, and more
  - Extracts code structure and documentation
  
- **Embedder**: 
  - Generates semantic embeddings using Sentence Transformers
  - Stores embeddings in ChromaDB for vector-based retrieval
  
- **Agent**: 
  - ReAct-style agentic reasoning with LangChain
  - Multi-step problem solving for complex queries
  - Semantic code search capabilities

### Data Layer

- **ChromaDB**: 
  - Vector database for storing code embeddings
  - Enables semantic search across repository codebase
  - Persistent collection-based storage
  
- **Ollama LLM**: 
  - Local language model inference
  - Privacy-respecting (no external API calls)
  - Multi-model support for flexible AI reasoning

## Data Flow

1. **Indexing Flow**:
   - User provides GitHub repository URL → Cloner fetches repository
   - Parser extracts all files and their content
   - Embedder generates semantic vectors via Sentence Transformers
   - Vectors stored in ChromaDB with metadata

2. **Query Flow**:
   - User asks natural language question → Frontend sends via HTTP
   - Agent receives query → Performs semantic search in ChromaDB
   - Retrieved context → Sent to Ollama LLM for reasoning
   - Response streamed back via SSE for real-time updates
   - Frontend displays results incrementally

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | JavaScript, HTML, CSS | User interface |
| Backend | FastAPI, Python 3.10+ | REST API, business logic |
| LLM | Ollama | Local inference engine |
| Vector DB | ChromaDB | Semantic search storage |
| Libraries | LangChain, Sentence-Transformers, GitPython, SSE-Starlette | Core functionality |

## Key Features

✅ Real-time SSE streaming for responsive UX  
✅ Semantic code search with embeddings  
✅ Local LLM inference (privacy-respecting)  
✅ Multi-language repository support  
✅ Persistent collection-based storage  
✅ Agentic reasoning with ReAct patterns  

---

*Generated for RepoMind: GitHub Repository Intelligence System*
