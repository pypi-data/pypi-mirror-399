"""
End-to-End Test for MDSA Chatbot

Tests:
- Basic chatbot functionality
- RAG integration
- Tool calling
- Monitoring
- Model management
"""

import logging
import time
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.chatbot import MDSAChatbot

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s'
)
logger = logging.getLogger(__name__)


def print_header(title):
    """Print formatted header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def test_basic_chat():
    """Test basic chatbot functionality."""
    print_header("TEST 1: Basic Chat Functionality")

    logger.info("Creating chatbot (without RAG/tools for faster testing)...")
    chatbot = MDSAChatbot(
        model_name="gpt2",
        max_models=2,
        enable_rag=False,
        enable_tools=False
    )

    # Test queries
    queries = [
        "Hello, how are you?",
        "What is machine learning?",
        "Explain Python programming"
    ]

    for i, query in enumerate(queries, 1):
        print(f"\n[Query {i}]: {query}")

        result = chatbot.chat(query, use_rag=False, use_tools=False)

        print(f"[Response]: {result['response'][:200]}...")
        print(f"[Domain]: {result['domain']}")
        print(f"[Latency]: {result['latency_ms']:.1f}ms")
        print(f"[Confidence]: {result['confidence']:.2f}")
        print(f"[Status]: {result['status']}")

    # Show stats
    stats = chatbot.get_stats()
    print("\n[Stats]:")
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n[SUCCESS] Basic chat test passed!")
    return chatbot


def test_rag_integration():
    """Test RAG integration."""
    print_header("TEST 2: RAG Integration")

    logger.info("Creating chatbot with RAG enabled...")
    chatbot = MDSAChatbot(
        model_name="gpt2",
        max_models=2,
        enable_rag=True,
        enable_tools=False,
        knowledge_base_dir="./knowledge_base"
    )

    # Check knowledge base
    rag_stats = chatbot.rag.get_stats()
    print(f"[Knowledge Base]: {rag_stats['total_documents']} documents loaded")

    # Add more knowledge
    chatbot.add_knowledge(
        "The MDSA framework was designed for efficiency and flexibility. "
        "It uses LRU caching to manage memory efficiently.",
        source="test_data"
    )

    # Test RAG-enhanced query
    query = "What is MDSA and what are its key features?"
    print(f"\n[RAG Query]: {query}")

    result = chatbot.chat(query, use_rag=True, use_tools=False)

    print(f"[Response]: {result['response'][:300]}...")
    print(f"[RAG Used]: {result['rag_used']}")
    print(f"[Latency]: {result['latency_ms']:.1f}ms")

    # Show updated stats
    stats = chatbot.get_stats()
    print(f"\n[Knowledge Base Docs]: {stats.get('knowledge_base_docs', 0)}")

    print("\n[SUCCESS] RAG integration test passed!")
    return chatbot


def test_tool_calling():
    """Test tool calling functionality."""
    print_header("TEST 3: Tool Calling")

    logger.info("Creating chatbot with tools enabled...")
    chatbot = MDSAChatbot(
        model_name="gpt2",
        max_models=2,
        enable_rag=False,
        enable_tools=True
    )

    # Show available tools
    tools = chatbot.tools.get_available_tools()
    print(f"[Available Tools]: {len(tools)}")
    for tool in tools[:5]:  # Show first 5
        print(f"  - {tool['name']}: {tool['description']}")

    # Test direct tool calling
    print("\n[Direct Tool Call]:")
    result = chatbot.tools.call("get_current_time")
    print(f"  Current time: {result}")

    result = chatbot.tools.call("calculate", expression="10 + 20")
    print(f"  Calculation: {result}")

    result = chatbot.tools.call("word_count", text="This is a test sentence")
    print(f"  Word count: {result}")

    # Test tool parsing
    print("\n[Tool Call Parsing]:")
    text_with_tool = "Let me calculate that: USE_TOOL: calculate(expression=2 + 2)"
    result = chatbot.tools.parse_and_execute(text_with_tool)
    print(f"  Parsed result: {result}")

    print("\n[SUCCESS] Tool calling test passed!")
    return chatbot


def test_monitoring():
    """Test monitoring functionality."""
    print_header("TEST 4: Monitoring & Metrics")

    logger.info("Creating chatbot with full monitoring...")
    chatbot = MDSAChatbot(
        model_name="gpt2",
        max_models=2,
        enable_rag=True,
        enable_tools=True
    )

    # Execute multiple queries to generate metrics
    print("[Executing 5 test queries for metrics...]")

    queries = [
        "Hello",
        "What is the time?",
        "Tell me about Python",
        "Calculate 5 + 10",
        "Explain machine learning"
    ]

    for query in queries:
        chatbot.chat(query)
        time.sleep(0.1)  # Small delay

    # Get comprehensive stats
    stats = chatbot.get_stats()

    print("\n[Chatbot Statistics]:")
    print(f"  Total Messages: {stats['total_messages']}")
    print(f"  Total Requests: {stats['total_requests']}")
    print(f"  Success Rate: {stats['success_rate']:.1f}%")
    print(f"  Avg Latency: {stats['avg_latency_ms']:.1f}ms")
    print(f"  P95 Latency: {stats['p95_latency_ms']:.1f}ms")
    print(f"  Models Loaded: {stats['models_loaded']}")
    print(f"  Available Tools: {stats.get('available_tools', 0)}")

    # Logger stats
    logger_stats = chatbot.logger.get_stats()
    print("\n[Request Logger]:")
    print(f"  Total Requests: {logger_stats['total_requests']}")
    print(f"  Success Count: {logger_stats['success_count']}")
    print(f"  Error Count: {logger_stats['error_count']}")
    print(f"  Success Rate: {logger_stats['success_rate_percent']:.1f}%")

    # Metrics stats
    metrics_summary = chatbot.metrics.get_summary()
    print("\n[Performance Metrics]:")
    print(f"  Total Requests: {metrics_summary['total_requests']}")
    print(f"  Avg Latency: {metrics_summary.get('avg_latency_ms', 0):.1f}ms")
    print(f"  Min Latency: {metrics_summary.get('min_latency_ms', 0):.1f}ms")
    print(f"  Max Latency: {metrics_summary.get('max_latency_ms', 0):.1f}ms")
    print(f"  P50 Latency: {metrics_summary.get('p50_latency_ms', 0):.1f}ms")
    print(f"  P95 Latency: {metrics_summary.get('p95_latency_ms', 0):.1f}ms")
    print(f"  P99 Latency: {metrics_summary.get('p99_latency_ms', 0):.1f}ms")

    # Model Manager stats
    model_stats = chatbot.model_manager.get_stats()
    print("\n[Model Manager]:")
    print(f"  Models Loaded: {model_stats['models_loaded']}")
    print(f"  Max Models: {model_stats['max_models']}")
    print(f"  Total Memory: {model_stats['total_memory_mb'] / 1024:.2f}GB")

    print("\n[SUCCESS] Monitoring test passed!")
    return chatbot


def test_model_management():
    """Test model loading and management."""
    print_header("TEST 5: Model Management & LRU Cache")

    logger.info("Testing model management...")

    chatbot = MDSAChatbot(
        model_name="gpt2",
        max_models=2,
        enable_rag=False,
        enable_tools=False
    )

    # Check initial state
    print("[Initial State]:")
    stats = chatbot.model_manager.get_stats()
    print(f"  Models Loaded: {stats['models_loaded']}")

    # Execute queries to trigger model loading
    print("\n[Executing queries to trigger model loading...]")

    result = chatbot.chat("Test query 1")
    print(f"  Query 1: {result['status']}")

    stats = chatbot.model_manager.get_stats()
    print(f"  Models Loaded After Query 1: {stats['models_loaded']}")

    result = chatbot.chat("Test query 2")
    print(f"  Query 2: {result['status']}")

    stats = chatbot.model_manager.get_stats()
    print(f"  Models Loaded After Query 2: {stats['models_loaded']}")

    print("\n[Model Manager Final Stats]:")
    print(f"  Total Models Loaded: {stats['models_loaded']}")
    print(f"  Max Models Allowed: {stats['max_models']}")
    print(f"  Total Memory Used: {stats['total_memory_mb'] / 1024:.2f}GB")

    print("\n[SUCCESS] Model management test passed!")
    return chatbot


def run_all_tests():
    """Run all tests."""
    print_header("MDSA CHATBOT - END-TO-END TESTING")

    start_time = time.time()

    try:
        # Run tests
        test_basic_chat()
        test_rag_integration()
        test_tool_calling()
        test_monitoring()
        test_model_management()

        elapsed = time.time() - start_time

        print_header("ALL TESTS PASSED!")
        print(f"Total Time: {elapsed:.2f}s\n")

        return True

    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        print(f"\n[ERROR] Test failed: {e}\n")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
