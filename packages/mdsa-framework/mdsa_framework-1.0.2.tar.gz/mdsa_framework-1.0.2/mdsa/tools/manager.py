"""
Tool Manager for MDSA Framework
Manages external API integrations and tools with encrypted credentials
"""

import os
import json
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from .encryption import encrypt_api_key, decrypt_api_key


class ToolIntegration:
    """Represents an external tool/API integration"""

    def __init__(
        self,
        tool_id: str,
        name: str,
        type: str,
        endpoint: str,
        api_key_encrypted: str,
        description: str = "",
        params: Optional[Dict[str, Any]] = None,
        enabled: bool = True,
        created_at: Optional[str] = None
    ):
        self.id = tool_id
        self.name = name
        self.type = type
        self.endpoint = endpoint
        self.api_key_encrypted = api_key_encrypted
        self.description = description
        self.params = params or {}
        self.enabled = enabled
        self.created_at = created_at or datetime.now().isoformat()

    def to_dict(self, include_key: bool = False) -> Dict[str, Any]:
        """
        Convert tool to dictionary.

        Args:
            include_key: If True, include decrypted API key (use with caution)

        Returns:
            Dictionary representation
        """
        data = {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "endpoint": self.endpoint,
            "description": self.description,
            "params": self.params,
            "enabled": self.enabled,
            "created_at": self.created_at
        }

        if include_key:
            try:
                data["api_key"] = decrypt_api_key(self.api_key_encrypted)
            except:
                data["api_key"] = None

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ToolIntegration':
        """Create ToolIntegration instance from dictionary."""
        return cls(
            tool_id=data.get("id", str(uuid.uuid4())),
            name=data["name"],
            type=data["type"],
            endpoint=data["endpoint"],
            api_key_encrypted=data["api_key_encrypted"],
            description=data.get("description", ""),
            params=data.get("params", {}),
            enabled=data.get("enabled", True),
            created_at=data.get("created_at")
        )


class ToolManager:
    """Manages external tools and API integrations"""

    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize tool manager.

        Args:
            storage_path: Path to store tools configuration
        """
        if storage_path is None:
            storage_path = Path(__file__).parent.parent.parent / "data" / "tools" / "tools.json"

        self.storage_path = storage_path
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        self.tools: Dict[str, ToolIntegration] = {}
        self.load_tools()

    def load_tools(self):
        """Load tools from storage."""
        if not self.storage_path.exists():
            return

        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                for tool_data in data.get("tools", []):
                    tool = ToolIntegration.from_dict(tool_data)
                    self.tools[tool.id] = tool
        except Exception as e:
            print(f"[WARN] Error loading tools: {e}")

    def save_tools(self):
        """Save tools to storage."""
        data = {
            "tools": [tool.to_dict() for tool in self.tools.values()],
            "updated_at": datetime.now().isoformat()
        }

        # Include encrypted keys in storage
        for i, tool in enumerate(self.tools.values()):
            data["tools"][i]["api_key_encrypted"] = tool.api_key_encrypted

        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)

    def add_tool(
        self,
        name: str,
        type: str,
        endpoint: str,
        api_key: str,
        description: str = "",
        params: Optional[Dict[str, Any]] = None,
        enabled: bool = True
    ) -> ToolIntegration:
        """
        Add a new tool.

        Args:
            name: Tool name
            type: Tool type (search, weather, database, etc.)
            endpoint: API endpoint URL
            api_key: API key (will be encrypted)
            description: Tool description
            params: Additional parameters
            enabled: Whether tool is enabled

        Returns:
            Created ToolIntegration instance
        """
        tool_id = str(uuid.uuid4())
        api_key_encrypted = encrypt_api_key(api_key)

        tool = ToolIntegration(
            tool_id=tool_id,
            name=name,
            type=type,
            endpoint=endpoint,
            api_key_encrypted=api_key_encrypted,
            description=description,
            params=params,
            enabled=enabled
        )

        self.tools[tool_id] = tool
        self.save_tools()

        return tool

    def update_tool(
        self,
        tool_id: str,
        name: Optional[str] = None,
        type: Optional[str] = None,
        endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
        description: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        enabled: Optional[bool] = None
    ) -> ToolIntegration:
        """
        Update an existing tool.

        Args:
            tool_id: Tool ID to update
            name: New name (optional)
            type: New type (optional)
            endpoint: New endpoint (optional)
            api_key: New API key (optional, will be encrypted)
            description: New description (optional)
            params: New parameters (optional)
            enabled: New enabled status (optional)

        Returns:
            Updated ToolIntegration instance

        Raises:
            KeyError: If tool not found
        """
        if tool_id not in self.tools:
            raise KeyError(f"Tool with ID '{tool_id}' not found")

        tool = self.tools[tool_id]

        if name is not None:
            tool.name = name
        if type is not None:
            tool.type = type
        if endpoint is not None:
            tool.endpoint = endpoint
        if api_key is not None:
            tool.api_key_encrypted = encrypt_api_key(api_key)
        if description is not None:
            tool.description = description
        if params is not None:
            tool.params = params
        if enabled is not None:
            tool.enabled = enabled

        self.save_tools()
        return tool

    def delete_tool(self, tool_id: str) -> bool:
        """
        Delete a tool.

        Args:
            tool_id: Tool ID to delete

        Returns:
            True if deleted, False if not found
        """
        if tool_id in self.tools:
            del self.tools[tool_id]
            self.save_tools()
            return True
        return False

    def get_tool(self, tool_id: str) -> Optional[ToolIntegration]:
        """Get a tool by ID."""
        return self.tools.get(tool_id)

    def list_tools(self, enabled_only: bool = False) -> List[ToolIntegration]:
        """
        List all tools.

        Args:
            enabled_only: If True, only return enabled tools

        Returns:
            List of ToolIntegration instances
        """
        tools = list(self.tools.values())
        if enabled_only:
            tools = [t for t in tools if t.enabled]
        return tools

    def toggle_tool(self, tool_id: str, enabled: bool) -> ToolIntegration:
        """
        Enable or disable a tool.

        Args:
            tool_id: Tool ID
            enabled: New enabled status

        Returns:
            Updated ToolIntegration instance

        Raises:
            KeyError: If tool not found
        """
        return self.update_tool(tool_id, enabled=enabled)


# Global tool manager instance
_tool_manager: Optional[ToolManager] = None


def get_tool_manager() -> ToolManager:
    """Get the global tool manager instance."""
    global _tool_manager
    if _tool_manager is None:
        _tool_manager = ToolManager()
    return _tool_manager
