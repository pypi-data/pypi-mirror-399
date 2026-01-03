"""
Smart Tool Executor for the MDSA framework.

This module implements intelligent tool detection and execution based on
semantic analysis of queries, without relying on specific model output formats.
"""

from typing import Dict, List, Optional, Any, Tuple
import re
import logging
from .registry import ToolRegistry
from .base import ToolResult


logger = logging.getLogger(__name__)


class SmartToolExecutor:
    """Framework-level intelligent tool detection and execution.

    The SmartToolExecutor uses semantic analysis to detect when tools should
    be used based on query content, rather than requiring models to generate
    specific output formats like "USE_TOOL: tool_name(args)".

    This approach is model-agnostic and works with any LLM (GPT-2, Phi-2, Llama, etc.).
    It's also future-ready for proper function calling with APIs and MCPs.

    Features:
    - Semantic intent detection from queries
    - Parameter extraction using regex and NLP techniques
    - Context-aware tool selection
    - Extensible pattern matching
    - Support for multiple tools per query
    - Fallback strategies for ambiguous queries

    Example:
        registry = ToolRegistry()
        registry.register(CurrentTimeTool())
        registry.register(CalculatorTool())

        executor = SmartToolExecutor(registry)

        # Detects time query and executes get_current_time
        results = executor.detect_and_execute("What time is it?")

        # Detects calculation and executes calculate
        results = executor.detect_and_execute("What is 5 plus 10?")
    """

    def __init__(self, tool_registry: ToolRegistry):
        """Initialize the smart tool executor.

        Args:
            tool_registry: ToolRegistry instance managing available tools
        """
        self.registry = tool_registry
        self.function_handler = None  # For future function calling support
        logger.info("SmartToolExecutor initialized")

    def detect_and_execute(self,
                          query: str,
                          context: Optional[Dict[str, Any]] = None) -> List[ToolResult]:
        """Detect which tools are needed and execute them.

        This is the main entry point for smart tool execution. It analyzes
        the query to detect tool needs and executes relevant tools.

        Args:
            query: The user's query text
            context: Optional context (user location, previous queries, etc.)

        Returns:
            List of ToolResult objects from executed tools
        """
        context = context or {}
        detected_tools: List[Tuple[str, Dict[str, Any]]] = []

        # Time-related queries
        if self._is_time_query(query):
            detected_tools.append(('get_current_time', {}))
            logger.debug("Detected time query")

        # Calculation queries
        if self._is_calculation_query(query):
            expression = self._extract_math_expression(query)
            if expression:
                detected_tools.append(('calculate', {'expression': expression}))
                logger.debug(f"Detected calculation query: {expression}")

        # Weather queries
        if self._is_weather_query(query):
            location = self._extract_location(query, context)
            detected_tools.append(('get_weather', {'location': location}))
            logger.debug(f"Detected weather query for location: {location}")

        # Web search queries
        if self._is_search_query(query):
            detected_tools.append(('search_web', {'query': query}))
            logger.debug("Detected web search query")

        # Unit conversion queries
        if self._is_conversion_query(query):
            params = self._extract_conversion_params(query)
            if params:
                detected_tools.append(('convert_units', params))
                logger.debug(f"Detected unit conversion: {params}")

        # Word count queries
        if self._is_word_count_query(query):
            text = self._extract_text_for_counting(query)
            detected_tools.append(('word_count', {'text': text}))
            logger.debug("Detected word count query")

        # URL extraction queries
        if self._is_url_extraction_query(query):
            detected_tools.append(('extract_urls', {'text': query}))
            logger.debug("Detected URL extraction query")

        # Execute all detected tools
        results = []
        for tool_name, params in detected_tools:
            # Check if tool is registered
            if not self.registry.has_tool(tool_name):
                logger.warning(f"Tool '{tool_name}' detected but not registered")
                continue

            result = self.registry.execute(tool_name, **params)
            results.append(result)

        if not results:
            logger.debug(f"No tools detected for query: {query}")

        return results

    # ==================== Intent Detection Methods ====================

    def _is_time_query(self, query: str) -> bool:
        """Detect if query is asking for time/date.

        Args:
            query: User query

        Returns:
            True if query is time-related
        """
        keywords = [
            'time', 'date', 'clock', 'when is it', 'what time',
            'current time', 'today', 'now', "what's the time",
            'what day', 'current date'
        ]
        query_lower = query.lower()
        return any(kw in query_lower for kw in keywords)

    def _is_calculation_query(self, query: str) -> bool:
        """Detect if query involves mathematical calculation.

        Args:
            query: User query

        Returns:
            True if query requires calculation
        """
        keywords = ['calculate', 'compute', 'solve', 'what is', 'how much is']
        math_ops = ['+', '-', '*', '/', 'plus', 'minus', 'times', 'divided', 'multiply']

        query_lower = query.lower()
        has_keyword = any(kw in query_lower for kw in keywords)
        has_math_op = any(op in query_lower for op in math_ops)
        has_numbers = bool(re.search(r'\d+', query))

        return has_keyword and (has_math_op or has_numbers)

    def _is_weather_query(self, query: str) -> bool:
        """Detect if query is asking for weather information.

        Args:
            query: User query

        Returns:
            True if query is weather-related
        """
        keywords = [
            'weather', 'temperature', 'forecast', 'rain', 'sunny',
            'cloudy', 'hot', 'cold', 'humidity', 'climate'
        ]
        query_lower = query.lower()
        return any(kw in query_lower for kw in keywords)

    def _is_search_query(self, query: str) -> bool:
        """Detect if query requires web search.

        Args:
            query: User query

        Returns:
            True if query should trigger web search
        """
        keywords = [
            'search', 'find', 'look up', 'google', 'web search',
            'search for', 'find information', 'look for'
        ]
        query_lower = query.lower()
        return any(kw in query_lower for kw in keywords)

    def _is_conversion_query(self, query: str) -> bool:
        """Detect if query involves unit conversion.

        Args:
            query: User query

        Returns:
            True if query requires unit conversion
        """
        keywords = ['convert', 'conversion', 'to', 'from']
        units = [
            'meter', 'km', 'mile', 'foot', 'inch',
            'kg', 'pound', 'gram', 'ounce',
            'celsius', 'fahrenheit', 'kelvin'
        ]

        query_lower = query.lower()
        has_keyword = any(kw in query_lower for kw in keywords)
        has_units = sum(1 for unit in units if unit in query_lower) >= 2

        return has_keyword and has_units

    def _is_word_count_query(self, query: str) -> bool:
        """Detect if query is asking for word count.

        Args:
            query: User query

        Returns:
            True if query asks for word count
        """
        keywords = ['word count', 'count words', 'how many words', 'number of words']
        query_lower = query.lower()
        return any(kw in query_lower for kw in keywords)

    def _is_url_extraction_query(self, query: str) -> bool:
        """Detect if query involves extracting URLs.

        Args:
            query: User query

        Returns:
            True if query asks to extract URLs
        """
        keywords = ['extract url', 'find url', 'get url', 'urls in', 'extract link']
        query_lower = query.lower()
        return any(kw in query_lower for kw in keywords)

    # ==================== Parameter Extraction Methods ====================

    def _extract_math_expression(self, query: str) -> Optional[str]:
        """Extract mathematical expression from query.

        Args:
            query: User query

        Returns:
            Mathematical expression string, or None if not found
        """
        query_lower = query.lower()

        # Pattern 1: "5 + 10", "5+10", "5 plus 10"
        pattern = r'(\d+\.?\d*)\s*([+\-*/]|\bplus\b|\bminus\b|\btimes\b|\bdivided\s+by\b)\s*(\d+\.?\d*)'
        match = re.search(pattern, query_lower)

        if match:
            num1, op, num2 = match.groups()

            # Convert word operators to symbols
            op_map = {
                'plus': '+',
                'minus': '-',
                'times': '*',
                'divided by': '/',
                'multiply': '*',
                'divide': '/'
            }
            op = op_map.get(op, op)

            return f"{num1}{op}{num2}"

        # Pattern 2: "what is X" where X is a simple math expression
        pattern2 = r'what\s+is\s+([\d\s+\-*/().]+)'
        match2 = re.search(pattern2, query_lower)
        if match2:
            expr = match2.group(1).strip()
            # Validate it looks like math
            if re.match(r'^[\d\s+\-*/().]+$', expr):
                return expr

        return None

    def _extract_location(self, query: str, context: Dict[str, Any]) -> str:
        """Extract location from query or context.

        Args:
            query: User query
            context: Context dictionary potentially containing location

        Returns:
            Location string (defaults to "current location" if not found)
        """
        # Try to extract location from query
        # Pattern: "in [Location]", "at [Location]", "weather for [Location]"
        patterns = [
            r'(?:in|at|for)\s+([A-Z][a-zA-Z\s]+)',  # "in New York"
            r'weather\s+([A-Z][a-zA-Z\s]+)',  # "weather New York"
        ]

        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                location = match.group(1).strip()
                if len(location) > 2:  # Avoid single letters
                    return location

        # Try context
        if 'location' in context:
            return context['location']

        # Default
        return "current location"

    def _extract_conversion_params(self, query: str) -> Optional[Dict[str, Any]]:
        """Extract unit conversion parameters.

        Args:
            query: User query

        Returns:
            Dictionary with 'value', 'from_unit', 'to_unit', or None
        """
        # Pattern: "convert X [unit] to [unit]"
        pattern = r'convert\s+(\d+\.?\d*)\s+(\w+)\s+to\s+(\w+)'
        match = re.search(pattern, query.lower())

        if match:
            value, from_unit, to_unit = match.groups()
            return {
                'value': float(value),
                'from_unit': from_unit,
                'to_unit': to_unit
            }

        return None

    def _extract_text_for_counting(self, query: str) -> str:
        """Extract text for word counting.

        Args:
            query: User query

        Returns:
            Text to count words in
        """
        # Try to extract quoted text
        quote_match = re.search(r'["\'](.+?)["\']', query)
        if quote_match:
            return quote_match.group(1)

        # Otherwise use the whole query
        return query

    # ==================== Future Function Calling Support ====================

    def register_function_calling_handler(self, handler: Any) -> None:
        """Register handler for models with native function calling.

        This is a hook for future enhancement when using models
        that support native function calling (e.g., GPT-4, Claude).

        Args:
            handler: Function calling handler
        """
        self.function_handler = handler
        logger.info("Function calling handler registered")

    def supports_function_calling(self) -> bool:
        """Check if function calling is available.

        Returns:
            True if a function calling handler is registered
        """
        return self.function_handler is not None

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"SmartToolExecutor(tools={len(self.registry)}, function_calling={self.supports_function_calling()})"
