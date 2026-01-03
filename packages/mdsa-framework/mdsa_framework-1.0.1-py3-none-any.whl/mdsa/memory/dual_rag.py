"""
Dual RAG System

Two-tier Retrieval-Augmented Generation architecture:
- Local RAG: Domain-specific, isolated knowledge (only accessible by owning domain)
- Global RAG: Shared knowledge base (accessible by all domains)

This enables:
1. Domain isolation: Medical coding can't access billing data
2. Knowledge sharing: Common medical terminology accessible by all
3. Privacy: Sensitive domain data stays isolated
4. Efficiency: Smaller local indices, faster retrieval

Author: MDSA Framework Team
Date: 2025-12-05
"""

import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import time
import hashlib
import json
import uuid

# ChromaDB and embeddings
try:
    import chromadb
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    chromadb = None
    SentenceTransformer = None

# Platform detection
try:
    from mdsa.config.platform_detector import get_vector_db_path, detect_platform_kb_path
    PLATFORM_DETECTOR_AVAILABLE = True
except ImportError:
    PLATFORM_DETECTOR_AVAILABLE = False
    get_vector_db_path = None
    detect_platform_kb_path = None

logger = logging.getLogger(__name__)


@dataclass
class RAGDocument:
    """Document for RAG storage"""
    doc_id: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None
    timestamp: float = field(default_factory=time.time)

    def __repr__(self) -> str:
        return f"<RAGDocument id={self.doc_id} content_len={len(self.content)}>"


@dataclass
class RAGResult:
    """Result from RAG retrieval"""
    documents: List[RAGDocument]
    scores: List[float]
    query: str
    retrieval_time_ms: float
    source: str  # 'local' or 'global'

    def __repr__(self) -> str:
        return (f"<RAGResult docs={len(self.documents)} "
                f"source={self.source} time={self.retrieval_time_ms:.1f}ms>")


