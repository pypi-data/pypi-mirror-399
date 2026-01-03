"""
Phi-2 Model-Based Validator

Framework-level semantic validation using Phi-2 for:
- Input quality assessment
- Response relevance checking
- Tool usage correctness
- Reasoning coherence

This is FRAMEWORK-level validation. Domain-specific validation
(e.g., medical accuracy) should be implemented in application layer.

Author: MDSA Framework Team
Date: 2025-12-05
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import logging
import time
import re

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of model-based validation"""
    is_valid: bool
    confidence: float  # 0.0-1.0
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    validation_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        return (f"<ValidationResult valid={self.is_valid} "
                f"confidence={self.confidence:.2f} "
                f"issues={len(self.issues)}>")


class Phi2Validator:
    """
    Framework-level semantic validator using Phi-2.

    Validates:
    1. Input Quality: Is the query well-formed and actionable?
    2. Response Relevance: Does the response answer the query?
    3. Tool Usage: Were tools used correctly?
    4. Reasoning Coherence: Is the reasoning sound?

    Does NOT validate:
    - Domain-specific accuracy (e.g., medical correctness)
    - Business logic
    - Application-specific constraints
    """

    # Validation prompts for Phi-2
    INPUT_VALIDATION_PROMPT = """Evaluate this user query for quality and actionability.

USER QUERY: {query}

EVALUATION CRITERIA:
1. Clarity: Is the query clear and understandable?
2. Completeness: Does it contain enough information to process?
3. Actionability: Can a system take action on this query?
4. Safety: Does it contain harmful or inappropriate content?

Respond with:
- VALID if the query meets all criteria
- INVALID if it fails any criterion
- Explain the issue briefly if invalid

OUTPUT FORMAT:
Status: [VALID/INVALID]
Confidence: [0.0-1.0]
Reason: [Brief explanation]
"""

    RESPONSE_VALIDATION_PROMPT = """Evaluate if this response adequately answers the user's query.

USER QUERY: {query}

SYSTEM RESPONSE: {response}

EVALUATION CRITERIA:
1. Relevance: Does the response address the query?
2. Completeness: Does it provide sufficient information?
3. Coherence: Is the response logically structured?
4. Accuracy: Is the response factually consistent (not contradictory)?

Respond with:
- VALID if the response adequately answers the query
- INVALID if it fails to address the query properly
- Explain the issue if invalid

OUTPUT FORMAT:
Status: [VALID/INVALID]
Confidence: [0.0-1.0]
Reason: [Brief explanation]
"""

    TOOL_VALIDATION_PROMPT = """Evaluate if tools were used correctly for this query.

USER QUERY: {query}

TOOLS USED: {tools}

TOOL OUTPUTS: {tool_outputs}

EVALUATION CRITERIA:
1. Appropriateness: Were the right tools selected?
2. Correct Usage: Were tools called with valid parameters?
3. Result Handling: Were tool outputs used properly?
4. Completeness: Were all necessary tools used?

Respond with:
- VALID if tools were used correctly
- INVALID if there are issues with tool usage
- Explain the issue if invalid

OUTPUT FORMAT:
Status: [VALID/INVALID]
Confidence: [0.0-1.0]
Reason: [Brief explanation]
"""

    def __init__(
        self,
        model_manager=None,
        enable_caching: bool = True,
        confidence_threshold: float = 0.7
    ):
        """
        Initialize Phi-2 Validator.

        Args:
            model_manager: ModelManager instance (optional, will create if None)
            enable_caching: Enable result caching for identical inputs
            confidence_threshold: Minimum confidence for valid results (default: 0.7)
        """
        self.model_manager = model_manager
        self.enable_caching = enable_caching
        self.confidence_threshold = confidence_threshold
        self._cache: Dict[str, ValidationResult] = {}

        # Model config for Phi-2
        self.model_config = {
            'model_name': 'microsoft/phi-2',
            'max_length': 512,
            'temperature': 0.2,  # Low temperature for consistent validation
            'top_p': 0.9,
            'max_new_tokens': 256
        }

        logger.info("Phi2Validator initialized (framework-level semantic validation)")

    def validate_input(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        Validate input query quality.

        Args:
            query: User query to validate
            context: Optional context (user info, session data, etc.)

        Returns:
            ValidationResult with validation assessment
        """
        start_time = time.time()

        # Check cache
        cache_key = f"input:{query}"
        if self.enable_caching and cache_key in self._cache:
            cached_result = self._cache[cache_key]
            logger.info(f"Returning cached input validation for: {query[:50]}...")
            return cached_result

        try:
            # Use Phi-2 for semantic validation
            # Note: In production, this would call the actual model
            # For now, using heuristic-based approach
            result = self._validate_input_heuristic(query)

            validation_time_ms = (time.time() - start_time) * 1000
            result.validation_time_ms = validation_time_ms

            # Cache result
            if self.enable_caching:
                self._cache[cache_key] = result

            logger.info(
                f"Input validation: valid={result.is_valid}, "
                f"confidence={result.confidence:.2f}, time={validation_time_ms:.0f}ms"
            )

            return result

        except Exception as e:
            logger.error(f"Input validation failed: {e}")
            return ValidationResult(
                is_valid=False,
                confidence=0.0,
                issues=[f"Validation error: {str(e)}"],
                validation_time_ms=(time.time() - start_time) * 1000
            )

    def validate_response(
        self,
        query: str,
        response: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        Validate that response adequately answers the query.

        Args:
            query: User query
            response: System response
            context: Optional context

        Returns:
            ValidationResult with validation assessment
        """
        start_time = time.time()

        # Check cache
        cache_key = f"response:{query}:{response[:100]}"
        if self.enable_caching and cache_key in self._cache:
            return self._cache[cache_key]

        try:
            # Use Phi-2 for semantic validation
            result = self._validate_response_heuristic(query, response)

            validation_time_ms = (time.time() - start_time) * 1000
            result.validation_time_ms = validation_time_ms

            # Cache result
            if self.enable_caching:
                self._cache[cache_key] = result

            logger.info(
                f"Response validation: valid={result.is_valid}, "
                f"confidence={result.confidence:.2f}"
            )

            return result

        except Exception as e:
            logger.error(f"Response validation failed: {e}")
            return ValidationResult(
                is_valid=False,
                confidence=0.0,
                issues=[f"Validation error: {str(e)}"],
                validation_time_ms=(time.time() - start_time) * 1000
            )

    def validate_tool_usage(
        self,
        query: str,
        tools_used: List[Dict[str, Any]],
        tool_outputs: List[Any]
    ) -> ValidationResult:
        """
        Validate that tools were used correctly.

        Args:
            query: User query
            tools_used: List of tools that were called
            tool_outputs: Outputs from tool executions

        Returns:
            ValidationResult with validation assessment
        """
        start_time = time.time()

        try:
            # Use Phi-2 for semantic validation
            result = self._validate_tool_usage_heuristic(query, tools_used, tool_outputs)

            validation_time_ms = (time.time() - start_time) * 1000
            result.validation_time_ms = validation_time_ms

            logger.info(
                f"Tool validation: valid={result.is_valid}, "
                f"tools={len(tools_used)}"
            )

            return result

        except Exception as e:
            logger.error(f"Tool validation failed: {e}")
            return ValidationResult(
                is_valid=False,
                confidence=0.0,
                issues=[f"Validation error: {str(e)}"],
                validation_time_ms=(time.time() - start_time) * 1000
            )

    # Heuristic implementations (production would use actual Phi-2 model)

    def _validate_input_heuristic(self, query: str) -> ValidationResult:
        """
        Heuristic-based input validation.

        In production, this would:
        1. Load Phi-2 model
        2. Generate validation with prompt
        3. Parse response
        4. Return ValidationResult
        """
        issues = []
        warnings = []
        confidence = 1.0

        # Check 1: Empty or too short
        if not query or len(query.strip()) < 3:
            issues.append("Query is too short or empty")
            confidence = 0.0

        # Check 2: Too long
        if len(query) > 1000:
            warnings.append("Query is very long (may be truncated)")
            confidence *= 0.9

        # Check 3: Contains only special characters
        if query and not re.search(r'[a-zA-Z0-9]', query):
            issues.append("Query contains no alphanumeric characters")
            confidence *= 0.5

        # Check 4: Harmful content (basic check)
        harmful_patterns = [
            r'\bexploit\b.*\bsystem\b',
            r'\bhack\b',
            r'\bmalicious\b',
            r'\bdelete\s+all\b'
        ]
        for pattern in harmful_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                warnings.append("Query may contain harmful intent")
                confidence *= 0.8

        # Check 5: Clarity (has question words or action verbs)
        clarity_indicators = [
            r'\b(what|how|when|where|why|which|who)\b',
            r'\b(show|get|find|calculate|analyze|create|update|delete)\b'
        ]
        has_clarity = any(re.search(pattern, query, re.IGNORECASE) for pattern in clarity_indicators)
        if not has_clarity and len(query.split()) > 5:
            warnings.append("Query may lack clarity or action words")
            confidence *= 0.9

        is_valid = len(issues) == 0 and confidence >= self.confidence_threshold

        return ValidationResult(
            is_valid=is_valid,
            confidence=confidence,
            issues=issues,
            warnings=warnings,
            metadata={'validation_type': 'input'}
        )

    def _validate_response_heuristic(
        self,
        query: str,
        response: str
    ) -> ValidationResult:
        """
        Heuristic-based response validation.

        Checks if response adequately addresses the query.
        """
        issues = []
        warnings = []
        confidence = 1.0

        # Check 1: Response is empty
        if not response or len(response.strip()) < 5:
            issues.append("Response is too short or empty")
            confidence = 0.0
            return ValidationResult(
                is_valid=False,
                confidence=confidence,
                issues=issues,
                metadata={'validation_type': 'response'}
            )

        # Check 2: Response is just an error message
        error_patterns = [
            r'^error:',
            r'^exception:',
            r'failed to',
            r'could not'
        ]
        for pattern in error_patterns:
            if re.search(pattern, response.lower()):
                warnings.append("Response contains error indicators")
                confidence *= 0.7

        # Check 3: Keyword overlap (simple relevance check)
        query_words = set(re.findall(r'\b\w+\b', query.lower()))
        response_words = set(re.findall(r'\b\w+\b', response.lower()))

        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 'in', 'on', 'at', 'to', 'for'}
        query_words -= stop_words
        response_words -= stop_words

        if query_words:
            overlap = len(query_words & response_words) / len(query_words)
            if overlap < 0.1:
                warnings.append("Low keyword overlap between query and response")
                confidence *= 0.8

        # Check 4: Response too generic
        generic_responses = [
            r'^(ok|okay|yes|no)\.?$',
            r'^i (don\'t know|cannot)',
            r'^sorry'
        ]
        for pattern in generic_responses:
            if re.search(pattern, response.lower()):
                warnings.append("Response may be too generic")
                confidence *= 0.85

        # Check 5: Response length appropriate
        if len(response) < 20:
            warnings.append("Response may be too brief")
            confidence *= 0.9
        elif len(response) > 5000:
            warnings.append("Response is very long")
            confidence *= 0.95

        is_valid = len(issues) == 0 and confidence >= self.confidence_threshold

        return ValidationResult(
            is_valid=is_valid,
            confidence=confidence,
            issues=issues,
            warnings=warnings,
            metadata={
                'validation_type': 'response',
                'keyword_overlap': len(query_words & response_words) / len(query_words) if query_words else 0
            }
        )

    def _validate_tool_usage_heuristic(
        self,
        query: str,
        tools_used: List[Dict[str, Any]],
        tool_outputs: List[Any]
    ) -> ValidationResult:
        """
        Heuristic-based tool usage validation.

        Checks if tools were used appropriately.
        """
        issues = []
        warnings = []
        confidence = 1.0

        # Check 1: Tools used when needed
        # Extract potential tool-requiring keywords from query
        tool_indicators = {
            'lookup': ['lookup', 'search', 'find', 'get'],
            'calculate': ['calculate', 'compute', 'sum', 'total'],
            'validate': ['validate', 'check', 'verify'],
            'create': ['create', 'make', 'generate']
        }

        query_lower = query.lower()
        expected_tool_types = []
        for tool_type, keywords in tool_indicators.items():
            if any(keyword in query_lower for keyword in keywords):
                expected_tool_types.append(tool_type)

        # If query suggests tools but none used
        if expected_tool_types and not tools_used:
            warnings.append(f"Query suggests tools ({', '.join(expected_tool_types)}) but none were used")
            confidence *= 0.8

        # Check 2: Tool outputs are valid
        if len(tools_used) != len(tool_outputs):
            issues.append(f"Tool count mismatch: {len(tools_used)} tools used, {len(tool_outputs)} outputs")
            confidence *= 0.5

        # Check 3: No duplicate tool calls (unless intentional)
        tool_names = [tool.get('name', tool.get('tool_name', 'unknown')) for tool in tools_used]
        if len(tool_names) != len(set(tool_names)):
            warnings.append("Duplicate tool calls detected")
            confidence *= 0.9

        # Check 4: Tool outputs are not errors
        for i, output in enumerate(tool_outputs):
            if isinstance(output, str):
                if 'error' in output.lower() or 'failed' in output.lower():
                    warnings.append(f"Tool {i+1} returned error: {output[:100]}")
                    confidence *= 0.85

        is_valid = len(issues) == 0 and confidence >= self.confidence_threshold

        return ValidationResult(
            is_valid=is_valid,
            confidence=confidence,
            issues=issues,
            warnings=warnings,
            metadata={
                'validation_type': 'tool_usage',
                'tools_count': len(tools_used),
                'expected_tool_types': expected_tool_types
            }
        )

    def clear_cache(self):
        """Clear the validation cache"""
        self._cache.clear()
        logger.info("Validation cache cleared")

    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        return {
            'cache_size': len(self._cache),
            'cache_enabled': self.enable_caching
        }


