"""
MDSA-Powered Chatbot with RAG and Tool Calling

Integrates:
- MDSA Framework (multi-domain routing)
- RAG Engine (ChromaDB for knowledge retrieval)
- Tool Calling (various utilities)
- Monitoring (request logging and metrics)
"""

import logging
import uuid
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List

# Add parent directory to path to import mdsa
sys.path.insert(0, str(Path(__file__).parent.parent))

from mdsa import (
    ModelManager,
    DomainExecutor,
    DomainConfig,
    RequestLogger,
    MetricsCollector
)

from chatbot_app.rag_engine import RAGEngine
from chatbot_app.shared_metrics import SharedMetrics

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'
)
logger = logging.getLogger(__name__)


class MDSAChatbot:
    """
    Multi-Domain Chatbot with RAG and Tool Calling.

    Features:
    - Uses local models (no API keys needed)
    - Domain-specific routing
    - Knowledge retrieval (RAG)
    - Tool calling capabilities
    - Comprehensive monitoring
    """

    def __init__(
        self,
        model_name: str = "gpt2",
        max_models: int = 2,
        enable_rag: bool = True,
        enable_tools: bool = True,
        knowledge_base_dir: Optional[str] = None
    ):
        """
        Initialize chatbot.

        Args:
            model_name: Default model to use
            max_models: Maximum models to keep in memory
            enable_rag: Enable RAG functionality
            enable_tools: Enable tool calling
            knowledge_base_dir: Directory containing knowledge base documents
        """
        logger.info("Initializing MDSA Chatbot...")

        # MDSA Components
        self.model_manager = ModelManager(max_models=max_models)
        self.executor = DomainExecutor(self.model_manager)

        # Monitoring
        self.logger = RequestLogger(max_logs=10000)
        self.metrics = MetricsCollector(window_size=1000)

        # Create domains
        self.domains = self._create_domains(model_name)

        # RAG Engine
        self.enable_rag = enable_rag
        if enable_rag:
            logger.info("Initializing RAG engine...")
            self.rag = RAGEngine(
                collection_name="chatbot_kb",
                persist_directory="./chroma_db"
            )

            # Load knowledge base if directory provided
            if knowledge_base_dir and Path(knowledge_base_dir).exists():
                self.rag.add_directory(knowledge_base_dir)
                logger.info(f"Loaded knowledge base from {knowledge_base_dir}")
        else:
            self.rag = None

        # Smart Tools (now handled by framework executor)
        self.enable_tools = enable_tools
        if enable_tools:
            # Tools are already registered in the executor
            tool_count = len(self.executor.tool_registry)
            logger.info(f"Framework smart tools enabled ({tool_count} tools)")

        # Legacy tools property for backwards compatibility
        self.tools = self.executor.tool_registry if enable_tools else None

        # Conversation history
        self.history: List[Dict[str, str]] = []

        # Shared metrics for dashboard
        self.shared_metrics = SharedMetrics()

        # Initialize shared metrics
        self._update_shared_metrics()

        logger.info("Chatbot initialized successfully!")

    def _create_domains(self, model_name: str) -> Dict[str, DomainConfig]:
        """Create domain configurations."""
        domains = {}

        # General domain (default)
        domains['general'] = DomainConfig(
            domain_id="general",
            name="General Assistant",
            description="General purpose chatbot assistant",
            keywords=["help", "question", "tell", "explain", "what", "how"],
            model_name=model_name,
            system_prompt="You are a helpful AI assistant. Provide accurate and concise information.",
            max_tokens=150,
            temperature=0.7
        )

        # Technical domain
        domains['technical'] = DomainConfig(
            domain_id="technical",
            name="Technical Support",
            description="Technical support and programming assistance",
            keywords=["code", "programming", "error", "bug", "install", "debug"],
            model_name=model_name,
            system_prompt="You are a technical support assistant. Help with programming and technical issues.",
            max_tokens=200,
            temperature=0.1
        )

        # Information domain
        domains['information'] = DomainConfig(
            domain_id="information",
            name="Information Retrieval",
            description="Information lookup and research assistance",
            keywords=["search", "find", "lookup", "information", "data"],
            model_name=model_name,
            system_prompt="You are an information specialist. Provide factual and well-researched answers.",
            max_tokens=180,
            temperature=0.4
        )

        return domains

    def _detect_domain(self, query: str) -> DomainConfig:
        """Detect appropriate domain for query."""
        query_lower = query.lower()

        # Check each domain's keywords
        for domain_id, domain_config in self.domains.items():
            if any(keyword in query_lower for keyword in domain_config.keywords):
                return domain_config

        # Default to general
        return self.domains['general']

    def _enhance_prompt_with_rag(self, query: str) -> str:
        """Enhance query with RAG context."""
        if not self.rag:
            return query

        # Get relevant context
        context = self.rag.get_context(query, n_results=3, max_length=500)

        # Enhance prompt
        enhanced = f"""Context from knowledge base:
{context}

Question: {query}

Answer based on the context above if relevant, otherwise answer from your general knowledge:"""

        return enhanced

    def _enhance_prompt_with_tools(self, query: str) -> str:
        """Enhance prompt with available tools."""
        if not self.tools:
            return query

        tools_info = self.tools.format_tools_for_prompt()

        enhanced = f"""{tools_info}

User Query: {query}

Response (use tools if helpful):"""

        return enhanced

    def chat(
        self,
        query: str,
        domain: Optional[str] = None,
        use_rag: bool = True,
        use_tools: bool = True
    ) -> Dict[str, Any]:
        """
        Process a chat query.

        Args:
            query: User query
            domain: Specific domain to use (auto-detect if None)
            use_rag: Use RAG enhancement
            use_tools: Enable tool calling

        Returns:
            dict: Chat response with metadata
        """
        request_id = str(uuid.uuid4())[:8]

        # Detect domain
        if domain and domain in self.domains:
            domain_config = self.domains[domain]
        else:
            domain_config = self._detect_domain(query)

        logger.info(f"[{request_id}] Query: {query[:50]}... | Domain: {domain_config.domain_id}")

        # Enhance with RAG
        enhanced_query = query
        context = {}
        if use_rag and self.enable_rag:
            enhanced_query = self._enhance_prompt_with_rag(query)
            logger.info(f"[{request_id}] RAG enabled")

        # Execute query with smart tool detection
        # The framework executor will automatically detect and execute tools
        result = self.executor.execute(
            enhanced_query,
            domain_config,
            context=context,
            enable_tools=use_tools and self.enable_tools
        )

        # Format tool results for display
        if result.get('tool_results'):
            tool_summaries = []
            for tool_res in result['tool_results']:
                if tool_res['success']:
                    tool_summaries.append(f"{tool_res['tool_name']}: {tool_res['result']}")
                else:
                    tool_summaries.append(f"{tool_res['tool_name']}: FAILED")

            if tool_summaries:
                result['response'] += f"\n\n[Tools Used]: {', '.join(tool_summaries)}"
                logger.info(f"[{request_id}] Smart tools executed: {len(result['tool_results'])}")

        # Log request
        self.logger.log_request(
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
        self.metrics.record_request(
            latency_ms=result['latency_ms'],
            tokens_generated=result['tokens_generated'],
            confidence=result['confidence'],
            domain=result['domain'],
            model=result['model'],
            status=result['status']
        )

        # Add to history
        self.history.append({
            'query': query,
            'response': result['response'],
            'domain': result['domain'],
            'request_id': request_id
        })

        # Prepare response
        response_data = {
            'request_id': request_id,
            'query': query,
            'response': result['response'],
            'domain': result['domain'],
            'model': result['model'],
            'status': result['status'],
            'latency_ms': result['latency_ms'],
            'confidence': result['confidence'],
            'rag_used': use_rag and self.enable_rag,
            'tools_used': bool(result.get('tool_results'))
        }

        # Update shared metrics for dashboard
        from datetime import datetime
        self.shared_metrics.add_recent_request({
            'timestamp': datetime.now().isoformat(),
            'query': query[:100],  # Truncate long queries
            'response': result['response'][:200],  # Truncate long responses
            'domain': result['domain'],
            'latency_ms': result['latency_ms'],
            'tokens': result.get('tokens', 0),
            'status': result['status']
        })
        self._update_shared_metrics()

        return response_data

    def add_knowledge(self, text: str, source: str = "user_provided") -> None:
        """Add text to knowledge base."""
        if not self.rag:
            logger.warning("RAG not enabled")
            return

        self.rag.add_documents(
            documents=[text],
            metadatas=[{'source': source}],
            ids=[f"user_{uuid.uuid4().hex[:8]}"]
        )
        logger.info(f"Added knowledge from {source}")

    def add_knowledge_file(self, file_path: str) -> None:
        """Add a file to knowledge base."""
        if not self.rag:
            logger.warning("RAG not enabled")
            return

        path = Path(file_path)
        if path.suffix == '.pdf':
            self.rag.add_pdf_file(file_path)
        else:
            self.rag.add_text_file(file_path)

        logger.info(f"Added file: {path.name}")

    def get_stats(self) -> Dict[str, Any]:
        """Get chatbot statistics."""
        stats = {
            'total_messages': len(self.history),
            'domains': list(self.domains.keys()),
            'models_loaded': self.model_manager.get_stats()['models_loaded'],
        }

        # Logger stats
        logger_stats = self.logger.get_stats()
        stats.update({
            'total_requests': logger_stats['total_requests'],
            'success_rate': logger_stats['success_rate_percent']
        })

        # Metrics stats
        metrics_summary = self.metrics.get_summary()
        stats.update({
            'avg_latency_ms': metrics_summary.get('avg_latency_ms', 0),
            'p95_latency_ms': metrics_summary.get('p95_latency_ms', 0)
        })

        # RAG stats
        if self.rag:
            rag_stats = self.rag.get_stats()
            stats['knowledge_base_docs'] = rag_stats['total_documents']

        # Tools stats
        if self.tools:
            stats['available_tools'] = len(self.tools.tools)

        return stats

    def _update_shared_metrics(self):
        """Update shared metrics for dashboard."""
        import time
        import statistics

        # System metrics
        self.shared_metrics.update_system("running", time.time())

        # Model metrics
        model_stats = self.model_manager.get_stats()
        loaded_models = []
        for model_id in self.model_manager.registry.list_models():
            model_info = self.model_manager.registry._models.get(model_id)
            if model_info:
                loaded_models.append({
                    "id": model_id,
                    "name": model_info.config.model_name,
                    "memory_mb": model_info.memory_mb,
                    "uses": model_info.use_count,
                    "active": True
                })

        self.shared_metrics.update_models(
            loaded_models,
            self.model_manager.registry.max_models,
            sum(m['memory_mb'] for m in loaded_models)
        )

        # Request metrics
        logger_stats = self.logger.get_stats()
        self.shared_metrics.update_requests(
            logger_stats['total_requests'],
            logger_stats['success_count'],
            logger_stats['error_count']
        )

        # Performance metrics
        metrics_summary = self.metrics.get_summary()
        self.shared_metrics.update_performance(
            metrics_summary.get('avg_latency_ms', 0),
            metrics_summary.get('p50_latency_ms', 0),
            metrics_summary.get('p95_latency_ms', 0),
            metrics_summary.get('p99_latency_ms', 0),
            metrics_summary.get('avg_tokens', 0),
            metrics_summary.get('throughput_rps', 0)
        )

        # Domain distribution
        domain_counts = {}
        for log in self.logger._logs:
            domain = log.domain if hasattr(log, 'domain') else 'unknown'
            domain_counts[domain] = domain_counts.get(domain, 0) + 1

        self.shared_metrics.update_domains(domain_counts)

        # Tools
        if self.tools:
            # Get tool names from framework registry
            tools_list = self.tools.list_tools()
            self.shared_metrics.update_tools(True, tools_list)
        else:
            self.shared_metrics.update_tools(False, [])

        # RAG
        if self.rag:
            rag_stats = self.rag.get_stats()
            self.shared_metrics.update_rag(
                True,
                rag_stats['total_documents'],
                rag_stats.get('embedding_model', 'N/A')
            )
        else:
            self.shared_metrics.update_rag(False, 0, 'N/A')

    def interactive_mode(self):
        """Start interactive chat mode."""
        print("=" * 70)
        print("MDSA CHATBOT - Interactive Mode")
        print("=" * 70)
        print(f"Domains: {', '.join(self.domains.keys())}")
        print(f"RAG: {'Enabled' if self.enable_rag else 'Disabled'}")
        print(f"Tools: {'Enabled' if self.enable_tools else 'Disabled'}")
        print("\nCommands:")
        print("  /stats - Show statistics")
        print("  /help - Show this help")
        print("  /quit - Exit")
        print("=" * 70)
        print()

        while True:
            try:
                query = input("You: ").strip()

                if not query:
                    continue

                if query == '/quit':
                    break
                elif query == '/stats':
                    stats = self.get_stats()
                    print("\nStatistics:")
                    for key, value in stats.items():
                        print(f"  {key}: {value}")
                    print()
                    continue
                elif query == '/help':
                    print("\nAvailable commands:")
                    print("  /stats - Show statistics")
                    print("  /quit - Exit chatbot")
                    if self.tools:
                        print("\nAvailable tools:")
                        for tool in self.tools.get_available_tools():
                            print(f"  - {tool['name']}: {tool['description']}")
                    print()
                    continue

                # Process query
                result = self.chat(query)

                print(f"\nBot [{result['domain']}]: {result['response']}")
                print(f"[{result['latency_ms']:.1f}ms | Confidence: {result['confidence']:.2f}]")
                print()

            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
            except Exception as e:
                print(f"\nError: {e}")
                logger.error(f"Error in interactive mode: {e}", exc_info=True)

        # Show final stats
        stats = self.get_stats()
        print("\n" + "=" * 70)
        print("FINAL STATISTICS")
        print("=" * 70)
        for key, value in stats.items():
            print(f"  {key}: {value}")


# Example usage
if __name__ == "__main__":
    # Create chatbot
    chatbot = MDSAChatbot(
        model_name="gpt2",
        max_models=2,
        enable_rag=True,
        enable_tools=True,
        knowledge_base_dir="./knowledge_base"  # Load knowledge base
    )

    # Start interactive mode
    chatbot.interactive_mode()
