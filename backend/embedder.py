"""
Embedding generation and ChromaDB vector store management.
Uses sentence-transformers for embeddings and ChromaDB for persistent storage.
"""

import uuid
from typing import Optional

import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_core.documents import Document
from sentence_transformers import SentenceTransformer

from config import (
    CHROMA_DIR,
    EMBEDDING_MODEL,
    EMBEDDING_BATCH_SIZE,
    RETRIEVER_TOP_K,
)

# ── Global State ──────────────────────────────────────────────────────────
_embed_model: Optional[SentenceTransformer] = None
_chroma_client: Optional[chromadb.PersistentClient] = None


def get_embed_model() -> SentenceTransformer:
    """Load the embedding model once (lazy singleton)."""
    global _embed_model
    if _embed_model is None:
        _embed_model = SentenceTransformer(EMBEDDING_MODEL)
    return _embed_model


def get_chroma_client() -> chromadb.PersistentClient:
    """Get or create the ChromaDB persistent client."""
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = chromadb.PersistentClient(
            path=str(CHROMA_DIR),
            settings=ChromaSettings(anonymized_telemetry=False),
        )
    return _chroma_client


class EmbeddingFunction(chromadb.EmbeddingFunction):
    """Wraps sentence-transformers model for ChromaDB."""

    def __call__(self, input: list[str]) -> list[list[float]]:
        model = get_embed_model()
        embeddings = model.encode(input, batch_size=EMBEDDING_BATCH_SIZE, show_progress_bar=False)
        return embeddings.tolist()


def _sanitize_collection_name(name: str) -> str:
    """ChromaDB collection names must be 3-63 chars, alphanumeric + underscores/hyphens."""
    sanitized = name.replace("/", "__").replace("\\", "__")
    # Remove any chars that aren't alphanumeric, underscore, or hyphen
    sanitized = "".join(c if c.isalnum() or c in ("_", "-") else "_" for c in sanitized)
    # Ensure length constraints
    if len(sanitized) < 3:
        sanitized = sanitized + "___"
    if len(sanitized) > 63:
        sanitized = sanitized[:63]
    return sanitized


def embed_and_store(
    chunks: list[Document],
    repo_name: str,
    progress_callback=None,
) -> dict:
    """
    Generate embeddings for all chunks and store in ChromaDB.
    Returns stats about what was stored.
    """
    if not chunks:
        return {"total_stored": 0}

    client = get_chroma_client()
    collection_name = _sanitize_collection_name(repo_name)

    # Delete existing collection if it exists (re-index scenario)
    try:
        client.delete_collection(collection_name)
    except Exception:
        pass

    embed_fn = EmbeddingFunction()
    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=embed_fn,
        metadata={"repo_name": repo_name},
    )

    if progress_callback:
        progress_callback(f"Generating embeddings for {len(chunks)} chunks...")

    # Process in batches
    total_batches = (len(chunks) + EMBEDDING_BATCH_SIZE - 1) // EMBEDDING_BATCH_SIZE

    for batch_idx in range(total_batches):
        start = batch_idx * EMBEDDING_BATCH_SIZE
        end = min(start + EMBEDDING_BATCH_SIZE, len(chunks))
        batch = chunks[start:end]

        ids = [str(uuid.uuid4()) for _ in batch]
        documents = [chunk.page_content for chunk in batch]
        metadatas = [chunk.metadata for chunk in batch]

        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
        )

        if progress_callback and (batch_idx + 1) % 5 == 0:
            progress_callback(
                f"Embedded batch {batch_idx + 1}/{total_batches} "
                f"({end}/{len(chunks)} chunks)"
            )

    if progress_callback:
        progress_callback(
            f"Embedding complete: {len(chunks)} chunks stored in vector database"
        )

    return {
        "total_stored": len(chunks),
        "collection_name": collection_name,
    }


def query_collection(
    repo_name: str,
    query: str,
    n_results: int = RETRIEVER_TOP_K,
    chunk_type: Optional[str] = None,
) -> list[dict]:
    """
    Query the ChromaDB collection for similar chunks.
    Optionally filter by chunk_type (code, documentation, config).
    """
    client = get_chroma_client()
    collection_name = _sanitize_collection_name(repo_name)

    try:
        embed_fn = EmbeddingFunction()
        collection = client.get_collection(
            name=collection_name,
            embedding_function=embed_fn,
        )
    except Exception:
        return []

    where_filter = None
    if chunk_type:
        where_filter = {"chunk_type": chunk_type}

    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        where=where_filter,
        include=["documents", "metadatas", "distances"],
    )

    output = []
    if results and results["documents"]:
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            output.append({
                "content": doc,
                "metadata": meta,
                "distance": dist,
            })

    return output


def list_collections() -> list[dict]:
    """List all indexed repositories."""
    client = get_chroma_client()
    collections = client.list_collections()
    result = []
    for col in collections:
        # ChromaDB 1.5+ returns strings; older versions return objects
        col_name = col if isinstance(col, str) else col.name
        try:
            embed_fn = EmbeddingFunction()
            collection = client.get_collection(col_name, embedding_function=embed_fn)
            count = collection.count()
            meta = collection.metadata or {}
        except Exception:
            count = 0
            meta = {}
        result.append({
            "name": col_name,
            "repo_name": meta.get("repo_name", col_name),
            "chunk_count": count,
        })
    return result


def delete_collection(repo_name: str) -> bool:
    """Delete a repository's collection from ChromaDB."""
    client = get_chroma_client()
    collection_name = _sanitize_collection_name(repo_name)
    try:
        client.delete_collection(collection_name)
        return True
    except Exception:
        return False


def get_repo_file_tree(repo_name: str) -> list[str]:
    """Get the list of unique file paths stored in a collection."""
    client = get_chroma_client()
    collection_name = _sanitize_collection_name(repo_name)

    try:
        embed_fn = EmbeddingFunction()
        collection = client.get_collection(
            name=collection_name,
            embedding_function=embed_fn,
        )
    except Exception:
        return []

    # Get all metadatas to extract unique file paths
    all_data = collection.get(include=["metadatas"])
    file_paths = set()
    if all_data and all_data["metadatas"]:
        for meta in all_data["metadatas"]:
            if "file_path" in meta:
                file_paths.add(meta["file_path"])

    return sorted(file_paths)
