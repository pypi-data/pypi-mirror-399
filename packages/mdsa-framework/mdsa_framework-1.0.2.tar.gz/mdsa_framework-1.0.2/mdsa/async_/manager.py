"""
MDSA Async Manager

Manages multiple concurrent async executions with resource pooling,
load balancing, and performance monitoring.

Features:
- Batch query processing
- Resource pooling
- Load balancing
- Performance tracking
- Graceful degradation
"""

import asyncio
import time
from typing import Dict, Any, List, Optional, Callable
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class ExecutionStats:
    """Statistics for async executions."""
    total_queries: int = 0
    successful_queries: int = 0
    failed_queries: int = 0
    total_latency_ms: float = 0.0
    avg_latency_ms: float = 0.0
    min_latency_ms: float = float('inf')
    max_latency_ms: float = 0.0
    concurrent_peak: int = 0
    timeouts: int = 0
    retries: int = 0

    def update(self, latency_ms: float, success: bool, timeout: bool = False, retry: bool = False):
        """Update statistics with new execution result."""
        self.total_queries += 1
        if success:
            self.successful_queries += 1
        else:
            self.failed_queries += 1

        if timeout:
            self.timeouts += 1
        if retry:
            self.retries += 1

        self.total_latency_ms += latency_ms
        self.avg_latency_ms = self.total_latency_ms / self.total_queries
        self.min_latency_ms = min(self.min_latency_ms, latency_ms)
        self.max_latency_ms = max(self.max_latency_ms, latency_ms)

    def to_dict(self) -> Dict[str, Any]:
        """Convert stats to dictionary."""
        return {
            'total_queries': self.total_queries,
            'successful_queries': self.successful_queries,
            'failed_queries': self.failed_queries,
            'success_rate': (
                self.successful_queries / self.total_queries * 100
                if self.total_queries > 0 else 0.0
            ),
            'avg_latency_ms': round(self.avg_latency_ms, 2),
            'min_latency_ms': round(self.min_latency_ms, 2) if self.min_latency_ms != float('inf') else 0.0,
            'max_latency_ms': round(self.max_latency_ms, 2),
            'concurrent_peak': self.concurrent_peak,
            'timeouts': self.timeouts,
            'retries': self.retries
        }


