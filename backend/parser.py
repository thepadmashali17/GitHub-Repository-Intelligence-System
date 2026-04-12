"""
Structure-aware code and documentation parsing module.
Uses LangChain's language-aware splitters for code and markdown splitters for docs.
"""

from pathlib import Path

from langchain_text_splitters import (
    Language,
    RecursiveCharacterTextSplitter,
    MarkdownHeaderTextSplitter,
)
from langchain_core.documents import Document

from cloner import FileInfo
from config import (
    CODE_CHUNK_SIZE,
    CODE_CHUNK_OVERLAP,
    DOC_CHUNK_SIZE,
    DOC_CHUNK_OVERLAP,
    CONFIG_CHUNK_SIZE,
    CONFIG_CHUNK_OVERLAP,
)

# ── Language Mapping ──────────────────────────────────────────────────────
LANG_MAP = {
    "python": Language.PYTHON,
    "javascript": Language.JS,
    "typescript": Language.TS,
    "java": Language.JAVA,
    "cpp": Language.CPP,
    "c": Language.C,
    "go": Language.GO,
    "rust": Language.RUST,
    "ruby": Language.RUBY,
    "php": Language.PHP,
    "swift": Language.SWIFT,
    "kotlin": Language.KOTLIN,
    "scala": Language.SCALA,
    "csharp": Language.CSHARP,
}


def _read_file_safe(path: Path) -> str | None:
    """Read a file, returning None if it can't be decoded."""
    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return path.read_text(encoding=encoding)
        except (UnicodeDecodeError, ValueError):
            continue
        except OSError:
            return None
    return None


def parse_code_file(file_info: FileInfo, repo_name: str) -> list[Document]:
    """
    Parse a code file using LangChain's language-aware splitter.
    Falls back to generic splitting if language not supported.
    """
    content = _read_file_safe(file_info.path)
    if not content or not content.strip():
        return []

    lang_enum = LANG_MAP.get(file_info.language)

    if lang_enum:
        splitter = RecursiveCharacterTextSplitter.from_language(
            language=lang_enum,
            chunk_size=CODE_CHUNK_SIZE,
            chunk_overlap=CODE_CHUNK_OVERLAP,
        )
    else:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CODE_CHUNK_SIZE,
            chunk_overlap=CODE_CHUNK_OVERLAP,
        )

    chunks = splitter.create_documents(
        texts=[content],
        metadatas=[{
            "repo_name": repo_name,
            "file_path": file_info.relative_path,
            "chunk_type": "code",
            "language": file_info.language or "unknown",
            "source": file_info.relative_path,
        }],
    )

    # Add chunk index
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_index"] = i

    return chunks


def parse_doc_file(file_info: FileInfo, repo_name: str) -> list[Document]:
    """
    Parse a documentation/markdown file using semantic header splitting
    followed by size-based splitting for large sections.
    """
    content = _read_file_safe(file_info.path)
    if not content or not content.strip():
        return []

    # First pass: split by markdown headers
    headers_to_split = [
        ("#", "header_1"),
        ("##", "header_2"),
        ("###", "header_3"),
    ]

    try:
        header_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=headers_to_split,
            strip_headers=False,
        )
        header_chunks = header_splitter.split_text(content)
    except Exception:
        # Fallback if markdown parsing fails
        header_chunks = [Document(page_content=content)]

    # Second pass: further split large sections
    size_splitter = RecursiveCharacterTextSplitter(
        chunk_size=DOC_CHUNK_SIZE,
        chunk_overlap=DOC_CHUNK_OVERLAP,
    )

    final_chunks = []
    for chunk in header_chunks:
        if len(chunk.page_content) > DOC_CHUNK_SIZE:
            sub_chunks = size_splitter.split_documents([chunk])
            final_chunks.extend(sub_chunks)
        else:
            final_chunks.append(chunk)

    # Enrich metadata
    for i, chunk in enumerate(final_chunks):
        chunk.metadata.update({
            "repo_name": repo_name,
            "file_path": file_info.relative_path,
            "chunk_type": "documentation",
            "language": "markdown",
            "source": file_info.relative_path,
            "chunk_index": i,
        })

    return final_chunks


def parse_config_file(file_info: FileInfo, repo_name: str) -> list[Document]:
    """
    Parse a configuration file using simple text splitting.
    """
    content = _read_file_safe(file_info.path)
    if not content or not content.strip():
        return []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CONFIG_CHUNK_SIZE,
        chunk_overlap=CONFIG_CHUNK_OVERLAP,
    )

    chunks = splitter.create_documents(
        texts=[content],
        metadatas=[{
            "repo_name": repo_name,
            "file_path": file_info.relative_path,
            "chunk_type": "config",
            "language": file_info.path.suffix.lstrip(".") or "config",
            "source": file_info.relative_path,
        }],
    )

    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_index"] = i

    return chunks


def parse_all_files(
    files: list[FileInfo],
    repo_name: str,
    progress_callback=None,
) -> list[Document]:
    """
    Parse all files in the repository and return a flat list of Document chunks.
    """
    all_chunks: list[Document] = []
    parsers = {
        "code": parse_code_file,
        "documentation": parse_doc_file,
        "config": parse_config_file,
    }

    for i, file_info in enumerate(files):
        parser = parsers.get(file_info.file_type)
        if parser is None:
            continue

        try:
            chunks = parser(file_info, repo_name)
            all_chunks.extend(chunks)
        except Exception as e:
            # Skip files that fail to parse
            if progress_callback:
                progress_callback(f"Warning: Skipped {file_info.relative_path}: {e}")
            continue

        if progress_callback and (i + 1) % 25 == 0:
            progress_callback(
                f"Parsed {i + 1}/{len(files)} files ({len(all_chunks)} chunks so far)"
            )

    if progress_callback:
        progress_callback(
            f"Parsing complete: {len(files)} files → {len(all_chunks)} chunks"
        )

    return all_chunks