class LocalRAG:
    """
    Domain-specific isolated RAG.

    Each domain has its own LocalRAG instance that other domains cannot access.
    Example: Medical coding domain has ICD-10 codes, medical billing cannot access them.
    """

    def __init__(self, domain_id: str, max_documents: int = 1000):
        """
        Initialize Local RAG for a specific domain.

        Args:
            domain_id: Domain identifier (owner of this RAG)
            max_documents: Maximum documents to store (LRU eviction)
        """
        self.domain_id = domain_id
        self.max_documents = max_documents
        self._documents: Dict[str, RAGDocument] = {}
        self._index: Dict[str, Set[str]] = {}  # keyword -> doc_ids

        logger.info(f"LocalRAG initialized for domain '{domain_id}'")

    def add_document(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        doc_id: Optional[str] = None
    ) -> str:
        """
        Add document to local RAG.

        Args:
            content: Document content
            metadata: Optional metadata
            doc_id: Optional document ID (auto-generated if not provided)

        Returns:
            Document ID
        """
        if doc_id is None:
            # Generate unique ID from content hash
            doc_id = hashlib.md5(content.encode()).hexdigest()[:16]

        # Check if already exists
        if doc_id in self._documents:
            logger.debug(f"Document {doc_id} already exists, updating")

        # Create document
        doc = RAGDocument(
            doc_id=doc_id,
            content=content,
            metadata=metadata or {},
            timestamp=time.time()
        )

        # Add to storage
        self._documents[doc_id] = doc

        # Index keywords
        self._index_document(doc)

        # Evict old documents if over limit
        if len(self._documents) > self.max_documents:
            self._evict_oldest()

        logger.debug(f"Added document {doc_id} to LocalRAG '{self.domain_id}'")
        return doc_id

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> RAGResult:
        """
        Retrieve relevant documents from local RAG.

        Args:
            query: Search query
            top_k: Number of top results to return
            metadata_filter: Optional metadata filter

        Returns:
            RAGResult with retrieved documents
        """
        start_time = time.time()

        # Extract keywords from query
        query_keywords = self._extract_keywords(query.lower())

        # Find matching documents
        doc_scores: Dict[str, float] = {}

        for keyword in query_keywords:
            if keyword in self._index:
                for doc_id in self._index[keyword]:
                    doc_scores[doc_id] = doc_scores.get(doc_id, 0) + 1.0

        # Apply metadata filter
        if metadata_filter:
            filtered_scores = {}
            for doc_id, score in doc_scores.items():
                doc = self._documents[doc_id]
                if self._matches_filter(doc.metadata, metadata_filter):
                    filtered_scores[doc_id] = score
            doc_scores = filtered_scores

        # Sort by score
        sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

        # Build result
        documents = [self._documents[doc_id] for doc_id, _ in sorted_docs]
        scores = [score for _, score in sorted_docs]

        retrieval_time_ms = (time.time() - start_time) * 1000

        result = RAGResult(
            documents=documents,
            scores=scores,
            query=query,
            retrieval_time_ms=retrieval_time_ms,
            source='local'
        )

        logger.debug(
            f"LocalRAG '{self.domain_id}' retrieved {len(documents)} docs "
            f"in {retrieval_time_ms:.1f}ms"
        )

        return result

    def delete_document(self, doc_id: str) -> bool:
        """Delete document from local RAG"""
        if doc_id in self._documents:
            doc = self._documents[doc_id]
            # Remove from index
            for keyword in self._extract_keywords(doc.content.lower()):
                if keyword in self._index:
                    self._index[keyword].discard(doc_id)
            # Remove document
            del self._documents[doc_id]
            logger.debug(f"Deleted document {doc_id} from LocalRAG '{self.domain_id}'")
            return True
        return False

    def clear(self):
        """Clear all documents from local RAG"""
        self._documents.clear()
        self._index.clear()
        logger.info(f"Cleared LocalRAG '{self.domain_id}'")

    def get_stats(self) -> Dict[str, Any]:
        """Get RAG statistics"""
        return {
            'domain_id': self.domain_id,
            'document_count': len(self._documents),
            'index_size': len(self._index),
            'max_documents': self.max_documents
        }

    def _index_document(self, doc: RAGDocument):
        """Index document keywords"""
        keywords = self._extract_keywords(doc.content.lower())
        for keyword in keywords:
            if keyword not in self._index:
                self._index[keyword] = set()
            self._index[keyword].add(doc.doc_id)

    def _extract_keywords(self, text: str) -> Set[str]:
        """Extract keywords from text (simple tokenization)"""
        # Remove punctuation and split
        import re
        words = re.findall(r'\b\w+\b', text.lower())
        # Filter stop words and short words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with'}
        keywords = {w for w in words if len(w) > 2 and w not in stop_words}
        return keywords

    def _matches_filter(self, metadata: Dict[str, Any], filter_dict: Dict[str, Any]) -> bool:
        """Check if metadata matches filter"""
        for key, value in filter_dict.items():
            if key not in metadata or metadata[key] != value:
                return False
        return True

    def _evict_oldest(self):
        """Evict oldest document (LRU)"""
        if not self._documents:
            return

        # Find oldest document
        oldest_id = min(self._documents.keys(), key=lambda k: self._documents[k].timestamp)
        self.delete_document(oldest_id)
        logger.debug(f"Evicted oldest document {oldest_id} from LocalRAG '{self.domain_id}'")


