"""
FastAPI application — REST API with SSE streaming for the GitHub Intelligence System.
"""

import asyncio
import json
import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from cloner import clone_repository
from parser import parse_all_files
from embedder import embed_and_store, list_collections, delete_collection
from agent import query_repository


# ── Lifespan ──────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 GitHub Repository Intelligence System starting...")
    yield
    print("👋 Shutting down.")


app = FastAPI(
    title="GitHub Repository Intelligence System",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request/Response Models ───────────────────────────────────────────────

class IndexRequest(BaseModel):
    url: str

class QueryRequest(BaseModel):
    repo_name: str
    question: str


# ── SSE Helpers ───────────────────────────────────────────────────────────

def _sse_event(event_type: str, data: dict) -> dict:
    return {"event": event_type, "data": json.dumps(data)}


# ── Endpoints ─────────────────────────────────────────────────────────────

@app.post("/api/index")
async def index_repository(request: IndexRequest):
    """
    Clone, parse, and embed a GitHub repository.
    Returns an SSE stream with progress updates.
    """
    url = request.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")
    if "github.com" not in url:
        raise HTTPException(status_code=400, detail="Only GitHub URLs are supported")

    async def event_stream():
        progress_messages = []

        def progress_callback(msg: str):
            progress_messages.append(msg)

        try:
            # Step 1: Clone
            yield _sse_event("progress", {"step": "cloning", "message": f"Cloning {url}..."})
            repo_info = await asyncio.to_thread(
                clone_repository, url, progress_callback
            )
            for msg in progress_messages:
                yield _sse_event("progress", {"step": "cloning", "message": msg})
            progress_messages.clear()

            # Step 2: Parse
            yield _sse_event("progress", {
                "step": "parsing",
                "message": f"Parsing {repo_info.stats['total']} files..."
            })
            chunks = await asyncio.to_thread(
                parse_all_files, repo_info.files, repo_info.name, progress_callback
            )
            for msg in progress_messages:
                yield _sse_event("progress", {"step": "parsing", "message": msg})
            progress_messages.clear()

            # Step 3: Embed
            yield _sse_event("progress", {
                "step": "embedding",
                "message": f"Generating embeddings for {len(chunks)} chunks..."
            })
            stats = await asyncio.to_thread(
                embed_and_store, chunks, repo_info.name, progress_callback
            )
            for msg in progress_messages:
                yield _sse_event("progress", {"step": "embedding", "message": msg})

            # Done
            yield _sse_event("complete", {
                "repo_name": repo_info.name,
                "stats": {
                    "files": repo_info.stats,
                    "chunks": stats["total_stored"],
                },
            })

        except Exception as e:
            traceback.print_exc()
            yield _sse_event("error", {"message": str(e)})

    return EventSourceResponse(event_stream())


@app.post("/api/query")
async def query_repo(request: QueryRequest):
    """
    Ask a question about an indexed repository.
    Returns SSE stream with the agent's answer.
    """
    if not request.repo_name or not request.question:
        raise HTTPException(status_code=400, detail="repo_name and question are required")

    async def event_stream():
        try:
            yield _sse_event("progress", {
                "message": "Analyzing your question and searching the repository..."
            })

            result = await asyncio.to_thread(
                query_repository, request.repo_name, request.question
            )

            # Send intermediate steps for transparency
            for step in result.get("steps", []):
                yield _sse_event("step", step)

            # Send final answer
            yield _sse_event("answer", {
                "content": result["answer"],
                "steps": result.get("steps", []),
            })

        except Exception as e:
            traceback.print_exc()
            yield _sse_event("error", {"message": str(e)})

    return EventSourceResponse(event_stream())


@app.get("/api/repos")
async def get_repos():
    """List all indexed repositories."""
    repos = await asyncio.to_thread(list_collections)
    return {"repos": repos}


@app.delete("/api/repos/{repo_name}")
async def remove_repo(repo_name: str):
    """Delete an indexed repository."""
    success = await asyncio.to_thread(delete_collection, repo_name)
    if not success:
        raise HTTPException(status_code=404, detail="Repository not found")
    return {"message": f"Repository {repo_name} deleted"}


# ── Serve Frontend ────────────────────────────────────────────────────────

app.mount("/static", StaticFiles(directory="../frontend"), name="static")


@app.get("/")
async def serve_frontend():
    return FileResponse("../frontend/index.html")
