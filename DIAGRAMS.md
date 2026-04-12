# RepoMind Architecture & Methodology Diagrams

## System Architecture Diagram

```mermaid
graph TB
    subgraph Client["Client Layer"]
        UI["JavaScript Frontend<br/>HTML + CSS + Vanilla JS<br/>(Obsidian-style UI)"]
    end

    subgraph Server["Server Layer - FastAPI Backend<br/>(Python 3.10+)"]
        Cloner["Repository Cloner<br/>GitPython"]
        Parser["Parser<br/>Multi-language<br/>Code Extraction"]
        Embedder["Embedder<br/>Sentence Transformers<br/>Vector Generation"]
        Agent["Agent<br/>ReAct-style Reasoning<br/>LangChain Integration"]
    end

    subgraph Data["Data Layer"]
        ChromaDB["ChromaDB<br/>Vector Database<br/>Semantic Search Store"]
        Ollama["Ollama LLM<br/>Local Inference<br/>Privacy-respecting"]
    end

    UI -->|HTTP/REST| Server
    UI -->|SSE Streaming| Agent
    
    Cloner --> Parser
    Parser --> Embedder
    Embedder --> ChromaDB
    
    Agent --> ChromaDB
    Agent --> Ollama
    
    Ollama -->|Response| Agent
    Agent -->|Streamed Results| UI
    
    style Client fill:#4a5568,stroke:#2d3748,color:#fff
    style Server fill:#3182ce,stroke:#2c5aa0,color:#fff
    style Data fill:#38a169,stroke:#2f855a,color:#fff
    style UI fill:#667eea,stroke:#5568d3,color:#fff
    style Cloner fill:#4299e1,stroke:#2b6cb0,color:#fff
    style Parser fill:#4299e1,stroke:#2b6cb0,color:#fff
    style Embedder fill:#4299e1,stroke:#2b6cb0,color:#fff
    style Agent fill:#4299e1,stroke:#2b6cb0,color:#fff
    style ChromaDB fill:#48bb78,stroke:#38a169,color:#fff
    style Ollama fill:#48bb78,stroke:#38a169,color:#fff
```

## Repository Analysis Workflow

```mermaid
graph LR
    A["Repository URL"] -->|Git Clone| B["Repository Downloaded"]
    B -->|Parse Files| C["Code Extracted"]
    C -->|Generate Embeddings| D["Vector Embeddings"]
    D -->|Store Vectors| E["ChromaDB Collection"]
    E -->|Ready| F["Indexed Repository"]
    
    style A fill:#fbb040,stroke:#f6ad55,color:#000
    style B fill:#f687b3,stroke:#ed64a6,color:#fff
    style C fill:#b794f6,stroke:#9f7aea,color:#fff
    style D fill:#667eea,stroke:#5568d3,color:#fff
    style E fill:#48bb78,stroke:#38a169,color:#fff
    style F fill:#38b2ac,stroke:#319795,color:#fff
```

## Query Processing Pipeline

```mermaid
graph LR
    A["User Query"] -->|HTTP Request| B["FastAPI Endpoint"]
    B -->|Extract Intent| C["Agent Router"]
    C -->|Semantic Search| D["ChromaDB Search"]
    D -->|Retrieve Context| E["Code Snippets"]
    E -->|Send to LLM| F["Ollama Inference"]
    F -->|Generate Response| G["Agent Reasoning"]
    G -->|Stream Results| H["SSE to Frontend"]
    H -->|Display| I["User Interface"]
    
    style A fill:#fbb040,stroke:#f6ad55,color:#000
    style B fill:#4299e1,stroke:#2b6cb0,color:#fff
    style C fill:#4299e1,stroke:#2b6cb0,color:#fff
    style D fill:#48bb78,stroke:#38a169,color:#fff
    style E fill:#48bb78,stroke:#38a169,color:#fff
    style F fill:#48bb78,stroke:#38a169,color:#fff
    style G fill:#4299e1,stroke:#2b6cb0,color:#fff
    style H fill:#ed64a6,stroke:#d69e2e,color:#fff
    style I fill:#667eea,stroke:#5568d3,color:#fff
```

## Component Interaction Diagram

