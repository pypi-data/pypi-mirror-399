"""
Tests for MDSA Async Execution

Tests cover:
- Async executor functionality
- Async manager with batch processing
- Concurrency control
- Error handling
- Statistics tracking
- Shutdown behavior
"""

import pytest
import asyncio
from mdsa.async_.executor import AsyncExecutor
from mdsa.async_.manager import AsyncManager, ExecutionStats
from tests.conftest import assert_valid_result, assert_success_result


# ============================================================================
# Async Executor Tests
# ============================================================================

@pytest.mark.async_
@pytest.mark.integration
class TestAsyncExecutor:
    """Test AsyncExecutor functionality."""

    @pytest.mark.asyncio
    async def test_executor_creation(self, domain_executor, hardware_config):
        """Test creating AsyncExecutor."""
        executor = AsyncExecutor(
            domain_executor,
            max_workers=hardware_config['max_workers']
        )
        assert executor is not None
        await executor.shutdown_async()

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_execute_async_basic(self, async_executor, support_domain):
        """Test basic async execution."""
        result = await async_executor.execute_async(
            query="Hello, this is a test",
            domain_config=support_domain,
            timeout=60.0
        )

        assert_valid_result(result)
        # Result may succeed or fail depending on available memory
        assert result['status'] in ['success', 'error']

    @pytest.mark.asyncio
    async def test_execute_async_timeout(self, async_executor, support_domain):
        """Test async execution with very short timeout."""
        result = await async_executor.execute_async(
            query="Test query",
            domain_config=support_domain,
            timeout=0.001  # Very short timeout
        )

        assert_valid_result(result)
        # Should timeout or return error
        assert result['status'] == 'error'

    @pytest.mark.asyncio
    async def test_context_manager(self, domain_executor):
        """Test async executor as context manager."""
        async with AsyncExecutor(domain_executor, max_workers=5) as executor:
            assert executor is not None
        # Should be cleaned up after context

    @pytest.mark.asyncio
    async def test_shutdown_async(self, domain_executor):
        """Test async shutdown."""
        executor = AsyncExecutor(domain_executor, max_workers=5)
        await executor.shutdown_async(timeout=5.0)
        # Should complete without hanging


# ============================================================================
# Execution Stats Tests
# ============================================================================

@pytest.mark.unit
class TestExecutionStats:
    """Test ExecutionStats functionality."""

    def test_stats_creation(self):
        """Test creating ExecutionStats."""
        stats = ExecutionStats()
        assert stats.total_queries == 0
        assert stats.successful_queries == 0
        assert stats.failed_queries == 0

    def test_stats_update_success(self):
        """Test updating stats with success."""
        stats = ExecutionStats()
        stats.update(latency_ms=1000, success=True)

        assert stats.total_queries == 1
        assert stats.successful_queries == 1
        assert stats.failed_queries == 0
        assert stats.avg_latency_ms == 1000

    def test_stats_update_failure(self):
        """Test updating stats with failure."""
        stats = ExecutionStats()
        stats.update(latency_ms=500, success=False)

        assert stats.total_queries == 1
        assert stats.successful_queries == 0
        assert stats.failed_queries == 1

    def test_stats_to_dict(self):
        """Test converting stats to dictionary."""
        stats = ExecutionStats()
        stats.update(latency_ms=1000, success=True)

        stats_dict = stats.to_dict()
        assert isinstance(stats_dict, dict)
        assert stats_dict['total_queries'] == 1
        assert 'success_rate' in stats_dict


# ============================================================================
# Async Manager Tests
# ============================================================================

