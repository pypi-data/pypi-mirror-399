"""
MDSA Configuration Module

Central configuration for MDSA framework including:
- Port configuration (ports.py)
- Model paths and settings
- Environment variable management
"""

from .ports import (
    MDSA_DASHBOARD_PORT,
    MDSA_DASHBOARD_WS_PORT,
    ENABLE_PORT_FORWARDING,
    PROXY_PORT,
    SUGGESTED_USER_PORTS,
    get_available_port,
    configure_port_forwarding
)

__all__ = [
    'MDSA_DASHBOARD_PORT',
    'MDSA_DASHBOARD_WS_PORT',
    'ENABLE_PORT_FORWARDING',
    'PROXY_PORT',
    'SUGGESTED_USER_PORTS',
    'get_available_port',
    'configure_port_forwarding'
]
