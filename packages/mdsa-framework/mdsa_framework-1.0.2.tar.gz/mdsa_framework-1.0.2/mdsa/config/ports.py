"""
MDSA Port Configuration

MDSA Dashboard: 9000-9099 (safe, uncommon range)
User Applications: User chooses (avoid common ports)

Common ports to AVOID (framework defaults):
- 3000: React, Next.js, Svelte
- 4200: Angular
- 5000: Flask, common FastAPI
- 8000: Django, common FastAPI
- 8080: Tomcat, Java apps
- 8081: Common alternative
- 8501: Streamlit default

Port Forwarding:
Enable nginx/proxy support for production deployments
"""

import os
from typing import Optional

# MDSA Control Dashboard (framework-agnostic)
MDSA_DASHBOARD_PORT = int(os.getenv('MDSA_DASHBOARD_PORT', 9000))
MDSA_DASHBOARD_WS_PORT = int(os.getenv('MDSA_DASHBOARD_WS_PORT', 9100))

# Port forwarding configuration
ENABLE_PORT_FORWARDING = os.getenv('ENABLE_PORT_FORWARDING', 'true').lower() == 'true'
PROXY_PORT = int(os.getenv('MDSA_PROXY_PORT', 9500))

# User application port hints (not enforced, just suggestions)
SUGGESTED_USER_PORTS = {
    'api': [6000, 6001, 6002],  # Safe API ports
    'ui': [7000, 7001, 7002],   # Safe UI ports
}


def get_available_port(category: str = 'api') -> int:
    """
    Find an available port from suggested range.

    Args:
        category: Port category ('api' or 'ui')

    Returns:
        Available port number
    """
    import socket

    suggested = SUGGESTED_USER_PORTS.get(category, [6000, 6001, 6002])

    for port in suggested:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('', port))
                return port
            except OSError:
                continue

    # Fallback: let OS choose
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]


def configure_port_forwarding():
    """
    Generate nginx config for port forwarding.

    Useful for production deployments where:
    - All services behind nginx proxy
    - SSL termination at proxy
    - Load balancing across multiple MDSA apps

    Returns:
        nginx configuration string or None if port forwarding disabled
    """
    if not ENABLE_PORT_FORWARDING:
        return None

    nginx_config = f"""
    # MDSA Port Forwarding Configuration
    # Place in /etc/nginx/sites-available/mdsa

    upstream mdsa_dashboard {{
        server localhost:{MDSA_DASHBOARD_PORT};
    }}

    upstream mdsa_dashboard_ws {{
        server localhost:{MDSA_DASHBOARD_WS_PORT};
    }}

    server {{
        listen {PROXY_PORT};
        server_name localhost;

        # MDSA Dashboard
        location /mdsa/ {{
            proxy_pass http://mdsa_dashboard/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }}

        # WebSocket for real-time updates
        location /mdsa/ws/ {{
            proxy_pass http://mdsa_dashboard_ws/;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }}
    }}
    """
    return nginx_config
