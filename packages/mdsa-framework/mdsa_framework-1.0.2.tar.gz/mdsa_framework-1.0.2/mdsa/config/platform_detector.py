"""
Platform-Specific Knowledge Base Path Detection

Automatically detects which platform is using MDSA and returns the
appropriate knowledge base path for storing RAG documents.

Supports:
- MedCode medical chatbot platform
- Generic chatbot applications
- Custom paths via environment variable
- MDSA default fallback
"""

import os
from pathlib import Path
from typing import Tuple


def detect_platform_kb_path() -> Path:
    """
    Auto-detect which platform is using MDSA and return appropriate KB path.

    Priority order:
    1. MDSA_KNOWLEDGE_BASE_PATH environment variable (if set and not 'auto')
    2. Example medical chatbot (examples/medical_chatbot/knowledge_base) - v1.0+
    3. Legacy MedCode platform (chatbot_app/medical_app/knowledge_base) - backward compatibility
    4. Legacy generic chatbot (chatbot_app/knowledge_base) - backward compatibility
    5. MDSA default (mdsa/data/knowledge_base)

    Returns:
        Path: Knowledge base directory path
    """
    # Check for explicit override via environment variable
    env_path = os.getenv('MDSA_KNOWLEDGE_BASE_PATH')
    if env_path and env_path != 'auto':
        kb_path = Path(env_path)
        kb_path.mkdir(parents=True, exist_ok=True)
        print(f"[KB] Using custom path from environment: {kb_path}")
        return kb_path

    # Get current working directory as base
    cwd = Path.cwd()

    # Priority 1: Check for new example location (v1.0+)
    example_kb = cwd / "examples" / "medical_chatbot" / "knowledge_base"
    if example_kb.exists():
        print(f"[KB] Detected example medical chatbot: {example_kb}")
        return example_kb

    # Priority 2: Check for legacy MedCode platform (backward compatibility)
    medcode_kb = cwd / "chatbot_app" / "medical_app" / "knowledge_base"
    if medcode_kb.exists():
        print(f"[KB] Detected legacy MedCode platform: {medcode_kb}")
        return medcode_kb

    # Priority 3: Check for legacy generic chatbot (backward compatibility)
    generic_kb = cwd / "chatbot_app" / "knowledge_base"
    if generic_kb.exists():
        print(f"[KB] Detected legacy chatbot platform: {generic_kb}")
        return generic_kb

    # Priority 4: Fallback to MDSA default
    mdsa_kb = cwd / "mdsa" / "data" / "knowledge_base"
    mdsa_kb.mkdir(parents=True, exist_ok=True)
    print(f"[KB] Using MDSA default: {mdsa_kb}")
    return mdsa_kb


def get_vector_db_path() -> Path:
    """
    Get ChromaDB persist directory (platform-specific).

    Creates vector_db directory alongside the knowledge_base directory.

    Returns:
        Path: Vector database directory path
    """
    kb_path = detect_platform_kb_path()
    vector_db = kb_path.parent / "vector_db"
    vector_db.mkdir(parents=True, exist_ok=True)
    return vector_db


def get_paths() -> Tuple[Path, Path]:
    """
    Get both knowledge base and vector database paths.

    Returns:
        Tuple[Path, Path]: (knowledge_base_path, vector_db_path)
    """
    kb_path = detect_platform_kb_path()
    vector_db = kb_path.parent / "vector_db"
    vector_db.mkdir(parents=True, exist_ok=True)
    return kb_path, vector_db


def create_rag_subdirectories(kb_path: Path) -> None:
    """
    Create standard RAG subdirectories within knowledge base.

    Structure:
    knowledge_base/
    ├── global/           # Global RAG documents
    ├── local/            # Local RAG documents (by domain)
    │   ├── medical/
    │   ├── finance/
    │   └── ...
    └── uploads/          # Temporary upload directory

    Args:
        kb_path: Knowledge base root path
    """
    (kb_path / "global").mkdir(parents=True, exist_ok=True)
    (kb_path / "local").mkdir(parents=True, exist_ok=True)
    (kb_path / "uploads").mkdir(parents=True, exist_ok=True)
    print(f"[KB] Created RAG subdirectories in: {kb_path}")


# Auto-initialize on import
if __name__ != "__main__":
    try:
        kb_path, vector_db = get_paths()
        create_rag_subdirectories(kb_path)
    except Exception as e:
        print(f"[WARN] Could not auto-initialize KB paths: {e}")
