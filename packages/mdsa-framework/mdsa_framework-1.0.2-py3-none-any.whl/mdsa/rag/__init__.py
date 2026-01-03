"""
MDSA RAG (Retrieval-Augmented Generation) Module

Contains local and global RAG systems, vector stores, and embedding management.
"""

# Import RAG components from memory module
try:
    from mdsa.memory.dual_rag import (
        DualRAG,
        LocalRAG,
        GlobalRAG,
        RAGDocument,
        RAGResult,
    )
    RAG_AVAILABLE = True
except ImportError as e:
    # RAG requires chromadb and sentence-transformers
    RAG_AVAILABLE = False
    DualRAG = None
    LocalRAG = None
    GlobalRAG = None
    RAGDocument = None
    RAGResult = None

__all__ = [
    "DualRAG",
    "LocalRAG",
    "GlobalRAG",
    "RAGDocument",
    "RAGResult",
    "RAG_AVAILABLE",
]
