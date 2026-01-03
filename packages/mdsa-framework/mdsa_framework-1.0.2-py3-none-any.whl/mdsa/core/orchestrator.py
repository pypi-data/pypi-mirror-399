"""
Orchestrator Module

Main orchestration engine coordinating intent routing, state management, and execution.
"""

import logging
import time
from pathlib import Path
from typing import Any, Dict, Optional, List

from mdsa.core.communication_bus import MessageBus, MessageType
from mdsa.core.router import IntentRouter
from mdsa.core.state_machine import StateMachine, WorkflowState
from mdsa.core.complexity_analyzer import ComplexityAnalyzer, ComplexityResult
from mdsa.core.reasoner import Phi2Reasoner, ReasoningResult, Task
from mdsa.utils.config_loader import ConfigLoader
from mdsa.utils.hardware import HardwareDetector
from mdsa.utils.logger import setup_logger

# Phase 3: RAG and model integration
try:
    from mdsa.memory.dual_rag import DualRAG
    DUAL_RAG_AVAILABLE = True
except ImportError:
    DUAL_RAG_AVAILABLE = False
    DualRAG = None

try:
    from mdsa.integrations.adapters.ollama_adapter import (
        load_ollama_model,
        is_ollama_model,
        OllamaConnectionError
    )
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    load_ollama_model = None
    is_ollama_model = None
    OllamaConnectionError = None

logger = logging.getLogger(__name__)


