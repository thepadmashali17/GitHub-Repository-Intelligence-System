# System Architecture

Technical architecture of the RepoMind: GitHub Repository Intelligence System.

---

## Overview

3-tier architecture with frontend, backend, and data layers for analyzing GitHub repositories through AI-powered semantic search and agentic reasoning.

```mermaid
graph TB
    subgraph Client["Client Layer"]
        UI["JavaScript Frontend<br/>HTML + CSS + Vanilla JS<br/>(Obsidian-style UI)"]
    end
    
    subgraph Server["Server Layer"]
        API["FastAPI Backend<br/>Python 3.10+"]
        Cloner["Repository Cloner<br/>GitPython"]
        Parser["Code Parser<br/>Multi-language"]
        Embedder["Embedder<br/>Sentence Transformers"]
        Agent["Agent<br/>LangChain ReAct"]
    end
    
    subgraph Data["Data Layer"]
        ChromaDB["ChromaDB<br/>Vector Database"]
        Ollama["Ollama LLM<br/>Local Inference"]
    end
    
    UI -->|HTTP/REST| API
    UI -->|SSE Streaming| Agent
    API --> Cloner
    API --> Parser
    API --> Embedder
    API --> Agent
    Cloner --> Parser
    Parser --> Embedder
    Embedder --> ChromaDB
    Agent --> ChromaDB
    Agent --> Ollama
    Ollama -->|Response| Agent
```

---

## Component Architecture

### Frontend Components

```mermaid
graph TD
    App["index.html<br/>Main App"]
    
    App --> Upload["Upload Page"]
    App --> Query["Query Interface"]
    App --> History["History View"]
    
    Upload --> Form["Repository Form"]
    Upload --> Status["Indexing Status"]
    Upload --> Progress["Progress Bar"]
    
    Query --> Search["Search Input"]
    Query --> Results["Results Display"]
    Query --> Streaming["Real-time Streaming"]
    
    History --> Collections["Collections List"]
    History --> Metadata["Repository Metadata"]
```

### Backend Structure

```mermaid
graph TD
    Main["main.py<br/>FastAPI App"]
    
    Main --> Routes["Routes/"]
    Main --> Services["Services/"]
    Main --> Utils["Utils/"]
    
    Routes --> Index["index.py<br/>/api/index"]
    Routes --> Query["query.py<br/>/api/query"]
    Routes --> Collections["collections.py<br/>/api/collections"]
    
    Services --> Cloner["cloner.py<br/>Repository Cloning"]
    Services --> Parser["parser.py<br/>Code Parsing"]
    Services --> Embedder["embedder.py<br/>Embeddings"]
    Services --> Agent["agent.py<br/>Query Agent"]
    
    Utils --> Config["config.py<br/>Configuration"]
    Utils --> Logger["logging.py<br/>Logger Setup"]
```

---

## Data Flow

### Indexing Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant Cloner
    participant Parser
    participant Embedder
    participant ChromaDB
    
    User->>Frontend: Submit Repository URL
    Frontend->>Backend: POST /api/index
    Backend->>Cloner: Clone Repository
    Cloner->>Cloner: Download from GitHub
    Cloner-->>Backend: Repository Files
    Backend->>Parser: Parse All Files
    Parser->>Parser: Extract Code Content
    Parser-->>Backend: Parsed Content
    Backend->>Embedder: Generate Embeddings
    Embedder->>Embedder: Compute Vectors
    Embedder-->>Backend: Vector Embeddings
    Backend->>ChromaDB: Store Collection
    ChromaDB-->>Backend: Collection Created
    Backend-->>Frontend: Indexing Complete
    Frontend->>User: Ready for Queries
```

### Query Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant Agent
    participant ChromaDB
    participant Ollama
    
    User->>Frontend: Ask Natural Language Question
    Frontend->>Backend: POST /api/query (SSE Stream)
    Backend->>Agent: Process Query
    Agent->>ChromaDB: Semantic Search
    ChromaDB-->>Agent: Relevant Code Snippets
    Agent->>Agent: Extract Context
    Agent->>Ollama: Send with LLM Prompt
    Ollama->>Ollama: Generate Response
    Ollama-->>Agent: Streamed Tokens
    Agent-->>Frontend: SSE Stream Response
    Frontend->>User: Display Real-time Results
```

---

## Technology Stack

- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Backend**: FastAPI, Python 3.10+, Uvicorn
- **LLM & Embeddings**: LangChain, Ollama, Sentence-Transformers
- **Vector Database**: ChromaDB, Persistent Collections
- **Repository Tools**: GitPython, Multi-language Parser
- **Streaming**: SSE-Starlette, Real-time Updates
- **DevOps**: Docker, Docker Compose

---

## API Endpoints

