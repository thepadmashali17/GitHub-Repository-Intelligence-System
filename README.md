# RepoMind: GitHub Repository Intelligence System

An AI-powered system that analyzes GitHub repositories through natural language queries, combining semantic search, embeddings, and agentic reasoning to provide intelligent insights into any codebase.

## Features

- **Repository Cloning & Analysis**: Clone any public GitHub repository and instantly analyze its structure
- **Multi-language Support**: Intelligent parsing of Python, JavaScript, TypeScript, Java, Go, Rust, and more
- **Semantic Code Search**: Vector-based embeddings for accurate code and documentation retrieval
- **Agentic Q&A**: Multi-step reasoning with ReAct-style loops for complex questions
- **Real-time Streaming**: SSE-based streaming responses for responsive user experience
- **Obsidian-style Interface**: Modern, clean UI for repository exploration
- **Persistent Vector Database**: ChromaDB for storing and retrieving embeddings
- **LLM Integration**: Powered by Ollama for local, privacy-respecting inference

## Prerequisites

- **Python 3.10+**
- **Node.js** (for frontend development)
- **Ollama** (for local LLM inference) - [Download](https://ollama.ai)
- **Git** (for cloning repositories)

## Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/thepadmashali17/GitHub-Repository-Intelligence-System-RepoMind-.git
cd "GitHub Repository Intelligence System (RepoMind)"
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Ollama

Make sure Ollama is running:

```bash
ollama serve
```

In a separate terminal, pull the default model:

```bash
ollama pull qwen3:8b
```

Or specify a different model by setting the environment variable:

```bash
set OLLAMA_MODEL=mistral  # Windows
export OLLAMA_MODEL=mistral  # macOS/Linux
```

### 4. Start the Backend API

```bash
cd backend
python main.py
```

The API will be available at `http://localhost:8000`

### 5. Open Frontend

Navigate to `http://localhost:8000` in your browser (frontend is served by FastAPI)

## Project Structure

```
RepoMind/
├── backend/
│   ├── main.py              # FastAPI application & REST API
│   ├── cloner.py            # Repository cloning & file discovery
│   ├── parser.py            # Language-aware code & doc parsing
│   ├── embedder.py          # Embedding generation & vector storage
│   ├── agent.py             # Agentic RAG with ReAct loops
│   ├── config.py            # Configuration & constants
│   ├── requirements.txt      # Python dependencies
│   └── agent_api.txt        # API endpoint documentation
├── frontend/
│   ├── index.html           # Main HTML structure
│   ├── app.js               # Application logic & SSE handler
│   ├── style.css            # Styling & Obsidian-style theming
│   └── assets/              # Icons, fonts, etc.
├── repos/                   # Cloned repositories storage
├── chroma_db/               # ChromaDB vector storage
└── README.md               # This file
```

Returns the file structure of a repository

## Architecture

### Data Pipeline

```
GitHub Repo
    ↓
[Cloner] → Clone & discover files
    ↓
[Parser] → Language-aware chunks
    ↓
[Embedder] → Generate embeddings
    ↓
[ChromaDB] → Persistent storage
    ↓
[Agent] ← Query with semantic search
```

### Query Flow

```
User Query
    ↓
[Frontend] → SSE Request
    ↓
[Agent] → Multi-step reasoning
    ├─→ Search Documentation
    ├─→ Search Code
    ├─→ Get File Tree
    └─→ Generate Answer (Ollama)
    ↓
[SSE Stream] → Real-time response
    ↓
Browser Display
```


## Usage Examples

### Example 1: Analyze Authentication Flow
```
Query: "Explain how user authentication works in this repository"
→ Agent searches code for auth-related files
→ Retrieves relevant code snippets
→ Queries documentation for auth details
→ Generates comprehensive explanation
```

### Example 2: Find API Endpoints
```
Query: "What API endpoints are available?"
→ Agent searches for route definitions
→ Retrieves endpoint documentation
→ Summarizes all available endpoints with methods
```

### Example 3: Understand Dependencies
```
Query: "What external libraries does this project use?"
→ Agent searches config files (requirements.txt, package.json, etc.)
→ Retrieves dependency lists
→ Explains purpose of major dependencies
```


