"""
Request/Response Logger Module

Tracks all requests and responses for monitoring and auditing.
"""

import logging
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
from threading import Lock

logger = logging.getLogger(__name__)


@dataclass
class RequestLog:
    """Log entry for a single request/response."""

    request_id: str
    timestamp: float
    query: str
    domain: str
    model: str

    # Response data
    response: str
    status: str  # 'success' or 'error'
    error: Optional[str] = None

    # Performance metrics
    latency_ms: float = 0.0
    tokens_generated: int = 0
    confidence: float = 0.0

    # Metadata
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        # Convert timestamp to ISO format for readability
        data['timestamp_iso'] = datetime.fromtimestamp(self.timestamp).isoformat()
        return data

    def __repr__(self) -> str:
        return (
            f"<RequestLog {self.request_id} "
            f"domain={self.domain} status={self.status} "
            f"latency={self.latency_ms:.1f}ms>"
        )


class RequestLogger:
    """
    Log and track all requests and responses.

    Thread-safe logging with in-memory storage and optional persistence.
    """

    def __init__(
        self,
        max_logs: int = 10000,
        enable_file_logging: bool = False,
        log_file_path: Optional[str] = None
    ):
        """
        Initialize request logger.

        Args:
            max_logs: Maximum number of logs to keep in memory
            enable_file_logging: Whether to log to file
            log_file_path: Path to log file (if file logging enabled)
        """
        self._logs: List[RequestLog] = []
        self._lock = Lock()
        self.max_logs = max_logs
        self.enable_file_logging = enable_file_logging
        self.log_file_path = log_file_path

        # Statistics
        self._request_count = 0
        self._success_count = 0
        self._error_count = 0

        logger.info(f"RequestLogger initialized (max_logs={max_logs})")

    def log_request(
        self,
        request_id: str,
        query: str,
        domain: str,
        model: str,
        response: str,
        status: str,
        error: Optional[str] = None,
        latency_ms: float = 0.0,
        tokens_generated: int = 0,
        confidence: float = 0.0,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> RequestLog:
        """
        Log a request/response.

        Args:
            request_id: Unique request identifier
            query: User query
            domain: Domain ID
            model: Model name
            response: Generated response
            status: 'success' or 'error'
            error: Error message (if status='error')
            latency_ms: Request latency in milliseconds
            tokens_generated: Number of tokens generated
            confidence: Confidence score
            user_id: Optional user identifier
            session_id: Optional session identifier
            metadata: Optional additional metadata

        Returns:
            RequestLog: The created log entry
        """
        with self._lock:
            log_entry = RequestLog(
                request_id=request_id,
                timestamp=time.time(),
                query=query,
                domain=domain,
                model=model,
                response=response,
                status=status,
                error=error,
                latency_ms=latency_ms,
                tokens_generated=tokens_generated,
                confidence=confidence,
                user_id=user_id,
                session_id=session_id,
                metadata=metadata or {}
            )

            # Add to memory
            self._logs.append(log_entry)

            # Trim if exceeds max
            if len(self._logs) > self.max_logs:
                self._logs.pop(0)  # Remove oldest

            # Update stats
            self._request_count += 1
            if status == 'success':
                self._success_count += 1
            else:
                self._error_count += 1

            # Log to file if enabled
            if self.enable_file_logging and self.log_file_path:
                self._write_to_file(log_entry)

            logger.debug(f"Logged request: {request_id} ({status})")

            return log_entry

    def _write_to_file(self, log_entry: RequestLog) -> None:
        """Write log entry to file."""
        try:
            import json
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry.to_dict()) + '\n')
        except Exception as e:
            logger.error(f"Failed to write log to file: {e}")

    def get_logs(
        self,
        limit: Optional[int] = None,
        domain: Optional[str] = None,
        status: Optional[str] = None,
        min_latency: Optional[float] = None
    ) -> List[RequestLog]:
        """
        Get logs with optional filtering.

        Args:
            limit: Maximum number of logs to return
            domain: Filter by domain
            status: Filter by status ('success' or 'error')
            min_latency: Filter by minimum latency

        Returns:
            List of matching logs
        """
        with self._lock:
            logs = list(self._logs)

        # Apply filters
        if domain:
            logs = [log for log in logs if log.domain == domain]
        if status:
            logs = [log for log in logs if log.status == status]
        if min_latency is not None:
            logs = [log for log in logs if log.latency_ms >= min_latency]

        # Sort by timestamp (most recent first)
        logs.sort(key=lambda x: x.timestamp, reverse=True)

        # Apply limit
        if limit:
            logs = logs[:limit]

        return logs

    def get_recent_logs(self, count: int = 10) -> List[RequestLog]:
        """Get most recent logs."""
        return self.get_logs(limit=count)

    def get_stats(self) -> Dict[str, Any]:
        """Get logging statistics."""
        with self._lock:
            total = self._request_count
            success_rate = (self._success_count / total * 100) if total > 0 else 0.0

            return {
                'total_requests': total,
                'success_count': self._success_count,
                'error_count': self._error_count,
                'success_rate_percent': success_rate,
                'logs_in_memory': len(self._logs),
                'max_logs': self.max_logs
            }

    def clear(self) -> None:
        """Clear all logs from memory."""
        with self._lock:
            self._logs.clear()
            logger.info("Cleared all logs from memory")

    def export_logs(self, file_path: str, format: str = 'json') -> None:
        """
        Export all logs to a file.

        Args:
            file_path: Path to output file
            format: 'json' or 'csv'
        """
        with self._lock:
            logs = list(self._logs)

        if format == 'json':
            import json
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump([log.to_dict() for log in logs], f, indent=2)
        elif format == 'csv':
            import csv
            if logs:
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=logs[0].to_dict().keys())
                    writer.writeheader()
                    for log in logs:
                        writer.writerow(log.to_dict())
        else:
            raise ValueError(f"Unsupported format: {format}")

        logger.info(f"Exported {len(logs)} logs to {file_path}")

    def __repr__(self) -> str:
        stats = self.get_stats()
        return (
            f"<RequestLogger "
            f"requests={stats['total_requests']} "
            f"success_rate={stats['success_rate_percent']:.1f}%>"
        )

    def __len__(self) -> int:
        with self._lock:
            return len(self._logs)
