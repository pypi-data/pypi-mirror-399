"""
Phi-2 Reasoner for MDSA Framework

Uses Phi-2 model to provide reasoning-based orchestration:
- Analyze user intent with understanding
- Decompose complex queries into sub-tasks
- Determine domain sequence for multi-domain tasks
- Identify tool requirements
- Generate execution plans

Author: MDSA Framework Team
Date: 2025-12-05
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import logging
import time
import re
import json

logger = logging.getLogger(__name__)


@dataclass
class Task:
    """Represents a single task in an execution plan"""
    task_id: int
    description: str
    domain: str
    query: str
    dependencies: List[int] = field(default_factory=list)  # Task IDs this depends on
    tools_needed: List[str] = field(default_factory=list)
    estimated_time_ms: float = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReasoningResult:
    """Result of Phi-2 reasoning analysis"""
    success: bool
    analysis: str  # Phi-2's understanding of the query
    execution_plan: List[Task]  # Ordered list of tasks
    total_estimated_time_ms: float
    reasoning_time_ms: float
    error: Optional[str] = None

    def __repr__(self) -> str:
        return (f"<ReasoningResult success={self.success} "
                f"tasks={len(self.execution_plan)} "
                f"time={self.reasoning_time_ms:.0f}ms>")


class Phi2Reasoner:
    """
    Uses Phi-2 model for intelligent query analysis and task decomposition.

    Capabilities:
    1. Understand user intent through reasoning
    2. Decompose complex queries into sequential/parallel tasks
    3. Identify domain requirements for each task
    4. Determine tool needs
    5. Handle conditional logic
    """

    REASONING_PROMPT_TEMPLATE = """You are an intelligent task planner for a medical AI system with multiple specialized domains.

AVAILABLE DOMAINS:
- medical_coding: Extract ICD-10, CPT, HCPCS codes from clinical documentation
- medical_billing: Calculate charges, apply modifiers, determine reimbursement
- claims_processing: Validate claims, handle denials, QC analysis

USER QUERY: {query}

YOUR TASK:
Analyze this query and create an execution plan with step-by-step tasks.

For each task, specify:
1. Task description
2. Which domain to use
3. Specific query for that domain
4. Any dependencies (which tasks must complete first)
5. Required tools (if any)

OUTPUT FORMAT (JSON):
{{
    "analysis": "Your understanding of what the user wants",
    "tasks": [
        {{
            "task_id": 1,
            "description": "Brief task description",
            "domain": "domain_name",
            "query": "Specific query for this domain",
            "dependencies": [],
            "tools_needed": ["tool1", "tool2"]
        }}
    ]
}}

