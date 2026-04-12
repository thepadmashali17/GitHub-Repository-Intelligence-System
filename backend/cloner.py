"""
Repository cloning and file discovery module.
"""

import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Generator

from git import Repo, GitCommandError

from config import (
    REPOS_DIR,
    CODE_EXTENSIONS,
    DOC_EXTENSIONS,
    CONFIG_FILES,
    CONFIG_EXTENSIONS,
    SKIP_DIRS,
    MAX_FILE_SIZE_KB,
)


@dataclass
class FileInfo:
    path: Path
    relative_path: str
    file_type: str  # "code", "documentation", "config"
    language: str | None = None


@dataclass
class RepoInfo:
    name: str
    url: str
    local_path: Path
    files: list[FileInfo] = field(default_factory=list)
    stats: dict = field(default_factory=dict)


def extract_repo_name(url: str) -> str:
    """Extract a clean repository name from a GitHub URL."""
    url = url.rstrip("/").rstrip(".git")
    match = re.search(r"github\.com/([^/]+/[^/]+)", url)
    if match:
        return match.group(1).replace("/", "__")
    # Fallback: use last path segment
    return url.split("/")[-1]


def clone_repository(url: str, progress_callback=None) -> RepoInfo:
    """
    Clone a public GitHub repository. If it already exists, remove and re-clone.
    """
    repo_name = extract_repo_name(url)
    local_path = REPOS_DIR / repo_name

    if local_path.exists():
        if progress_callback:
            progress_callback(f"Removing existing clone of {repo_name}...")
        shutil.rmtree(local_path, ignore_errors=True)

    if progress_callback:
        progress_callback(f"Cloning {url}...")

    try:
        Repo.clone_from(url, str(local_path), depth=1)  # Shallow clone for speed
    except GitCommandError as e:
        raise RuntimeError(f"Failed to clone repository: {e}")

    if progress_callback:
        progress_callback("Clone complete. Discovering files...")

    files = list(discover_files(local_path, repo_name))

    stats = {"total": len(files)}
    for ftype in ("code", "documentation", "config"):
        stats[ftype] = sum(1 for f in files if f.file_type == ftype)

    if progress_callback:
        progress_callback(
            f"Found {stats['total']} files: "
            f"{stats['code']} code, {stats['documentation']} docs, {stats['config']} config"
        )

    return RepoInfo(
        name=repo_name,
        url=url,
        local_path=local_path,
        files=files,
        stats=stats,
    )


def classify_file(file_path: Path) -> tuple[str, str | None] | None:
    """
    Classify a file as code, documentation, or config.
    Returns (file_type, language) or None if the file should be skipped.
    """
    name_lower = file_path.name.lower()
    ext_lower = file_path.suffix.lower()

    # Check code extensions
    if ext_lower in CODE_EXTENSIONS:
        return ("code", CODE_EXTENSIONS[ext_lower])

    # Check documentation
    if ext_lower in DOC_EXTENSIONS:
        return ("documentation", None)
    if name_lower.startswith("readme"):
        return ("documentation", None)

    # Check config files (by exact name)
    if name_lower in CONFIG_FILES:
        return ("config", None)

    # Check config files (by extension)
    if ext_lower in CONFIG_EXTENSIONS:
        return ("config", None)

    return None


def discover_files(repo_path: Path, repo_name: str) -> Generator[FileInfo, None, None]:
    """
    Walk the repository tree and yield classified FileInfo objects.
    Skips binary files, large files, and ignored directories.
    """
    for item in repo_path.rglob("*"):
        if not item.is_file():
            continue

        # Skip files in ignored directories
        parts_lower = {p.lower() for p in item.relative_to(repo_path).parts}
        if parts_lower & SKIP_DIRS:
            continue

        # Skip large files
        try:
            size_kb = item.stat().st_size / 1024
            if size_kb > MAX_FILE_SIZE_KB:
                continue
        except OSError:
            continue

        classification = classify_file(item)
        if classification is None:
            continue

        file_type, language = classification

        yield FileInfo(
            path=item,
            relative_path=str(item.relative_to(repo_path)).replace("\\", "/"),
            file_type=file_type,
            language=language,
        )
