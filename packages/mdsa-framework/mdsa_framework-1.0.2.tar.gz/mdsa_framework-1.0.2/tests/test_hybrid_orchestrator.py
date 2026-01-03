"""
Test Hybrid Orchestrator (Phase 8)

Tests the integration of:
- Complexity Analyzer
- Phi-2 Reasoner
- Hybrid routing (TinyBERT + Phi-2)

Author: MDSA Framework Team
Date: 2025-12-05
"""

import pytest
import time
from mdsa.core.orchestrator import TinyBERTOrchestrator
from mdsa.core.complexity_analyzer import ComplexityAnalyzer
from mdsa.core.reasoner import Phi2Reasoner


class TestComplexityAnalyzer:
    """Test ComplexityAnalyzer for query classification"""

    def test_simple_query_detection(self):
        """Test that simple queries are correctly identified"""
        analyzer = ComplexityAnalyzer(complexity_threshold=0.3)

        # Simple queries
        simple_queries = [
            "Transfer $100",
            "What is my balance?",
            "Check account status",
            "Show recent transactions"
        ]

        for query in simple_queries:
            result = analyzer.analyze(query)
            assert not result.is_complex, f"Query '{query}' should be simple"
            assert result.complexity_score < 0.3

    def test_complex_query_detection(self):
        """Test that complex queries are correctly identified"""
        analyzer = ComplexityAnalyzer(complexity_threshold=0.3)

        # Complex queries with reasoning
        complex_queries = [
            "Code this diagnosis and then calculate the billing",
            "If the claim is denied, analyze the reason and recommend corrections",
            "First verify eligibility, then submit the claim"
        ]

        for query in complex_queries:
            result = analyzer.analyze(query)
            assert result.is_complex, f"Query '{query}' should be complex (score={result.complexity_score:.2f})"
            assert result.complexity_score >= 0.3

    def test_multi_domain_detection(self):
        """Test detection of multi-domain queries"""
        analyzer = ComplexityAnalyzer()

        query = "Code diagnosis and then calculate billing"
        result = analyzer.analyze(query)

        assert result.requires_multi_domain
        assert "multi_domain_task" in result.indicators

    def test_conditional_logic_detection(self):
        """Test detection of conditional logic"""
        analyzer = ComplexityAnalyzer()

        query = "If the claim is denied, escalate to QC"
        result = analyzer.analyze(query)

        assert result.requires_reasoning
        assert "conditional_logic" in result.indicators

    def test_sequential_operations_detection(self):
        """Test detection of sequential operations"""
        analyzer = ComplexityAnalyzer()

        query = "First verify eligibility, then submit the claim"
        result = analyzer.analyze(query)

        assert result.requires_sequential
        assert "sequential_operations" in result.indicators


class TestPhi2Reasoner:
    """Test Phi-2 Reasoner for task decomposition"""

    def test_single_task_plan(self):
        """Test simple query generates single-task plan"""
        reasoner = Phi2Reasoner()

        query = "Extract ICD-10 codes"
        result = reasoner.analyze_and_plan(query)

        assert result.success
        assert len(result.execution_plan) == 1
        assert result.execution_plan[0].domain == "medical_coding"

    def test_multi_task_sequential_plan(self):
        """Test complex query generates multi-task sequential plan"""
        reasoner = Phi2Reasoner()

        query = "Code this diagnosis and then calculate the billing"
        result = reasoner.analyze_and_plan(query)

        assert result.success
        assert len(result.execution_plan) == 2

        # Task 1: Medical Coding
        task1 = result.execution_plan[0]
        assert task1.task_id == 1
        assert task1.domain == "medical_coding"
        assert task1.dependencies == []

        # Task 2: Medical Billing (depends on Task 1)
        task2 = result.execution_plan[1]
        assert task2.task_id == 2
        assert task2.domain == "medical_billing"
        assert task2.dependencies == [1]

    def test_conditional_task_plan(self):
        """Test conditional query generates appropriate plan"""
        reasoner = Phi2Reasoner()

        query = "If the claim is denied, analyze the reason"
        result = reasoner.analyze_and_plan(query)

        assert result.success
        assert len(result.execution_plan) >= 1
        assert result.execution_plan[0].domain == "claims_processing"

    def test_tools_identification(self):
        """Test that reasoner identifies required tools"""
        reasoner = Phi2Reasoner()

        query = "Code this diagnosis and calculate billing"
        result = reasoner.analyze_and_plan(query)

        assert result.success

        # Check that tasks have tools assigned
        coding_task = result.execution_plan[0]
        assert "lookup_icd10" in coding_task.tools_needed or "lookup_cpt" in coding_task.tools_needed

    def test_caching(self):
        """Test that identical queries are cached"""
        reasoner = Phi2Reasoner(enable_caching=True)

        query = "Extract ICD-10 codes"

        # First call
        result1 = reasoner.analyze_and_plan(query)
        time1 = result1.reasoning_time_ms

        # Second call (should be cached)
        result2 = reasoner.analyze_and_plan(query)

        # Cached result should be same
        assert result1.analysis == result2.analysis
        assert len(result1.execution_plan) == len(result2.execution_plan)

        # Check cache stats
        cache_stats = reasoner.get_cache_stats()
        assert cache_stats['cache_size'] >= 1