class TinyBERTOrchestrator:
    """
    Main orchestration engine for MDSA framework.

    Coordinates:
    - Intent classification (TinyBERT) - <50ms target
    - State machine workflow
    - Message bus communication
    - Domain lifecycle management

    Example:
        >>> orchestrator = TinyBERTOrchestrator()
        >>> orchestrator.register_domain("finance", "Financial operations", ["money"])
        >>> result = orchestrator.process_request("Transfer $100")
        >>> print(result['status'])
    """

    def __init__(
        self,
        config_path: Optional[str] = None,
        log_level: str = "INFO",
        enable_reasoning: bool = True,
        complexity_threshold: float = 0.3,
        enable_rag: bool = True,
        ollama_base_url: str = "http://localhost:11434"
    ):
        """
        Initialize orchestrator with hybrid routing support and Phase 3 RAG integration.

        Args:
            config_path: Path to configuration file
            log_level: Logging level
            enable_reasoning: Enable Phi-2 reasoning for complex queries (default: True)
            complexity_threshold: Threshold for complexity detection (0.0-1.0, default: 0.3)
            enable_rag: Enable RAG retrieval for context augmentation (default: True, Phase 3)
            ollama_base_url: Ollama server URL (default: http://localhost:11434, Phase 3)
        """
        # Initialize logger
        self.logger = setup_logger('mdsa.orchestrator', level=log_level)

        # Load configuration
        self.config = self._load_config(config_path)

        # Hardware detection
        self.hardware = HardwareDetector()
        self.logger.info(f"Hardware: {self.hardware.get_summary()}")

        # Core components
        self.router = IntentRouter(
            device=self.hardware.best_device_for_tier1(),
            confidence_threshold=self.config.get('orchestrator', {}).get('confidence_threshold', 0.85)
        )
        self.state_machine = StateMachine()
        self.message_bus = MessageBus()

        # Phase 8: Hybrid orchestration components
        self.enable_reasoning = enable_reasoning
        self.complexity_analyzer = ComplexityAnalyzer(complexity_threshold=complexity_threshold)
        self.reasoner = Phi2Reasoner() if enable_reasoning else None

        # Phase 3: RAG and model integration
        self.enable_rag = enable_rag
        self.ollama_base_url = ollama_base_url
        self.dual_rag = None
        self.domain_models = {}  # Maps domain_id -> (model, tokenizer)

        # Initialize DualRAG if available and enabled
        if enable_rag and DUAL_RAG_AVAILABLE:
            try:
                self.dual_rag = DualRAG(
                    max_global_docs=10000,
                    max_local_docs=1000
                )
                self.logger.info("[Phase 3] DualRAG initialized (global + local knowledge bases)")
            except Exception as e:
                self.logger.warning(f"[Phase 3] DualRAG initialization failed: {e}")
                self.logger.warning("[Phase 3] RAG features disabled, continuing with routing only")
                self.dual_rag = None
                self.enable_rag = False
        elif enable_rag and not DUAL_RAG_AVAILABLE:
            self.logger.warning("[Phase 3] DualRAG not available (missing dependencies)")
            self.logger.warning("[Phase 3] Install with: pip install chromadb sentence-transformers")
            self.enable_rag = False
        else:
            self.logger.info("[Phase 3] RAG disabled (enable_rag=False)")

        # Domain registry
        self.domains = {}

        # Statistics
        self.stats = {
            'requests_total': 0,
            'requests_success': 0,
            'requests_failed': 0,
            'requests_reasoning': 0,  # Track reasoning-based requests
            'requests_rag': 0,  # Track RAG-augmented requests (Phase 3)
            'total_latency_ms': 0
        }

        # Build mode description
        components = ["TinyBERT"]
        if enable_reasoning:
            components.append("Phi-2")
        if self.enable_rag:
            components.append("RAG")
        mode = " + ".join(components)

        self.logger.info(f"TinyBERTOrchestrator initialized ({mode})")

    def _load_config(self, config_path: Optional[str]) -> Dict:
        """
        Load configuration from file or use defaults.

        Args:
            config_path: Path to config file

        Returns:
            dict: Configuration
        """
        if config_path:
            try:
                loader = ConfigLoader()
                return loader.load(config_path)
            except FileNotFoundError:
                logger.warning(f"Config file not found: {config_path}. Using defaults.")

        # Default configuration
        return {
            'framework': {
                'name': 'MDSA',
                'version': '1.0.0'
            },
            'orchestrator': {
                'confidence_threshold': 0.80,  # Lowered from 0.85 to reduce false escalations
                'device': 'auto'
            },
            'monitoring': {
                'metrics': True,
                'logging': True
            }
        }

    def register_domain(
        self,
        name: str,
        description: str,
        keywords: Optional[list] = None,
        model_name: Optional[str] = None
    ):
        """
        Register a domain for routing with optional RAG and model configuration (Phase 3).

        Args:
            name: Domain name
            description: Domain description
            keywords: Optional keywords for fallback routing
            model_name: Optional Ollama model for this domain (e.g., "ollama://llama3.2:3b")
                       If not provided, domain will use routing only (Phase 2)

        Example:
            >>> # Phase 2: Routing only
            >>> orchestrator.register_domain(
            ...     "finance",
            ...     "Financial transactions",
            ...     ["money", "transfer"]
            ... )
            >>>
            >>> # Phase 3: With Ollama model
            >>> orchestrator.register_domain(
            ...     "medical",
            ...     "Medical diagnosis",
            ...     ["diagnosis", "treatment"],
            ...     model_name="ollama://llama3.2:3b"
            ... )
        """
        # Register with router (Phase 2)
        self.router.register_domain(name, description, keywords)

        # Register with DualRAG if available (Phase 3)
        if self.dual_rag:
            self.dual_rag.register_domain(name)
            self.logger.info(f"[Phase 3] Domain '{name}' registered with LocalRAG")

        # Load Ollama model if specified (Phase 3)
        if model_name and OLLAMA_AVAILABLE:
            try:
                model, tokenizer = load_ollama_model(
                    model_name=model_name,
                    base_url=self.ollama_base_url
                )
                self.domain_models[name] = (model, tokenizer)
                self.logger.info(f"[Phase 3] Ollama model loaded for domain '{name}': {model_name}")
            except OllamaConnectionError as e:
                self.logger.warning(
                    f"[Phase 3] Failed to load Ollama model for '{name}': {e}"
                )
                self.logger.warning(
                    f"[Phase 3] Domain '{name}' will use routing only (Phase 2 mode)"
                )
            except Exception as e:
                self.logger.error(f"[Phase 3] Unexpected error loading model for '{name}': {e}")
        elif model_name and not OLLAMA_AVAILABLE:
            self.logger.warning(
                f"[Phase 3] Ollama adapter not available for domain '{name}'"
            )
            self.logger.warning("[Phase 3] Install with: pip install requests")

        # Store domain metadata
        self.domains[name] = {
            'description': description,
            'keywords': keywords or [],
            'model_name': model_name,
            'has_model': name in self.domain_models,
            'has_rag': self.dual_rag is not None
        }

        self.logger.info(f"Domain registered: {name}")

        # Publish event
        self.message_bus.publish(
            "system",
            "orchestrator",
            {"action": "domain_registered", "domain": name},
            MessageType.LOG
        )

    def process_request(self, query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Process user query through full orchestration workflow.

        Workflow:
        1. INIT -> CLASSIFY: Intent routing (TinyBERT <50ms)
        2. CLASSIFY -> VALIDATE_PRE: Check confidence threshold
        3. VALIDATE_PRE -> LOAD_SLM: Would load domain SLM (Phase 4)
        4. LOAD_SLM -> EXECUTE: Would execute domain logic (Phase 4)
        5. EXECUTE -> VALIDATE_POST: Would validate output (Phase 7)
        6. VALIDATE_POST -> LOG: Log execution
        7. LOG -> RETURN: Return result

        Args:
            query: User query string
            context: Optional context dictionary

        Returns:
            dict: Result with status, metadata, and (later) actual response

        Example:
            >>> result = orchestrator.process_request("Transfer money")
            >>> print(result['metadata']['domain'])
        """
        start_time = time.time()
        correlation_id = f"req_{int(time.time() * 1000)}"

        # Initialize state machine
        self.state_machine.reset()
        self.state_machine.set_metadata('correlation_id', correlation_id)
        self.state_machine.set_metadata('query', query)

        try:
            # Phase 8: Check query complexity for hybrid routing
            if self.enable_reasoning:
                complexity_result = self.complexity_analyzer.analyze(query)
                self.logger.info(
                    f"Complexity analysis: score={complexity_result.complexity_score:.2f}, "
                    f"complex={complexity_result.is_complex}, indicators={complexity_result.indicators}"
                )

                # Route to reasoning path if complex
                if complexity_result.is_complex:
                    return self._process_with_reasoning(query, context, correlation_id, start_time)

            # Simple query path: Use TinyBERT routing
            # 1. CLASSIFY: Intent routing
            self.state_machine.transition(WorkflowState.CLASSIFY)
            self._publish_state_change(WorkflowState.CLASSIFY, correlation_id)

            domain, confidence = self.router.classify(query)

            self.logger.info(
                f"Query classified (TinyBERT): domain={domain}, confidence={confidence:.3f}, "
                f"query='{query[:50]}...'"
            )

            # 2. Check confidence threshold
            threshold = self.config.get('orchestrator', {}).get('confidence_threshold', 0.85)
            if confidence < threshold:
                return self._escalate_to_human(query, domain, confidence, correlation_id)

            # 3. VALIDATE_PRE (placeholder - will be implemented in Phase 7)
            self.state_machine.transition(WorkflowState.VALIDATE_PRE)
            self._publish_state_change(WorkflowState.VALIDATE_PRE, correlation_id)

            # Phase 3: RAG retrieval (if enabled)
            rag_context = []
            rag_retrieval_time_ms = 0
            if self.enable_rag and self.dual_rag:
                rag_start = time.time()
                try:
                    rag_results = self.dual_rag.retrieve(
                        query=query,
                        domain_id=domain,
                        top_k=3,  # Retrieve top 3 from each (local + global)
                        search_local=True,
                        search_global=True
                    )

                    # Combine local and global RAG results
                    for source_type in ['local', 'global']:
                        if source_type in rag_results:
                            for doc, score in zip(
                                rag_results[source_type].documents,
                                rag_results[source_type].scores
                            ):
                                rag_context.append({
                                    'source': source_type,
                                    'content': doc.content,
                                    'score': score,
                                    'metadata': doc.metadata
                                })

                    rag_retrieval_time_ms = (time.time() - rag_start) * 1000
                    self.stats['requests_rag'] += 1
                    self.logger.info(
                        f"[Phase 3] RAG retrieval: {len(rag_context)} docs in {rag_retrieval_time_ms:.1f}ms"
                    )

                except Exception as e:
                    self.logger.error(f"[Phase 3] RAG retrieval failed: {e}")
                    # Continue without RAG context

            # 4. LOAD_SLM / EXECUTE with Ollama (Phase 3)
            response_text = None
            execution_time_ms = 0

            if domain in self.domain_models:
                # Phase 3: Execute with Ollama model
                self.state_machine.transition(WorkflowState.LOAD_SLM)
                self._publish_state_change(WorkflowState.LOAD_SLM, correlation_id)

                self.state_machine.transition(WorkflowState.EXECUTE)
                self._publish_state_change(WorkflowState.EXECUTE, correlation_id)

                exec_start = time.time()
                try:
                    model, tokenizer = self.domain_models[domain]

                    # Build prompt with RAG context
                    prompt = self._build_prompt_with_rag(query, rag_context)

                    # Tokenize
                    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)

                    # Generate response
                    outputs = model.generate(
                        input_ids=inputs['input_ids'],
                        max_new_tokens=256,
                        temperature=0.7,
                        top_p=0.9,
                        do_sample=True
                    )

                    # Decode response
                    response_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

                    # Extract only the generated part (remove prompt)
                    if hasattr(outputs[0], 'generated_text'):
                        response_text = outputs[0].generated_text
                    elif len(response_text) > len(prompt):
                        response_text = response_text[len(prompt):].strip()

                    execution_time_ms = (time.time() - exec_start) * 1000
                    self.logger.info(
                        f"[Phase 3] Ollama execution: {len(response_text)} chars in {execution_time_ms:.1f}ms"
                    )

                except Exception as e:
                    self.logger.error(f"[Phase 3] Ollama execution failed: {e}")
                    response_text = f"Error: Failed to generate response - {str(e)}"
                    execution_time_ms = (time.time() - exec_start) * 1000
            else:
                # Phase 2: No model configured, routing only
                self.state_machine.transition(WorkflowState.LOAD_SLM)
                self._publish_state_change(WorkflowState.LOAD_SLM, correlation_id)

                self.state_machine.transition(WorkflowState.EXECUTE)
                self._publish_state_change(WorkflowState.EXECUTE, correlation_id)

                response_text = None
                self.logger.info(f"[Phase 2] No model configured for domain '{domain}' - routing only")

            # 5. VALIDATE_POST (placeholder - will be implemented in Phase 7)
            self.state_machine.transition(WorkflowState.VALIDATE_POST)
            self._publish_state_change(WorkflowState.VALIDATE_POST, correlation_id)

            # 7. LOG
            self.state_machine.transition(WorkflowState.LOG)
            self._publish_state_change(WorkflowState.LOG, correlation_id)

            # 8. RETURN
            self.state_machine.transition(WorkflowState.RETURN)
            self._publish_state_change(WorkflowState.RETURN, correlation_id)

            # Calculate latency
            latency_ms = (time.time() - start_time) * 1000

            # Update statistics
            self.stats['requests_total'] += 1
            self.stats['requests_success'] += 1
            self.stats['total_latency_ms'] += latency_ms

            # Build result with Phase 3 enhancements
            result = {
                'status': 'success',
                'message': self._build_result_message(domain, response_text, rag_context),
                'metadata': {
                    'domain': domain,
                    'confidence': confidence,
                    'latency_ms': latency_ms,
                    'correlation_id': correlation_id,
                    'state_history': [s.value for s in self.state_machine.get_state_history()],
                    # Phase 3 metrics
                    'rag_retrieval_ms': rag_retrieval_time_ms,
                    'rag_docs_count': len(rag_context),
                    'execution_ms': execution_time_ms,
                    'has_response': response_text is not None,
                    'has_rag': len(rag_context) > 0
                }
            }

            # Phase 3: Add response and RAG context if available
            if response_text:
                result['response'] = response_text

            if rag_context:
                result['rag_context'] = rag_context

            # Publish completion
            self.message_bus.publish(
                "orchestrator",
                "orchestrator",
                result,
                MessageType.RESPONSE,
                correlation_id=correlation_id
            )

            return result

        except Exception as e:
            self.logger.error(f"Request processing failed: {e}", exc_info=True)

            # Transition to ERROR state
            if not self.state_machine.is_terminal_state():
                try:
                    self.state_machine.transition(WorkflowState.ERROR)
                except Exception:
                    pass  # Already in terminal state

            # Update statistics
            self.stats['requests_total'] += 1
            self.stats['requests_failed'] += 1

            return {
                'status': 'error',
                'message': str(e),
                'metadata': {
                    'correlation_id': correlation_id,
                    'latency_ms': (time.time() - start_time) * 1000
                }
            }

    def _escalate_to_human(
        self,
        query: str,
        domain: str,
        confidence: float,
        correlation_id: str
    ) -> Dict[str, Any]:
        """
        Escalate low-confidence queries to human review.

        Args:
            query: User query
            domain: Predicted domain
            confidence: Confidence score
            correlation_id: Request correlation ID

        Returns:
            dict: Escalation result
        """
        self.logger.warning(
            f"Low confidence escalation: domain={domain}, confidence={confidence:.3f}"
        )

        # Transition to RETURN (bypass processing)
        self.state_machine.transition(WorkflowState.RETURN, force=True)

        # Update statistics for escalated requests
        self.stats['requests_total'] += 1
        # Note: escalated requests are not counted as success or failure
        # They represent a distinct category requiring human intervention

        return {
            'status': 'escalated',
            'message': 'Low confidence - escalated to human review',
            'metadata': {
                'domain': domain,
                'confidence': confidence,
                'threshold': self.config.get('orchestrator', {}).get('confidence_threshold', 0.85),
                'correlation_id': correlation_id,
                'requires_human_review': True
            }
        }

    def _publish_state_change(self, state: WorkflowState, correlation_id: str):
        """
        Publish state change event to message bus.

        Args:
            state: New state
            correlation_id: Request correlation ID
        """
        self.message_bus.publish(
            "state_changes",
            "orchestrator",
            {"state": state.value},
            MessageType.STATE_CHANGE,
            correlation_id=correlation_id
        )

    def _process_with_reasoning(
        self,
        query: str,
        context: Optional[Dict],
        correlation_id: str,
        start_time: float
    ) -> Dict[str, Any]:
        """
        Process complex query using Phi-2 reasoning for task decomposition.

        This method handles multi-domain, sequential, or conditional queries
        by breaking them into sub-tasks and executing in the correct order.

        Args:
            query: User query string
            context: Optional context dictionary
            correlation_id: Request correlation ID
            start_time: Request start time

        Returns:
            dict: Result with consolidated task outputs and metadata

        Example:
            Query: "Code diagnosis and then calculate billing"
            → Task 1: Extract codes (medical_coding domain)
            → Task 2: Calculate billing (medical_billing domain, depends on Task 1)
        """
        self.logger.info(f"Using Phi-2 reasoning for complex query: '{query[:50]}...'")

        try:
            # 1. CLASSIFY state (but using reasoning instead of TinyBERT)
            self.state_machine.transition(WorkflowState.CLASSIFY)
            self._publish_state_change(WorkflowState.CLASSIFY, correlation_id)

            # 2. Use Phi-2 Reasoner to analyze and plan
            reasoning_result = self.reasoner.analyze_and_plan(query, context)

            if not reasoning_result.success:
                return {
                    'status': 'error',
                    'message': f'Reasoning failed: {reasoning_result.error}',
                    'metadata': {
                        'correlation_id': correlation_id,
                        'latency_ms': (time.time() - start_time) * 1000,
                        'reasoning_error': reasoning_result.error
                    }
                }

            execution_plan = reasoning_result.execution_plan
            self.logger.info(
                f"Reasoning analysis: {reasoning_result.analysis}\n"
                f"Execution plan: {len(execution_plan)} task(s), "
                f"estimated {reasoning_result.total_estimated_time_ms:.0f}ms"
            )

            # Log task breakdown
            for task in execution_plan:
                deps = f" (depends on {task.dependencies})" if task.dependencies else ""
                self.logger.info(
                    f"  Task {task.task_id}: {task.description} → {task.domain}{deps}"
                )

            # 3. Execute tasks in dependency order
            # For multi-task execution, do state transitions only once at workflow level
            # Individual task execution is logged but doesn't cycle through all states

            # Initial transitions for the workflow
            self.state_machine.transition(WorkflowState.VALIDATE_PRE)
            self._publish_state_change(WorkflowState.VALIDATE_PRE, correlation_id)

            self.state_machine.transition(WorkflowState.LOAD_SLM)
            self._publish_state_change(WorkflowState.LOAD_SLM, correlation_id)

            self.state_machine.transition(WorkflowState.EXECUTE)
            self._publish_state_change(WorkflowState.EXECUTE, correlation_id)

            task_results = {}
            for task in execution_plan:
                # Check if dependencies are satisfied
                if task.dependencies:
                    for dep_id in task.dependencies:
                        if dep_id not in task_results:
                            return {
                                'status': 'error',
                                'message': f'Task {task.task_id} dependency {dep_id} not satisfied',
                                'metadata': {
                                    'correlation_id': correlation_id,
                                    'latency_ms': (time.time() - start_time) * 1000
                                }
                            }

                # Execute task (placeholder - Phase 4 will implement actual domain execution)
                # For now, route through TinyBERT for the specific task query
                domain, confidence = self.router.classify(task.query)

                self.logger.info(
                    f"Executing Task {task.task_id}: domain={domain}, "
                    f"confidence={confidence:.3f}, query='{task.query[:50]}...'"
                )

                # Store task result
                task_results[task.task_id] = {
                    'task_id': task.task_id,
                    'description': task.description,
                    'domain': domain,
                    'confidence': confidence,
                    'query': task.query,
                    'tools_used': task.tools_needed,
                    'status': 'completed'
                }

            # Transition to VALIDATE_POST after all tasks complete
            self.state_machine.transition(WorkflowState.VALIDATE_POST)
            self._publish_state_change(WorkflowState.VALIDATE_POST, correlation_id)

            # 4. LOG
            self.state_machine.transition(WorkflowState.LOG)
            self._publish_state_change(WorkflowState.LOG, correlation_id)

            # 5. RETURN
            self.state_machine.transition(WorkflowState.RETURN)
            self._publish_state_change(WorkflowState.RETURN, correlation_id)

            # Calculate latency
            latency_ms = (time.time() - start_time) * 1000

            # Update statistics
            self.stats['requests_total'] += 1
            self.stats['requests_success'] += 1
            self.stats['requests_reasoning'] += 1  # Track reasoning-based requests
            self.stats['total_latency_ms'] += latency_ms

            # Build consolidated result
            result = {
                'status': 'success',
                'message': f'Complex query processed with {len(execution_plan)} task(s) (reasoning-based)',
                'metadata': {
                    'reasoning_used': True,
                    'num_tasks': len(execution_plan),
                    'reasoning_analysis': reasoning_result.analysis,
                    'reasoning_time_ms': reasoning_result.reasoning_time_ms,
                    'execution_time_ms': latency_ms - reasoning_result.reasoning_time_ms,
                    'total_latency_ms': latency_ms,
                    'correlation_id': correlation_id,
                    'state_history': [s.value for s in self.state_machine.get_state_history()],
                    'task_results': list(task_results.values())
                }
            }

            # Publish completion
            self.message_bus.publish(
                "orchestrator",
                "orchestrator",
                result,
                MessageType.RESPONSE,
                correlation_id=correlation_id
            )

            return result

        except Exception as e:
            self.logger.error(f"Reasoning-based processing failed: {e}", exc_info=True)

            # Transition to ERROR state
            if not self.state_machine.is_terminal_state():
                try:
                    self.state_machine.transition(WorkflowState.ERROR)
                except Exception:
                    pass

            # Update statistics
            self.stats['requests_total'] += 1
            self.stats['requests_failed'] += 1

            return {
                'status': 'error',
                'message': str(e),
                'metadata': {
                    'correlation_id': correlation_id,
                    'latency_ms': (time.time() - start_time) * 1000,
                    'reasoning_used': True,
                    'state_history': [s.value for s in self.state_machine.get_state_history()]
                }
            }

    def _build_prompt_with_rag(self, query: str, rag_context: List[Dict]) -> str:
        """
        Build prompt with RAG context for model generation (Phase 3).

        Args:
            query: User query
            rag_context: List of retrieved documents with metadata

        Returns:
            Formatted prompt string

        Example:
            >>> prompt = orchestrator._build_prompt_with_rag(
            ...     "What is diabetes?",
            ...     [{'content': 'Diabetes is...', 'source': 'global', 'score': 0.95}]
            ... )
        """
        if not rag_context:
            # No context, return simple prompt
            return f"User question: {query}\n\nAnswer:"

        # Build context section from RAG documents
        context_parts = []
        for i, doc in enumerate(rag_context[:5], 1):  # Limit to top 5 docs
            source_label = "Domain Knowledge" if doc['source'] == 'local' else "General Knowledge"
            context_parts.append(f"[{source_label} {i}] {doc['content'][:200]}")  # Truncate long docs

        context_section = "\n".join(context_parts)

        # Build full prompt
        prompt = f"""Context information:
{context_section}

User question: {query}

Based on the context above, provide a detailed answer:"""

        return prompt

    def _build_result_message(
        self,
        domain: str,
        response_text: Optional[str],
        rag_context: List[Dict]
    ) -> str:
        """
        Build appropriate result message based on Phase 2 vs Phase 3 execution (Phase 3).

        Args:
            domain: Classified domain
            response_text: Generated response (None for Phase 2)
            rag_context: RAG context documents (empty for Phase 2)

        Returns:
            Human-readable result message

        Example:
            >>> msg = orchestrator._build_result_message("medical", "Diabetes is...", [])
            >>> # Returns: "Request processed by medical domain (Phase 3: routing + RAG + generation)"
        """
        if response_text and rag_context:
            return (
                f"Request processed by {domain} domain "
                f"(Phase 3: routing + RAG ({len(rag_context)} docs) + generation)"
            )
        elif response_text:
            return (
                f"Request processed by {domain} domain "
                f"(Phase 3: routing + generation, no RAG context)"
            )
        elif rag_context:
            return (
                f"Request routed to {domain} domain "
                f"(Phase 3: routing + RAG ({len(rag_context)} docs), no model configured)"
            )
        else:
            return f"Request routed to {domain} domain (Phase 2: routing only)"

    def get_stats(self) -> Dict[str, Any]:
        """
        Get orchestrator statistics.

        Returns:
            dict: Statistics including request counts, latencies, domains, reasoning usage

        Example:
            >>> stats = orchestrator.get_stats()
            >>> print(f"Success rate: {stats['success_rate']:.1%}")
            >>> print(f"Reasoning usage: {stats['reasoning_rate']:.1%}")
        """
        total = self.stats['requests_total']
        avg_latency = (
            self.stats['total_latency_ms'] / total if total > 0 else 0
        )

        return {
            'requests_total': total,
            'requests_success': self.stats['requests_success'],
            'requests_failed': self.stats['requests_failed'],
            'requests_reasoning': self.stats['requests_reasoning'],
            'requests_rag': self.stats.get('requests_rag', 0),  # Phase 3
            'success_rate': self.stats['requests_success'] / total if total > 0 else 0,
            'reasoning_rate': self.stats['requests_reasoning'] / total if total > 0 else 0,
            'rag_rate': self.stats.get('requests_rag', 0) / total if total > 0 else 0,  # Phase 3
            'average_latency_ms': avg_latency,
            'domains_registered': len(self.router.domains),
            'domain_stats': self.router.get_domain_stats(),
            'message_bus': self.message_bus.get_stats(),
            # Phase 3 specific stats
            'rag_enabled': self.enable_rag,
            'dual_rag_available': self.dual_rag is not None,
            'domains_with_models': len(self.domain_models)
        }

    def reset_stats(self):
        """Reset all statistics."""
        self.stats = {
            'requests_total': 0,
            'requests_success': 0,
            'requests_failed': 0,
            'requests_reasoning': 0,
            'requests_rag': 0,  # Phase 3
            'total_latency_ms': 0
        }
        self.router.reset_stats()
        self.logger.info("Statistics reset")

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<TinyBERTOrchestrator domains={len(self.router.domains)} "
            f"requests={self.stats['requests_total']}>"
        )


if __name__ == "__main__":
    # Demo usage
    print("=== TinyBERTOrchestrator Demo ===\n")

    # Initialize orchestrator
    orchestrator = TinyBERTOrchestrator(log_level="INFO")

    # Register domains
    print("--- Registering Domains ---")
    orchestrator.register_domain(
        "finance",
        "Financial transactions and banking operations",
        ["money", "transfer", "payment", "balance"]
    )
    orchestrator.register_domain(
        "support",
        "Customer support and help desk",
        ["help", "support", "issue", "problem"]
    )

    # Process requests
    print("\n--- Processing Requests ---")
    test_queries = [
        "Transfer $100 to my savings",
        "I need help with my account",
        "What is my balance?",
    ]

    for query in test_queries:
        print(f"\nQuery: '{query}'")
        result = orchestrator.process_request(query)
        print(f"Status: {result['status']}")
        print(f"Domain: {result['metadata']['domain']}")
        print(f"Confidence: {result['metadata']['confidence']:.3f}")
        print(f"Latency: {result['metadata']['latency_ms']:.2f}ms")

    # Statistics
    print("\n--- Statistics ---")
    stats = orchestrator.get_stats()
    for key, value in stats.items():
        if not isinstance(value, dict):
            print(f"{key}: {value}")