```mermaid
graph TB
    subgraph Frontend["Frontend (Client)"]
        UI1["User Input"]
        UI2["Results Display"]
    end
    
    subgraph Backend["Backend (FastAPI)"]
        Route["API Routes"]
        Cloner1["Repository Cloner"]
        Parser1["Code Parser"]
        Embedder1["Embedder"]
        Agent1["Query Agent"]
    end
    
    subgraph Services["External Services & Storage"]
        Git["Git Repository"]
        ChromaDB1["ChromaDB"]
        Ollama1["Ollama LLM"]
    end
    
    UI1 -->|Index Request| Route
    UI1 -->|Query Request| Route
    
    Route -->|Trigger| Cloner1
    Route -->|Process| Agent1
    
    Cloner1 -->|Fetch| Git
    Cloner1 -->|Pass Files| Parser1
    Parser1 -->|Pass Content| Embedder1
    Embedder1 -->|Store| ChromaDB1
    
    Agent1 -->|Search| ChromaDB1
    Agent1 -->|Query| Ollama1
    Ollama1 -->|Response| Agent1
    
    Agent1 -->|Stream Response| UI2
    
    style Frontend fill:#667eea,stroke:#5568d3,color:#fff
    style Backend fill:#4299e1,stroke:#2b6cb0,color:#fff
    style Services fill:#48bb78,stroke:#38a169,color:#fff
```

## Methodology: Multi-Step Reasoning Loop

```mermaid
graph TB
    A["Input: Natural Language Query"] -->|Parse| B["Extract Intent & Context"]
    B -->|Semantic Search| C["Find Relevant Code Snippets<br/>from ChromaDB"]
    C -->|Retrieve| D["Gather Additional Context"]
    D -->|Reason| E["LLM: Analyze & Generate<br/>Initial Response"]
    E -->|Evaluate| F{"Is Response<br/>Complete?"}
    F -->|No| G["Refine Query"]
    G -->|Re-search| C
    F -->|Yes| H["Generate Final Response"]
    H -->|Stream| I["Output to Frontend"]
    
    style A fill:#fbb040,stroke:#f6ad55,color:#000
    style B fill:#4299e1,stroke:#2b6cb0,color:#fff
    style C fill:#48bb78,stroke:#38a169,color:#fff
    style D fill:#48bb78,stroke:#38a169,color:#fff
    style E fill:#667eea,stroke:#5568d3,color:#fff
    style F fill:#ed64a6,stroke:#d69e2e,color:#fff
    style G fill:#4299e1,stroke:#2b6cb0,color:#fff
    style H fill:#667eea,stroke:#5568d3,color:#fff
    style I fill:#38b2ac,stroke:#319795,color:#fff
```

## Technology Stack Visualization

```mermaid
graph TB
    subgraph Frontend_Stack["Frontend Stack"]
        JS["JavaScript (Vanilla)"]
        HTML["HTML5"]
        CSS["CSS3"]
    end
    
    subgraph Backend_Stack["Backend Stack"]
        FastAPI["FastAPI"]
        Python["Python 3.10+"]
        SSE["SSE-Starlette"]
    end
    
    subgraph Libraries["Core Libraries"]
        LangChain["LangChain"]
        GitPython["GitPython"]
        ST["Sentence-Transformers"]
    end
    
    subgraph Infrastructure["Infrastructure"]
        ChromaDB2["ChromaDB<br/>(Vector DB)"]
        Ollama2["Ollama<br/>(LLM Engine)"]
        Git2["Git<br/>(Version Control)"]
    end
    
    Frontend_Stack -->|HTTP/REST| Backend_Stack
    Backend_Stack -->|Uses| Libraries
    Libraries -->|Interfaces| Infrastructure
    
    style Frontend_Stack fill:#667eea,stroke:#5568d3,color:#fff
    style Backend_Stack fill:#4299e1,stroke:#2b6cb0,color:#fff
    style Libraries fill:#b794f6,stroke:#9f7aea,color:#fff
    style Infrastructure fill:#48bb78,stroke:#38a169,color:#fff
```

---

*RepoMind: AI-Powered GitHub Repository Intelligence System*
*Combines semantic search, embeddings, and agentic reasoning for intelligent codebase analysis*
