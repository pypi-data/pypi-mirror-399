"""
MDSA Chatbot with Built-in Dashboard

This script runs the MDSA chatbot in the background and starts the
built-in HTML/CSS/JS dashboard for monitoring.

Usage:
    python run_with_dashboard.py

Then open your browser to: http://127.0.0.1:5000
"""

import logging
import threading
import time
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mdsa import ModelManager, DomainExecutor, DomainConfig
from mdsa.monitoring import RequestLogger, MetricsCollector
from mdsa.ui import DashboardServer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'
)
logger = logging.getLogger(__name__)


class MDSAChatbotWithDashboard:
    """
    MDSA Chatbot with integrated monitoring dashboard.
    """

    def __init__(self):
        logger.info("Initializing MDSA Chatbot with Dashboard...")

        # MDSA Components
        self.model_manager = ModelManager(max_models=2)
        self.request_logger = RequestLogger(max_logs=10000)
        self.metrics_collector = MetricsCollector(window_size=1000)
        self.executor = DomainExecutor(self.model_manager)

        # Create test domain
        self.domain = DomainConfig(
            domain_id="general",
            name="General Assistant",
            description="General purpose assistant",
            keywords=["help", "question", "tell", "what", "how"],
            model_name="gpt2",
            system_prompt="You are a helpful AI assistant.",
            max_tokens=150,
            temperature=0.7
        )

        # Create dashboard server
        self.dashboard = DashboardServer(
            model_manager=self.model_manager,
            request_logger=self.request_logger,
            metrics_collector=self.metrics_collector,
            host="127.0.0.1",
            port=5000
        )

        logger.info("Initialization complete!")

    def process_query(self, query: str):
        """Process a query and log metrics."""
        import uuid

        request_id = str(uuid.uuid4())[:8]

        # Execute query
        result = self.executor.execute(query, self.domain)

        # Log request
        self.request_logger.log_request(
            request_id=request_id,
            query=query,
            domain=result['domain'],
            model=result['model'],
            response=result['response'],
            status=result['status'],
            error=result['error'],
            latency_ms=result['latency_ms'],
            tokens_generated=result['tokens_generated'],
            confidence=result['confidence']
        )

        # Record metrics
        self.metrics_collector.record_request(
            latency_ms=result['latency_ms'],
            tokens_generated=result['tokens_generated'],
            confidence=result['confidence'],
            domain=result['domain'],
            model=result['model'],
            status=result['status']
        )

        return result

    def run_background_processing(self):
        """
        Simulate background query processing to generate metrics.
        This keeps the dashboard interesting with live data.
        """
        test_queries = [
            "What is machine learning?",
            "Explain artificial intelligence",
            "What is deep learning?",
            "How does neural network work?",
            "What is natural language processing?"
        ]

        index = 0
        while True:
            try:
                time.sleep(30)  # Process query every 30 seconds

                query = test_queries[index % len(test_queries)]
                logger.info(f"Background processing: {query}")

                result = self.process_query(query)
                logger.info(f"Processed successfully: {result['response'][:50]}...")

                index += 1

            except Exception as e:
                logger.error(f"Background processing error: {e}")

    def run(self):
        """Run chatbot with dashboard."""
        print("=" * 70)
        print("MDSA CHATBOT WITH BUILT-IN DASHBOARD")
        print("=" * 70)
        print()
        print("The chatbot is running with the MDSA built-in dashboard.")
        print()
        print("Dashboard URL: http://127.0.0.1:5000")
        print()
        print("Pages available:")
        print("  • Welcome: http://127.0.0.1:5000/welcome")
        print("  • Monitor: http://127.0.0.1:5000/monitor")
        print("  • API:     http://127.0.0.1:5000/api/metrics")
        print()
        print("The dashboard will show real-time metrics as queries are processed.")
        print()
        print("To test the chatbot:")
        print("  1. Open the Monitor page in your browser")
        print("  2. Run test queries using the /test command below")
        print("  3. Watch metrics update in real-time")
        print()
        print("Commands:")
        print("  /test <query>  - Process a test query")
        print("  /stats         - Show statistics")
        print("  /quit          - Exit")
        print()
        print("=" * 70)
        print()

        # Start background processing in a thread
        bg_thread = threading.Thread(target=self.run_background_processing, daemon=True)
        bg_thread.start()
        logger.info("Background processing thread started")

        # Start dashboard in a thread
        dashboard_thread = threading.Thread(target=self.dashboard.run, daemon=True)
        dashboard_thread.start()
        logger.info("Dashboard server thread started")

        # Give dashboard time to start
        time.sleep(2)

        # Interactive mode
        while True:
            try:
                user_input = input("Command: ").strip()

                if not user_input:
                    continue

                if user_input == '/quit':
                    print("\nShutting down...")
                    break

                elif user_input == '/stats':
                    stats = self.request_logger.get_stats()
                    metrics_summary = self.metrics_collector.get_summary()

                    print("\n" + "=" * 70)
                    print("STATISTICS")
                    print("=" * 70)
                    print(f"Total Requests: {stats['total_requests']}")
                    print(f"Success Rate:   {stats['success_rate_percent']:.1f}%")
                    print(f"Avg Latency:    {metrics_summary.get('avg_latency_ms', 0):.1f}ms")
                    print(f"P95 Latency:    {metrics_summary.get('p95_latency_ms', 0):.1f}ms")
                    print("=" * 70)
                    print()

                elif user_input.startswith('/test '):
                    query = user_input[6:].strip()
                    if not query:
                        print("Error: Please provide a query after /test")
                        continue

                    print(f"\nProcessing: {query}")
                    result = self.process_query(query)

                    print(f"\nResponse: {result['response']}")
                    print(f"Latency: {result['latency_ms']:.1f}ms | Confidence: {result['confidence']:.2f}")
                    print()

                else:
                    print("Unknown command. Use /test, /stats, or /quit")

            except KeyboardInterrupt:
                print("\n\nShutting down...")
                break
            except Exception as e:
                print(f"\nError: {e}")
                logger.error(f"Error: {e}", exc_info=True)

        print("Goodbye!")


def main():
    chatbot = MDSAChatbotWithDashboard()
    chatbot.run()


if __name__ == "__main__":
    main()