```mermaid
graph LR
    A["Client"] 
    
    A -->|POST /api/index| B["Index Repository"]
    A -->|POST /api/query| C["Query with SSE Stream"]
    A -->|GET /api/collections| D["List Collections"]
    A -->|DELETE /api/collections| E["Delete Collection"]
    A -->|GET /api/health| F["Health Check"]
    
    B --> G["ChromaDB"]
    C --> G
    D --> G
```

---

## Repository Indexing Pipeline

```mermaid
graph LR
    A["Repository URL"] 
    
    A -->|Git Clone| B["Downloaded"]
    B -->|Parse| C["Content Extracted"]
    C -->|Tokenize| D["Text Segmented"]
    D -->|Embed| E["Vectors Created"]
    E -->|Store| F["ChromaDB Collection"]
    F --> G["Ready for Queries"]
    
    style A fill:#fbb040,stroke:#f6ad55,color:#000
    style B fill:#ed64a6,stroke:#d69e2e,color:#fff
    style C fill:#b794f6,stroke:#9f7aea,color:#fff
    style D fill:#667eea,stroke:#5568d3,color:#fff
    style E fill:#48bb78,stroke:#38a169,color:#fff
    style F fill:#38b2ac,stroke:#319795,color:#fff
    style G fill:#2b6cb0,stroke:#2c5aa0,color:#fff
```

---

## Agent Reasoning Loop

```mermaid
graph TD
    A["User Query"] -->|1. Parse| B["Extract Intent"]
    B -->|2. Search| C["Semantic Search in ChromaDB"]
    C -->|3. Retrieve| D["Get Code Context"]
    D -->|4. Reason| E["Send to Ollama LLM"]
    E -->|5. Generate| F["Process Response"]
    F -->|6. Evaluate| G{"Complete<br/>Answer?"}
    G -->|No| H["Refine Search"]
    H -->|Re-search| C
    G -->|Yes| I["Stream to Frontend"]
    I -->|7. Display| J["User Views Response"]
    
    style A fill:#fbb040,stroke:#f6ad55,color:#000
    style B fill:#4299e1,stroke:#2b6cb0,color:#fff
    style C fill:#48bb78,stroke:#38a169,color:#fff
    style D fill:#48bb78,stroke:#38a169,color:#fff
    style E fill:#667eea,stroke:#5568d3,color:#fff
    style F fill:#667eea,stroke:#5568d3,color:#fff
    style G fill:#ed64a6,stroke:#d69e2e,color:#fff
    style H fill:#4299e1,stroke:#2b6cb0,color:#fff
    style I fill:#38b2ac,stroke:#319795,color:#fff
    style J fill:#667eea,stroke:#5568d3,color:#fff
```

---

## Data Model

### ChromaDB Collection Structure

```mermaid
erDiagram
    COLLECTION ||--o{ DOCUMENT : contains
    DOCUMENT ||--o{ EMBEDDING : has
    DOCUMENT ||--o{ METADATA : has
    
    COLLECTION {
        string id "Repository name"
        string name "Collection identifier"
        timestamp created_at
    }
    
    DOCUMENT {
        string id "Unique document ID"
        string content "File content"
        string source_file "Repository path"
        int line_start
        int line_end
    }
    
    EMBEDDING {
        vector embedding "384-dimension vector"
        float similarity "For search results"
    }
    
    METADATA {
        string language "Programming language"
        string file_type "Extension"
        string directory "Folder path"
        int token_count "Content length"
    }
```

---

## Deployment Architecture

```mermaid
graph TB
    subgraph Local["Local Development Environment"]
        Frontend["Frontend<br/>Port 5500<br/>HTTP Server"]
        Backend["Backend<br/>Port 8000<br/>FastAPI + Uvicorn"]
        ChromaDB_Local["ChromaDB<br/>Persistent Storage"]
        Ollama_Local["Ollama<br/>Port 11434<br/>LLM Service"]
    end
    
    User["Developer"] -->|localhost:5500| Frontend
    Frontend -->|HTTP/SSE| Backend
    Backend --> ChromaDB_Local
    Backend --> Ollama_Local
    
    Git["GitHub"] -.->|Clone| Backend
```

---

## Supported Languages

✅ Python  
✅ JavaScript / TypeScript  
✅ Java  
✅ Go  
✅ Rust  
✅ C/C++  
✅ C#  
✅ Ruby  
✅ PHP  
✅ And more...

---

## Key Features

🔍 **Semantic Code Search** - Vector embeddings for intelligent retrieval  
🤖 **Agentic Reasoning** - Multi-step problem solving with ReAct patterns  
⚡ **Real-time Streaming** - SSE for responsive user experience  
🔐 **Privacy-First** - Local LLM inference, no external API calls  
📚 **Multi-language Support** - Intelligent parsing across programming languages  
🎯 **Persistent Collections** - Collections stored and retrieved from ChromaDB  

---

*RepoMind: AI-Powered GitHub Repository Intelligence System*
*Combines semantic search, embeddings, and agentic reasoning for intelligent codebase analysis*
