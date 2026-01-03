"""
MDSA Memory Module

Provides Dual RAG (Retrieval-Augmented Generation) system:
- LocalRAG: Domain-specific isolated knowledge
- GlobalRAG: Shared knowledge accessible by all domains
- DualRAG: Unified interface for both

Example:
    >>> from mdsa.memory import DualRAG, RAGDocument
    >>> rag = DualRAG(max_global_docs=10000, max_local_docs=1000)
    >>> rag.register_domain("medical")
    >>> rag.add_to_global("Common medical knowledge", {"type": "reference"})
    >>> rag.add_to_local("medical", "ICD-10 codes", {"type": "codes"})
    >>> results = rag.retrieve("diabetes", domain_id="medical")
"""

from mdsa.memory.dual_rag import (
    RAGDocument,
    RAGResult,
    LocalRAG,
    GlobalRAG,
    DualRAG,
)

__all__ = [
    "RAGDocument",
    "RAGResult",
    "LocalRAG",
    "GlobalRAG",
    "DualRAG",
]
