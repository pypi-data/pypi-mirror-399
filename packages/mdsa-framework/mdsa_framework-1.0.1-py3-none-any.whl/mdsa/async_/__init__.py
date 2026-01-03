"""
MDSA Async Module

Provides asynchronous execution support for concurrent domain processing and
multi-query handling in the MDSA framework.

Key Components:
- AsyncExecutor: Execute domain queries asynchronously
- AsyncManager: Manage multiple concurrent async executions
- Utilities: Helper functions for async operations

Features:
- Concurrent domain execution
- Multi-query batch processing
- Resource pooling and management
- Graceful error handling
- Performance monitoring

Usage:
    from mdsa.async_ import AsyncExecutor, AsyncManager

    # Create async executor
    executor = AsyncExecutor(domain_executor)

    # Execute query asynchronously
    result = await executor.execute_async("What is AI?", domain_config)

    # Batch processing
    manager = AsyncManager(max_workers=5)
    results = await manager.execute_batch(queries, domain_configs)
"""

from .executor import AsyncExecutor
from .manager import AsyncManager

__all__ = ['AsyncExecutor', 'AsyncManager']