class AsyncManager:
    """
    Manages multiple concurrent async executions.

    Provides batch processing, resource pooling, load balancing,
    and performance monitoring for async domain executions.

    Example:
        from mdsa.async_ import AsyncManager, AsyncExecutor

        # Create manager
        manager = AsyncManager(
            async_executor=async_executor,
            max_concurrent=10,
            enable_stats=True
        )

        # Batch execution
        queries = ["Query 1", "Query 2", "Query 3"]
        configs = [config1, config2, config3]
        results = await manager.execute_batch(queries, configs)

        # Get statistics
        stats = manager.get_stats()
    """

    def __init__(
        self,
        async_executor: 'AsyncExecutor',
        max_concurrent: int = 10,
        enable_stats: bool = True,
        enable_monitoring: bool = True
    ):
        """
        Initialize async manager.

        Args:
            async_executor: AsyncExecutor instance
            max_concurrent: Maximum concurrent executions
            enable_stats: Enable statistics tracking
            enable_monitoring: Enable performance monitoring
        """
        self.async_executor = async_executor
        self.max_concurrent = max_concurrent
        self.enable_stats = enable_stats
        self.enable_monitoring = enable_monitoring

        # Statistics
        self.stats = ExecutionStats() if enable_stats else None

        # Monitoring
        self.current_concurrent = 0
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def execute_batch(
        self,
        queries: List[str],
        domain_configs: List['DomainConfig'],
        timeout: Optional[float] = None,
        context: Optional[Dict[str, Any]] = None,
        enable_tools: bool = True,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute batch of queries with concurrency control.

        Args:
            queries: List of user queries
            domain_configs: List of domain configurations
            timeout: Execution timeout for each query
            context: Optional context dictionary
            enable_tools: Enable tool execution
            progress_callback: Optional callback(completed, total) for progress tracking

        Returns:
            List of result dictionaries

        Raises:
            ValueError: If queries and domain_configs lengths don't match
        """
        if len(queries) != len(domain_configs):
            raise ValueError(
                f"Length mismatch: {len(queries)} queries vs {len(domain_configs)} configs"
            )

        total = len(queries)
        completed = 0
        results = []

        # Create tasks with concurrency control
        async def execute_with_semaphore(query: str, config: 'DomainConfig', index: int):
            """Execute single query with semaphore control."""
            nonlocal completed

            async with self.semaphore:
                # Update concurrent count
                self.current_concurrent += 1
                if self.stats:
                    self.stats.concurrent_peak = max(
                        self.stats.concurrent_peak,
                        self.current_concurrent
                    )

                # Execute query
                start_time = time.time()
                result = await self.async_executor.execute_async(
                    query=query,
                    domain_config=config,
                    timeout=timeout,
                    context=context,
                    enable_tools=enable_tools
                )
                latency_ms = (time.time() - start_time) * 1000

                # Update statistics
                if self.stats:
                    self.stats.update(
                        latency_ms=latency_ms,
                        success=(result['status'] == 'success'),
                        timeout=('timed out' in result.get('error', '').lower()),
                        retry=('retries' in result)
                    )

                # Update progress
                self.current_concurrent -= 1
                completed += 1
                if progress_callback:
                    progress_callback(completed, total)

                return (index, result)

        # Create all tasks
        tasks = [
            execute_with_semaphore(query, config, i)
            for i, (query, config) in enumerate(zip(queries, domain_configs))
        ]

        # Execute with concurrency control
        completed_tasks = await asyncio.gather(*tasks, return_exceptions=True)

        # Sort results by original order
        sorted_results = [None] * total
        for i, task_result in enumerate(completed_tasks):
            if isinstance(task_result, Exception):
                # Convert exception to error dict (don't skip!)
                error_result = {
                    'response': '',
                    'status': 'error',
                    'error': f'Task execution failed: {str(task_result)}',
                    'domain': 'unknown',
                    'model': 'unknown',
                    'latency_ms': 0
                }
                sorted_results[i] = error_result

                # Update stats for exception
                if self.stats:
                    self.stats.update(
                        latency_ms=0,
                        success=False,
                        timeout=False,
                        retry=False
                    )
                continue

            index, result = task_result
            sorted_results[index] = result

        return sorted_results

    async def execute_with_fallback(
        self,
        query: str,
        domain_configs: List['DomainConfig'],
        timeout: Optional[float] = None,
        context: Optional[Dict[str, Any]] = None,
        enable_tools: bool = True
    ) -> Dict[str, Any]:
        """
        Execute query with fallback to alternative domains on failure.

        Tries domains in order until one succeeds or all fail.

        Args:
            query: User query
            domain_configs: List of domain configurations (in priority order)
            timeout: Execution timeout for each attempt
            context: Optional context dictionary
            enable_tools: Enable tool execution

        Returns:
            Result dictionary from first successful domain
        """
        last_error = None
        attempts = []

        for i, config in enumerate(domain_configs):
            result = await self.async_executor.execute_async(
                query=query,
                domain_config=config,
                timeout=timeout,
                context=context,
                enable_tools=enable_tools
            )

            attempts.append({
                'domain': config.domain_id,
                'status': result['status'],
                'latency_ms': result.get('latency_ms', 0)
            })

            # Return on success
            if result['status'] == 'success':
                result['fallback_used'] = (i > 0)
                result['fallback_attempts'] = attempts
                return result

            last_error = result.get('error', 'Unknown error')

        # All domains failed
        return {
            'response': '',
            'status': 'error',
            'error': f'All {len(domain_configs)} fallback domains failed: {last_error}',
            'domain': 'fallback_failed',
            'model': 'none',
            'latency_ms': 0,
            'fallback_attempts': attempts
        }

    async def execute_parallel_domains(
        self,
        query: str,
        domain_configs: List['DomainConfig'],
        timeout: Optional[float] = None,
        context: Optional[Dict[str, Any]] = None,
        enable_tools: bool = True,
        return_first: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Execute same query across multiple domains in parallel.

        Useful for:
        - Comparing domain responses
        - Finding best response through voting
        - Redundancy and reliability

        Args:
            query: User query
            domain_configs: List of domain configurations
            timeout: Execution timeout
            context: Optional context dictionary
            enable_tools: Enable tool execution
            return_first: Return as soon as first domain succeeds

        Returns:
            List of results from all domains (or first success if return_first=True)
        """
        # Create tasks for all domains
        tasks = [
            self.async_executor.execute_async(
                query=query,
                domain_config=config,
                timeout=timeout,
                context=context,
                enable_tools=enable_tools
            )
            for config in domain_configs
        ]

        if return_first:
            # Return first completed task
            for coro in asyncio.as_completed(tasks):
                result = await coro
                if result['status'] == 'success':
                    return [result]

            # All failed, return all results
            return await asyncio.gather(*tasks)
        else:
            # Wait for all tasks
            return await asyncio.gather(*tasks)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get execution statistics.

        Returns:
            Statistics dictionary
        """
        if not self.stats:
            return {
                'stats_enabled': False,
                'message': 'Statistics tracking is disabled'
            }

        return {
            'stats_enabled': True,
            **self.stats.to_dict(),
            'current_concurrent': self.current_concurrent,
            'max_concurrent': self.max_concurrent
        }

    def reset_stats(self):
        """Reset statistics counters."""
        if self.stats:
            self.stats = ExecutionStats()

    async def shutdown(self):
        """Shutdown manager and clean up resources."""
        # Wait for all current executions to complete
        while self.current_concurrent > 0:
            await asyncio.sleep(0.1)

        # Shutdown executor (use async shutdown to avoid blocking)
        await self.async_executor.shutdown_async()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.shutdown()