class GlobalRAG:
    """
    Shared knowledge base accessible by all domains.

    Contains common knowledge that all domains can access.
    Example: Common medical terminology, drug databases, etc.
    """

    def __init__(self, max_documents: int = 10000):
        """
        Initialize Global RAG.

        Args:
            max_documents: Maximum documents to store
        """
        self.max_documents = max_documents
        self._documents: Dict[str, RAGDocument] = {}
        self._index: Dict[str, Set[str]] = {}
        self._access_log: List[Dict[str, Any]] = []  # Track which domains access what

        logger.info("GlobalRAG initialized (shared knowledge base)")

    def add_document(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        doc_id: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> str:
        """
        Add document to global RAG.

        Args:
            content: Document content
            metadata: Optional metadata
            doc_id: Optional document ID
            tags: Optional tags for categorization

        Returns:
            Document ID
        """
        if doc_id is None:
            doc_id = hashlib.md5(content.encode()).hexdigest()[:16]

        # Ensure tags in metadata
        if metadata is None:
            metadata = {}
        if tags:
            metadata['tags'] = tags

        # Create document
        doc = RAGDocument(
            doc_id=doc_id,
            content=content,
            metadata=metadata,
            timestamp=time.time()
        )

        # Add to storage
        self._documents[doc_id] = doc

        # Index
        self._index_document(doc)

        # Evict if needed
        if len(self._documents) > self.max_documents:
            self._evict_oldest()

        logger.debug(f"Added document {doc_id} to GlobalRAG")
        return doc_id

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        metadata_filter: Optional[Dict[str, Any]] = None,
        requesting_domain: Optional[str] = None
    ) -> RAGResult:
        """
        Retrieve relevant documents from global RAG.

        Args:
            query: Search query
            top_k: Number of top results
            metadata_filter: Optional metadata filter
            requesting_domain: Domain making the request (for logging)

        Returns:
            RAGResult with retrieved documents
        """
        start_time = time.time()

        # Log access
        if requesting_domain:
            self._access_log.append({
                'domain': requesting_domain,
                'query': query[:50],
                'timestamp': time.time()
            })

        # Extract keywords
        query_keywords = self._extract_keywords(query.lower())

        # Find matching documents
        doc_scores: Dict[str, float] = {}

        for keyword in query_keywords:
            if keyword in self._index:
                for doc_id in self._index[keyword]:
                    doc_scores[doc_id] = doc_scores.get(doc_id, 0) + 1.0

        # Apply metadata filter
        if metadata_filter:
            filtered_scores = {}
            for doc_id, score in doc_scores.items():
                doc = self._documents[doc_id]
                if self._matches_filter(doc.metadata, metadata_filter):
                    filtered_scores[doc_id] = score
            doc_scores = filtered_scores

        # Sort by score
        sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

        # Build result
        documents = [self._documents[doc_id] for doc_id, _ in sorted_docs]
        scores = [score for _, score in sorted_docs]

        retrieval_time_ms = (time.time() - start_time) * 1000

        result = RAGResult(
            documents=documents,
            scores=scores,
            query=query,
            retrieval_time_ms=retrieval_time_ms,
            source='global'
        )

        logger.debug(
            f"GlobalRAG retrieved {len(documents)} docs "
            f"for domain '{requesting_domain}' in {retrieval_time_ms:.1f}ms"
        )

        return result

    def delete_document(self, doc_id: str) -> bool:
        """Delete document from global RAG"""
        if doc_id in self._documents:
            doc = self._documents[doc_id]
            # Remove from index
            for keyword in self._extract_keywords(doc.content.lower()):
                if keyword in self._index:
                    self._index[keyword].discard(doc_id)
            del self._documents[doc_id]
            logger.debug(f"Deleted document {doc_id} from GlobalRAG")
            return True
        return False

    def clear(self):
        """Clear all documents"""
        self._documents.clear()
        self._index.clear()
        self._access_log.clear()
        logger.info("Cleared GlobalRAG")

    def get_stats(self) -> Dict[str, Any]:
        """Get RAG statistics"""
        # Count access by domain
        domain_access = {}
        for log_entry in self._access_log:
            domain = log_entry['domain']
            domain_access[domain] = domain_access.get(domain, 0) + 1

        return {
            'document_count': len(self._documents),
            'index_size': len(self._index),
            'max_documents': self.max_documents,
            'total_accesses': len(self._access_log),
            'domain_access': domain_access
        }

    def _index_document(self, doc: RAGDocument):
        """Index document keywords"""
        keywords = self._extract_keywords(doc.content.lower())
        for keyword in keywords:
            if keyword not in self._index:
                self._index[keyword] = set()
            self._index[keyword].add(doc.doc_id)

    def _extract_keywords(self, text: str) -> Set[str]:
        """Extract keywords from text"""
        import re
        words = re.findall(r'\b\w+\b', text.lower())
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with'}
        keywords = {w for w in words if len(w) > 2 and w not in stop_words}
        return keywords

    def _matches_filter(self, metadata: Dict[str, Any], filter_dict: Dict[str, Any]) -> bool:
        """Check if metadata matches filter"""
        for key, value in filter_dict.items():
            if key not in metadata or metadata[key] != value:
                return False
        return True

    def _evict_oldest(self):
        """Evict oldest document"""
        if not self._documents:
            return
        oldest_id = min(self._documents.keys(), key=lambda k: self._documents[k].timestamp)
        self.delete_document(oldest_id)
        logger.debug(f"Evicted oldest document {oldest_id} from GlobalRAG")


