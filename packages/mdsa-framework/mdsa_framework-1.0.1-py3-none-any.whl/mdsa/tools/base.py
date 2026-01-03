"""
Base classes for the MDSA framework tool system.

This module provides the foundational classes for creating and managing tools.
"""

from typing import Any, Dict, Optional, List
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import time


@dataclass
class ToolResult:
    """Result from tool execution.

    This standardized result format makes it easy to handle tool outputs
    consistently across the framework.

    Attributes:
        tool_name: Name of the tool that was executed
        success: Whether the tool executed successfully
        result: The actual result data from the tool
        error: Error message if execution failed (None if successful)
        execution_time_ms: Time taken to execute the tool in milliseconds
        metadata: Additional metadata about the execution
    """
    tool_name: str
    success: bool
    result: Any
    error: Optional[str] = None
    execution_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'tool_name': self.tool_name,
            'success': self.success,
            'result': self.result,
            'error': self.error,
            'execution_time_ms': self.execution_time_ms,
            'metadata': self.metadata
        }

    def __str__(self) -> str:
        """String representation for logging."""
        if self.success:
            return f"[{self.tool_name}] SUCCESS ({self.execution_time_ms:.1f}ms): {self.result}"
        else:
            return f"[{self.tool_name}] FAILED ({self.execution_time_ms:.1f}ms): {self.error}"


class Tool(ABC):
    """Base class for all MDSA framework tools.

    All tools should inherit from this class and implement the execute() method.
    The tool system handles error handling, timing, and result formatting.

    Example:
        class CurrentTimeTool(Tool):
            def __init__(self):
                super().__init__(
                    name="get_current_time",
                    description="Get the current date and time",
                    parameters={}
                )

            def _execute(self, **kwargs) -> Any:
                from datetime import datetime
                return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    Attributes:
        name: Unique identifier for the tool
        description: Human-readable description of what the tool does
        parameters: Schema describing expected parameters
    """

    def __init__(self,
                 name: str,
                 description: str,
                 parameters: Optional[Dict[str, Any]] = None):
        """Initialize a tool.

        Args:
            name: Unique tool identifier
            description: What the tool does
            parameters: Parameter schema (optional)
        """
        self.name = name
        self.description = description
        self.parameters = parameters or {}

    @abstractmethod
    def _execute(self, **kwargs) -> Any:
        """Execute the tool logic.

        This method must be implemented by subclasses.
        It should contain the actual tool functionality.

        Args:
            **kwargs: Tool-specific parameters

        Returns:
            The result of the tool execution

        Raises:
            Any exceptions raised will be caught and returned as ToolResult errors
        """
        raise NotImplementedError(f"Tool {self.name} must implement _execute()")

    def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with error handling and timing.

        This wrapper method handles:
        - Execution timing
        - Error catching and formatting
        - Result standardization

        Args:
            **kwargs: Tool-specific parameters

        Returns:
            ToolResult containing the execution outcome
        """
        start_time = time.time()

        try:
            result = self._execute(**kwargs)
            execution_time_ms = (time.time() - start_time) * 1000

            return ToolResult(
                tool_name=self.name,
                success=True,
                result=result,
                error=None,
                execution_time_ms=execution_time_ms,
                metadata={'parameters': kwargs}
            )

        except Exception as e:
            execution_time_ms = (time.time() - start_time) * 1000

            return ToolResult(
                tool_name=self.name,
                success=False,
                result=None,
                error=str(e),
                execution_time_ms=execution_time_ms,
                metadata={'parameters': kwargs, 'exception_type': type(e).__name__}
            )

    def get_schema(self) -> Dict[str, Any]:
        """Get the tool's schema for documentation/validation.

        Returns:
            Dictionary containing tool metadata
        """
        return {
            'name': self.name,
            'description': self.description,
            'parameters': self.parameters
        }

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"Tool(name='{self.name}', description='{self.description}')"
