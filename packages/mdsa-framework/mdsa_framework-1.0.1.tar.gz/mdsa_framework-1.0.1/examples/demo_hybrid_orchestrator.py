"""
Demo: Hybrid Orchestrator with TinyBERT + Phi-2 Reasoning

This demo shows:
1. Simple queries using fast TinyBERT routing (<50ms)
2. Complex queries using Phi-2 reasoning (<2s)
3. Multi-task decomposition and execution
4. Statistics tracking

Author: MDSA Framework Team
Date: 2025-12-05
"""

from mdsa.core.orchestrator import TinyBERTOrchestrator
import json


def print_separator(title=""):
    """Print a section separator"""
    print("\n" + "=" * 80)
    if title:
        print(f"  {title}")
        print("=" * 80)


def print_result(result):
    """Pretty print result"""
    print(f"\nStatus: {result['status']}")
    print(f"Message: {result['message']}")
    print("\nMetadata:")
    metadata = result['metadata']

    # Basic info
    print(f"  Correlation ID: {metadata['correlation_id']}")
    print(f"  Latency: {metadata.get('total_latency_ms', metadata.get('latency_ms', 0)):.2f}ms")

    # Reasoning info (if used)
    if metadata.get('reasoning_used'):
        print(f"  [*] Reasoning Used: Yes")
        print(f"  Number of Tasks: {metadata.get('num_tasks', 0)}")
        print(f"  Reasoning Analysis: {metadata.get('reasoning_analysis', 'N/A')}")
        print(f"  Reasoning Time: {metadata.get('reasoning_time_ms', 0):.2f}ms")
        print(f"  Execution Time: {metadata.get('execution_time_ms', 0):.2f}ms")

        if 'task_results' in metadata:
            print("\n  Task Execution Plan:")
            for task_result in metadata['task_results']:
                print(f"    Task {task_result['task_id']}: {task_result['description']}")
                print(f"      Domain: {task_result['domain']}")
                print(f"      Confidence: {task_result['confidence']:.3f}")
                print(f"      Status: {task_result['status']}")
                if task_result.get('tools_used'):
                    print(f"      Tools: {', '.join(task_result['tools_used'])}")
    else:
        print(f"  [*] Reasoning Used: No (Fast TinyBERT routing)")
        if 'domain' in metadata:
            print(f"  Domain: {metadata['domain']}")
            print(f"  Confidence: {metadata.get('confidence', 0):.3f}")

    # State history
    if 'state_history' in metadata:
        print(f"  State History: {' -> '.join(metadata['state_history'])}")


def main():
    print_separator("MDSA Hybrid Orchestrator Demo")
    print("\nInitializing hybrid orchestrator...")
    print("  - TinyBERT for fast routing (<50ms)")
    print("  - Phi-2 for complex reasoning (<2s)")

    # Initialize orchestrator with reasoning enabled
    orchestrator = TinyBERTOrchestrator(
        log_level="WARNING",  # Reduce noise
        enable_reasoning=True,
        complexity_threshold=0.3
    )

    # Register medical domains
    print("\nRegistering medical domains...")
    orchestrator.register_domain(
        "medical_coding",
        "Medical coding for ICD-10, CPT, and HCPCS codes",
        ["code", "coding", "diagnosis", "icd", "cpt", "hcpcs"]
    )
    orchestrator.register_domain(
        "medical_billing",
        "Medical billing and charge calculation",
        ["billing", "charge", "cost", "payment", "reimbursement"]
    )
    orchestrator.register_domain(
        "claims_processing",
        "Claims processing and denial management",
        ["claim", "claims", "denial", "qc", "submit", "reject"]
    )

    print("  [+] medical_coding")
    print("  [+] medical_billing")
    print("  [+] claims_processing")

    # Test queries
    test_cases = [
        {
            "category": "SIMPLE QUERY (TinyBERT Routing)",
            "query": "Extract ICD-10 codes from this patient record",
            "expected": "Fast routing to medical_coding domain"
        },
        {
            "category": "SIMPLE QUERY (TinyBERT Routing)",
            "query": "Calculate billing charges",
            "expected": "Fast routing to medical_billing domain"
        },
        {
            "category": "COMPLEX QUERY (Phi-2 Reasoning)",
            "query": "Code this diagnosis and then calculate the billing",
            "expected": "Multi-task: coding -> billing"
        },
        {
            "category": "COMPLEX QUERY (Phi-2 Reasoning)",
            "query": "If the claim is denied, analyze the reason and recommend corrections",
            "expected": "Conditional logic requiring reasoning"
        },
        {
            "category": "COMPLEX QUERY (Phi-2 Reasoning)",
            "query": "First verify eligibility, then submit the claim",
            "expected": "Sequential operations"
        }
    ]

    # Process queries
    for i, test_case in enumerate(test_cases, 1):
        print_separator(f"Test Case {i}: {test_case['category']}")
        print(f"\nQuery: \"{test_case['query']}\"")
        print(f"Expected: {test_case['expected']}")

        result = orchestrator.process_request(test_case['query'])
        print_result(result)

    # Show statistics
    print_separator("FINAL STATISTICS")
    stats = orchestrator.get_stats()

    print(f"\nRequest Summary:")
    print(f"  Total Requests: {stats['requests_total']}")
    print(f"  Successful: {stats['requests_success']}")
    print(f"  Failed: {stats['requests_failed']}")
    print(f"  Reasoning-based: {stats['requests_reasoning']}")
    print(f"  Success Rate: {stats['success_rate']:.1%}")
    print(f"  Reasoning Usage: {stats['reasoning_rate']:.1%}")
    print(f"  Average Latency: {stats['average_latency_ms']:.2f}ms")

    print(f"\nDomain Distribution:")
    for domain, count in stats['domain_stats'].items():
        print(f"  {domain}: {count} requests")

    print_separator("DEMO COMPLETE")
    print("\n[SUCCESS] Hybrid orchestration demonstrated successfully!")
    print("\nKey Takeaways:")
    print("  - Simple queries use TinyBERT for fast routing")
    print("  - Complex queries use Phi-2 for intelligent task decomposition")
    print("  - Multi-task execution handles dependencies automatically")
    print("  - All statistics tracked for monitoring and optimization")


if __name__ == "__main__":
    main()
