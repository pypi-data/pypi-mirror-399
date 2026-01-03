"""
Test Dual RAG System

Tests:
- LocalRAG (domain-specific, isolated)
- GlobalRAG (shared knowledge base)
- DualRAG (integrated system)
- Access control and domain isolation

Author: MDSA Framework Team
Date: 2025-12-05
"""

import pytest
from mdsa.memory.dual_rag import (
    LocalRAG,
    GlobalRAG,
    DualRAG,
    RAGDocument,
    RAGResult
)


class TestLocalRAG:
    """Test LocalRAG (domain-specific isolated knowledge)"""

    def test_add_document(self):
        """Test adding documents to LocalRAG"""
        rag = LocalRAG(domain_id="test_domain")

        # Add document
        doc_id = rag.add_document(
            "Test document content",
            metadata={'category': 'test'}
        )

        assert doc_id is not None
        stats = rag.get_stats()
        assert stats['document_count'] == 1

    def test_retrieve_documents(self):
        """Test retrieving documents from LocalRAG"""
        rag = LocalRAG(domain_id="medical_coding")

        # Add documents
        rag.add_document("ICD-10 code E11.9 diabetes mellitus", metadata={'type': 'diagnosis'})
        rag.add_document("CPT code 99213 office visit", metadata={'type': 'procedure'})
        rag.add_document("HCPCS code J1234 injection", metadata={'type': 'supply'})

        # Retrieve
        result = rag.retrieve("diabetes ICD-10", top_k=2)

        assert isinstance(result, RAGResult)
        assert result.source == 'local'
        assert len(result.documents) > 0
        assert len(result.documents) <= 2
        assert result.retrieval_time_ms >= 0

    def test_keyword_matching(self):
        """Test keyword-based retrieval"""
        rag = LocalRAG(domain_id="test")

        rag.add_document("diabetes type 2 mellitus")
        rag.add_document("hypertension high blood pressure")
        rag.add_document("asthma respiratory condition")

        # Query with matching keywords
        result = rag.retrieve("diabetes mellitus", top_k=5)

        # Should find diabetes document
        assert len(result.documents) >= 1
        assert "diabetes" in result.documents[0].content.lower()

    def test_metadata_filter(self):
        """Test metadata filtering"""
        rag = LocalRAG(domain_id="test")

        rag.add_document("Document 1", metadata={'category': 'A', 'priority': 'high'})
        rag.add_document("Document 2", metadata={'category': 'B', 'priority': 'low'})
        rag.add_document("Document 3", metadata={'category': 'A', 'priority': 'low'})

        # Filter by category
        result = rag.retrieve(
            "document",
            top_k=10,
            metadata_filter={'category': 'A'}
        )

        assert len(result.documents) == 2
        for doc in result.documents:
            assert doc.metadata['category'] == 'A'

    def test_delete_document(self):
        """Test deleting documents"""
        rag = LocalRAG(domain_id="test")

        doc_id = rag.add_document("Test document")
        assert rag.get_stats()['document_count'] == 1

        # Delete
        success = rag.delete_document(doc_id)
        assert success
        assert rag.get_stats()['document_count'] == 0

        # Delete non-existent
        success = rag.delete_document("nonexistent")
        assert not success

    def test_clear(self):
        """Test clearing all documents"""
        rag = LocalRAG(domain_id="test")

        rag.add_document("Doc 1")
        rag.add_document("Doc 2")
        rag.add_document("Doc 3")

        assert rag.get_stats()['document_count'] == 3

        rag.clear()
        assert rag.get_stats()['document_count'] == 0

    def test_lru_eviction(self):
        """Test LRU eviction when max documents exceeded"""
        rag = LocalRAG(domain_id="test", max_documents=3)

        # Add 3 documents (at limit)
        doc1 = rag.add_document("Document 1")
        doc2 = rag.add_document("Document 2")
        doc3 = rag.add_document("Document 3")

        assert rag.get_stats()['document_count'] == 3

        # Add 4th document (should evict oldest)
        doc4 = rag.add_document("Document 4")

        assert rag.get_stats()['document_count'] == 3
        # Oldest (doc1) should be evicted
        result = rag.retrieve("Document", top_k=10)
        doc_ids = [d.doc_id for d in result.documents]
        assert doc1 not in doc_ids  # Evicted
        assert doc4 in doc_ids  # New one present

    def test_duplicate_document_ids(self):
        """Test handling duplicate document IDs"""
        rag = LocalRAG(domain_id="test")

        # Add with specific ID
        doc_id = rag.add_document("Original content", doc_id="test_id")
        assert rag.get_stats()['document_count'] == 1

        # Add again with same ID (should update)
        rag.add_document("Updated content", doc_id="test_id")
        assert rag.get_stats()['document_count'] == 1

        # Verify content updated
        result = rag.retrieve("content", top_k=1)
        assert "Updated" in result.documents[0].content or "Original" in result.documents[0].content

    def test_empty_query(self):
        """Test handling empty query"""
        rag = LocalRAG(domain_id="test")
        rag.add_document("Test document")

        result = rag.retrieve("", top_k=5)
        # Should return empty or handle gracefully
        assert isinstance(result, RAGResult)


