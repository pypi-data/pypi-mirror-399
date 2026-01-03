"""
Tool Calling for Chatbot (All Free & Open Source)

Provides various tools that the chatbot can call to perform actions.
"""

import logging
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
import re

logger = logging.getLogger(__name__)


class ToolRegistry:
    """Registry for chatbot tools."""

    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        self.descriptions: Dict[str, str] = {}

        # Register default tools
        self._register_default_tools()

    def register(self, name: str, description: str):
        """Decorator to register a tool."""
        def decorator(func: Callable):
            self.tools[name] = func
            self.descriptions[name] = description
            logger.info(f"Registered tool: {name}")
            return func
        return decorator

    def _register_default_tools(self):
        """Register default tools."""

        @self.register("get_current_time", "Get the current date and time")
        def get_current_time() -> str:
            """Get current date and time."""
            now = datetime.now()
            return now.strftime("%Y-%m-%d %H:%M:%S")

        @self.register("calculate", "Perform mathematical calculations")
        def calculate(expression: str) -> str:
            """
            Evaluate a mathematical expression safely.

            Args:
                expression: Math expression (e.g., "2 + 2", "10 * 5")

            Returns:
                str: Result of calculation
            """
            try:
                # Safe evaluation (only allow numbers and basic operators)
                allowed_chars = set('0123456789+-*/() .')
                if not all(c in allowed_chars for c in expression):
                    return "Error: Invalid characters in expression"

                result = eval(expression, {"__builtins__": {}}, {})
                return f"Result: {result}"
            except Exception as e:
                return f"Error: {str(e)}"

        @self.register("search_web", "Search the web for information")
        def search_web(query: str, num_results: int = 3) -> str:
            """
            Search the web using DuckDuckGo (no API key needed).

            Args:
                query: Search query
                num_results: Number of results to return

            Returns:
                str: Search results
            """
            try:
                # Use DuckDuckGo Instant Answer API (free, no key)
                url = f"https://api.duckduckgo.com/?q={query}&format=json"
                response = requests.get(url, timeout=5)
                data = response.json()

                if data.get('Abstract'):
                    return f"Summary: {data['Abstract']}\nSource: {data.get('AbstractURL', 'N/A')}"
                elif data.get('RelatedTopics'):
                    results = []
                    for i, topic in enumerate(data['RelatedTopics'][:num_results]):
                        if isinstance(topic, dict) and 'Text' in topic:
                            results.append(f"{i+1}. {topic['Text']}")
                    return "\n".join(results) if results else "No results found"
                else:
                    return "No results found"

            except Exception as e:
                return f"Error searching: {str(e)}"

        @self.register("get_weather", "Get weather information")
        def get_weather(city: str) -> str:
            """
            Get weather for a city using wttr.in (free, no API key).

            Args:
                city: City name

            Returns:
                str: Weather information
            """
            try:
                url = f"https://wttr.in/{city}?format=j1"
                response = requests.get(url, timeout=5)
                data = response.json()

                current = data['current_condition'][0]
                temp_c = current['temp_C']
                desc = current['weatherDesc'][0]['value']
                humidity = current['humidity']

                return f"Weather in {city}: {temp_c}°C, {desc}, Humidity: {humidity}%"

            except Exception as e:
                return f"Error getting weather: {str(e)}"

        @self.register("word_count", "Count words in text")
        def word_count(text: str) -> str:
            """Count words in text."""
            words = text.split()
            return f"Word count: {len(words)}"

        @self.register("extract_urls", "Extract URLs from text")
        def extract_urls(text: str) -> str:
            """Extract URLs from text."""
            url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
            urls = re.findall(url_pattern, text)

            if urls:
                return "Found URLs:\n" + "\n".join(f"- {url}" for url in urls)
            else:
                return "No URLs found"

        @self.register("convert_units", "Convert between units")
        def convert_units(value: float, from_unit: str, to_unit: str) -> str:
            """
            Convert between common units.

            Supported conversions:
            - Temperature: celsius, fahrenheit, kelvin
            - Distance: meters, kilometers, miles, feet
            - Weight: kg, pounds, grams
            """
            try:
                # Temperature conversions
                if from_unit.lower() in ['celsius', 'c'] and to_unit.lower() in ['fahrenheit', 'f']:
                    result = (value * 9/5) + 32
                    return f"{value}°C = {result:.2f}°F"
                elif from_unit.lower() in ['fahrenheit', 'f'] and to_unit.lower() in ['celsius', 'c']:
                    result = (value - 32) * 5/9
                    return f"{value}°F = {result:.2f}°C"

                # Distance conversions
                elif from_unit.lower() in ['km', 'kilometers'] and to_unit.lower() in ['miles']:
                    result = value * 0.621371
                    return f"{value} km = {result:.2f} miles"
                elif from_unit.lower() in ['miles'] and to_unit.lower() in ['km', 'kilometers']:
                    result = value * 1.60934
                    return f"{value} miles = {result:.2f} km"

                # Weight conversions
                elif from_unit.lower() in ['kg', 'kilograms'] and to_unit.lower() in ['pounds', 'lbs']:
                    result = value * 2.20462
                    return f"{value} kg = {result:.2f} lbs"
                elif from_unit.lower() in ['pounds', 'lbs'] and to_unit.lower() in ['kg', 'kilograms']:
                    result = value * 0.453592
                    return f"{value} lbs = {result:.2f} kg"

                else:
                    return f"Conversion from {from_unit} to {to_unit} not supported"

            except Exception as e:
                return f"Error converting units: {str(e)}"

    def call(self, tool_name: str, **kwargs) -> str:
        """
        Call a tool by name with arguments.

        Args:
            tool_name: Name of the tool
            **kwargs: Tool arguments

        Returns:
            str: Tool result
        """
        if tool_name not in self.tools:
            return f"Error: Unknown tool '{tool_name}'"

        try:
            result = self.tools[tool_name](**kwargs)
            return str(result)
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            return f"Error: {str(e)}"

    def get_available_tools(self) -> List[Dict[str, str]]:
        """Get list of available tools with descriptions."""
        return [
            {"name": name, "description": desc}
            for name, desc in self.descriptions.items()
        ]

    def format_tools_for_prompt(self) -> str:
        """Format tools as a string for LLM prompt."""
        tools = self.get_available_tools()

        parts = ["Available Tools:"]
        for tool in tools:
            parts.append(f"- {tool['name']}: {tool['description']}")

        parts.append("\nTo use a tool, respond with: USE_TOOL: tool_name(arg1=value1, arg2=value2)")

        return "\n".join(parts)

    def parse_and_execute(self, text: str) -> Optional[str]:
        """
        Parse text for tool calls and execute them.

        Args:
            text: Text that might contain tool calls

        Returns:
            str: Tool results if found, None otherwise
        """
        # Look for pattern: USE_TOOL: tool_name(args)
        pattern = r'USE_TOOL:\s*(\w+)\((.*?)\)'
        match = re.search(pattern, text)

        if not match:
            return None

        tool_name = match.group(1)
        args_str = match.group(2)

        # Parse arguments
        kwargs = {}
        if args_str.strip():
            # Simple parsing: arg1=value1, arg2=value2
            for part in args_str.split(','):
                if '=' in part:
                    key, value = part.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"\'')

                    # Try to convert to appropriate type
                    if value.isdigit():
                        value = int(value)
                    elif value.replace('.', '').isdigit():
                        value = float(value)

                    kwargs[key] = value

        # Execute tool
        result = self.call(tool_name, **kwargs)
        return result

    def __repr__(self) -> str:
        return f"<ToolRegistry tools={len(self.tools)}>"


# Example usage
if __name__ == "__main__":
    # Create registry
    registry = ToolRegistry()

    # List tools
    print("Available Tools:")
    for tool in registry.get_available_tools():
        print(f"  - {tool['name']}: {tool['description']}")

    # Call tools
    print("\nTesting tools:")
    print(registry.call("get_current_time"))
    print(registry.call("calculate", expression="2 + 2 * 5"))
    print(registry.call("word_count", text="Hello world this is a test"))
    print(registry.call("convert_units", value=100, from_unit="celsius", to_unit="fahrenheit"))

    # Parse and execute
    print("\nParsing tool call:")
    text = "Let me calculate that: USE_TOOL: calculate(expression=10 * 5)"
    result = registry.parse_and_execute(text)
    print(f"Result: {result}")
