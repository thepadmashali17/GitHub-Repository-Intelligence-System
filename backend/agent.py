"""
Agentic RAG module — implements multi-step reasoning for repository Q&A.
Uses a manual ReAct-style loop with Ollama for maximum compatibility.
"""

import json
import re

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from config import OLLAMA_MODEL, OLLAMA_BASE_URL, RETRIEVER_TOP_K
from embedder import query_collection, get_repo_file_tree


# ── Tool Implementations ─────────────────────────────────────────────────

def search_documentation(repo_name: str, query: str) -> str:
    """Search the repository's documentation files."""
    results = query_collection(
        repo_name=repo_name,
        query=query,
        n_results=RETRIEVER_TOP_K,
        chunk_type="documentation",
    )
    if not results:
        return "No documentation found matching this query."

    output_parts = []
    for r in results:
        meta = r["metadata"]
        output_parts.append(
            f"📄 File: {meta.get('file_path', 'unknown')}\n"
            f"---\n{r['content']}\n---"
        )
    return "\n\n".join(output_parts)


def search_code(repo_name: str, query: str) -> str:
    """Search the repository's source code files."""
    results = query_collection(
        repo_name=repo_name,
        query=query,
        n_results=RETRIEVER_TOP_K,
        chunk_type="code",
    )
    if not results:
        return "No code found matching this query."

    output_parts = []
    for r in results:
        meta = r["metadata"]
        lang = meta.get("language", "")
        output_parts.append(
            f"📦 File: {meta.get('file_path', 'unknown')} ({lang})\n"
            f"```{lang}\n{r['content']}\n```"
        )
    return "\n\n".join(output_parts)


def search_config(repo_name: str, query: str) -> str:
    """Search the repository's configuration files."""
    results = query_collection(
        repo_name=repo_name,
        query=query,
        n_results=4,
        chunk_type="config",
    )
    if not results:
        return "No configuration files found matching this query."

    output_parts = []
    for r in results:
        meta = r["metadata"]
        output_parts.append(
            f"⚙️ File: {meta.get('file_path', 'unknown')}\n"
            f"```\n{r['content']}\n```"
        )
    return "\n\n".join(output_parts)


def list_repository_structure(repo_name: str, query: str = "") -> str:
    """List all indexed files in the repository."""
    files = get_repo_file_tree(repo_name)
    if not files:
        return "No files indexed for this repository."

    tree: dict[str, list[str]] = {}
    for f in files:
        parts = f.split("/")
        key = parts[0] if len(parts) > 1 else "."
        tree.setdefault(key, []).append(f)

    output = f"Repository structure ({len(files)} indexed files):\n\n"
    for dir_name, dir_files in sorted(tree.items()):
        output += f"{dir_name}/\n"
        for fpath in sorted(dir_files)[:30]:
            output += f"  └── {fpath}\n"
        if len(dir_files) > 30:
            output += f"  └── ... and {len(dir_files) - 30} more\n"
        output += "\n"

    return output


# ── Tool Registry ────────────────────────────────────────────────────────

TOOLS = {
    "search_documentation": {
        "fn": search_documentation,
        "desc": "Search documentation files (README, markdown docs, guides) for high-level info about architecture, setup, or API docs.",
    },
    "search_code": {
        "fn": search_code,
        "desc": "Search source code files for implementations, functions, classes, and logic.",
    },
    "search_config": {
        "fn": search_config,
        "desc": "Search configuration files (package.json, requirements.txt, Dockerfile, YAML) for dependencies and setup.",
    },
    "list_repository_structure": {
        "fn": list_repository_structure,
        "desc": "Get an overview of the repository's file structure.",
    },
}


# ── System Prompt ─────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are an expert software developer assistant analyzing a GitHub repository. 
You have access to these tools to search the repository:

AVAILABLE TOOLS:
{tool_descriptions}

TO USE A TOOL, respond with EXACTLY this format (no extra text before it):
Action: <tool_name>
Action Input: <your search query>

After receiving the tool's output (shown as "Observation:"), you can either:
1. Use another tool for more information
2. Give your final answer with "Final Answer:" prefix

STRATEGY:
1. For architecture/overview questions → search_documentation first, then search_code
2. For implementation questions → search_code directly
3. For dependency/setup questions → search_config
4. When unsure about structure → list_repository_structure first
5. Always combine information from multiple searches when needed

RESPONSE FORMAT for Final Answer:
- Clear explanation of the concept
- Reference specific file paths
- Include relevant code snippets in markdown code blocks
- Use markdown formatting for readability

IMPORTANT: Always start with a tool search, never guess. After searching, cite specific files."""


def _build_system_prompt() -> str:
    tool_descs = "\n".join(
        f"- {name}: {info['desc']}" for name, info in TOOLS.items()
    )
    return SYSTEM_PROMPT.format(tool_descriptions=tool_descs)


# ── ReAct Loop ────────────────────────────────────────────────────────────

def _parse_action(text: str) -> tuple[str | None, str | None]:
    """Parse Action/Action Input from LLM response."""
    # Match "Action: tool_name" and "Action Input: query"
    action_match = re.search(r"Action:\s*(.+?)(?:\n|$)", text)
    input_match = re.search(r"Action Input:\s*(.+?)(?:\n|$)", text)

    if action_match and input_match:
        return action_match.group(1).strip(), input_match.group(1).strip()
    return None, None


def query_repository(repo_name: str, question: str) -> dict:
    """
    Run the agentic RAG pipeline using a manual ReAct loop.
    """
    llm = ChatOllama(
        model=OLLAMA_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=0.1,
        num_ctx=8192,
    )

    system_prompt = _build_system_prompt()
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Question: {question}"),
    ]

    steps = []
    max_iterations = 6

    for iteration in range(max_iterations):
        try:
            response = llm.invoke(messages)
            response_text = response.content
        except Exception as e:
            return {
                "answer": f"Error communicating with the LLM: {str(e)}\n\n"
                          "Please make sure Ollama is running (`ollama serve`) "
                          f"and the model `{OLLAMA_MODEL}` is pulled.",
                "steps": steps,
                "error": str(e),
            }

        # Check if model wants to use a tool
        action, action_input = _parse_action(response_text)

        if action and action in TOOLS:
            # Execute the tool
            tool_fn = TOOLS[action]["fn"]
            try:
                observation = tool_fn(repo_name, action_input)
            except Exception as e:
                observation = f"Tool error: {str(e)}"

            steps.append({
                "tool": action,
                "input": action_input,
                "output": observation[:500] + "..." if len(observation) > 500 else observation,
            })

            # Add the exchange to messages
            messages.append(AIMessage(content=response_text))
            messages.append(HumanMessage(content=f"Observation: {observation}"))

        elif "Final Answer:" in response_text:
            # Extract final answer
            final = response_text.split("Final Answer:", 1)[1].strip()
            return {
                "answer": final,
                "steps": steps,
            }
        else:
            # Model didn't follow format — treat entire response as answer
            # (This handles the case where model gives a direct answer)
            return {
                "answer": response_text,
                "steps": steps,
            }

    # Max iterations reached — return what we have
    return {
        "answer": "I searched through the repository but reached the maximum number of search steps. "
                  "Here's what I found so far — please try a more specific question.\n\n"
                  + (messages[-1].content if messages else "No results found."),
        "steps": steps,
    }
