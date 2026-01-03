"""
Run All MDSA Performance Benchmarks

Executes all available benchmarks in sequence and generates a summary report.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Import benchmark modules
try:
    from benchmark_latency import benchmark_latency
    from benchmark_accuracy import benchmark_accuracy
except ImportError:
    print("ERROR: Unable to import benchmark modules.")
    print("Make sure you're running from the tests/performance/ directory.")
    sys.exit(1)


def run_all_benchmarks(num_queries_latency: int = 1000,
                       num_queries_accuracy: int = 10000,
                       config_path: str = None):
    """
    Run all implemented benchmarks.

    Args:
        num_queries_latency: Number of queries for latency benchmark
        num_queries_accuracy: Number of queries for accuracy benchmark
        config_path: Path to MDSA config file
    """
    print("=" * 70)
    print(" MDSA FRAMEWORK - PERFORMANCE BENCHMARK SUITE")
    print("=" * 70)
    print(f"\nStarted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    results_summary = {
        "timestamp": datetime.now().isoformat(),
        "benchmarks": {}
    }

    # Benchmark 1: Latency
    print("\n" + "=" * 70)
    print(" BENCHMARK 1: END-TO-END LATENCY")
    print("=" * 70)
    try:
        latency_results = benchmark_latency(
            num_queries=num_queries_latency,
            config_path=config_path
        )
        results_summary["benchmarks"]["latency"] = {
            "status": "completed",
            "median_ms": latency_results.get("median_ms", 0),
            "p95_ms": latency_results.get("p95_ms", 0),
            "passed": 10 <= latency_results.get("median_ms", 0) <= 100 if latency_results else False
        }
    except Exception as e:
        print(f"ERROR in latency benchmark: {e}")
        results_summary["benchmarks"]["latency"] = {
            "status": "failed",
            "error": str(e)
        }

    # Benchmark 2: Accuracy
    print("\n" + "=" * 70)
    print(" BENCHMARK 2: ROUTING ACCURACY")
    print("=" * 70)
    try:
        accuracy_results = benchmark_accuracy(
            num_queries=num_queries_accuracy,
            config_path=config_path
        )
        results_summary["benchmarks"]["accuracy"] = {
            "status": "completed",
            "accuracy_pct": accuracy_results.get("accuracy", 0),
            "passed": 55.0 <= accuracy_results.get("accuracy", 0) <= 85.0 if accuracy_results else False
        }
    except Exception as e:
        print(f"ERROR in accuracy benchmark: {e}")
        results_summary["benchmarks"]["accuracy"] = {
            "status": "failed",
            "error": str(e)
        }

    # Future benchmarks (not yet implemented)
    results_summary["benchmarks"]["rag_precision"] = {
        "status": "not_implemented",
        "note": "See README.md for implementation details"
    }
    results_summary["benchmarks"]["memory_profiling"] = {
        "status": "not_implemented",
        "note": "See README.md for implementation details"
    }

    # Print summary
    print("\n" + "=" * 70)
    print(" BENCHMARK SUMMARY")
    print("=" * 70)

    for benchmark_name, benchmark_data in results_summary["benchmarks"].items():
        status = benchmark_data.get("status", "unknown")
        passed = benchmark_data.get("passed", False)

        print(f"\n{benchmark_name.upper().replace('_', ' ')}:")
        print(f"  Status: {status}")

        if status == "completed":
            if benchmark_name == "latency":
                print(f"  Median Latency: {benchmark_data['median_ms']:.2f} ms")
                print(f"  P95 Latency: {benchmark_data['p95_ms']:.2f} ms")
                print(f"  Validation: {'[PASS]' if passed else '[FAIL]'}")
            elif benchmark_name == "accuracy":
                print(f"  Accuracy: {benchmark_data['accuracy_pct']:.2f}%")
                print(f"  Validation: {'[PASS]' if passed else '[FAIL]'}")
        elif status == "failed":
            print(f"  Error: {benchmark_data.get('error', 'Unknown error')}")
        elif status == "not_implemented":
            print(f"  Note: {benchmark_data.get('note', 'Implementation pending')}")

    # Overall status
    completed_count = sum(1 for b in results_summary["benchmarks"].values()
                          if b.get("status") == "completed")
    passed_count = sum(1 for b in results_summary["benchmarks"].values()
                       if b.get("passed") == True)

    print("\n" + "=" * 70)
    print(f" OVERALL: {passed_count}/{completed_count} benchmarks passed")
    print("=" * 70)
    print(f"\nFinished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Save summary
    output_file = Path(__file__).parent / "results" / "benchmark_summary.json"
    with open(output_file, 'w') as f:
        json.dump(results_summary, f, indent=2)
    print(f"\nSummary saved to: {output_file}")

    return results_summary


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run All MDSA Benchmarks")
    parser.add_argument("--latency-queries", type=int, default=1000,
                        help="Number of queries for latency benchmark (default: 1000)")
    parser.add_argument("--accuracy-queries", type=int, default=10000,
                        help="Number of queries for accuracy benchmark (default: 10000)")
    parser.add_argument("-c", "--config", type=str, default=None,
                        help="Path to MDSA config file")

    args = parser.parse_args()

    results = run_all_benchmarks(
        num_queries_latency=args.latency_queries,
        num_queries_accuracy=args.accuracy_queries,
        config_path=args.config
    )

    # Exit with appropriate code
    completed = [b for b in results["benchmarks"].values()
                 if b.get("status") == "completed"]
    passed = [b for b in completed if b.get("passed") == True]

    if len(passed) == len(completed) and len(completed) > 0:
        sys.exit(0)  # All benchmarks passed
    else:
        sys.exit(1)  # Some benchmarks failed or none completed
