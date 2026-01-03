"""
Tool Registry for the MDSA framework.

This module provides centralized management of tools including
registration, discovery, and execution.
"""

from typing import Dict, List, Optional, Any
import logging
from .base import Tool, ToolResult


logger = logging.getLogger(__name__)


class ToolRegistry:
    """Central registry for managing framework tools.

    The ToolRegistry provides:
    - Tool registration and discovery
    - Tool execution with error handling
    - Tool metadata and schemas
    - Extensibility for custom tools

    Example:
        registry = ToolRegistry()

        # Register a tool
        registry.register(CurrentTimeTool())

        # Execute a tool
        result = registry.execute("get_current_time")

        # List all tools
        tools = registry.list_tools()
    """

    def __init__(self):
        """Initialize the tool registry."""
        self._tools: Dict[str, Tool] = {}
        self._execution_count: Dict[str, int] = {}
        logger.info("ToolRegistry initialized")

    def register(self, tool: Tool) -> None:
        """Register a tool in the registry.

        Args:
            tool: Tool instance to register

        Raises:
            ValueError: If a tool with the same name already exists
        """
        if tool.name in self._tools:
            logger.warning(f"Tool '{tool.name}' already registered, replacing...")

        self._tools[tool.name] = tool
        self._execution_count[tool.name] = 0
        logger.info(f"Registered tool: {tool.name}")

    def unregister(self, tool_name: str) -> bool:
        """Unregister a tool from the registry.

        Args:
            tool_name: Name of the tool to unregister

        Returns:
            True if tool was unregistered, False if not found
        """
        if tool_name in self._tools:
            del self._tools[tool_name]
            del self._execution_count[tool_name]
            logger.info(f"Unregistered tool: {tool_name}")
            return True

        logger.warning(f"Tool '{tool_name}' not found for unregistration")
        return False

    def get_tool(self, tool_name: str) -> Optional[Tool]:
        """Get a tool by name.

        Args:
            tool_name: Name of the tool

        Returns:
            Tool instance if found, None otherwise
        """
        return self._tools.get(tool_name)

    def has_tool(self, tool_name: str) -> bool:
        """Check if a tool is registered.

        Args:
            tool_name: Name of the tool

        Returns:
            True if tool is registered, False otherwise
        """
        return tool_name in self._tools

    def list_tools(self) -> List[str]:
        """List all registered tool names.

        Returns:
            List of tool names
        """
        return list(self._tools.keys())

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """Get schemas for all registered tools.

        Returns:
            List of tool schemas containing name, description, parameters
        """
        return [tool.get_schema() for tool in self._tools.values()]

    def execute(self, tool_name: str, **kwargs) -> ToolResult:
        """Execute a tool by name.

        This is the primary method for executing tools. It handles
        tool lookup, execution, error handling, and result formatting.

        Args:
            tool_name: Name of the tool to execute
            **kwargs: Tool-specific parameters

        Returns:
            ToolResult containing the execution outcome
        """
        # Check if tool exists
        if tool_name not in self._tools:
            return ToolResult(
                tool_name=tool_name,
                success=False,
                result=None,
                error=f"Tool '{tool_name}' not found in registry",
                execution_time_ms=0.0,
                metadata={'available_tools': self.list_tools()}
            )

        # Execute the tool
        tool = self._tools[tool_name]
        result = tool.execute(**kwargs)

        # Track execution count
        self._execution_count[tool_name] += 1

        # Log execution
        if result.success:
            logger.debug(f"Tool '{tool_name}' executed successfully in {result.execution_time_ms:.1f}ms")
        else:
            logger.error(f"Tool '{tool_name}' failed: {result.error}")

        return result

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about tool usage.

        Returns:
            Dictionary containing:
                - total_tools: Number of registered tools
                - tool_names: List of tool names
                - execution_counts: Execution count per tool
                - total_executions: Total executions across all tools
        """
        return {
            'total_tools': len(self._tools),
            'tool_names': self.list_tools(),
            'execution_counts': self._execution_count.copy(),
            'total_executions': sum(self._execution_count.values())
        }

    def clear(self) -> None:
        """Clear all registered tools.

        This removes all tools and resets execution counts.
        Use with caution in production.
        """
        tool_count = len(self._tools)
        self._tools.clear()
        self._execution_count.clear()
        logger.info(f"Cleared all {tool_count} tools from registry")

    def __len__(self) -> int:
        """Return the number of registered tools."""
        return len(self._tools)

    def __contains__(self, tool_name: str) -> bool:
        """Check if a tool is registered using 'in' operator."""
        return tool_name in self._tools

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"ToolRegistry(tools={len(self._tools)}, executions={sum(self._execution_count.values())})"
