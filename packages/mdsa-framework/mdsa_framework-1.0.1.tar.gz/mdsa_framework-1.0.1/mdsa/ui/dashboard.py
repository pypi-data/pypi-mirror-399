"""
MDSA Built-in Web Dashboard

A lightweight Flask-based dashboard for monitoring MDSA framework.

Usage:
    python -m mdsa.ui.dashboard

Or programmatically:
    from mdsa.ui.dashboard import DashboardServer
    server = DashboardServer(monitor_instance)
    server.run(port=5000)
"""

import os
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any
from flask import Flask, render_template, jsonify, send_from_directory, request, redirect, url_for, flash
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Import MDSA components
try:
    from mdsa import __version__
except ImportError:
    __version__ = "1.0.0"

try:
    from mdsa.monitoring import RequestLogger, MetricsCollector
except ImportError:
    RequestLogger = None
    MetricsCollector = None

try:
    from mdsa.models import ModelManager
except ImportError:
    ModelManager = None

try:
    from mdsa.utils import HardwareDetector
except ImportError:
    HardwareDetector = None

# Import auth components separately - critical for authentication
try:
    from mdsa.ui.auth import UserManager, get_user_manager, User
except ImportError as e:
    UserManager = None
    User = None
    get_user_manager = None
    import warnings
    warnings.warn(
        f"Auth module import failed: {e}. Dashboard authentication will be disabled.",
        RuntimeWarning
    )


