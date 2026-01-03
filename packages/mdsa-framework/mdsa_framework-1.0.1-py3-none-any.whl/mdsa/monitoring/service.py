"""
MDSA Monitoring Service - Application-Agnostic

This service allows ANY MDSA application (medical chatbot, EduAI, custom apps)
to publish metrics that the dashboard can subscribe to. No hardcoding required.

Features:
- File-based shared state (no external dependencies)
- Automatic cleanup of old metrics
- Thread-safe operations
- Works with multiple concurrent applications

Usage in Application:
    from mdsa.monitoring.service import MonitoringService

    # Initialize service
    monitor = MonitoringService(app_name="MedicalChatbot")

    # Publish request metrics
    monitor.publish_request(
        query="What is diabetes?",
        domain="clinical_diagnosis",
        confidence=0.92,
        latency_ms=1245.3,
        success=True
    )

Usage in Dashboard:
    from mdsa.monitoring.service import MonitoringService

    # Subscribe to all applications
    monitor = MonitoringService()
    metrics = monitor.get_all_metrics()
"""

import json
import os
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class RequestMetric:
    """Single request metric."""
    timestamp: float
    app_name: str
    query: str
    domain: str
    confidence: float
    latency_ms: float
    success: bool
    error: Optional[str] = None
    metadata: Optional[Dict] = None