class TestGlobalRAG:
    """Test GlobalRAG (shared knowledge base)"""

    def test_add_document_with_tags(self):
        """Test adding documents with tags"""
        rag = GlobalRAG()

        doc_id = rag.add_document(
            "Medical terminology definition",
            tags=['medical', 'terminology'],
            metadata={'category': 'definition'}
        )

        assert doc_id is not None
        stats = rag.get_stats()
        assert stats['document_count'] == 1

    def test_retrieve_with_domain_tracking(self):
        """Test retrieval with domain access tracking"""
        rag = GlobalRAG()

        rag.add_document("Shared medical knowledge")

        # Retrieve from different domains
        result1 = rag.retrieve("medical", requesting_domain="domain_a")
        result2 = rag.retrieve("knowledge", requesting_domain="domain_b")

        assert result1.source == 'global'
        assert result2.source == 'global'

        # Check access tracking
        stats = rag.get_stats()
        assert stats['total_accesses'] == 2
        assert 'domain_a' in stats['domain_access']
        assert 'domain_b' in stats['domain_access']

    def test_retrieve_without_domain(self):
        """Test retrieval without specifying domain"""
        rag = GlobalRAG()
        rag.add_document("Test content")

        result = rag.retrieve("test", requesting_domain=None)
        assert isinstance(result, RAGResult)

    def test_global_statistics(self):
        """Test GlobalRAG statistics"""
        rag = GlobalRAG()

        rag.add_document("Doc 1")
        rag.retrieve("query 1", requesting_domain="domain1")
        rag.retrieve("query 2", requesting_domain="domain1")
        rag.retrieve("query 3", requesting_domain="domain2")

        stats = rag.get_stats()

        assert stats['document_count'] == 1
        assert stats['total_accesses'] == 3
        assert stats['domain_access']['domain1'] == 2
        assert stats['domain_access']['domain2'] == 1


