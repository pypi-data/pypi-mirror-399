"""
Built-in tools for the MDSA framework.

This module provides ready-to-use tools that cover common use cases.
Users can also create custom tools by inheriting from the Tool base class.
"""

from typing import Any
from datetime import datetime
import re
from .base import Tool


class CurrentTimeTool(Tool):
    """Tool to get the current date and time."""

    def __init__(self):
        super().__init__(
            name="get_current_time",
            description="Get the current date and time",
            parameters={}
        )

    def _execute(self, **kwargs) -> str:
        """Return current date and time in readable format."""
        now = datetime.now()
        return now.strftime("%Y-%m-%d %H:%M:%S")


class CalculatorTool(Tool):
    """Tool to perform mathematical calculations."""

    def __init__(self):
        super().__init__(
            name="calculate",
            description="Perform mathematical calculations",
            parameters={
                'expression': {
                    'type': 'string',
                    'description': 'Mathematical expression to evaluate (e.g., "5+10")',
                    'required': True
                }
            }
        )

    def _execute(self, expression: str, **kwargs) -> str:
        """Evaluate a mathematical expression safely.

        Args:
            expression: Math expression like "5+10", "20*3"

        Returns:
            Result as string

        Raises:
            ValueError: If expression is invalid or contains unsafe operations
        """
        # Sanitize expression - only allow numbers and basic operators
        if not re.match(r'^[\d\s+\-*/().]+$', expression):
            raise ValueError(f"Invalid expression: {expression}")

        try:
            # Evaluate safely
            result = eval(expression, {"__builtins__": {}}, {})
            return f"Result: {result}"
        except Exception as e:
            raise ValueError(f"Cannot evaluate expression: {str(e)}")


class WebSearchTool(Tool):
    """Tool to search the web (placeholder implementation)."""

    def __init__(self):
        super().__init__(
            name="search_web",
            description="Search the web for information",
            parameters={
                'query': {
                    'type': 'string',
                    'description': 'Search query',
                    'required': True
                }
            }
        )

    def _execute(self, query: str, **kwargs) -> str:
        """Search the web (placeholder).

        In production, this would integrate with a search API
        like Google, Bing, or DuckDuckGo.

        Args:
            query: Search query

        Returns:
            Search results or placeholder message
        """
        # Placeholder implementation
        return f"[Web Search] This would search for: '{query}' (API integration required)"


class WeatherTool(Tool):
    """Tool to get weather information (placeholder implementation)."""

    def __init__(self):
        super().__init__(
            name="get_weather",
            description="Get weather information for a location",
            parameters={
                'location': {
                    'type': 'string',
                    'description': 'Location to get weather for',
                    'required': True
                }
            }
        )

    def _execute(self, location: str, **kwargs) -> str:
        """Get weather for a location (placeholder).

        In production, this would integrate with a weather API
        like OpenWeatherMap, Weather.gov, or AccuWeather.

        Args:
            location: Location name or coordinates

        Returns:
            Weather information or placeholder message
        """
        # Placeholder implementation
        return f"[Weather] This would get weather for: '{location}' (API integration required)"


class WordCountTool(Tool):
    """Tool to count words in text."""

    def __init__(self):
        super().__init__(
            name="word_count",
            description="Count the number of words in text",
            parameters={
                'text': {
                    'type': 'string',
                    'description': 'Text to count words in',
                    'required': True
                }
            }
        )

    def _execute(self, text: str, **kwargs) -> str:
        """Count words in text.

        Args:
            text: Text to analyze

        Returns:
            Word count as string
        """
        # Split by whitespace and count non-empty strings
        words = [w for w in text.split() if w.strip()]
        count = len(words)
        return f"Word count: {count}"


class URLExtractorTool(Tool):
    """Tool to extract URLs from text."""

    def __init__(self):
        super().__init__(
            name="extract_urls",
            description="Extract URLs from text",
            parameters={
                'text': {
                    'type': 'string',
                    'description': 'Text to extract URLs from',
                    'required': True
                }
            }
        )

    def _execute(self, text: str, **kwargs) -> str:
        """Extract URLs from text.

        Args:
            text: Text containing URLs

        Returns:
            List of URLs as string
        """
        # Regex pattern for URLs
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, text)

        if urls:
            return f"Found {len(urls)} URL(s): {', '.join(urls)}"
        else:
            return "No URLs found in text"


class UnitConverterTool(Tool):
    """Tool to convert between different units."""

    def __init__(self):
        super().__init__(
            name="convert_units",
            description="Convert between different units (temperature, distance, weight)",
            parameters={
                'value': {
                    'type': 'number',
                    'description': 'Value to convert',
                    'required': True
                },
                'from_unit': {
                    'type': 'string',
                    'description': 'Source unit (e.g., "celsius", "km", "kg")',
                    'required': True
                },
                'to_unit': {
                    'type': 'string',
                    'description': 'Target unit (e.g., "fahrenheit", "miles", "pounds")',
                    'required': True
                }
            }
        )

        # Conversion factors (base unit conversions)
        self.conversions = {
            # Temperature (special case - formulas)
            ('celsius', 'fahrenheit'): lambda x: (x * 9/5) + 32,
            ('fahrenheit', 'celsius'): lambda x: (x - 32) * 5/9,
            ('celsius', 'kelvin'): lambda x: x + 273.15,
            ('kelvin', 'celsius'): lambda x: x - 273.15,

            # Distance (to meters)
            ('km', 'meter'): lambda x: x * 1000,
            ('meter', 'km'): lambda x: x / 1000,
            ('mile', 'meter'): lambda x: x * 1609.34,
            ('meter', 'mile'): lambda x: x / 1609.34,
            ('foot', 'meter'): lambda x: x * 0.3048,
            ('meter', 'foot'): lambda x: x / 0.3048,

            # Weight (to kg)
            ('pound', 'kg'): lambda x: x * 0.453592,
            ('kg', 'pound'): lambda x: x / 0.453592,
            ('gram', 'kg'): lambda x: x / 1000,
            ('kg', 'gram'): lambda x: x * 1000,
        }

    def _execute(self, value: float, from_unit: str, to_unit: str, **kwargs) -> str:
        """Convert between units.

        Args:
            value: Numeric value to convert
            from_unit: Source unit
            to_unit: Target unit

        Returns:
            Conversion result as string

        Raises:
            ValueError: If conversion is not supported
        """
        from_unit = from_unit.lower()
        to_unit = to_unit.lower()

        # Check if same unit
        if from_unit == to_unit:
            return f"{value} {from_unit} = {value} {to_unit}"

        # Check if conversion exists
        key = (from_unit, to_unit)
        if key in self.conversions:
            result = self.conversions[key](value)
            return f"{value} {from_unit} = {result:.2f} {to_unit}"
        else:
            raise ValueError(f"Conversion from '{from_unit}' to '{to_unit}' not supported")


def get_default_tools() -> list[Tool]:
    """Get all default built-in tools.

    Returns:
        List of Tool instances
    """
    return [
        CurrentTimeTool(),
        CalculatorTool(),
        WebSearchTool(),
        WeatherTool(),
        WordCountTool(),
        URLExtractorTool(),
        UnitConverterTool(),
    ]