class DashboardServer:
    """
    Built-in web dashboard server for MDSA framework.

    Features:
    - Welcome page with framework info
    - Real-time monitoring of models, requests, performance
    - Automatic hardware detection
    - RESTful API for metrics
    """

    def __init__(
        self,
        model_manager: Optional['ModelManager'] = None,
        request_logger: Optional['RequestLogger'] = None,
        metrics_collector: Optional['MetricsCollector'] = None,
        host: str = "127.0.0.1",
        port: int = 5000,
        enable_auth: bool = True,
        enable_rate_limiting: bool = True
    ):
        """
        Initialize dashboard server.

        Args:
            model_manager: ModelManager instance to monitor
            request_logger: RequestLogger instance to monitor
            metrics_collector: MetricsCollector instance to monitor
            host: Host to bind to
            port: Port to bind to
            enable_auth: Enable authentication (default: True)
            enable_rate_limiting: Enable rate limiting (default: True)
        """
        self.model_manager = model_manager
        self.request_logger = request_logger
        self.metrics_collector = metrics_collector
        self.host = host
        self.port = port
        self.start_time = time.time()
        self.enable_auth = enable_auth
        self.enable_rate_limiting = enable_rate_limiting

        # Create Flask app
        self.app = Flask(
            __name__,
            template_folder=str(Path(__file__).parent / "templates"),
            static_folder=str(Path(__file__).parent / "static")
        )
        self.app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'mdsa-dev-secret-key-change-in-production')

        # Initialize authentication
        if self.enable_auth and UserManager:
            from mdsa.ui.auth import setup_auth  # Use existing helper function
            self.user_manager = get_user_manager()
            self.login_manager = setup_auth(self.app)  # Proper LoginManager initialization
        else:
            self.user_manager = None
            self.login_manager = None

        # Initialize rate limiting
        if self.enable_rate_limiting:
            self.limiter = Limiter(
                app=self.app,
                key_func=get_remote_address,
                default_limits=["200 per day", "50 per hour"],
                storage_uri="memory://"
            )
        else:
            self.limiter = None

        # Register routes
        self._register_routes()

    def _register_routes(self):
        """Register Flask routes."""

        # Authentication routes
        @self.app.route('/login', methods=['GET', 'POST'])
        def login():
            """Login page."""
            if self.enable_auth:
                if current_user.is_authenticated:
                    return redirect(url_for('welcome'))

                if request.method == 'POST':
                    username = request.form.get('username')
                    password = request.form.get('password')

                    user = self.user_manager.authenticate(username, password)
                    if user:
                        login_user(user, remember=request.form.get('remember_me', False))
                        flash('Login successful!', 'success')

                        next_page = request.args.get('next')
                        return redirect(next_page) if next_page else redirect(url_for('welcome'))
                    else:
                        flash('Invalid username or password.', 'error')

                return render_template('login.html', version=__version__)
            else:
                # Authentication disabled, redirect to welcome
                return redirect(url_for('welcome'))

        @self.app.route('/logout')
        @login_required
        def logout():
            """Logout user."""
            if self.enable_auth:
                logout_user()
                flash('You have been logged out.', 'info')
            return redirect(url_for('login'))

        # Public routes
        @self.app.route('/')
        def index():
            """Redirect to welcome page."""
            if self.enable_auth and not current_user.is_authenticated:
                return redirect(url_for('login'))
            return redirect(url_for('welcome'))

        @self.app.route('/welcome')
        def welcome():
            """Welcome page."""
            if self.enable_auth and not current_user.is_authenticated:
                return redirect(url_for('login'))

            user = current_user if self.enable_auth else None
            return render_template('welcome.html', version=__version__, user=user)

        @self.app.route('/monitor')
        def monitor():
            """Monitoring page."""
            if self.enable_auth and not current_user.is_authenticated:
                return redirect(url_for('login'))

            user = current_user if self.enable_auth else None
            return render_template('monitor.html', version=__version__, user=user)

        # API routes with rate limiting
        @self.app.route('/api/metrics')
        def api_metrics():
            """API endpoint for metrics data."""
            if self.enable_auth:
                @login_required
                def protected_metrics():
                    if self.limiter:
                        return self.limiter.limit("30 per minute")(lambda: jsonify(self.get_metrics()))()
                    return jsonify(self.get_metrics())
                return protected_metrics()

            if self.limiter:
                return self.limiter.limit("30 per minute")(lambda: jsonify(self.get_metrics()))()
            return jsonify(self.get_metrics())

        @self.app.route('/api/health')
        def api_health():
            """Health check endpoint - no authentication required."""
            if self.limiter:
                return self.limiter.limit("60 per minute")(lambda: jsonify({
                    'status': 'running',
                    'version': __version__,
                    'uptime_seconds': time.time() - self.start_time,
                    'authentication_enabled': self.enable_auth,
                    'rate_limiting_enabled': self.enable_rate_limiting
                }))()
            return jsonify({
                'status': 'running',
                'version': __version__,
                'uptime_seconds': time.time() - self.start_time,
                'authentication_enabled': self.enable_auth,
                'rate_limiting_enabled': self.enable_rate_limiting
            })

        @self.app.route('/static/<path:filename>')
        def static_files(filename):
            """Serve static files."""
            return send_from_directory(self.app.static_folder, filename)

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get current metrics data.

        Returns:
            dict: Comprehensive metrics data
        """
        metrics = {
            'timestamp': time.time(),
            'version': __version__,
            'uptime_seconds': time.time() - self.start_time,
            'system': self._get_system_metrics(),
            'models': self._get_model_metrics(),
            'requests': self._get_request_metrics(),
            'performance': self._get_performance_metrics()
        }

        return metrics

    def _get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics."""
        try:
            detector = HardwareDetector()
            hw = detector.get_summary()
            return {
                'status': 'running',
                'cpu_cores': hw.get('cpu_cores', 0),
                'memory_gb': hw.get('memory_gb', 0),
                'has_gpu': hw.get('has_cuda', False) or hw.get('has_mps', False),
                'gpu_type': 'CUDA' if hw.get('has_cuda') else ('MPS' if hw.get('has_mps') else 'None')
            }
        except:
            return {
                'status': 'running',
                'cpu_cores': 0,
                'memory_gb': 0,
                'has_gpu': False,
                'gpu_type': 'Unknown'
            }

    def _get_model_metrics(self) -> Dict[str, Any]:
        """Get model metrics."""
        if not self.model_manager:
            return {
                'loaded': [],
                'count': 0,
                'max_models': 0,
                'total_memory_mb': 0
            }

        try:
            stats = self.model_manager.get_stats()
            loaded_models = []

            for model_id in self.model_manager.registry.list_models():
                model_info = self.model_manager.registry._models.get(model_id)
                if model_info:
                    loaded_models.append({
                        'id': model_id,
                        'name': model_info.config.model_name,
                        'memory_mb': model_info.memory_mb,
                        'use_count': model_info.use_count,
                        'last_used': model_info.last_used
                    })

            return {
                'loaded': loaded_models,
                'count': len(loaded_models),
                'max_models': self.model_manager.registry.max_models,
                'total_memory_mb': sum(m['memory_mb'] for m in loaded_models)
            }
        except Exception as e:
            return {
                'loaded': [],
                'count': 0,
                'max_models': 0,
                'total_memory_mb': 0,
                'error': str(e)
            }

    def _get_request_metrics(self) -> Dict[str, Any]:
        """Get request metrics."""
        if not self.request_logger:
            return {
                'total': 0,
                'success': 0,
                'errors': 0,
                'success_rate': 0
            }

        try:
            stats = self.request_logger.get_stats()
            return {
                'total': stats.get('total_requests', 0),
                'success': stats.get('success_count', 0),
                'errors': stats.get('error_count', 0),
                'success_rate': stats.get('success_rate_percent', 0)
            }
        except Exception as e:
            return {
                'total': 0,
                'success': 0,
                'errors': 0,
                'success_rate': 0,
                'error': str(e)
            }

    def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        if not self.metrics_collector:
            return {
                'avg_latency_ms': 0,
                'p50_latency_ms': 0,
                'p95_latency_ms': 0,
                'p99_latency_ms': 0,
                'avg_tokens': 0,
                'throughput_rps': 0
            }

        try:
            summary = self.metrics_collector.get_summary()
            return {
                'avg_latency_ms': summary.get('avg_latency_ms', 0),
                'p50_latency_ms': summary.get('p50_latency_ms', 0),
                'p95_latency_ms': summary.get('p95_latency_ms', 0),
                'p99_latency_ms': summary.get('p99_latency_ms', 0),
                'avg_tokens': summary.get('avg_tokens', 0),
                'throughput_rps': summary.get('throughput_rps', 0)
            }
        except Exception as e:
            return {
                'avg_latency_ms': 0,
                'p50_latency_ms': 0,
                'p95_latency_ms': 0,
                'p99_latency_ms': 0,
                'avg_tokens': 0,
                'throughput_rps': 0,
                'error': str(e)
            }

    def run(self, debug: bool = False):
        """
        Run the dashboard server.

        Args:
            debug: Enable debug mode
        """
        print(f"""
========================================================================
MDSA Dashboard Server
========================================================================
Version: {__version__}
URL: http://{self.host}:{self.port}

Pages:
  • Welcome: http://{self.host}:{self.port}/welcome
  • Monitor: http://{self.host}:{self.port}/monitor
  • API:     http://{self.host}:{self.port}/api/metrics

Press Ctrl+C to stop
========================================================================
""")

        self.app.run(host=self.host, port=self.port, debug=debug)


def main():
    """Run dashboard without monitoring components (demo mode)."""
    print("Starting MDSA Dashboard in demo mode...")
    print("Note: No monitoring components connected. Dashboard will show placeholder data.")

    server = DashboardServer()
    server.run(debug=False)


if __name__ == "__main__":
    main()
