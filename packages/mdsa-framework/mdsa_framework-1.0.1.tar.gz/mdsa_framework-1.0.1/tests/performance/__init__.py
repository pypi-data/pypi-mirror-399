"""
MDSA Performance Benchmark Suite

This package contains performance benchmarks to validate metrics reported
in the MDSA research paper.

Benchmarks Available:
- benchmark_latency: End-to-end response latency measurement
- benchmark_accuracy: Routing accuracy validation
- benchmark_all: Run all benchmarks in sequence

Usage:
    python tests/performance/benchmark_latency.py -n 1000
    python tests/performance/benchmark_accuracy.py -n 10000
    python tests/performance/benchmark_all.py

Prerequisites:
- MDSA framework installed: pip install -e .
- TinyBERT model will be downloaded on first run
- Test data in test_data/ directory (optional, uses defaults if missing)
"""

__version__ = "1.0.0"
__all__ = ["benchmark_latency", "benchmark_accuracy"]

# Expose benchmark functions for programmatic use
try:
    from .benchmark_latency import benchmark_latency
    from .benchmark_accuracy import benchmark_accuracy
except ImportError:
    # Benchmarks not available (MDSA not installed)
    pass
