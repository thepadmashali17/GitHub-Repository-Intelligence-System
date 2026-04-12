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

## API Endpoints

### Repository Management

#### Index a Repository
```http
POST /index
Content-Type: application/json

{
  "url": "https://github.com/user/repo"
}
```

**Response**: Server-Sent Events (SSE) stream with indexing progress

#### List Collections
```http
GET /collections
```

Returns all indexed repositories

#### Delete a Repository
```http
DELETE /collections/{collection_name}
```

Removes a repository from the database

### Query & Analysis

#### Query Repository
```http
POST /query
Content-Type: application/json

{
  "repo_name": "repo-name",
  "query": "How does the authentication system work?"
}
```

**Response**: Server-Sent Events (SSE) stream with agentic response

#### Get Repository Tree
```http
GET /repo-tree/{repo_name}
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

## Key Components

### 1. **Cloner** (`cloner.py`)
- Clones GitHub repositories using GitPython
- Discovers and categorizes files (code, documentation, config)
- Respects file size limits (MAX_FILE_SIZE_KB = 500)
- Skips unnecessary directories (node_modules, .git, etc.)

### 2. **Parser** (`parser.py`)
- Language-aware code splitting using LangChain
- Markdown-aware documentation splitting
- Configurable chunk sizes for different file types:
  - Code: 1500 chars with 200 overlap
  - Documentation: 1000 chars with 150 overlap
  - Config: 800 chars with 100 overlap
- Preserves code structure and semantics

### 3. **Embedder** (`embedder.py`)
- Uses `sentence-transformers` (all-MiniLM-L6-v2)
- ChromaDB for persistent vector storage
- Batch embedding processing (64 items/batch)
- Multi-type retrieval (code, documentation, config)

### 4. **Agent** (`agent.py`)
- ReAct-style agentic loop with manual reasoning
- Tools:
  - `search_documentation()` - Find relevant documentation
  - `search_code()` - Find relevant code snippets
  - `get_repo_file_tree()` - Understand repository structure
- LLM: Ollama with configurable models
- Streaming responses via SSE

### 5. **Frontend** (`app.js`)
- SSE integration for real-time updates
- Repository management (add, select, delete)
- Chat interface for Q&A
- Markdown rendering with Marked.js
- Obsidian-inspired UI styling

## Configuration

Edit `backend/config.py` to customize:

```python
# LLM Configuration
OLLAMA_MODEL = "qwen3:8b"              # Model name
OLLAMA_BASE_URL = "http://localhost:11434"

# Embedding Configuration
EMBEDDING_MODEL = "all-MiniLM-L6-v2"   # Sentence transformer model
EMBEDDING_BATCH_SIZE = 64

# Chunk Sizes
CODE_CHUNK_SIZE = 1500
CODE_CHUNK_OVERLAP = 200
DOC_CHUNK_SIZE = 1000
DOC_CHUNK_OVERLAP = 150

# File Type Configurations
RETRIEVER_TOP_K = 5                    # Number of results to retrieve
MAX_FILE_SIZE_KB = 500                 # Max file size to process
```

### Supported Languages

Code analysis supports:
- Python, JavaScript, TypeScript
- Java, C/C++, Go, Rust, Ruby
- And many more (configurable in `CODE_EXTENSIONS`)

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

## Workflow

1. **Index Repository**: Provide GitHub URL → System clones and embeds
2. **Wait for Completion**: Monitor indexing progress via SSE
3. **Query Repository**: Ask questions about the codebase
4. **Receive Insights**: Get AI-powered answers with code references
5. **Explore Further**: Navigate file structure and documents

## Development

### Running Tests

```bash
cd backend
pytest tests/
```

### Code Formatting

```bash
black . --line-length=90
isort .
```

### Debugging

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Dependencies

### Backend
- **FastAPI**: Modern Python web framework
- **LangChain**: Framework for LLM applications
- **ChromaDB**: Vector database
- **sentence-transformers**: Embedding model
- **Ollama**: Local LLM inference
- **GitPython**: Git operations
- **SSE-Starlette**: Server-Sent Events

### Frontend
- **Marked.js**: Markdown parser & renderer
- **Fetch API**: Modern HTTP client
- **Vanilla JavaScript**: No frameworks needed



---

**Built with ❤️ for developers who want to understand code faster**
