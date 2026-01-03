"""
MDSA Tools Module
Manages both framework tools and external API integrations
"""

# Framework tools (existing)
from .base import Tool, ToolResult
from .registry import ToolRegistry
from .smart_executor import SmartToolExecutor

# External API integrations (new - Phase 2)
from .manager import ToolIntegration, ToolManager, get_tool_manager
from .encryption import encrypt_api_key, decrypt_api_key, get_encryption

__all__ = [
    # Framework tools (existing)
    'Tool',
    'ToolResult',
    'ToolRegistry',
    'SmartToolExecutor',
    # External API integrations (new)
    'ToolIntegration',
    'ToolManager',
    'get_tool_manager',
    'encrypt_api_key',
    'decrypt_api_key',
    'get_encryption'
]