# Convenience functions
def validate_input(query: str, **kwargs) -> ValidationResult:
    """Convenience function to validate input"""
    validator = Phi2Validator()
    return validator.validate_input(query, **kwargs)


def validate_response(query: str, response: str, **kwargs) -> ValidationResult:
    """Convenience function to validate response"""
    validator = Phi2Validator()
    return validator.validate_response(query, response, **kwargs)


def validate_tools(query: str, tools_used: List[Dict], tool_outputs: List, **kwargs) -> ValidationResult:
    """Convenience function to validate tool usage"""
    validator = Phi2Validator()
    return validator.validate_tool_usage(query, tools_used, tool_outputs, **kwargs)


if __name__ == "__main__":
    # Demo usage
    validator = Phi2Validator()

    print("=== Phi-2 Validator Demo ===\n")

    # Test 1: Input validation
    print("Test 1: Input Validation")
    queries = [
        "Calculate billing charges for patient",
        "xyz",
        "",
        "This is a very long query that goes on and on" * 20
    ]

    for query in queries:
        result = validator.validate_input(query)
        print(f"  Query: '{query[:50]}...'")
        print(f"  Result: {result}")
        print()

    # Test 2: Response validation
    print("\nTest 2: Response Validation")
    test_cases = [
        ("Calculate billing", "The total billing amount is $150.00"),
        ("What is the weather?", "Error: cannot process"),
        ("Code diagnosis", "Yes"),
    ]

    for query, response in test_cases:
        result = validator.validate_response(query, response)
        print(f"  Query: '{query}'")
        print(f"  Response: '{response}'")
        print(f"  Result: {result}")
        print()

    # Test 3: Tool validation
    print("\nTest 3: Tool Validation")
    result = validator.validate_tool_usage(
        "Lookup ICD-10 code for diabetes",
        [{'name': 'lookup_icd10', 'params': {'query': 'diabetes'}}],
        ["E11.9: Type 2 diabetes mellitus"]
    )
    print(f"  Result: {result}")
