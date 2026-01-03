"""
RAG Engine using ChromaDB (Free & Open Source)

Handles document ingestion, embedding, and retrieval for RAG-enhanced chatbot.
"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class RAGEngine:
    """
    Retrieval-Augmented Generation engine using ChromaDB.

    Features:
    - Free & open-source (ChromaDB + Sentence Transformers)
    - Local vector database (no API keys needed)
    - Persistent storage
    - Multiple document formats support
    """

    def __init__(
        self,
        collection_name: str = "knowledge_base",
        persist_directory: str = "./chroma_db",
        embedding_model: str = "all-MiniLM-L6-v2"  # Fast, free, 384-dim embeddings
    ):
        """
        Initialize RAG engine.

        Args:
            collection_name: Name of the ChromaDB collection
            persist_directory: Directory to persist vector database
            embedding_model: Sentence Transformers model name
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory

        # Create persist directory
        Path(persist_directory).mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB client (persistent)
        self.client = chromadb.Client(Settings(
            persist_directory=persist_directory,
            anonymized_telemetry=False
        ))

        # Load embedding model
        logger.info(f"Loading embedding model: {embedding_model}")
        self.embedding_model = SentenceTransformer(embedding_model)
        logger.info("Embedding model loaded")

        # Get or create collection
        try:
            self.collection = self.client.get_collection(name=collection_name)
            logger.info(f"Loaded existing collection: {collection_name}")
        except:
            self.collection = self.client.create_collection(name=collection_name)
            logger.info(f"Created new collection: {collection_name}")

    def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> None:
        """
        Add documents to the knowledge base.

        Args:
            documents: List of document texts
            metadatas: Optional metadata for each document
            ids: Optional IDs for each document
        """
        if not documents:
            logger.warning("No documents to add")
            return

        # Generate IDs if not provided
        if ids is None:
            ids = [f"doc_{i}" for i in range(len(documents))]

        # Generate embeddings
        logger.info(f"Generating embeddings for {len(documents)} documents...")
        embeddings = self.embedding_model.encode(documents, show_progress_bar=True)

        # Add to collection
        self.collection.add(
            documents=documents,
            embeddings=embeddings.tolist(),
            metadatas=metadatas or [{} for _ in documents],
            ids=ids
        )

        logger.info(f"Added {len(documents)} documents to collection")

    def add_text_file(self, file_path: str) -> None:
        """Add a text file to the knowledge base."""
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Read file
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Split into chunks (simple splitting by paragraphs)
        chunks = [chunk.strip() for chunk in content.split('\n\n') if chunk.strip()]

        # Add with metadata
        metadatas = [{'source': path.name, 'chunk_id': i} for i in range(len(chunks))]
        ids = [f"{path.stem}_chunk_{i}" for i in range(len(chunks))]

        self.add_documents(chunks, metadatas, ids)
        logger.info(f"Added {len(chunks)} chunks from {path.name}")

    def add_pdf_file(self, file_path: str) -> None:
        """Add a PDF file to the knowledge base."""
        try:
            from PyPDF2 import PdfReader
        except ImportError:
            logger.error("PyPDF2 not installed. Install with: pip install pypdf2")
            return

        path = Path(file_path)
        reader = PdfReader(str(path))

        # Extract text from all pages
        chunks = []
        metadatas = []
        ids = []

        for i, page in enumerate(reader.pages):
            text = page.extract_text().strip()
            if text:
                chunks.append(text)
                metadatas.append({'source': path.name, 'page': i + 1})
                ids.append(f"{path.stem}_page_{i + 1}")

        self.add_documents(chunks, metadatas, ids)
        logger.info(f"Added {len(chunks)} pages from {path.name}")

    def add_directory(
        self,
        directory: str,
        extensions: List[str] = ['.txt', '.md', '.pdf']
    ) -> None:
        """
        Add all files from a directory.

        Args:
            directory: Directory path
            extensions: File extensions to process
        """
        path = Path(directory)

        if not path.exists() or not path.is_dir():
            raise ValueError(f"Invalid directory: {directory}")

        files_added = 0

        for ext in extensions:
            for file_path in path.glob(f'**/*{ext}'):
                try:
                    if ext == '.pdf':
                        self.add_pdf_file(str(file_path))
                    else:
                        self.add_text_file(str(file_path))
                    files_added += 1
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}")

        logger.info(f"Processed {files_added} files from {directory}")

    def search(
        self,
        query: str,
        n_results: int = 3
    ) -> Dict[str, Any]:
        """
        Search for relevant documents.

        Args:
            query: Search query
            n_results: Number of results to return

        Returns:
            dict: Search results with documents, metadatas, and distances
        """
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])[0]

        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=n_results
        )

        return results

    def get_context(
        self,
        query: str,
        n_results: int = 3,
        max_length: int = 2000
    ) -> str:
        """
        Get context for a query (formatted for prompts).

        Args:
            query: Search query
            n_results: Number of results to retrieve
            max_length: Maximum context length

        Returns:
            str: Formatted context string
        """
        results = self.search(query, n_results)

        if not results['documents'] or not results['documents'][0]:
            return "No relevant context found."

        # Format context
        context_parts = []
        total_length = 0

        for i, (doc, metadata) in enumerate(zip(
            results['documents'][0],
            results['metadatas'][0]
        )):
            source = metadata.get('source', 'Unknown')
            chunk_info = f"[Source: {source}]"

            part = f"{chunk_info}\n{doc}\n"

            if total_length + len(part) > max_length:
                break

            context_parts.append(part)
            total_length += len(part)

        if not context_parts:
            return results['documents'][0][0][:max_length]

        return "\n".join(context_parts)

    def clear(self) -> None:
        """Clear all documents from the collection."""
        self.client.delete_collection(name=self.collection_name)
        self.collection = self.client.create_collection(name=self.collection_name)
        logger.info("Collection cleared")

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base."""
        count = self.collection.count()

        return {
            'total_documents': count,
            'collection_name': self.collection_name,
            'persist_directory': self.persist_directory,
            'embedding_model': self.embedding_model.get_sentence_embedding_dimension(),
            'embedding_dimension': self.embedding_model.get_sentence_embedding_dimension()
        }

    def __repr__(self) -> str:
        stats = self.get_stats()
        return (
            f"<RAGEngine "
            f"documents={stats['total_documents']} "
            f"collection={self.collection_name}>"
        )


# Example usage
if __name__ == "__main__":
    # Create RAG engine
    rag = RAGEngine()

    # Add sample documents
    docs = [
        "The capital of France is Paris. Paris is known for the Eiffel Tower.",
        "Python is a popular programming language used for AI and ML.",
        "Machine learning is a subset of artificial intelligence."
    ]

    rag.add_documents(docs)

    # Search
    results = rag.search("What is the capital of France?", n_results=2)
    print("Search Results:", results)

    # Get formatted context
    context = rag.get_context("Tell me about Python", n_results=2)
    print("\nContext:", context)

    # Stats
    print("\nStats:", rag.get_stats())
