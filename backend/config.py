"""
Configuration and constants for the GitHub Repository Intelligence System.
"""

import os
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
REPOS_DIR = BASE_DIR / "repos"
CHROMA_DIR = BASE_DIR / "chroma_db"
FRONTEND_DIR = BASE_DIR / "frontend"

REPOS_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DIR.mkdir(parents=True, exist_ok=True)

# ── Ollama ────────────────────────────────────────────────────────────
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# ── API Runtime ───────────────────────────────────────────────────────
API_HOST = os.getenv("API_HOST", "0.0.0.0")
try:
    API_PORT = int(os.getenv("API_PORT", "8000"))
except ValueError:
    API_PORT = 8000

_cors_origins = os.getenv(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:8000,http://127.0.0.1:8000",
)
CORS_ALLOWED_ORIGINS = [origin.strip() for origin in _cors_origins.split(",") if origin.strip()]

# ── Embedding ─────────────────────────────────────────────────────────
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_BATCH_SIZE = 64

# ── Chunk Sizes ────────────────────────────────────────────────────────
CODE_CHUNK_SIZE = 1500
CODE_CHUNK_OVERLAP = 200

DOC_CHUNK_SIZE = 1000
DOC_CHUNK_OVERLAP = 150

CONFIG_CHUNK_SIZE = 800
CONFIG_CHUNK_OVERLAP = 100

# ── File Classification ───────────────────────────────────────────────
CODE_EXTENSIONS = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".java": "java",
    ".cpp": "cpp",
    ".cxx": "cpp",
    ".cc": "cpp",
    ".c": "c",
    ".h": "c",
    ".hpp": "cpp",
    ".go": "go",
    ".rs": "rust",
    ".rb": "ruby",
    ".php": "php",
    ".swift": "swift",
    ".kt": "kotlin",
    ".scala": "scala",
    ".cs": "csharp",
}

DOC_EXTENSIONS = {".md", ".mdx", ".rst", ".txt", ".adoc"}

CONFIG_FILES = {
    "package.json",
    "requirements.txt",
    "setup.py",
    "setup.cfg",
    "pyproject.toml",
    "cargo.toml",
    "go.mod",
    "go.sum",
    "dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    ".env.example",
    "makefile",
    "cmakelists.txt",
    "build.gradle",
    "pom.xml",
    "tsconfig.json",
    "webpack.config.js",
    "vite.config.js",
    "vite.config.ts",
    ".eslintrc.json",
    ".prettierrc",
    "jest.config.js",
}

CONFIG_EXTENSIONS = {
    ".yml", ".yaml", ".toml", ".ini", ".cfg", ".conf",
    ".json", ".xml", ".properties",
}

# ── Skip Patterns ──────────────────────────────────────────────────────
SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", "env",
    ".idea", ".vscode", ".vs", "dist", "build", "target", ".next",
    "vendor", "bower_components", ".tox", ".mypy_cache", ".pytest_cache",
    "coverage", ".nyc_output", "bin", "obj",
}

MAX_FILE_SIZE_KB = 500  # Skip files larger than this

# ── Retrieval ──────────────────────────────────────────────────────────
RETRIEVER_TOP_K = 6