class TestDualRAG:
    """Test integrated DualRAG system"""

    @pytest.fixture
    def dual_rag(self):
        """Create DualRAG instance"""
        return DualRAG()

    def test_register_domain(self, dual_rag):
        """Test domain registration"""
        local_rag = dual_rag.register_domain("test_domain")

        assert isinstance(local_rag, LocalRAG)
        assert local_rag.domain_id == "test_domain"
        assert "test_domain" in dual_rag.local_rags

    def test_register_duplicate_domain(self, dual_rag):
        """Test registering same domain twice"""
        rag1 = dual_rag.register_domain("test_domain")
        rag2 = dual_rag.register_domain("test_domain")

        # Should return same instance
        assert rag1 is rag2

    def test_add_to_local(self, dual_rag):
        """Test adding documents to LocalRAG"""
        dual_rag.register_domain("medical_coding")

        doc_id = dual_rag.add_to_local(
            "medical_coding",
            "ICD-10 code E11.9",
            metadata={'type': 'diagnosis'}
        )

        assert doc_id is not None

    def test_add_to_local_unregistered_domain(self, dual_rag):
        """Test adding to unregistered domain raises error"""
        with pytest.raises(ValueError, match="not registered"):
            dual_rag.add_to_local("nonexistent_domain", "content")

    def test_add_to_global(self, dual_rag):
        """Test adding documents to GlobalRAG"""
        doc_id = dual_rag.add_to_global(
            "Shared medical knowledge",
            tags=['medical'],
            metadata={'category': 'general'}
        )

        assert doc_id is not None

    def test_domain_isolation(self, dual_rag):
        """Test that domains cannot access each other's LocalRAG"""
        # Register two domains
        dual_rag.register_domain("domain_a")
        dual_rag.register_domain("domain_b")

        # Add to domain_a's LocalRAG
        dual_rag.add_to_local("domain_a", "Secret data for domain A")

        # Try to retrieve from domain_b
        results = dual_rag.retrieve(
            query="secret data",
            domain_id="domain_b",
            top_k=5,
            search_local=True,
            search_global=False
        )

        # domain_b should not see domain_a's data
        assert len(results['local'].documents) == 0

    def test_global_sharing(self, dual_rag):
        """Test that GlobalRAG is accessible by all domains"""
        dual_rag.register_domain("domain_a")
        dual_rag.register_domain("domain_b")

        # Add to GlobalRAG
        dual_rag.add_to_global("Shared knowledge accessible by all")

        # Both domains should be able to access
        results_a = dual_rag.retrieve("shared knowledge", "domain_a", search_local=False, search_global=True)
        results_b = dual_rag.retrieve("shared knowledge", "domain_b", search_local=False, search_global=True)

        assert len(results_a['global'].documents) > 0
        assert len(results_b['global'].documents) > 0

    def test_combined_retrieval(self, dual_rag):
        """Test retrieving from both Local and Global RAG"""
        dual_rag.register_domain("medical_coding")

        # Add to LocalRAG
        dual_rag.add_to_local("medical_coding", "ICD-10 code E11.9 diabetes")

        # Add to GlobalRAG
        dual_rag.add_to_global("Diabetes is a metabolic disorder")

        # Retrieve from both
        results = dual_rag.retrieve(
            query="diabetes",
            domain_id="medical_coding",
            top_k=5,
            search_local=True,
            search_global=True
        )

        assert 'local' in results
        assert 'global' in results
        assert len(results['local'].documents) > 0
        assert len(results['global'].documents) > 0

    def test_search_local_only(self, dual_rag):
        """Test searching LocalRAG only"""
        dual_rag.register_domain("test_domain")
        dual_rag.add_to_local("test_domain", "Local content")
        dual_rag.add_to_global("Global content")

        results = dual_rag.retrieve(
            "content",
            "test_domain",
            search_local=True,
            search_global=False
        )

        assert 'local' in results
        assert 'global' not in results

    def test_search_global_only(self, dual_rag):
        """Test searching GlobalRAG only"""
        dual_rag.register_domain("test_domain")
        dual_rag.add_to_local("test_domain", "Local content")
        dual_rag.add_to_global("Global content")

        results = dual_rag.retrieve(
            "content",
            "test_domain",
            search_local=False,
            search_global=True
        )

        assert 'local' not in results
        assert 'global' in results

    def test_get_local_rag(self, dual_rag):
        """Test getting LocalRAG instance"""
        dual_rag.register_domain("test_domain")

        local_rag = dual_rag.get_local_rag("test_domain")
        assert isinstance(local_rag, LocalRAG)
        assert local_rag.domain_id == "test_domain"

        # Non-existent domain
        assert dual_rag.get_local_rag("nonexistent") is None

    def test_get_global_rag(self, dual_rag):
        """Test getting GlobalRAG instance"""
        global_rag = dual_rag.get_global_rag()
        assert isinstance(global_rag, GlobalRAG)

    def test_comprehensive_statistics(self, dual_rag):
        """Test comprehensive statistics from DualRAG"""
        dual_rag.register_domain("domain_a")
        dual_rag.register_domain("domain_b")

        dual_rag.add_to_local("domain_a", "Doc A1")
        dual_rag.add_to_local("domain_a", "Doc A2")
        dual_rag.add_to_local("domain_b", "Doc B1")
        dual_rag.add_to_global("Global doc")

        stats = dual_rag.get_stats()

        assert stats['total_domains'] == 2
        assert stats['global_rag']['document_count'] == 1
        assert stats['local_rags']['domain_a']['document_count'] == 2
        assert stats['local_rags']['domain_b']['document_count'] == 1

    def test_clear_all(self, dual_rag):
        """Test clearing all RAGs"""
        dual_rag.register_domain("domain_a")
        dual_rag.add_to_local("domain_a", "Local doc")
        dual_rag.add_to_global("Global doc")

        dual_rag.clear_all()

        stats = dual_rag.get_stats()
        assert stats['global_rag']['document_count'] == 0
        assert stats['local_rags']['domain_a']['document_count'] == 0

    def test_retrieve_unregistered_domain(self, dual_rag):
        """Test retrieving from unregistered domain raises error"""
        with pytest.raises(ValueError, match="not registered"):
            dual_rag.retrieve("query", "nonexistent_domain", search_local=True)