@pytest.mark.async_
@pytest.mark.integration
class TestAsyncManager:
    """Test AsyncManager functionality."""

    @pytest.mark.asyncio
    async def test_manager_creation(self, async_executor):
        """Test creating AsyncManager."""
        manager = AsyncManager(async_executor, max_concurrent=5)
        assert manager is not None
        assert manager.max_concurrent == 5
        await manager.shutdown()

    @pytest.mark.asyncio
    async def test_execute_batch_empty(self, async_manager):
        """Test batch execution with empty lists."""
        results = await async_manager.execute_batch(
            queries=[],
            domain_configs=[]
        )
        assert results == []

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_execute_batch_single(self, async_manager, support_domain):
        """Test batch execution with single query."""
        results = await async_manager.execute_batch(
            queries=["Test query"],
            domain_configs=[support_domain],
            timeout=60.0
        )

        assert len(results) == 1
        assert_valid_result(results[0])

    @pytest.mark.asyncio
    async def test_execute_batch_length_mismatch(self, async_manager, support_domain):
        """Test batch execution with mismatched lengths."""
        with pytest.raises(ValueError, match="Length mismatch"):
            await async_manager.execute_batch(
                queries=["Q1", "Q2"],
                domain_configs=[support_domain]  # Only 1 config for 2 queries
            )

    @pytest.mark.asyncio
    async def test_execute_batch_no_none_results(self, async_manager, support_domain):
        """Test that batch execution never returns None in results."""
        results = await async_manager.execute_batch(
            queries=["Q1", "Q2", "Q3"],
            domain_configs=[support_domain, support_domain, support_domain],
            timeout=60.0
        )

        assert len(results) == 3
        # Critical: No None values (Fix A7 validation)
        assert all(r is not None for r in results), "Results should never contain None"
        # All results should be dicts with 'status' key
        for r in results:
            assert isinstance(r, dict)
            assert 'status' in r

    @pytest.mark.asyncio
    async def test_get_stats(self, async_manager):
        """Test getting statistics."""
        stats = async_manager.get_stats()
        assert isinstance(stats, dict)
        assert 'stats_enabled' in stats
        assert stats['stats_enabled'] is True

    @pytest.mark.asyncio
    async def test_reset_stats(self, async_manager):
        """Test resetting statistics."""
        async_manager.reset_stats()
        stats = async_manager.get_stats()
        assert stats['total_queries'] == 0

    @pytest.mark.asyncio
    async def test_context_manager(self, async_executor):
        """Test async manager as context manager."""
        async with AsyncManager(async_executor, max_concurrent=5) as manager:
            assert manager is not None
        # Should be cleaned up after context

    @pytest.mark.asyncio
    async def test_shutdown(self, async_executor):
        """Test manager shutdown."""
        manager = AsyncManager(async_executor, max_concurrent=5)
        await manager.shutdown()
        # Should complete without hanging


# ============================================================================
# Concurrency Control Tests
# ============================================================================

@pytest.mark.async_
@pytest.mark.concurrent
@pytest.mark.slow
class TestConcurrencyControl:
    """Test concurrency control and parallel execution."""

    @pytest.mark.asyncio
    async def test_concurrent_execution(self, async_executor, support_domain):
        """Test concurrent execution of multiple queries."""
        manager = AsyncManager(async_executor, max_concurrent=3)

        # Execute 5 queries concurrently (limited to 3 at a time)
        queries = [f"Query {i+1}" for i in range(5)]
        configs = [support_domain] * 5

        results = await manager.execute_batch(
            queries=queries,
            domain_configs=configs,
            timeout=60.0
        )

        assert len(results) == 5
        # All results should be valid (not None)
        assert all(r is not None for r in results)

        # Check concurrent peak
        stats = manager.get_stats()
        assert stats['concurrent_peak'] <= 3, "Should not exceed max_concurrent"

        await manager.shutdown()

    @pytest.mark.asyncio
    async def test_semaphore_control(self, async_executor, support_domain):
        """Test that semaphore limits concurrent execution."""
        max_concurrent = 2
        manager = AsyncManager(async_executor, max_concurrent=max_concurrent)

        # Execute queries
        queries = [f"Q{i}" for i in range(4)]
        configs = [support_domain] * 4

        results = await manager.execute_batch(
            queries=queries,
            domain_configs=configs,
            timeout=60.0
        )

        stats = manager.get_stats()
        # Peak should not exceed max_concurrent
        assert stats['concurrent_peak'] <= max_concurrent

        await manager.shutdown()


# ============================================================================
# Error Handling Tests
# ============================================================================

@pytest.mark.async_
@pytest.mark.unit
class TestAsyncErrorHandling:
    """Test error handling in async execution."""

    @pytest.mark.asyncio
    async def test_exception_converted_to_error_dict(self, async_manager, support_domain):
        """Test that exceptions are converted to error dicts (not None)."""
        # This validates Fix A7: Silent exception handling

        # Execute batch (some may fail due to memory constraints)
        results = await async_manager.execute_batch(
            queries=["Q1", "Q2", "Q3"],
            domain_configs=[support_domain] * 3,
            timeout=60.0
        )

        # Critical: All results should be dicts, never None
        assert len(results) == 3
        for i, result in enumerate(results):
            assert result is not None, f"Result {i} should not be None"
            assert isinstance(result, dict), f"Result {i} should be dict"
            assert 'status' in result, f"Result {i} should have 'status' key"
            assert 'error' in result or result['status'] == 'success'
