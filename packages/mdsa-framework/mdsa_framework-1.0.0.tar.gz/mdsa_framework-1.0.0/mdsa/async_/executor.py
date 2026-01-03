"""
MDSA Async Executor

Provides asynchronous execution capabilities for domain queries.
Wraps synchronous domain execution in async/await patterns.

Features:
- Async wrapper for DomainExecutor
- Non-blocking query execution
- Concurrent query processing
- Resource-efficient execution
- Error handling and timeout support
"""

import asyncio
import time
from typing import Dict, Any, Optional
from functools import partial
from concurrent.futures import ThreadPoolExecutor


class AsyncExecutor:
    """
    Asynchronous executor for domain queries.

    Wraps synchronous DomainExecutor to provide async execution,
    enabling concurrent processing of multiple queries.

    Example:
        from mdsa import DomainExecutor, DomainConfig
        from mdsa.async_ import AsyncExecutor

        # Create executors
        domain_executor = DomainExecutor(model_manager)
        async_executor = AsyncExecutor(domain_executor)

        # Execute async
        result = await async_executor.execute_async(
            query="What is machine learning?",
            domain_config=ml_config
        )
    """

    def __init__(
        self,
        domain_executor: 'DomainExecutor',
        max_workers: int = 10,  # Increased from 5 to match AsyncManager default
        default_timeout: float = 30.0
    ):
        """
        Initialize async executor.

        Args:
            domain_executor: Synchronous domain executor to wrap
            max_workers: Maximum thread pool workers for async execution (default 10)
            default_timeout: Default timeout for queries (seconds)
        """
        self.domain_executor = domain_executor
        self.max_workers = max_workers
        self.default_timeout = default_timeout
        self.executor_pool = ThreadPoolExecutor(max_workers=max_workers)
        self._shutdown_requested = False

    async def execute_async(
        self,
        query: str,
        domain_config: 'DomainConfig',
        timeout: Optional[float] = None,
        context: Optional[Dict[str, Any]] = None,
        enable_tools: bool = True
    ) -> Dict[str, Any]:
        """
        Execute query asynchronously.

        Args:
            query: User query
            domain_config: Domain configuration
            timeout: Execution timeout (uses default if None)
            context: Optional context dictionary
            enable_tools: Enable tool execution

        Returns:
            Dict containing:
                - response: Generated response
                - status: 'success' or 'error'
                - latency_ms: Execution time
                - domain: Domain ID
                - model: Model name
                - error: Error message (if status='error')
        """
        if timeout is None:
            timeout = self.default_timeout

        # Wrap synchronous execution in async
        loop = asyncio.get_event_loop()

        try:
            # Execute in thread pool to avoid blocking
            result = await asyncio.wait_for(
                loop.run_in_executor(
                    self.executor_pool,
                    partial(
                        self.domain_executor.execute,
                        query=query,
                        domain_config=domain_config,
                        context=context,
                        enable_tools=enable_tools
                    )
                ),
                timeout=timeout
            )

            return result

        except asyncio.TimeoutError:
            return {
                'response': '',
                'status': 'error',
                'error': f'Query timed out after {timeout}s',
                'domain': domain_config.domain_id,
                'model': domain_config.model_name,
                'latency_ms': timeout * 1000
            }

        except Exception as e:
            return {
                'response': '',
                'status': 'error',
                'error': str(e),
                'domain': domain_config.domain_id,
                'model': domain_config.model_name,
                'latency_ms': 0
            }

    async def execute_multiple(
        self,
        queries: list[str],
        domain_configs: list['DomainConfig'],
        timeout: Optional[float] = None,
        context: Optional[Dict[str, Any]] = None,
        enable_tools: bool = True
    ) -> list[Dict[str, Any]]:
        """
        Execute multiple queries concurrently.

        Args:
            queries: List of user queries
            domain_configs: List of domain configurations (same length as queries)
            timeout: Execution timeout for each query
            context: Optional context dictionary
            enable_tools: Enable tool execution

        Returns:
            List of result dictionaries (same order as input queries)

        Raises:
            ValueError: If queries and domain_configs lengths don't match
        """
        if len(queries) != len(domain_configs):
            raise ValueError(
                f"Length mismatch: {len(queries)} queries vs {len(domain_configs)} configs"
            )

        # Create async tasks for all queries
        tasks = [
            self.execute_async(
                query=query,
                domain_config=config,
                timeout=timeout,
                context=context,
                enable_tools=enable_tools
            )
            for query, config in zip(queries, domain_configs)
        ]

        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results and handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    'response': '',
                    'status': 'error',
                    'error': str(result),
                    'domain': domain_configs[i].domain_id,
                    'model': domain_configs[i].model_name,
                    'latency_ms': 0
                })
            else:
                processed_results.append(result)

        return processed_results

    async def execute_with_retry(
        self,
        query: str,
        domain_config: 'DomainConfig',
        max_retries: int = 3,
        retry_delay: float = 1.0,
        timeout: Optional[float] = None,
        context: Optional[Dict[str, Any]] = None,
        enable_tools: bool = True
    ) -> Dict[str, Any]:
        """
        Execute query with automatic retry on failure.

        Args:
            query: User query
            domain_config: Domain configuration
            max_retries: Maximum retry attempts
            retry_delay: Delay between retries (seconds)
            timeout: Execution timeout
            context: Optional context dictionary
            enable_tools: Enable tool execution

        Returns:
            Result dictionary (same format as execute_async)
        """
        last_error = None

        for attempt in range(max_retries + 1):
            result = await self.execute_async(
                query=query,
                domain_config=domain_config,
                timeout=timeout,
                context=context,
                enable_tools=enable_tools
            )

            # Return on success
            if result['status'] == 'success':
                if attempt > 0:
                    result['retries'] = attempt
                return result

            # Store error for final attempt
            last_error = result.get('error', 'Unknown error')

            # Don't retry on timeout
            if 'timed out' in last_error.lower():
                break

            # Wait before retry (except on last attempt)
            if attempt < max_retries:
                await asyncio.sleep(retry_delay)

        # All retries failed
        return {
            'response': '',
            'status': 'error',
            'error': f'Failed after {max_retries} retries: {last_error}',
            'domain': domain_config.domain_id,
            'model': domain_config.model_name,
            'latency_ms': 0,
            'retries': max_retries
        }

    def shutdown(self):
        """
        Shutdown executor and clean up resources (blocking).

        DEPRECATED: Use shutdown_async() for async contexts.
        This method is kept for backward compatibility.
        """
        self.executor_pool.shutdown(wait=True)

    async def shutdown_async(self, timeout: float = 10.0):
        """
        Async shutdown with timeout (prevents event loop blocking).

        This method properly shuts down the thread pool without blocking
        the async event loop, preventing system freezes during cleanup.

        Args:
            timeout: Maximum time to wait for shutdown (seconds)
        """
        # Signal shutdown request
        self._shutdown_requested = True

        # Wait for executor with timeout in separate thread
        loop = asyncio.get_event_loop()

        try:
            # Shutdown with wait=False to avoid blocking
            await asyncio.wait_for(
                loop.run_in_executor(
                    None,  # Use default executor
                    lambda: self.executor_pool.shutdown(wait=False)
                ),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            # Force shutdown if timeout exceeded
            self.executor_pool.shutdown(wait=False)
        except Exception as e:
            # Log error but continue shutdown
            pass

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.shutdown_async()  # Use async shutdown