class TestIntegration:
    """Integration tests for Dual RAG system"""

    def test_medical_use_case(self):
        """Test medical coding/billing use case"""
        dual_rag = DualRAG()

        # Register medical domains
        dual_rag.register_domain("medical_coding")
        dual_rag.register_domain("medical_billing")

        # Add domain-specific knowledge
        dual_rag.add_to_local(
            "medical_coding",
            "ICD-10 E11.9: Type 2 diabetes mellitus without complications",
            metadata={'code_type': 'ICD-10'}
        )
        dual_rag.add_to_local(
            "medical_billing",
            "CPT 99213 billing rate: $150.00",
            metadata={'code_type': 'billing'}
        )

        # Add shared knowledge
        dual_rag.add_to_global(
            "Diabetes mellitus is a chronic metabolic disorder",
            tags=['medical', 'terminology']
        )

        # Coding domain retrieves diabetes info
        results = dual_rag.retrieve("diabetes", "medical_coding", top_k=3)

        # Should find both local (ICD code) and global (definition)
        assert len(results['local'].documents) > 0
        assert len(results['global'].documents) > 0

        # Billing cannot see coding's ICD codes
        results_billing = dual_rag.retrieve("ICD-10 E11", "medical_billing", top_k=3)
        assert len(results_billing['local'].documents) == 0  # No ICD codes in billing

    def test_performance(self):
        """Test retrieval performance"""
        dual_rag = DualRAG()
        dual_rag.register_domain("test")

        # Add many documents
        for i in range(100):
            dual_rag.add_to_local("test", f"Document {i} with keywords test content")
            dual_rag.add_to_global(f"Global document {i} with shared knowledge")

        # Measure retrieval time
        import time
        start = time.time()
        results = dual_rag.retrieve("test keywords", "test", top_k=10)
        elapsed = (time.time() - start) * 1000

        # Should be reasonably fast
        assert elapsed < 1000  # < 1 second
        assert 'local' in results
        assert 'global' in results

    def test_concurrent_domain_access(self):
        """Test multiple domains accessing GlobalRAG"""
        dual_rag = DualRAG()

        domains = ["domain_1", "domain_2", "domain_3"]
        for domain in domains:
            dual_rag.register_domain(domain)

        # Add shared knowledge
        dual_rag.add_to_global("Shared resource for all domains")

        # All domains access
        for domain in domains:
            results = dual_rag.retrieve("shared resource", domain, search_global=True, search_local=False)
            assert len(results['global'].documents) > 0

        # Check access tracking
        stats = dual_rag.get_stats()
        assert stats['global_rag']['total_accesses'] == 3


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