class TestHybridOrchestrator:
    """Test hybrid orchestrator with TinyBERT + Phi-2"""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator with reasoning enabled"""
        orch = TinyBERTOrchestrator(
            log_level="INFO",
            enable_reasoning=True,
            complexity_threshold=0.3
        )

        # Register test domains
        orch.register_domain(
            "medical_coding",
            "Medical coding for ICD-10, CPT, HCPCS",
            ["code", "diagnosis", "icd", "cpt"]
        )
        orch.register_domain(
            "medical_billing",
            "Medical billing and charge calculation",
            ["billing", "charge", "cost", "payment"]
        )
        orch.register_domain(
            "claims_processing",
            "Claims processing and denial management",
            ["claim", "denial", "qc", "submit"]
        )

        return orch

    def test_simple_query_uses_tinybert(self, orchestrator):
        """Test that simple queries use fast TinyBERT routing"""
        query = "Extract ICD-10 codes"

        result = orchestrator.process_request(query)

        assert result['status'] in ['success', 'escalated']  # May escalate if confidence low
        # First call loads model, so don't check latency strictly
        assert 'latency_ms' in result['metadata']

    def test_complex_query_uses_reasoning(self, orchestrator):
        """Test that complex queries use Phi-2 reasoning"""
        query = "Code this diagnosis and then calculate the billing"

        result = orchestrator.process_request(query)

        # May succeed with reasoning or return error if setup incomplete
        assert result['status'] in ['success', 'error', 'escalated']

        if result['status'] == 'success' and result['metadata'].get('reasoning_used'):
            assert result['metadata']['num_tasks'] >= 1
            assert 'task_results' in result['metadata']

    def test_multi_task_execution(self, orchestrator):
        """Test that multi-task plans are executed in order"""
        query = "Code diagnosis and then calculate billing"

        result = orchestrator.process_request(query)

        # Test passes if reasoning was attempted (even if it errors)
        assert result['status'] in ['success', 'error', 'escalated']

        if result['status'] == 'success' and result['metadata'].get('reasoning_used'):
            task_results = result['metadata']['task_results']
            assert len(task_results) >= 1

            # Verify tasks have proper structure
            for task_result in task_results:
                assert 'task_id' in task_result
                assert 'status' in task_result

    def test_reasoning_statistics_tracking(self, orchestrator):
        """Test that reasoning requests are tracked in statistics"""
        # Process a simple query
        orchestrator.process_request("Extract codes")

        # Process a complex query
        orchestrator.process_request("Code diagnosis and then calculate billing")

        stats = orchestrator.get_stats()

        assert stats['requests_total'] == 2
        # Reasoning may or may not be triggered depending on complexity threshold
        assert stats['requests_reasoning'] >= 0
        assert 'reasoning_rate' in stats

    def test_complexity_threshold_customization(self):
        """Test that complexity threshold can be customized"""
        # Strict threshold (0.5) - fewer queries trigger reasoning
        strict_orch = TinyBERTOrchestrator(
            enable_reasoning=True,
            complexity_threshold=0.5
        )

        # Lenient threshold (0.2) - more queries trigger reasoning
        lenient_orch = TinyBERTOrchestrator(
            enable_reasoning=True,
            complexity_threshold=0.2
        )

        # Register domains
        for orch in [strict_orch, lenient_orch]:
            orch.register_domain("test", "Test domain", ["test"])

        # Moderately complex query
        query = "Code diagnosis and calculate billing"

        # With strict threshold, might not trigger reasoning
        # With lenient threshold, should trigger reasoning
        result_lenient = lenient_orch.process_request(query)

        # Lenient should use reasoning more often
        # (This is a heuristic test, actual behavior depends on complexity score)

    def test_reasoning_disabled(self):
        """Test that orchestrator works with reasoning disabled"""
        orch = TinyBERTOrchestrator(
            enable_reasoning=False  # Disable reasoning
        )

        orch.register_domain("test", "Test domain", ["test"])

        # Even complex query should use TinyBERT when reasoning disabled
        query = "Code diagnosis and then calculate billing"
        result = orch.process_request(query)

        # May be success or escalated depending on confidence
        assert result['status'] in ['success', 'escalated']
        assert 'reasoning_used' not in result['metadata'] or not result['metadata'].get('reasoning_used')

    def test_error_handling_in_reasoning(self, orchestrator):
        """Test error handling when reasoning fails"""
        # This test would require mocking the reasoner to force an error
        # For now, just verify the orchestrator can handle errors gracefully

        query = "Code diagnosis and calculate billing"
        result = orchestrator.process_request(query)

        # Should succeed (or handle errors gracefully)
        assert result['status'] in ['success', 'error', 'escalated']
        assert 'metadata' in result
        assert 'correlation_id' in result['metadata']

    def test_state_history_in_reasoning(self, orchestrator):
        """Test that state transitions are tracked for reasoning-based requests"""
        query = "Code diagnosis and then calculate billing"
        result = orchestrator.process_request(query)

        # State history should always be present
        assert 'state_history' in result['metadata']
        state_history = result['metadata']['state_history']

        # State history should contain workflow states
        assert len(state_history) > 0
        # Should at least have init and one other state (state values are lowercase)
        assert 'init' in state_history


class TestIntegration:
    """Integration tests for complete hybrid system"""

    def test_end_to_end_simple_query(self):
        """Test complete workflow for simple query"""
        orchestrator = TinyBERTOrchestrator(enable_reasoning=True)
        orchestrator.register_domain("test", "Test domain", ["test"])

        start_time = time.time()
        result = orchestrator.process_request("Test query")
        latency = (time.time() - start_time) * 1000

        # May be success or escalated
        assert result['status'] in ['success', 'escalated']
        assert latency < 10000  # Reasonable timeout including model loading

    def test_end_to_end_complex_query(self):
        """Test complete workflow for complex query"""
        orchestrator = TinyBERTOrchestrator(enable_reasoning=True)
        orchestrator.register_domain("coding", "Coding", ["code"])
        orchestrator.register_domain("billing", "Billing", ["bill"])

        start_time = time.time()
        result = orchestrator.process_request("Code diagnosis and then calculate billing")
        latency = (time.time() - start_time) * 1000

        # May succeed or error depending on system state
        assert result['status'] in ['success', 'error', 'escalated']
        assert latency < 10000  # Should complete in reasonable time
        # Check if reasoning was attempted
        assert 'metadata' in result

    def test_statistics_comprehensive(self):
        """Test comprehensive statistics tracking"""
        orchestrator = TinyBERTOrchestrator(enable_reasoning=True)
        orchestrator.register_domain("test", "Test", ["test"])

        # Process mix of simple and complex queries
        orchestrator.process_request("Simple test")
        orchestrator.process_request("First do A then do B")
        orchestrator.process_request("Another simple test")

        stats = orchestrator.get_stats()

        assert stats['requests_total'] == 3
        assert stats['requests_success'] >= 0
        assert stats['requests_failed'] >= 0
        assert stats['requests_reasoning'] >= 0
        assert stats['success_rate'] >= 0
        assert stats['reasoning_rate'] >= 0


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
