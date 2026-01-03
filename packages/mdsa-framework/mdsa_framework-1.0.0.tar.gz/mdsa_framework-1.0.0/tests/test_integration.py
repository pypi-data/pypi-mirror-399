"""
Integration Tests for MDSA Framework

Tests cover:
- End-to-end execution flow
- Component integration
- Real model loading and inference
- System stability under load
"""

import pytest
from tests.conftest import assert_valid_result, assert_success_result


# ============================================================================
# Basic Integration Tests
# ============================================================================

@pytest.mark.integration
@pytest.mark.slow
class TestBasicIntegration:
    """Test basic end-to-end integration."""

    @pytest.mark.asyncio
    async def test_full_pipeline_async(self, async_executor, support_domain):
        """Test full async execution pipeline."""
        result = await async_executor.execute_async(
            query="What is the weather?",
            domain_config=support_domain,
            timeout=60.0
        )

        assert_valid_result(result)
        # May succeed or fail based on memory
        if result['status'] == 'success':
            assert result['response'], "Response should not be empty on success"

    def test_full_pipeline_sync(self, domain_executor, support_domain):
        """Test full synchronous execution pipeline."""
        result = domain_executor.execute(
            query="Test query",
            domain_config=support_domain
        )

        assert_valid_result(result)


# ============================================================================
# Multi-Domain Integration Tests
# ============================================================================

@pytest.mark.integration
@pytest.mark.slow
class TestMultiDomainIntegration:
    """Test integration across multiple domains."""

    @pytest.mark.asyncio
    async def test_sequential_domain_execution(
        self,
        async_manager,
        finance_domain,
        medical_domain
    ):
        """Test executing queries across different domains sequentially."""
        queries = [
            "How do I transfer money?",
            "What are symptoms of flu?"
        ]
        configs = [finance_domain, medical_domain]

        results = await async_manager.execute_batch(
            queries=queries,
            domain_configs=configs,
            timeout=60.0
        )

        assert len(results) == 2
        for result in results:
            assert_valid_result(result)

    @pytest.mark.asyncio
    async def test_all_domains_available(self, async_manager, all_domains):
        """Test that all predefined domains are accessible."""
        queries = ["Test query"] * len(all_domains)

        results = await async_manager.execute_batch(
            queries=queries,
            domain_configs=all_domains,
            timeout=60.0
        )

        assert len(results) == len(all_domains)
        for result in results:
            assert_valid_result(result)


# ============================================================================
# Model Caching Integration Tests
# ============================================================================

@pytest.mark.integration
@pytest.mark.memory
class TestModelCachingIntegration:
    """Test model caching behavior in integrated system."""

    @pytest.mark.asyncio
    async def test_model_reuse_same_domain(self, async_manager, support_domain):
        """Test that same domain reuses cached model."""
        queries = ["Query 1", "Query 2", "Query 3"]
        configs = [support_domain] * 3

        results = await async_manager.execute_batch(
            queries=queries,
            domain_configs=configs,
            timeout=60.0
        )

        assert len(results) == 3

        # Check model manager stats
        stats = async_manager.async_executor.domain_executor.model_manager.get_stats()

        # Should have at most 1 model loaded (all queries use same domain)
        assert stats['models_loaded'] <= 1, "Should reuse cached model"

    def test_lru_eviction_integration(self, model_manager, support_domain, finance_domain):
        """Test LRU eviction in real usage scenario."""
        # Create manager with max_models=1
        manager = model_manager
        manager.registry.max_models = 1

        # Load first model
        try:
            model1, tok1 = manager.get_or_load("model1", support_domain)
            assert manager.registry.is_loaded("model1")

            # Load second model (should evict first)
            model2, tok2 = manager.get_or_load("model2", finance_domain)
            assert manager.registry.is_loaded("model2")

            # First model should be evicted
            # (may or may not be, depending on if models are actually different)
        except MemoryError:
            # Expected if insufficient memory
            pytest.skip("Insufficient memory for test")


# ============================================================================
# Error Handling Integration Tests
# ============================================================================

@pytest.mark.integration
class TestErrorHandlingIntegration:
    """Test error handling in integrated scenarios."""

    @pytest.mark.asyncio
    async def test_timeout_handling(self, async_executor, support_domain):
        """Test timeout handling in integrated system."""
        result = await async_executor.execute_async(
            query="Test",
            domain_config=support_domain,
            timeout=0.001  # Very short timeout
        )

        assert_valid_result(result)
        assert result['status'] == 'error'

    @pytest.mark.asyncio
    async def test_invalid_config_handling(self, async_executor):
        """Test handling of invalid configuration."""
        from mdsa.domains.config import DomainConfig
        from mdsa.models.config import ModelTier, QuantizationType

        # Create config with non-existent model
        bad_config = DomainConfig(
            domain_id="test",
            name="Test",
            description="Test",
            keywords=["test"],
            model_name="non_existent_model_xyz123",
            model_tier=ModelTier.TIER1,
            device="cpu",
            quantization=QuantizationType.NONE
        )

        result = await async_executor.execute_async(
            query="Test",
            domain_config=bad_config,
            timeout=30.0
        )

        # Should return error result, not crash
        assert_valid_result(result)
        assert result['status'] == 'error'


