"""
Helper Utilities Module

Common utility functions used across the MDSA framework.
"""

import time
from functools import wraps
from typing import Any, Callable, Dict, List, Optional


def timer(func: Callable) -> Callable:
    """
    Decorator to measure function execution time.

    Args:
        func: Function to time

    Returns:
        Wrapped function that prints execution time

    Example:
        >>> @timer
        ... def my_function():
        ...     time.sleep(1)
        >>> my_function()
        # my_function executed in 1.00s
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"{func.__name__} executed in {elapsed:.2f}s")
        return result
    return wrapper


def measure_latency(func: Callable, iterations: int = 100) -> Dict[str, float]:
    """
    Measure function latency statistics.

    Args:
        func: Function to measure
        iterations: Number of iterations to run

    Returns:
        dict: Statistics (min, max, mean, p50, p95, p99)

    Example:
        >>> stats = measure_latency(my_function, iterations=100)
        >>> print(f"P99 latency: {stats['p99']:.2f}ms")
    """
    import statistics

    latencies = []
    for _ in range(iterations):
        start = time.perf_counter()
        func()
        elapsed = (time.perf_counter() - start) * 1000  # Convert to ms
        latencies.append(elapsed)

    latencies.sort()

    return {
        'min': latencies[0],
        'max': latencies[-1],
        'mean': statistics.mean(latencies),
        'median': statistics.median(latencies),
        'p50': latencies[int(len(latencies) * 0.50)],
        'p95': latencies[int(len(latencies) * 0.95)],
        'p99': latencies[int(len(latencies) * 0.99)],
    }


def safe_import(module_name: str, package: Optional[str] = None) -> Optional[Any]:
    """
    Safely import a module without raising exceptions.

    Args:
        module_name: Name of module to import
        package: Package name for relative imports

    Returns:
        Imported module or None if import fails

    Example:
        >>> torch = safe_import('torch')
        >>> if torch:
        ...     print("PyTorch available")
    """
    try:
        if package:
            return __import__(module_name, fromlist=[package])
        else:
            return __import__(module_name)
    except ImportError:
        return None


def format_size(size_bytes: float) -> str:
    """
    Format byte size as human-readable string.

    Args:
        size_bytes: Size in bytes

    Returns:
        str: Formatted size (e.g., "1.5 GB")

    Example:
        >>> format_size(1536000000)
        '1.43 GB'
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate string to maximum length.

    Args:
        text: String to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        str: Truncated string

    Example:
        >>> truncate_string("Long text here", max_length=10)
        'Long te...'
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def flatten_dict(d: Dict, parent_key: str = '', sep: str = '.') -> Dict:
    """
    Flatten nested dictionary.

    Args:
        d: Dictionary to flatten
        parent_key: Parent key for recursion
        sep: Separator for keys

    Returns:
        dict: Flattened dictionary

    Example:
        >>> nested = {'a': {'b': {'c': 1}}}
        >>> flatten_dict(nested)
        {'a.b.c': 1}
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """
    Split list into chunks.

    Args:
        lst: List to chunk
        chunk_size: Size of each chunk

    Returns:
        list: List of chunks

    Example:
        >>> chunk_list([1, 2, 3, 4, 5], chunk_size=2)
        [[1, 2], [3, 4], [5]]
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    Decorator to retry function on exception.

    Args:
        max_attempts: Maximum number of attempts
        delay: Initial delay between attempts (seconds)
        backoff: Multiplier for delay after each attempt

    Returns:
        Decorated function

    Example:
        >>> @retry(max_attempts=3, delay=1.0)
        ... def unstable_function():
        ...     # Might fail sometimes
        ...     pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        raise
                    print(f"Attempt {attempt}/{max_attempts} failed: {e}. Retrying in {current_delay}s...")
                    time.sleep(current_delay)
                    current_delay *= backoff
            return None
        return wrapper
    return decorator


class Timer:
    """
    Context manager for timing code blocks.

    Example:
        >>> with Timer("processing"):
        ...     time.sleep(1)
        # processing took 1.00s
    """

    def __init__(self, name: str = "Operation", verbose: bool = True):
        """
        Initialize timer.

        Args:
            name: Name of operation being timed
            verbose: Whether to print timing info
        """
        self.name = name
        self.verbose = verbose
        self.start_time = None
        self.elapsed = None

    def __enter__(self):
        """Start timer."""
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop timer and print elapsed time."""
        self.elapsed = (time.perf_counter() - self.start_time) * 1000  # ms
        if self.verbose:
            print(f"{self.name} took {self.elapsed:.2f}ms")


if __name__ == "__main__":
    # Demo usage
    print("=== Timer Demo ===")
    with Timer("Sleep test"):
        time.sleep(0.1)

    print("\n=== Format Size Demo ===")
    print(f"1.5 GB = {format_size(1.5 * 1024**3)}")

    print("\n=== Flatten Dict Demo ===")
    nested = {'a': {'b': {'c': 1}, 'd': 2}}
    print(f"Nested: {nested}")
    print(f"Flat: {flatten_dict(nested)}")

    print("\n=== Chunk List Demo ===")
    data = list(range(10))
    chunks = chunk_list(data, chunk_size=3)
    print(f"Chunks: {chunks}")