class DualRAG:
    """
    Dual RAG System combining Local and Global RAG.

    Provides:
    1. Domain isolation: Each domain has isolated LocalRAG
    2. Knowledge sharing: GlobalRAG accessible by all
    3. Access control: Domains cannot access other domains' LocalRAG
    4. Unified interface: Single query interface for both RAGs
    """

    def __init__(self, max_global_docs: int = 10000, max_local_docs: int = 1000):
        """
        Initialize Dual RAG system with ChromaDB persistence.

        Args:
            max_global_docs: Maximum documents in GlobalRAG
            max_local_docs: Maximum documents per LocalRAG
        """
        self.global_rag = GlobalRAG(max_documents=max_global_docs)
        self.local_rags: Dict[str, LocalRAG] = {}
        self.max_local_docs = max_local_docs

        # ChromaDB persistence
        self.chroma_client = None
        self.global_collection = None
        self.local_collections: Dict[str, Any] = {}
        self.embedding_model = None
        self.vector_db_path = None

        # Initialize ChromaDB if available
        if CHROMADB_AVAILABLE and PLATFORM_DETECTOR_AVAILABLE:
            try:
                self.vector_db_path = get_vector_db_path()
                self.chroma_client = chromadb.PersistentClient(
                    path=str(self.vector_db_path),
                    settings=Settings(anonymized_telemetry=False)
                )

                # Global collection
                self.global_collection = self.chroma_client.get_or_create_collection(
                    name="global_rag",
                    metadata={"description": "Global RAG documents (shared knowledge)"}
                )

                # Initialize embedding model
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

                logger.info(f"[RAG] ChromaDB initialized at: {self.vector_db_path}")
                logger.info(f"[RAG] Embedding model loaded: all-MiniLM-L6-v2")

                # Load existing documents from disk
                self._load_from_disk()

            except Exception as e:
                logger.warning(f"[RAG] ChromaDB initialization failed: {e}")
                logger.warning("[RAG] Falling back to in-memory RAG only")
                self.chroma_client = None
        else:
            missing = []
            if not CHROMADB_AVAILABLE:
                missing.append("chromadb, sentence-transformers")
            if not PLATFORM_DETECTOR_AVAILABLE:
                missing.append("platform_detector")
            logger.warning(f"[RAG] Missing dependencies: {', '.join(missing)}")
            logger.warning("[RAG] Using in-memory RAG only (no persistence)")

        logger.info("DualRAG system initialized")

    def register_domain(self, domain_id: str) -> LocalRAG:
        """
        Register a domain and create its LocalRAG.

        Args:
            domain_id: Domain identifier

        Returns:
            LocalRAG instance for the domain
        """
        if domain_id in self.local_rags:
            logger.warning(f"Domain '{domain_id}' already registered")
            return self.local_rags[domain_id]

        local_rag = LocalRAG(domain_id=domain_id, max_documents=self.max_local_docs)
        self.local_rags[domain_id] = local_rag

        logger.info(f"Registered domain '{domain_id}' with LocalRAG")
        return local_rag

    def add_to_local(
        self,
        domain_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        doc_id: Optional[str] = None
    ) -> str:
        """
        Add document to domain's LocalRAG with ChromaDB persistence.

        Args:
            domain_id: Domain identifier
            content: Document content
            metadata: Optional metadata
            doc_id: Optional document ID

        Returns:
            Document ID

        Raises:
            ValueError: If domain not registered
        """
        if domain_id not in self.local_rags:
            raise ValueError(f"Domain '{domain_id}' not registered. Call register_domain() first.")

        # Add to in-memory LocalRAG
        doc_id = self.local_rags[domain_id].add_document(content, metadata, doc_id)

        # Persist to ChromaDB if available
        if self.chroma_client and self.embedding_model:
            try:
                # Get or create collection for this domain
                collection_name = f"local_rag_{domain_id}"
                if domain_id not in self.local_collections:
                    self.local_collections[domain_id] = self.chroma_client.get_or_create_collection(
                        name=collection_name,
                        metadata={"domain": domain_id, "description": f"Local RAG for {domain_id}"}
                    )

                # Generate embedding
                embedding = self.embedding_model.encode(content).tolist()

                # Prepare metadata
                chroma_metadata = metadata.copy() if metadata else {}
                chroma_metadata['domain'] = domain_id
                chroma_metadata['timestamp'] = datetime.now().isoformat()

                # Convert all metadata values to strings
                chroma_metadata = {k: str(v) for k, v in chroma_metadata.items()}

                # Add to ChromaDB
                self.local_collections[domain_id].add(
                    ids=[doc_id],
                    documents=[content],
                    metadatas=[chroma_metadata],
                    embeddings=[embedding]
                )

                logger.debug(f"[RAG] Persisted local document {doc_id} to ChromaDB (domain: {domain_id})")

            except Exception as e:
                logger.error(f"[RAG] Failed to persist local document to ChromaDB: {e}")

        return doc_id

    def add_to_global(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        doc_id: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> str:
        """
        Add document to GlobalRAG (accessible by all domains) with ChromaDB persistence.

        Args:
            content: Document content
            metadata: Optional metadata
            doc_id: Optional document ID
            tags: Optional tags

        Returns:
            Document ID
        """
        # Add to in-memory GlobalRAG
        doc_id = self.global_rag.add_document(content, metadata, doc_id, tags)

        # Persist to ChromaDB if available
        if self.chroma_client and self.global_collection and self.embedding_model:
            try:
                # Generate embedding
                embedding = self.embedding_model.encode(content).tolist()

                # Prepare metadata (ChromaDB requires dict with string values)
                chroma_metadata = metadata.copy() if metadata else {}
                if tags:
                    chroma_metadata['tags'] = ','.join(tags)
                chroma_metadata['timestamp'] = datetime.now().isoformat()

                # Convert all metadata values to strings for ChromaDB
                chroma_metadata = {k: str(v) for k, v in chroma_metadata.items()}

                # Add to ChromaDB
                self.global_collection.add(
                    ids=[doc_id],
                    documents=[content],
                    metadatas=[chroma_metadata],
                    embeddings=[embedding]
                )

                logger.debug(f"[RAG] Persisted global document {doc_id} to ChromaDB")

            except Exception as e:
                logger.error(f"[RAG] Failed to persist document to ChromaDB: {e}")

        return doc_id

    def retrieve(
        self,
        query: str,
        domain_id: str,
        top_k: int = 5,
        search_local: bool = True,
        search_global: bool = True,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> Dict[str, RAGResult]:
        """
        Retrieve from both Local and Global RAG using embedding-based similarity search.

        If ChromaDB is available, uses vector similarity search.
        Otherwise, falls back to keyword-based search.

        Args:
            query: Search query
            domain_id: Requesting domain
            top_k: Number of results per RAG
            search_local: Search LocalRAG
            search_global: Search GlobalRAG
            metadata_filter: Optional metadata filter

        Returns:
            Dict with 'local' and 'global' RAGResults

        Raises:
            ValueError: If domain not registered and search_local=True
        """
        results = {}
        start_time = time.time()

        # Use ChromaDB if available, otherwise fallback to keyword search
        use_chromadb = self.chroma_client and self.embedding_model

        # Search LocalRAG (domain-specific)
        if search_local:
            if domain_id not in self.local_rags:
                raise ValueError(f"Domain '{domain_id}' not registered")

            if use_chromadb and domain_id in self.local_collections:
                # Use ChromaDB embedding-based search
                try:
                    query_embedding = self.embedding_model.encode(query).tolist()

                    # Prepare where filter if metadata_filter provided
                    where_filter = None
                    if metadata_filter:
                        where_filter = {k: {"$eq": str(v)} for k, v in metadata_filter.items()}

                    chroma_results = self.local_collections[domain_id].query(
                        query_embeddings=[query_embedding],
                        n_results=top_k,
                        where=where_filter
                    )

                    # Convert to RAGResult format
                    documents = []
                    scores = []
                    if chroma_results['ids'] and chroma_results['ids'][0]:
                        for i, doc_id in enumerate(chroma_results['ids'][0]):
                            doc = RAGDocument(
                                doc_id=doc_id,
                                content=chroma_results['documents'][0][i],
                                metadata=chroma_results['metadatas'][0][i],
                                timestamp=time.time()
                            )
                            documents.append(doc)
                            # Convert distance to score (lower distance = higher score)
                            distance = chroma_results['distances'][0][i]
                            scores.append(1.0 / (1.0 + distance))

                    retrieval_time_ms = (time.time() - start_time) * 1000
                    results['local'] = RAGResult(
                        documents=documents,
                        scores=scores,
                        query=query,
                        retrieval_time_ms=retrieval_time_ms,
                        source='local'
                    )

                    logger.debug(f"[RAG] ChromaDB local search: {len(documents)} docs in {retrieval_time_ms:.1f}ms")

                except Exception as e:
                    logger.error(f"[RAG] ChromaDB local search failed: {e}, falling back to keyword search")
                    # Fallback to keyword search
                    results['local'] = self.local_rags[domain_id].retrieve(
                        query=query,
                        top_k=top_k,
                        metadata_filter=metadata_filter
                    )
            else:
                # Fallback to keyword-based search
                results['local'] = self.local_rags[domain_id].retrieve(
                    query=query,
                    top_k=top_k,
                    metadata_filter=metadata_filter
                )

        # Search GlobalRAG (shared)
        if search_global:
            if use_chromadb and self.global_collection:
                # Use ChromaDB embedding-based search
                try:
                    query_embedding = self.embedding_model.encode(query).tolist()

                    # Prepare where filter
                    where_filter = None
                    if metadata_filter:
                        where_filter = {k: {"$eq": str(v)} for k, v in metadata_filter.items()}

                    chroma_results = self.global_collection.query(
                        query_embeddings=[query_embedding],
                        n_results=top_k,
                        where=where_filter
                    )

                    # Convert to RAGResult format
                    documents = []
                    scores = []
                    if chroma_results['ids'] and chroma_results['ids'][0]:
                        for i, doc_id in enumerate(chroma_results['ids'][0]):
                            doc = RAGDocument(
                                doc_id=doc_id,
                                content=chroma_results['documents'][0][i],
                                metadata=chroma_results['metadatas'][0][i],
                                timestamp=time.time()
                            )
                            documents.append(doc)
                            distance = chroma_results['distances'][0][i]
                            scores.append(1.0 / (1.0 + distance))

                    retrieval_time_ms = (time.time() - start_time) * 1000
                    results['global'] = RAGResult(
                        documents=documents,
                        scores=scores,
                        query=query,
                        retrieval_time_ms=retrieval_time_ms,
                        source='global'
                    )

                    logger.debug(f"[RAG] ChromaDB global search: {len(documents)} docs in {retrieval_time_ms:.1f}ms")

                except Exception as e:
                    logger.error(f"[RAG] ChromaDB global search failed: {e}, falling back to keyword search")
                    # Fallback to keyword search
                    results['global'] = self.global_rag.retrieve(
                        query=query,
                        top_k=top_k,
                        metadata_filter=metadata_filter,
                        requesting_domain=domain_id
                    )
            else:
                # Fallback to keyword-based search
                results['global'] = self.global_rag.retrieve(
                    query=query,
                    top_k=top_k,
                    metadata_filter=metadata_filter,
                    requesting_domain=domain_id
                )

        return results

    def get_local_rag(self, domain_id: str) -> Optional[LocalRAG]:
        """Get LocalRAG for a domain (for direct access)"""
        return self.local_rags.get(domain_id)

    def get_global_rag(self) -> GlobalRAG:
        """Get GlobalRAG (for direct access)"""
        return self.global_rag

    def _load_from_disk(self):
        """
        Load existing documents from ChromaDB into memory on startup.

        This restores all global and local RAG documents that were persisted.
        """
        if not self.chroma_client:
            return

        try:
            # Load global documents
            if self.global_collection:
                global_data = self.global_collection.get()
                loaded_global = 0

                if global_data['ids']:
                    for i, doc_id in enumerate(global_data['ids']):
                        content = global_data['documents'][i]
                        metadata = global_data['metadatas'][i]

                        # Add to in-memory GlobalRAG (skip ChromaDB persistence)
                        self.global_rag._documents[doc_id] = RAGDocument(
                            doc_id=doc_id,
                            content=content,
                            metadata=metadata,
                            timestamp=time.time()
                        )
                        # Index for keyword search
                        self.global_rag._index_document(self.global_rag._documents[doc_id])
                        loaded_global += 1

                logger.info(f"[RAG] Loaded {loaded_global} documents from global collection")

            # Load local collections
            all_collections = self.chroma_client.list_collections()
            loaded_local = 0

            for collection in all_collections:
                if collection.name.startswith('local_rag_'):
                    domain_id = collection.name.replace('local_rag_', '')

                    # Register domain if not already registered
                    if domain_id not in self.local_rags:
                        self.register_domain(domain_id)

                    # Store collection reference
                    self.local_collections[domain_id] = collection

                    # Load documents
                    local_data = collection.get()
                    if local_data and local_data.get('ids'):
                        for i, doc_id in enumerate(local_data['ids']):
                            content = local_data['documents'][i]
                            metadata = local_data['metadatas'][i]

                            # Add to in-memory LocalRAG (skip ChromaDB persistence)
                            self.local_rags[domain_id]._documents[doc_id] = RAGDocument(
                                doc_id=doc_id,
                                content=content,
                                metadata=metadata,
                                timestamp=time.time()
                            )
                            # Index for keyword search
                            self.local_rags[domain_id]._index_document(
                                self.local_rags[domain_id]._documents[doc_id]
                            )
                            loaded_local += 1

                        logger.info(f"[RAG] Loaded {len(local_data['ids'])} documents from local collection '{domain_id}'")

            if loaded_local > 0:
                logger.info(f"[RAG] Total local documents loaded: {loaded_local}")

        except Exception as e:
            logger.error(f"[RAG] Failed to load documents from disk: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics"""
        local_stats = {
            domain_id: rag.get_stats()
            for domain_id, rag in self.local_rags.items()
        }

        return {
            'global_rag': self.global_rag.get_stats(),
            'local_rags': local_stats,
            'total_domains': len(self.local_rags)
        }

    def clear_all(self):
        """Clear all RAGs (global and all local)"""
        self.global_rag.clear()
        for rag in self.local_rags.values():
            rag.clear()
        logger.info("Cleared all RAGs in DualRAG system")


if __name__ == "__main__":
    # Demo usage
    print("=== Dual RAG System Demo ===\n")

    # Initialize
    dual_rag = DualRAG()

    # Register domains
    print("1. Registering domains...")
    dual_rag.register_domain("medical_coding")
    dual_rag.register_domain("medical_billing")
    print("   [+] medical_coding")
    print("   [+] medical_billing\n")

    # Add to LocalRAG (domain-specific, isolated)
    print("2. Adding domain-specific knowledge (LocalRAG)...")
    dual_rag.add_to_local(
        "medical_coding",
        "ICD-10 code E11.9: Type 2 diabetes mellitus without complications",
        metadata={'code_type': 'ICD-10', 'category': 'diagnosis'}
    )
    dual_rag.add_to_local(
        "medical_coding",
        "CPT code 99213: Office visit, established patient, level 3",
        metadata={'code_type': 'CPT', 'category': 'procedure'}
    )
    print("   [+] Added ICD-10 codes to medical_coding")
    print("   [+] Added CPT codes to medical_coding\n")

    # Add to GlobalRAG (shared)
    print("3. Adding shared knowledge (GlobalRAG)...")
    dual_rag.add_to_global(
        "Diabetes mellitus is a metabolic disorder characterized by high blood sugar",
        tags=['medical', 'terminology'],
        metadata={'category': 'definition'}
    )
    dual_rag.add_to_global(
        "Common diabetes medications: Metformin, Insulin, Glipizide",
        tags=['medical', 'pharmacy'],
        metadata={'category': 'treatment'}
    )
    print("   [+] Added medical definitions")
    print("   [+] Added medication information\n")

    # Retrieve from medical_coding domain
    print("4. Querying from medical_coding domain...")
    results = dual_rag.retrieve(
        query="diabetes ICD-10 code",
        domain_id="medical_coding",
        top_k=3
    )

    print("   LocalRAG results:")
    for doc, score in zip(results['local'].documents, results['local'].scores):
        print(f"     - [{score:.1f}] {doc.content[:60]}...")

    print("   GlobalRAG results:")
    for doc, score in zip(results['global'].documents, results['global'].scores):
        print(f"     - [{score:.1f}] {doc.content[:60]}...")

    # Try to access from medical_billing (should not see coding's LocalRAG)
    print("\n5. Querying from medical_billing domain...")
    results = dual_rag.retrieve(
        query="diabetes",
        domain_id="medical_billing",
        top_k=3
    )

    print(f"   LocalRAG results: {len(results['local'].documents)} docs (billing has no diabetes data)")
    print(f"   GlobalRAG results: {len(results['global'].documents)} docs (shared knowledge)")

    # Statistics
    print("\n6. Statistics:")
    stats = dual_rag.get_stats()
    print(f"   GlobalRAG: {stats['global_rag']['document_count']} documents")
    print(f"   medical_coding LocalRAG: {stats['local_rags']['medical_coding']['document_count']} documents")
    print(f"   medical_billing LocalRAG: {stats['local_rags']['medical_billing']['document_count']} documents")

    print("\n[SUCCESS] Dual RAG system demonstration complete!")