class MonitoringService:
    """
    Application-agnostic monitoring service.

    Allows any MDSA application to publish metrics to a shared location
    that the dashboard can read from.
    """

    def __init__(
        self,
        app_name: Optional[str] = None,
        shared_dir: Optional[str] = None,
        max_age_hours: int = 24
    ):
        """
        Initialize monitoring service.

        Args:
            app_name: Name of this application (e.g., "MedicalChatbot", "EduAI")
            shared_dir: Directory for shared metrics (default: ~/.mdsa/metrics)
            max_age_hours: Maximum age of metrics to keep (default: 24 hours)
        """
        self.app_name = app_name or "UnknownApp"
        self.max_age_hours = max_age_hours

        # Default shared directory in user's home
        if shared_dir is None:
            home = Path.home()
            self.shared_dir = home / ".mdsa" / "metrics"
        else:
            self.shared_dir = Path(shared_dir)

        # Create directory if it doesn't exist
        self.shared_dir.mkdir(parents=True, exist_ok=True)

        # File paths
        self.metrics_file = self.shared_dir / "requests.jsonl"  # JSONL for append efficiency
        self.apps_file = self.shared_dir / "applications.json"

        # Thread lock for thread-safe operations
        self._lock = threading.Lock()

        # Register this application
        if app_name:
            self._register_app()

        logger.debug(f"MonitoringService initialized: app={self.app_name}, dir={self.shared_dir}")

    def _register_app(self):
        """Register this application in the shared registry."""
        with self._lock:
            # Load existing apps
            apps = self._load_json(self.apps_file, default={})

            # Add/update this app
            apps[self.app_name] = {
                "name": self.app_name,
                "registered_at": datetime.now().isoformat(),
                "last_seen": datetime.now().isoformat(),
                "pid": os.getpid()
            }

            # Save
            self._save_json(self.apps_file, apps)

    def publish_request(
        self,
        query: str,
        domain: str,
        confidence: float,
        latency_ms: float,
        success: bool = True,
        error: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        """
        Publish a request metric.

        Args:
            query: User query
            domain: Domain that handled the request
            confidence: Routing confidence
            latency_ms: Request latency in milliseconds
            success: Whether request succeeded
            error: Error message if failed
            metadata: Additional metadata
        """
        metric = RequestMetric(
            timestamp=time.time(),
            app_name=self.app_name,
            query=query,
            domain=domain,
            confidence=confidence,
            latency_ms=latency_ms,
            success=success,
            error=error,
            metadata=metadata or {}
        )

        self._append_metric(metric)

        # Update last seen
        self._update_last_seen()

    def _append_metric(self, metric: RequestMetric):
        """Append metric to JSONL file (thread-safe)."""
        with self._lock:
            try:
                with open(self.metrics_file, 'a', encoding='utf-8') as f:
                    json.dump(asdict(metric), f)
                    f.write('\n')
            except Exception as e:
                logger.error(f"Failed to append metric: {e}")

    def _update_last_seen(self):
        """Update last_seen timestamp for this app."""
        with self._lock:
            apps = self._load_json(self.apps_file, default={})
            if self.app_name in apps:
                apps[self.app_name]['last_seen'] = datetime.now().isoformat()
                self._save_json(self.apps_file, apps)

    def get_all_metrics(
        self,
        max_age_hours: Optional[int] = None
    ) -> List[RequestMetric]:
        """
        Get all metrics from all applications.

        Args:
            max_age_hours: Maximum age of metrics (default: use instance setting)

        Returns:
            List of RequestMetric objects
        """
        max_age = max_age_hours or self.max_age_hours
        cutoff_time = time.time() - (max_age * 3600)

        metrics = []

        with self._lock:
            if not self.metrics_file.exists():
                return metrics

            try:
                with open(self.metrics_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            data = json.loads(line)

                            # Filter by age
                            if data['timestamp'] >= cutoff_time:
                                metric = RequestMetric(**data)
                                metrics.append(metric)
            except Exception as e:
                logger.error(f"Failed to load metrics: {e}")

        return metrics

    def get_metrics_by_app(self, app_name: str) -> List[RequestMetric]:
        """Get metrics for a specific application."""
        all_metrics = self.get_all_metrics()
        return [m for m in all_metrics if m.app_name == app_name]

    def get_metrics_by_domain(self, domain: str) -> List[RequestMetric]:
        """Get metrics for a specific domain."""
        all_metrics = self.get_all_metrics()
        return [m for m in all_metrics if m.domain == domain]

    def get_active_apps(self) -> Dict[str, Dict]:
        """
        Get all registered applications.

        Returns:
            Dict mapping app_name to app info
        """
        with self._lock:
            return self._load_json(self.apps_file, default={})

    def get_summary_stats(self) -> Dict[str, Any]:
        """
        Get summary statistics across all applications.

        Returns:
            Dict with aggregated stats
        """
        metrics = self.get_all_metrics()

        if not metrics:
            return {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "avg_latency_ms": 0.0,
                "domains": {},
                "applications": {}
            }

        # Calculate stats
        total = len(metrics)
        successful = sum(1 for m in metrics if m.success)
        failed = total - successful

        # Average latency
        avg_latency = sum(m.latency_ms for m in metrics) / total if total > 0 else 0.0

        # Domain breakdown
        domains = {}
        for metric in metrics:
            if metric.domain not in domains:
                domains[metric.domain] = {
                    "count": 0,
                    "success": 0,
                    "failed": 0,
                    "avg_latency": 0.0,
                    "latencies": []
                }

            domains[metric.domain]["count"] += 1
            if metric.success:
                domains[metric.domain]["success"] += 1
            else:
                domains[metric.domain]["failed"] += 1
            domains[metric.domain]["latencies"].append(metric.latency_ms)

        # Calculate avg latency per domain
        for domain_stats in domains.values():
            latencies = domain_stats.pop("latencies")
            domain_stats["avg_latency"] = sum(latencies) / len(latencies) if latencies else 0.0

        # Application breakdown
        applications = {}
        for metric in metrics:
            if metric.app_name not in applications:
                applications[metric.app_name] = {
                    "count": 0,
                    "success": 0,
                    "failed": 0
                }

            applications[metric.app_name]["count"] += 1
            if metric.success:
                applications[metric.app_name]["success"] += 1
            else:
                applications[metric.app_name]["failed"] += 1

        return {
            "total_requests": total,
            "successful_requests": successful,
            "failed_requests": failed,
            "avg_latency_ms": round(avg_latency, 2),
            "domains": domains,
            "applications": applications
        }

    def cleanup_old_metrics(self, max_age_hours: Optional[int] = None):
        """
        Remove metrics older than max_age_hours.

        Args:
            max_age_hours: Maximum age (default: use instance setting)
        """
        max_age = max_age_hours or self.max_age_hours
        cutoff_time = time.time() - (max_age * 3600)

        with self._lock:
            if not self.metrics_file.exists():
                return

            try:
                # Read all metrics
                metrics = []
                with open(self.metrics_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            data = json.loads(line)
                            if data['timestamp'] >= cutoff_time:
                                metrics.append(data)

                # Rewrite file with only recent metrics
                with open(self.metrics_file, 'w', encoding='utf-8') as f:
                    for metric in metrics:
                        json.dump(metric, f)
                        f.write('\n')

                logger.info(f"Cleaned up old metrics: kept {len(metrics)} recent entries")

            except Exception as e:
                logger.error(f"Failed to cleanup metrics: {e}")

    def _load_json(self, path: Path, default=None):
        """Load JSON file with error handling."""
        try:
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load {path}: {e}")

        return default if default is not None else {}

    def _save_json(self, path: Path, data: Any):
        """Save JSON file with error handling."""
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save {path}: {e}")


__all__ = ["MonitoringService", "RequestMetric"]
