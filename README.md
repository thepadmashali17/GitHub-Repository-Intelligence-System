# RepoMind: GitHub Repository Intelligence System

RepoMind is a Python/FastAPI application that:
- clones a public GitHub repository,
- parses source/docs/config files,
- stores embeddings in ChromaDB,
- answers repository questions with an Ollama-backed agent,
- serves a built-in browser UI from the same FastAPI server.

## Runtime Model

- **Backend**: FastAPI (`backend/main.py`)
- **Frontend**: static HTML/CSS/JS (`frontend/`) served by FastAPI
- **Vector Store**: local ChromaDB files in `chroma_db/`
- **Cloned repos**: stored under `repos/`
- **LLM provider**: Ollama (`OLLAMA_BASE_URL`, `OLLAMA_MODEL`)

## Prerequisites

- Python 3.11+ (3.10 may work, CI uses 3.11)
- Git installed on host
- Ollama running and reachable from this app

## Local Setup

```bash
git clone https://github.com/thepadmashali17/GitHub-Repository-Intelligence-System.git
cd GitHub-Repository-Intelligence-System

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install --upgrade pip
pip install -r backend/requirements.txt
```

Copy environment template and adjust as needed:

```bash
cp backend/.env.example .env
```

Start Ollama and ensure the model exists:

```bash
ollama serve
ollama pull qwen3:8b
```

Run the app:

```bash
cd backend
python main.py
```

Open `http://localhost:8000`.

## Environment Variables

| Variable | Default | Required | Description |
|---|---|---:|---|
| `OLLAMA_MODEL` | `qwen3:8b` | No | Ollama chat model name |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Yes (unless default works) | Base URL for Ollama server |
| `API_HOST` | `0.0.0.0` | No | FastAPI bind host |
| `API_PORT` | `8000` | No | FastAPI bind port |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:8000,http://127.0.0.1:8000` | No | Comma-separated origins (`*` allowed) |

## Health Check

- Endpoint: `GET /healthz`
- Expected response: `{"status":"ok"}`

Example:

```bash
curl http://localhost:8000/healthz
```

## Usage

1. Open the web app.
2. Paste a public GitHub repo URL and click **INDEX**.
3. Wait until indexing completes.
4. Ask questions in chat (architecture, flow, APIs, dependencies, etc.).

API endpoints:
- `POST /api/index` — index repository (SSE stream)
- `POST /api/query` — ask question (SSE stream)
- `GET /api/repos` — list indexed repos
- `DELETE /api/repos/{repo_name}` — delete indexed repo
- `GET /healthz` — health check

## Production Deployment (Docker)

A production Dockerfile is included at repo root.

Build image:

```bash
docker build -t repomind:latest .
```

Run container:

```bash
docker run --rm -p 8000:8000 \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  -e OLLAMA_MODEL=qwen3:8b \
  -e API_HOST=0.0.0.0 \
  -e API_PORT=8000 \
  repomind:latest
```

If Ollama runs on another host, set `OLLAMA_BASE_URL` accordingly.

## CI / Automated Checks

GitHub Actions workflow: `.github/workflows/ci.yml`
- installs dependencies,
- compiles backend Python files,
- runs tests in `tests/`.

## Required Secrets

This project does **not** require repository secrets by default.
Do not commit `.env` files, tokens, or private credentials.
