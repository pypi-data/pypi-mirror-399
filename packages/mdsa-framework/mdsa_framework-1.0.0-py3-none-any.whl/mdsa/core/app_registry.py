"""
MDSA Application Registry

Framework-agnostic registry for discovering and managing all applications
built with MDSA, regardless of their web framework (Flask, Django, FastAPI, etc.)

This enables the MDSA dashboard to control multiple applications from a single
control panel without framework dependencies.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import requests

logger = logging.getLogger(__name__)


class MDSAAppRegistry:
    """
    Registry for all applications built with MDSA.
    Framework-agnostic - works with any web framework.
    """

    def __init__(self, persist_path: Optional[str] = None):
        """
        Initialize the app registry.

        Args:
            persist_path: Optional path to persist registry data (JSON file)
        """
        self.apps: Dict[str, Dict[str, Any]] = {}
        self.persist_path = persist_path or "data/registry/apps.json"

        # Load existing registry if available
        self._load_registry()

    def register_app(
        self,
        app_id: str,
        app_name: str,
        framework: str,
        api_endpoint: str,
        health_check_url: str,
        metrics_url: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Register an MDSA app (any framework).

        Args:
            app_id: Unique identifier for the app
            app_name: Human-readable name
            framework: Framework used ("flask", "fastapi", "django", "express", etc.)
            api_endpoint: Base API endpoint (e.g., "http://localhost:5000")
            health_check_url: Health check endpoint
            metrics_url: Metrics endpoint
            metadata: Optional additional metadata

        Returns:
            Registered app information
        """
        app_info = {
            'app_id': app_id,
            'name': app_name,
            'framework': framework,
            'endpoint': api_endpoint,
            'health': health_check_url,
            'metrics': metrics_url,
            'metadata': metadata or {},
            'registered_at': datetime.now().isoformat(),
            'last_seen': datetime.now().isoformat()
        }

        self.apps[app_id] = app_info
        self._save_registry()

        logger.info(f"Registered MDSA app: {app_name} ({framework}) at {api_endpoint}")
        return app_info

    def unregister_app(self, app_id: str) -> bool:
        """
        Unregister an app from the registry.

        Args:
            app_id: App ID to unregister

        Returns:
            True if app was unregistered, False if not found
        """
        if app_id in self.apps:
            app_name = self.apps[app_id]['name']
            del self.apps[app_id]
            self._save_registry()
            logger.info(f"Unregistered app: {app_name} (ID: {app_id})")
            return True
        return False

    def get_app(self, app_id: str) -> Optional[Dict[str, Any]]:
        """
        Get app information by ID.

        Args:
            app_id: App ID

        Returns:
            App information or None if not found
        """
        return self.apps.get(app_id)

    def list_apps(self) -> List[Dict[str, Any]]:
        """
        List all registered apps.

        Returns:
            List of all registered apps
        """
        return list(self.apps.values())

    def check_health(self, app_id: str) -> Dict[str, Any]:
        """
        Check health status of a registered app.

        Args:
            app_id: App ID to check

        Returns:
            Health check result with status and response time
        """
        app = self.apps.get(app_id)
        if not app:
            return {'status': 'unknown', 'error': 'App not found'}

        try:
            start_time = datetime.now()
            response = requests.get(app['health'], timeout=5)
            elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000

            if response.status_code == 200:
                # Update last seen
                self.apps[app_id]['last_seen'] = datetime.now().isoformat()
                self._save_registry()

                return {
                    'status': 'healthy',
                    'response_time_ms': elapsed_ms,
                    'data': response.json() if response.content else {}
                }
            else:
                return {
                    'status': 'unhealthy',
                    'response_time_ms': elapsed_ms,
                    'error': f'HTTP {response.status_code}'
                }

        except requests.exceptions.Timeout:
            return {'status': 'timeout', 'error': 'Health check timed out'}
        except requests.exceptions.ConnectionError:
            return {'status': 'unreachable', 'error': 'Cannot connect to app'}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}

    def get_metrics(self, app_id: str) -> Dict[str, Any]:
        """
        Fetch metrics from a registered app.

        Args:
            app_id: App ID

        Returns:
            Metrics data or error
        """
        app = self.apps.get(app_id)
        if not app:
            return {'error': 'App not found'}

        try:
            response = requests.get(app['metrics'], timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {'error': f'HTTP {response.status_code}'}

        except Exception as e:
            return {'error': str(e)}

    def discover_apps(self, ports: List[int] = None) -> List[Dict[str, Any]]:
        """
        Auto-discover MDSA apps on common ports.

        Args:
            ports: List of ports to check (default: common ports)

        Returns:
            List of discovered apps
        """
        if ports is None:
            ports = [5000, 5001, 5002, 6000, 6001, 6002, 7000, 7001, 8000, 8001]

        discovered = []

        for port in ports:
            health_url = f"http://localhost:{port}/api/health"
            try:
                response = requests.get(health_url, timeout=2)
                if response.status_code == 200:
                    data = response.json()

                    # Check if it's an MDSA app
                    if 'mdsa' in data or 'orchestrator' in data:
                        discovered.append({
                            'port': port,
                            'health_url': health_url,
                            'data': data
                        })
                        logger.info(f"Discovered MDSA app on port {port}")

            except:
                continue

        return discovered

    def _save_registry(self):
        """Save registry to disk."""
        try:
            registry_file = Path(self.persist_path)
            registry_file.parent.mkdir(parents=True, exist_ok=True)

            with open(registry_file, 'w') as f:
                json.dump(self.apps, f, indent=2)

        except Exception as e:
            logger.warning(f"Failed to save registry: {e}")

    def _load_registry(self):
        """Load registry from disk."""
        try:
            registry_file = Path(self.persist_path)
            if registry_file.exists():
                with open(registry_file, 'r') as f:
                    self.apps = json.load(f)
                logger.info(f"Loaded {len(self.apps)} apps from registry")

        except Exception as e:
            logger.warning(f"Failed to load registry: {e}")
            self.apps = {}


# Global registry instance
_global_registry: Optional[MDSAAppRegistry] = None


def get_registry() -> MDSAAppRegistry:
    """
    Get the global app registry instance.

    Returns:
        Global MDSAAppRegistry instance
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = MDSAAppRegistry()
    return _global_registry


def register_current_app(
    app_id: str,
    app_name: str,
    framework: str,
    port: int,
    base_path: str = ""
) -> Dict[str, Any]:
    """
    Convenience function to register the current app with standard endpoints.

    Args:
        app_id: Unique app ID
        app_name: App name
        framework: Framework name
        port: Port number
        base_path: Optional base path (e.g., "/api/v1")

    Returns:
        Registered app info
    """
    registry = get_registry()

    api_endpoint = f"http://localhost:{port}{base_path}"
    health_url = f"{api_endpoint}/api/health"
    metrics_url = f"{api_endpoint}/api/metrics"

    return registry.register_app(
        app_id=app_id,
        app_name=app_name,
        framework=framework,
        api_endpoint=api_endpoint,
        health_check_url=health_url,
        metrics_url=metrics_url
    )