Provide ONLY the JSON output, nothing else.
"""

    def __init__(self, model_manager=None, enable_caching: bool = True):
        """
        Initialize Phi-2 Reasoner.

        Args:
            model_manager: ModelManager instance (optional, will create if None)
            enable_caching: Enable result caching for identical queries
        """
        self.model_manager = model_manager
        self.enable_caching = enable_caching
        self._cache: Dict[str, ReasoningResult] = {}

        # Model config for Phi-2
        self.model_config = {
            'model_name': 'microsoft/phi-2',
            'max_length': 1024,
            'temperature': 0.3,  # Low temperature for consistent reasoning
            'top_p': 0.9,
            'max_new_tokens': 512
        }

        logger.info("Phi2Reasoner initialized (reasoning-based orchestration)")

    def analyze_and_plan(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ReasoningResult:
        """
        Analyze query and generate execution plan using Phi-2.

        Args:
            query: User query
            context: Optional context (user preferences, session data, etc.)

        Returns:
            ReasoningResult with execution plan
        """
        start_time = time.time()

        # Check cache
        if self.enable_caching and query in self._cache:
            cached_result = self._cache[query]
            logger.info(f"Returning cached reasoning result for query: {query[:50]}...")
            return cached_result

        try:
            # Build reasoning prompt
            prompt = self.REASONING_PROMPT_TEMPLATE.format(query=query)

            # Use Phi-2 for reasoning
            # Note: In production, this would call the actual model
            # For now, using a simplified heuristic-based approach
            execution_plan = self._generate_plan_heuristic(query)

            reasoning_time_ms = (time.time() - start_time) * 1000

            result = ReasoningResult(
                success=True,
                analysis=f"Query requires {len(execution_plan)} step(s)",
                execution_plan=execution_plan,
                total_estimated_time_ms=sum(task.estimated_time_ms for task in execution_plan),
                reasoning_time_ms=reasoning_time_ms,
                error=None
            )

            # Cache result
            if self.enable_caching:
                self._cache[query] = result

            logger.info(f"Reasoning completed: {len(execution_plan)} tasks, {reasoning_time_ms:.0f}ms")
            return result

        except Exception as e:
            reasoning_time_ms = (time.time() - start_time) * 1000
            logger.error(f"Reasoning failed: {e}")

            return ReasoningResult(
                success=False,
                analysis="",
                execution_plan=[],
                total_estimated_time_ms=0,
                reasoning_time_ms=reasoning_time_ms,
                error=str(e)
            )

    def _generate_plan_heuristic(self, query: str) -> List[Task]:
        """
        Generate execution plan using heuristics.

        This is a simplified version. In production, this would:
        1. Load Phi-2 model
        2. Generate reasoning with the prompt
        3. Parse JSON response
        4. Validate and return tasks

        For now, uses pattern matching to create reasonable plans.
        """
        query_lower = query.lower()
        tasks = []
        task_id = 1

        # Pattern 1: "Code AND bill" or "Code then bill"
        if re.search(r'code.*(?:and|then).*bill', query_lower):
            # Task 1: Medical Coding
            tasks.append(Task(
                task_id=task_id,
                description="Extract medical codes from clinical documentation",
                domain="medical_coding",
                query="Extract ICD-10 and CPT codes",
                dependencies=[],
                tools_needed=["lookup_icd10", "lookup_cpt"],
                estimated_time_ms=2000
            ))
            task_id += 1

            # Task 2: Medical Billing (depends on coding)
            tasks.append(Task(
                task_id=task_id,
                description="Calculate billing amounts",
                domain="medical_billing",
                query="Calculate claim total based on extracted codes",
                dependencies=[1],  # Depends on coding task
                tools_needed=["calculate_claim_cost"],
                estimated_time_ms=1500
            ))
            task_id += 1

        # Pattern 2: "Submit claim" or "Process claim"
        elif re.search(r'(submit|process).*claim', query_lower):
            # Task 1: Claims Processing
            tasks.append(Task(
                task_id=task_id,
                description="Validate and submit claim",
                domain="claims_processing",
                query="Validate claim for submission",
                dependencies=[],
                tools_needed=["validate_claim"],
                estimated_time_ms=1000
            ))
            task_id += 1

        # Pattern 3: "If denied" or denial-related
        elif re.search(r'(?:if|when).*deni(?:ed|al)', query_lower):
            # Task 1: Denial Analysis
            tasks.append(Task(
                task_id=task_id,
                description="Analyze denial and recommend corrections",
                domain="claims_processing",
                query="Analyze denial reason and recommend corrective action",
                dependencies=[],
                tools_needed=[],
                estimated_time_ms=2000
            ))
            task_id += 1

        # Pattern 4: Sequential with "first", "then", "finally"
        elif re.search(r'first.*then|step\s*1.*step\s*2', query_lower):
            # Extract steps using patterns
            steps = re.split(r'(?:then|and then|after that|next|finally)', query_lower)

            for idx, step in enumerate(steps, 1):
                step = step.strip()
                if not step:
                    continue

                # Determine domain based on keywords
                if any(kw in step for kw in ['code', 'diagnos', 'icd', 'cpt']):
                    domain = "medical_coding"
                    tools = ["lookup_icd10", "lookup_cpt"]
                elif any(kw in step for kw in ['bill', 'charge', 'cost', 'payment']):
                    domain = "medical_billing"
                    tools = ["calculate_claim_cost"]
                elif any(kw in step for kw in ['claim', 'submit', 'denial', 'qc']):
                    domain = "claims_processing"
                    tools = ["validate_claim"]
                else:
                    domain = "medical_coding"  # Default
                    tools = []

                tasks.append(Task(
                    task_id=task_id,
                    description=f"Step {idx}: {step[:50]}",
                    domain=domain,
                    query=step,
                    dependencies=[task_id - 1] if idx > 1 else [],
                    tools_needed=tools,
                    estimated_time_ms=1500
                ))
                task_id += 1

        # Default: Single task with domain detection
        else:
            if any(kw in query_lower for kw in ['code', 'diagnos', 'icd', 'cpt']):
                domain = "medical_coding"
                description = "Extract medical codes"
                tools = ["lookup_icd10", "lookup_cpt"]
            elif any(kw in query_lower for kw in ['bill', 'charge', 'cost']):
                domain = "medical_billing"
                description = "Calculate billing"
                tools = ["calculate_claim_cost"]
            elif any(kw in query_lower for kw in ['claim', 'denial', 'qc']):
                domain = "claims_processing"
                description = "Process claim"
                tools = ["validate_claim"]
            else:
                domain = "medical_coding"  # Default fallback
                description = "Process medical query"
                tools = []

            tasks.append(Task(
                task_id=1,
                description=description,
                domain=domain,
                query=query,
                dependencies=[],
                tools_needed=tools,
                estimated_time_ms=1500
            ))

        return tasks

    def clear_cache(self):
        """Clear the reasoning cache"""
        self._cache.clear()
        logger.info("Reasoning cache cleared")

    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        return {
            'cache_size': len(self._cache),
            'cache_enabled': self.enable_caching
        }


# Convenience function
def reason_about_query(query: str, model_manager=None) -> ReasoningResult:
    """
    Convenience function to reason about a query.

    Args:
        query: User query
        model_manager: Optional ModelManager

    Returns:
        ReasoningResult
    """
    reasoner = Phi2Reasoner(model_manager)
    return reasoner.analyze_and_plan(query)


if __name__ == "__main__":
    # Demo usage
    reasoner = Phi2Reasoner()

    test_queries = [
        "Code this diagnosis and then calculate the billing",
        "If the claim is denied, analyze the reason and recommend corrections",
        "First verify eligibility, then submit the claim",
        "Extract ICD-10 codes",
    ]

    print("=== Phi-2 Reasoner Demo ===\n")
    for query in test_queries:
        print(f"Query: {query}")
        result = reasoner.analyze_and_plan(query)
        print(f"Result: {result}")
        print(f"Analysis: {result.analysis}")
        print(f"Tasks ({len(result.execution_plan)}):")
        for task in result.execution_plan:
            deps = f" (depends on {task.dependencies})" if task.dependencies else ""
            print(f"  {task.task_id}. {task.description} → {task.domain}{deps}")
        print()
