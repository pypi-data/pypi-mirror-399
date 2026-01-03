"""
Complexity Analyzer for MDSA Framework

Analyzes query complexity to determine routing strategy:
- Simple queries: Use TinyBERT for fast domain routing (<50ms)
- Complex queries: Use Phi-2 for reasoning-based task decomposition (<2s)

Author: MDSA Framework Team
Date: 2025-12-05
"""

from typing import Tuple, List, Dict, Any
from dataclasses import dataclass
import re


@dataclass
class ComplexityResult:
    """Result of complexity analysis"""
    is_complex: bool
    complexity_score: float  # 0.0-1.0, higher = more complex
    indicators: List[str]  # Reasons why query is complex
    requires_reasoning: bool  # Needs Phi-2 reasoning
    requires_multi_domain: bool  # Needs multiple domains
    requires_sequential: bool  # Needs sequential execution

    def __repr__(self) -> str:
        return (f"<ComplexityResult complex={self.is_complex} "
                f"score={self.complexity_score:.2f} indicators={len(self.indicators)}>")


class ComplexityAnalyzer:
    """
    Analyzes query complexity to determine optimal routing strategy.

    Simple queries (complexity < 0.3):
    - Single domain
    - No conditional logic
    - No multi-step reasoning
    → Route with TinyBERT (<50ms)

    Complex queries (complexity >= 0.3):
    - Multi-domain tasks
    - Sequential operations
    - Conditional logic
    - Reasoning required
    → Route with Phi-2 Reasoner (<2s)
    """

    # Keywords indicating complexity
    MULTI_DOMAIN_KEYWORDS = [
        'and then', 'then', 'after that', 'next', 'followed by',
        'also', 'plus', 'additionally', 'furthermore', 'as well as'
    ]

    CONDITIONAL_KEYWORDS = [
        'if', 'when', 'unless', 'in case', 'should', 'would',
        'depending on', 'based on', 'according to'
    ]

    SEQUENTIAL_KEYWORDS = [
        'first', 'second', 'third', 'finally', 'lastly',
        'step 1', 'step 2', 'step 3', 'before', 'after'
    ]

    REASONING_KEYWORDS = [
        'why', 'how', 'explain', 'compare', 'analyze',
        'evaluate', 'recommend', 'suggest', 'determine'
    ]

    MULTI_TASK_PATTERNS = [
        r'\band\b.*\b(code|bill|claim|submit)',  # "code and bill"
        r'(code|bill|claim).*\band\b',  # "bill and submit"
        r'\bthen\b',  # "do X then Y"
        r'first.*then',  # "first X then Y"
        r'after.*then',  # "after X then Y"
    ]

    def __init__(self, complexity_threshold: float = 0.3):
        """
        Initialize ComplexityAnalyzer.

        Args:
            complexity_threshold: Threshold for complex vs simple (0.0-1.0)
                                 Default 0.3 means queries with 30%+ complexity
                                 indicators will use Phi-2 reasoning
        """
        self.complexity_threshold = complexity_threshold

    def analyze(self, query: str) -> ComplexityResult:
        """
        Analyze query complexity.

        Args:
            query: User query string

        Returns:
            ComplexityResult with complexity assessment
        """
        query_lower = query.lower()
        indicators = []
        score = 0.0

        # Check 1: Multi-domain indicators (weight: 0.3)
        multi_domain = self._check_multi_domain(query_lower)
        if multi_domain:
            indicators.append("multi_domain_task")
            score += 0.3

        # Check 2: Conditional logic (weight: 0.25)
        has_conditional = self._check_conditional(query_lower)
        if has_conditional:
            indicators.append("conditional_logic")
            score += 0.25

        # Check 3: Sequential operations (weight: 0.2)
        has_sequential = self._check_sequential(query_lower)
        if has_sequential:
            indicators.append("sequential_operations")
            score += 0.2

        # Check 4: Reasoning required (weight: 0.15)
        needs_reasoning = self._check_reasoning(query_lower)
        if needs_reasoning:
            indicators.append("reasoning_required")
            score += 0.15

        # Check 5: Long query (weight: 0.1)
        word_count = len(query.split())
        if word_count > 20:
            indicators.append("long_query")
            score += 0.1

        # Determine if complex
        is_complex = score >= self.complexity_threshold

        return ComplexityResult(
            is_complex=is_complex,
            complexity_score=min(score, 1.0),  # Cap at 1.0
            indicators=indicators,
            requires_reasoning=needs_reasoning or has_conditional,
            requires_multi_domain=multi_domain,
            requires_sequential=has_sequential
        )

    def _check_multi_domain(self, query: str) -> bool:
        """Check if query involves multiple domains or tasks"""
        # Check for explicit multi-domain keywords
        if any(keyword in query for keyword in self.MULTI_DOMAIN_KEYWORDS):
            return True

        # Check for multi-task patterns
        for pattern in self.MULTI_TASK_PATTERNS:
            if re.search(pattern, query):
                return True

        return False

    def _check_conditional(self, query: str) -> bool:
        """Check if query contains conditional logic"""
        return any(keyword in query for keyword in self.CONDITIONAL_KEYWORDS)

    def _check_sequential(self, query: str) -> bool:
        """Check if query requires sequential operations"""
        return any(keyword in query for keyword in self.SEQUENTIAL_KEYWORDS)

    def _check_reasoning(self, query: str) -> bool:
        """Check if query requires reasoning"""
        return any(keyword in query for keyword in self.REASONING_KEYWORDS)

    def get_routing_recommendation(self, query: str) -> Dict[str, Any]:
        """
        Get routing recommendation for a query.

        Args:
            query: User query string

        Returns:
            dict: Routing recommendation with strategy and rationale
        """
        result = self.analyze(query)

        if result.is_complex:
            strategy = "phi2_reasoning"
            rationale = f"Complex query (score={result.complexity_score:.2f}): {', '.join(result.indicators)}"
        else:
            strategy = "tinybert_routing"
            rationale = f"Simple query (score={result.complexity_score:.2f}): Fast domain routing sufficient"

        return {
            'strategy': strategy,
            'rationale': rationale,
            'complexity_score': result.complexity_score,
            'indicators': result.indicators,
            'estimated_latency_ms': 2000 if result.is_complex else 50
        }


# Convenience function
def analyze_query_complexity(query: str, threshold: float = 0.3) -> ComplexityResult:
    """
    Convenience function to analyze query complexity.

    Args:
        query: User query
        threshold: Complexity threshold (default 0.3)

    Returns:
        ComplexityResult
    """
    analyzer = ComplexityAnalyzer(threshold)
    return analyzer.analyze(query)


if __name__ == "__main__":
    # Demo usage
    analyzer = ComplexityAnalyzer()

    test_queries = [
        "Transfer $100",  # Simple
        "Code this diagnosis and then calculate the billing",  # Complex
        "If denied, escalate to QC",  # Complex
        "What is the weather today?",  # Simple
        "First verify eligibility, then submit the claim, and if denied, analyze the reason",  # Very complex
    ]

    print("=== Complexity Analysis Demo ===\n")
    for query in test_queries:
        result = analyzer.analyze(query)
        recommendation = analyzer.get_routing_recommendation(query)

        print(f"Query: {query}")
        print(f"  Result: {result}")
        print(f"  Strategy: {recommendation['strategy']}")
        print(f"  Rationale: {recommendation['rationale']}")
        print()
