"""
Metrics Collector Module

Collects and aggregates performance metrics for monitoring.
"""

import logging
import time
from typing import Dict, Any, List, Optional
from collections import defaultdict, deque
from threading import Lock
from dataclasses import dataclass
import statistics

logger = logging.getLogger(__name__)


@dataclass
class MetricSnapshot:
    """Snapshot of metrics at a point in time."""

    timestamp: float
    total_requests: int
    success_count: int
    error_count: int
    avg_latency_ms: float
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    avg_tokens: float
    avg_confidence: float
    requests_per_second: float


class MetricsCollector:
    """
    Collect and aggregate performance metrics.

    Tracks latency, throughput, success rates, and other performance indicators.
    """

    def __init__(self, window_size: int = 1000):
        """
        Initialize metrics collector.

        Args:
            window_size: Number of recent metrics to keep for windowed calculations
        """
        self._lock = Lock()
        self.window_size = window_size

        # Raw metrics
        self._latencies: deque = deque(maxlen=window_size)
        self._tokens: deque = deque(maxlen=window_size)
        self._confidences: deque = deque(maxlen=window_size)
        self._timestamps: deque = deque(maxlen=window_size)

        # Counters
        self._total_requests = 0
        self._success_count = 0
        self._error_count = 0

        # Per-domain metrics
        self._domain_requests: Dict[str, int] = defaultdict(int)
        self._domain_latencies: Dict[str, List[float]] = defaultdict(list)
        self._domain_errors: Dict[str, int] = defaultdict(int)

        # Per-model metrics
        self._model_requests: Dict[str, int] = defaultdict(int)
        self._model_latencies: Dict[str, List[float]] = defaultdict(list)

        # Snapshots for historical tracking
        self._snapshots: List[MetricSnapshot] = []
        self._last_snapshot_time = time.time()

        logger.info(f"MetricsCollector initialized (window_size={window_size})")

    def record_request(
        self,
        latency_ms: float,
        tokens_generated: int,
        confidence: float,
        domain: str,
        model: str,
        status: str
    ) -> None:
        """
        Record metrics for a request.

        Args:
            latency_ms: Request latency in milliseconds
            tokens_generated: Number of tokens generated
            confidence: Confidence score (0-1)
            domain: Domain ID
            model: Model name
            status: 'success' or 'error'
        """
        with self._lock:
            timestamp = time.time()

            # Add to windowed metrics
            self._latencies.append(latency_ms)
            self._tokens.append(tokens_generated)
            self._confidences.append(confidence)
            self._timestamps.append(timestamp)

            # Update counters
            self._total_requests += 1
            if status == 'success':
                self._success_count += 1
            else:
                self._error_count += 1

            # Update per-domain metrics
            self._domain_requests[domain] += 1
            self._domain_latencies[domain].append(latency_ms)
            if status == 'error':
                self._domain_errors[domain] += 1

            # Update per-model metrics
            self._model_requests[model] += 1
            self._model_latencies[model].append(latency_ms)

            logger.debug(
                f"Recorded metrics: domain={domain} model={model} "
                f"latency={latency_ms:.1f}ms status={status}"
            )

    def get_summary(self) -> Dict[str, Any]:
        """Get overall metrics summary."""
        with self._lock:
            if not self._latencies:
                return {
                    'total_requests': 0,
                    'success_count': 0,
                    'error_count': 0,
                    'success_rate_percent': 0.0,
                    'avg_latency_ms': 0.0,
                    'avg_tokens': 0.0,
                    'avg_confidence': 0.0
                }

            success_rate = (
                (self._success_count / self._total_requests * 100)
                if self._total_requests > 0 else 0.0
            )

            return {
                'total_requests': self._total_requests,
                'success_count': self._success_count,
                'error_count': self._error_count,
                'success_rate_percent': success_rate,
                'avg_latency_ms': statistics.mean(self._latencies),
                'min_latency_ms': min(self._latencies),
                'max_latency_ms': max(self._latencies),
                'p50_latency_ms': self._percentile(self._latencies, 50),
                'p95_latency_ms': self._percentile(self._latencies, 95),
                'p99_latency_ms': self._percentile(self._latencies, 99),
                'avg_tokens': statistics.mean(self._tokens) if self._tokens else 0.0,
                'avg_confidence': statistics.mean(self._confidences) if self._confidences else 0.0,
                'window_size': len(self._latencies)
            }

    def get_domain_metrics(self, domain: Optional[str] = None) -> Dict[str, Any]:
        """
        Get per-domain metrics.

        Args:
            domain: Specific domain (returns all if None)

        Returns:
            Domain metrics
        """
        with self._lock:
            if domain:
                if domain not in self._domain_requests:
                    return {}

                latencies = self._domain_latencies[domain]
                return {
                    'domain': domain,
                    'requests': self._domain_requests[domain],
                    'errors': self._domain_errors[domain],
                    'error_rate_percent': (
                        self._domain_errors[domain] / self._domain_requests[domain] * 100
                        if self._domain_requests[domain] > 0 else 0.0
                    ),
                    'avg_latency_ms': statistics.mean(latencies) if latencies else 0.0,
                    'p95_latency_ms': self._percentile(latencies, 95) if latencies else 0.0
                }
            else:
                # Return all domains
                return {
                    d: self.get_domain_metrics(d)
                    for d in self._domain_requests.keys()
                }

    def get_model_metrics(self, model: Optional[str] = None) -> Dict[str, Any]:
        """
        Get per-model metrics.

        Args:
            model: Specific model (returns all if None)

        Returns:
            Model metrics
        """
        with self._lock:
            if model:
                if model not in self._model_requests:
                    return {}

                latencies = self._model_latencies[model]
                return {
                    'model': model,
                    'requests': self._model_requests[model],
                    'avg_latency_ms': statistics.mean(latencies) if latencies else 0.0,
                    'p95_latency_ms': self._percentile(latencies, 95) if latencies else 0.0
                }
            else:
                # Return all models
                return {
                    m: self.get_model_metrics(m)
                    for m in self._model_requests.keys()
                }

    def get_throughput(self, window_seconds: int = 60) -> float:
        """
        Calculate requests per second over recent window.

        Args:
            window_seconds: Time window in seconds

        Returns:
            Requests per second
        """
        with self._lock:
            if not self._timestamps:
                return 0.0

            current_time = time.time()
            cutoff_time = current_time - window_seconds

            # Count requests in window
            recent_requests = sum(
                1 for ts in self._timestamps if ts >= cutoff_time
            )

            return recent_requests / window_seconds if window_seconds > 0 else 0.0

    def take_snapshot(self) -> MetricSnapshot:
        """Take a snapshot of current metrics."""
        with self._lock:
            summary = self.get_summary()
            throughput = self.get_throughput()

            snapshot = MetricSnapshot(
                timestamp=time.time(),
                total_requests=summary['total_requests'],
                success_count=summary['success_count'],
                error_count=summary['error_count'],
                avg_latency_ms=summary['avg_latency_ms'],
                p50_latency_ms=summary['p50_latency_ms'],
                p95_latency_ms=summary['p95_latency_ms'],
                p99_latency_ms=summary['p99_latency_ms'],
                avg_tokens=summary['avg_tokens'],
                avg_confidence=summary['avg_confidence'],
                requests_per_second=throughput
            )

            self._snapshots.append(snapshot)
            self._last_snapshot_time = snapshot.timestamp

            logger.debug(f"Snapshot taken: {len(self._snapshots)} total")

            return snapshot

    def get_snapshots(self, limit: Optional[int] = None) -> List[MetricSnapshot]:
        """Get historical snapshots."""
        with self._lock:
            snapshots = list(self._snapshots)
            if limit:
                snapshots = snapshots[-limit:]
            return snapshots

    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile of data."""
        if not data:
            return 0.0

        sorted_data = sorted(data)
        index = int(len(sorted_data) * (percentile / 100.0))
        index = min(index, len(sorted_data) - 1)
        return sorted_data[index]

    def reset(self) -> None:
        """Reset all metrics."""
        with self._lock:
            self._latencies.clear()
            self._tokens.clear()
            self._confidences.clear()
            self._timestamps.clear()

            self._total_requests = 0
            self._success_count = 0
            self._error_count = 0

            self._domain_requests.clear()
            self._domain_latencies.clear()
            self._domain_errors.clear()

            self._model_requests.clear()
            self._model_latencies.clear()

            self._snapshots.clear()

            logger.info("Metrics reset")

    def __repr__(self) -> str:
        summary = self.get_summary()
        return (
            f"<MetricsCollector "
            f"requests={summary['total_requests']} "
            f"avg_latency={summary['avg_latency_ms']:.1f}ms "
            f"success_rate={summary['success_rate_percent']:.1f}%>"
        )
