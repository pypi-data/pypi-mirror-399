"""
Shared Metrics System for Chatbot and Dashboard

Enables communication between chatbot and dashboard through JSON files.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import threading

logger = logging.getLogger(__name__)


class SharedMetrics:
    """Shared metrics that can be read by dashboard."""

    def __init__(self, metrics_file: str = "./chatbot_metrics.json"):
        self.metrics_file = Path(metrics_file)
        self.lock = threading.Lock()

        # Initialize metrics file if it doesn't exist
        if not self.metrics_file.exists():
            self._write_metrics(self._get_empty_metrics())

    def _get_empty_metrics(self) -> Dict[str, Any]:
        """Get empty metrics structure."""
        return {
            "last_updated": datetime.now().isoformat(),
            "system": {
                "mdsa_version": "1.0.0",
                "status": "running",
                "uptime_seconds": 0
            },
            "models": {
                "loaded": [],
                "max_models": 2,
                "total_memory_mb": 0
            },
            "requests": {
                "total": 0,
                "success": 0,
                "errors": 0,
                "success_rate": 0.0
            },
            "performance": {
                "avg_latency_ms": 0.0,
                "p50_latency_ms": 0.0,
                "p95_latency_ms": 0.0,
                "p99_latency_ms": 0.0,
                "avg_tokens": 0.0,
                "throughput_rps": 0.0
            },
            "domains": {},
            "tools": {
                "enabled": False,
                "available": []
            },
            "rag": {
                "enabled": False,
                "documents": 0,
                "embedding_model": "N/A"
            },
            "recent_requests": []
        }

    def _read_metrics(self) -> Dict[str, Any]:
        """Read metrics from file."""
        try:
            with self.lock:
                if self.metrics_file.exists():
                    with open(self.metrics_file, 'r') as f:
                        return json.load(f)
        except Exception as e:
            logger.error(f"Error reading metrics: {e}")

        return self._get_empty_metrics()

    def _write_metrics(self, metrics: Dict[str, Any]):
        """Write metrics to file."""
        try:
            with self.lock:
                metrics["last_updated"] = datetime.now().isoformat()
                with open(self.metrics_file, 'w') as f:
                    json.dump(metrics, f, indent=2)
        except Exception as e:
            logger.error(f"Error writing metrics: {e}")

    def update_system(self, status: str, uptime: float):
        """Update system metrics."""
        metrics = self._read_metrics()
        metrics["system"]["status"] = status
        metrics["system"]["uptime_seconds"] = uptime
        self._write_metrics(metrics)

    def update_models(self, loaded_models: List[Dict[str, Any]], max_models: int, total_memory: float):
        """Update model metrics."""
        metrics = self._read_metrics()
        metrics["models"]["loaded"] = loaded_models
        metrics["models"]["max_models"] = max_models
        metrics["models"]["total_memory_mb"] = total_memory
        self._write_metrics(metrics)

    def update_requests(self, total: int, success: int, errors: int):
        """Update request metrics."""
        metrics = self._read_metrics()
        metrics["requests"]["total"] = total
        metrics["requests"]["success"] = success
        metrics["requests"]["errors"] = errors
        metrics["requests"]["success_rate"] = (success / total * 100) if total > 0 else 0.0
        self._write_metrics(metrics)

    def update_performance(self, avg_latency: float, p50: float, p95: float, p99: float,
                          avg_tokens: float, throughput: float):
        """Update performance metrics."""
        metrics = self._read_metrics()
        metrics["performance"]["avg_latency_ms"] = avg_latency
        metrics["performance"]["p50_latency_ms"] = p50
        metrics["performance"]["p95_latency_ms"] = p95
        metrics["performance"]["p99_latency_ms"] = p99
        metrics["performance"]["avg_tokens"] = avg_tokens
        metrics["performance"]["throughput_rps"] = throughput
        self._write_metrics(metrics)

    def update_domains(self, domains: Dict[str, int]):
        """Update domain distribution."""
        metrics = self._read_metrics()
        metrics["domains"] = domains
        self._write_metrics(metrics)

    def update_tools(self, enabled: bool, tools: List[Dict[str, str]]):
        """Update tools info."""
        metrics = self._read_metrics()
        metrics["tools"]["enabled"] = enabled
        metrics["tools"]["available"] = tools
        self._write_metrics(metrics)

    def update_rag(self, enabled: bool, documents: int, embedding_model: str):
        """Update RAG info."""
        metrics = self._read_metrics()
        metrics["rag"]["enabled"] = enabled
        metrics["rag"]["documents"] = documents
        metrics["rag"]["embedding_model"] = embedding_model
        self._write_metrics(metrics)

    def add_recent_request(self, request: Dict[str, Any]):
        """Add a recent request (keep last 10)."""
        metrics = self._read_metrics()
        metrics["recent_requests"].insert(0, request)
        metrics["recent_requests"] = metrics["recent_requests"][:10]  # Keep last 10
        self._write_metrics(metrics)

    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all metrics."""
        return self._read_metrics()

    def clear(self):
        """Clear all metrics."""
        self._write_metrics(self._get_empty_metrics())