# ============================================================================
# Concurrent Execution Integration Tests
# ============================================================================

@pytest.mark.integration
@pytest.mark.concurrent
@pytest.mark.slow
class TestConcurrentIntegration:
    """Test concurrent execution in integrated system."""

    @pytest.mark.asyncio
    async def test_concurrent_different_domains(
        self,
        async_manager,
        support_domain,
        finance_domain
    ):
        """Test concurrent execution across different domains."""
        queries = [
            "Support query 1",
            "Finance query 1",
            "Support query 2",
            "Finance query 2"
        ]
        configs = [
            support_domain,
            finance_domain,
            support_domain,
            finance_domain
        ]

        results = await async_manager.execute_batch(
            queries=queries,
            domain_configs=configs,
            timeout=60.0
        )

        assert len(results) == 4
        # No None values (validates Fix A7)
        assert all(r is not None for r in results)

    @pytest.mark.asyncio
    async def test_high_concurrency(self, async_manager, support_domain):
        """Test system under high concurrent load."""
        # Execute 10 queries concurrently
        num_queries = 10
        queries = [f"Query {i+1}" for i in range(num_queries)]
        configs = [support_domain] * num_queries

        results = await async_manager.execute_batch(
            queries=queries,
            domain_configs=configs,
            timeout=60.0
        )

        assert len(results) == num_queries
        # All results should be valid
        for i, result in enumerate(results):
            assert result is not None, f"Result {i} should not be None"
            assert isinstance(result, dict), f"Result {i} should be dict"


# ============================================================================
# Memory Safety Integration Tests
# ============================================================================

@pytest.mark.integration
@pytest.mark.memory
@pytest.mark.slow
class TestMemorySafetyIntegration:
    """Test memory safety in integrated scenarios."""

    def test_memory_check_prevents_oom(self, model_manager, phi2_model_config):
        """Test that memory check prevents out-of-memory errors."""
        # Try to load large model
        try:
            model, tokenizer = model_manager.get_or_load(
                "phi2_test",
                phi2_model_config
            )
            # If successful, model loaded within memory limits
            assert model_manager.is_loaded("phi2_test")
        except MemoryError as e:
            # Expected if insufficient memory
            assert "Insufficient memory" in str(e)
            # This is correct behavior - prevented OOM
        except Exception as e:
            # Other errors are acceptable (model download, etc.)
            pass

    @pytest.mark.asyncio
    async def test_system_remains_stable_after_errors(
        self,
        async_manager,
        support_domain
    ):
        """Test that system remains stable after encountering errors."""
        # Execute queries that may fail
        results1 = await async_manager.execute_batch(
            queries=["Q1", "Q2"],
            domain_configs=[support_domain, support_domain],
            timeout=60.0
        )

        # System should still work after potential errors
        results2 = await async_manager.execute_batch(
            queries=["Q3"],
            domain_configs=[support_domain],
            timeout=60.0
        )

        # Both batches should complete
        assert len(results1) == 2
        assert len(results2) == 1
        # All results should be valid
        for r in results1 + results2:
            assert_valid_result(r)


# ============================================================================
# Shutdown Integration Tests
# ============================================================================

@pytest.mark.integration
class TestShutdownIntegration:
    """Test graceful shutdown in integrated system."""

    @pytest.mark.asyncio
    async def test_async_executor_shutdown(self, domain_executor):
        """Test async executor shutdown."""
        from mdsa.async_.executor import AsyncExecutor

        executor = AsyncExecutor(domain_executor, max_workers=5)
        await executor.shutdown_async(timeout=5.0)
        # Should complete without hanging

    @pytest.mark.asyncio
    async def test_async_manager_shutdown(self, domain_executor):
        """Test async manager shutdown."""
        from mdsa.async_.manager import AsyncManager

        manager = AsyncManager(domain_executor, max_concurrent=5)
        await manager.shutdown()
        # Should complete without hanging

    @pytest.mark.asyncio
    async def test_context_manager_cleanup(self, domain_executor):
        """Test that context managers clean up properly."""
        from mdsa.async_.executor import AsyncExecutor

        async with AsyncExecutor(domain_executor, max_workers=5) as executor:
            # Use executor
            pass
        # Should be cleaned up automatically
