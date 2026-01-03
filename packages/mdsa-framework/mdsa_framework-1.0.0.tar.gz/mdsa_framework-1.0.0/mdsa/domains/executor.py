"""
Domain Executor Module

Executes queries using domain-specific SLMs with proper lifecycle management.
"""

import logging
import time
from typing import Dict, Any, Optional, Tuple, List

from mdsa.domains.config import DomainConfig
from mdsa.domains.prompts import PromptBuilder
from mdsa.domains.validator import ResponseValidator
from mdsa.models import ModelManager, ModelConfig
from mdsa.tools import ToolRegistry, SmartToolExecutor, ToolResult
from mdsa.tools.builtin import get_default_tools

logger = logging.getLogger(__name__)


class DomainExecutor:
    """
    Execute queries with domain-specific SLMs.

    Handles model loading, prompt building, response generation, and validation.
    """

    def __init__(
        self,
        model_manager: ModelManager,
        prompt_builder: Optional[PromptBuilder] = None,
        validator: Optional[ResponseValidator] = None,
        enable_tools: bool = True
    ):
        """
        Initialize domain executor.

        Args:
            model_manager: Model manager for loading models
            prompt_builder: Prompt builder (creates default if None)
            validator: Response validator (creates default if None)
            enable_tools: Whether to enable smart tool system (default True)
        """
        self.model_manager = model_manager
        self.prompt_builder = prompt_builder or PromptBuilder()
        self.validator = validator or ResponseValidator()

        # Initialize smart tool system
        self.tool_registry = ToolRegistry()
        self.smart_tools = SmartToolExecutor(self.tool_registry)

        # Register default built-in tools
        if enable_tools:
            for tool in get_default_tools():
                self.tool_registry.register(tool)
            logger.info(f"Registered {len(self.tool_registry)} default tools")

        logger.info("DomainExecutor initialized")

    def execute(
        self,
        query: str,
        domain_config: DomainConfig,
        context: Optional[Dict[str, Any]] = None,
        enable_tools: bool = True
    ) -> Dict[str, Any]:
        """
        Execute a query with domain SLM.

        Args:
            query: User query
            domain_config: Domain configuration
            context: Optional context dictionary
            enable_tools: Whether to use smart tool detection (default True)

        Returns:
            Dictionary with execution results:
            {
                'response': str,  # Generated response
                'domain': str,  # Domain ID
                'model': str,  # Model name
                'latency_ms': float,  # Execution time
                'tokens_generated': int,  # Approximate tokens
                'confidence': float,  # Confidence score (0-1)
                'status': str,  # 'success' or 'error'
                'error': str,  # Error message if status='error'
                'tool_results': List[Dict],  # Tool execution results if any
            }
        """
        start_time = time.time()
        context = context or {}
        tool_results = []

        try:
            # Smart tool detection and execution (BEFORE model generation)
            if enable_tools and self.smart_tools:
                detected_tools = self.smart_tools.detect_and_execute(query, context)
                if detected_tools:
                    tool_results = [result.to_dict() for result in detected_tools]
                    # Add tool results to context for model
                    context['tool_results'] = self._format_tool_results(detected_tools)
                    logger.info(f"Executed {len(detected_tools)} tools for query")

            # Load model
            logger.info(
                f"Executing query for domain '{domain_config.domain_id}' "
                f"with model '{domain_config.model_name}'"
            )

            model, tokenizer = self._load_model(domain_config)

            # Build prompt
            prompt = self.prompt_builder.build_prompt(
                query,
                domain_config,
                context
            )

            # Generate response
            response_text, tokens_generated = self._generate_response(
                model,
                tokenizer,
                prompt,
                domain_config
            )

            # Sanitize response
            response_text = self.validator.sanitize_response(response_text)

            # Validate response
            is_valid, error_msg = self.validator.validate(
                response_text,
                domain_config
            )

            if not is_valid:
                logger.warning(f"Response validation failed: {error_msg}")
                return {
                    'response': '',
                    'domain': domain_config.domain_id,
                    'model': domain_config.model_name,
                    'latency_ms': (time.time() - start_time) * 1000,
                    'tokens_generated': 0,
                    'confidence': 0.0,
                    'status': 'error',
                    'error': f"Validation failed: {error_msg}"
                }

            # Calculate confidence (simple heuristic for now)
            confidence = self._calculate_confidence(
                response_text,
                query,
                domain_config
            )

            latency_ms = (time.time() - start_time) * 1000

            logger.info(
                f"Query executed successfully in {latency_ms:.1f}ms "
                f"({tokens_generated} tokens)"
            )

            return {
                'response': response_text,
                'domain': domain_config.domain_id,
                'model': domain_config.model_name,
                'latency_ms': latency_ms,
                'tokens_generated': tokens_generated,
                'confidence': confidence,
                'status': 'success',
                'error': None,
                'tool_results': tool_results
            }

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            logger.error(f"Execution failed: {e}", exc_info=True)

            return {
                'response': '',
                'domain': domain_config.domain_id,
                'model': domain_config.model_name,
                'latency_ms': latency_ms,
                'tokens_generated': 0,
                'confidence': 0.0,
                'status': 'error',
                'error': str(e),
                'tool_results': tool_results
            }

    def _load_model(
        self,
        domain_config: DomainConfig
    ) -> Tuple[Any, Any]:
        """
        Load domain model using ModelManager.

        Args:
            domain_config: Domain configuration

        Returns:
            Tuple of (model, tokenizer)
        """
        # Create model config from domain config
        model_config = ModelConfig(
            model_name=domain_config.model_name,
            tier=domain_config.model_tier,
            device=domain_config.device,
            quantization=domain_config.quantization,
            max_length=domain_config.max_tokens,
            batch_size=domain_config.batch_size
        )

        # Use model manager to get or load model
        model_id = f"{domain_config.domain_id}_{domain_config.model_name}"
        model, tokenizer = self.model_manager.get_or_load(
            model_id,
            model_config
        )

        return model, tokenizer

    def _generate_response(
        self,
        model: Any,
        tokenizer: Any,
        prompt: str,
        config: DomainConfig
    ) -> Tuple[str, int]:
        """
        Generate response from model.

        Args:
            model: Loaded model
            tokenizer: Loaded tokenizer
            prompt: Formatted prompt
            config: Domain configuration

        Returns:
            Tuple of (response_text, tokens_generated)
        """
        try:
            # Check if we have real transformers models or dummy models
            if hasattr(model, 'generate') and hasattr(tokenizer, 'encode'):
                # Real transformers model
                return self._generate_with_transformers(
                    model,
                    tokenizer,
                    prompt,
                    config
                )
            else:
                # Dummy model for testing (Phase 3/4 development)
                return self._generate_dummy_response(prompt, config)

        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise

    def _generate_with_transformers(
        self,
        model: Any,
        tokenizer: Any,
        prompt: str,
        config: DomainConfig
    ) -> Tuple[str, int]:
        """Generate response using real transformers model."""
        import torch

        # Encode prompt
        inputs = tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=config.max_tokens
        )

        # Move to same device as model
        device = next(model.parameters()).device
        inputs = {k: v.to(device) for k, v in inputs.items()}

        # Generate with optimized parameters for Phi-2
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=config.max_tokens,
                min_new_tokens=10,  # Prevent too-short responses
                temperature=config.temperature,  # 0.3 for deterministic output
                top_p=config.top_p,
                top_k=config.top_k,
                do_sample=True,
                repetition_penalty=2.5,  # Strong penalty to reduce hallucination
                no_repeat_ngram_size=4,  # Prevent repeating 4-grams
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id,
                use_cache=True  # Enable KV cache for faster CPU inference
            )

        # Decode
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Remove the prompt from response (model may include it)
        if response.startswith(prompt):
            response = response[len(prompt):].strip()

        # Calculate tokens generated
        # For Ollama models, outputs[0] is OllamaGeneratedOutput (not a tensor)
        try:
            # Try tensor length (HuggingFace models)
            tokens_generated = len(outputs[0]) - len(inputs['input_ids'][0])
        except (TypeError, AttributeError):
            # For Ollama models: estimate tokens from text length (~4 chars per token)
            # This catches both OllamaGeneratedOutput and OllamaPseudoTensor
            tokens_generated = len(response) // 4 + 1

        return response, tokens_generated

    def _generate_dummy_response(
        self,
        prompt: str,
        config: DomainConfig
    ) -> Tuple[str, int]:
        """
        Generate dummy response for testing without real models.

        This is used during development when real models aren't loaded.
        """
        domain_id = config.domain_id

        # Create domain-specific dummy responses
        dummy_responses = {
            "finance": (
                "To transfer funds, log into your online banking account, "
                "select 'Transfer Funds', choose the source and destination accounts, "
                "enter the amount, and confirm the transfer. "
                "Most transfers complete within minutes for accounts at the same bank."
            ),
            "medical": (
                "For general health concerns, it's important to maintain a balanced diet, "
                "get regular exercise, and ensure adequate sleep. "
                "However, for specific medical advice regarding your symptoms, "
                "please consult with a qualified healthcare professional."
            ),
            "support": (
                "Thank you for contacting customer support. "
                "I'd be happy to help you with your question. "
                "To better assist you, could you provide more details about the issue you're experiencing? "
                "This will help me provide the most accurate solution."
            ),
            "technical": (
                "To resolve this technical issue, please try the following steps:\n"
                "1. Restart your device\n"
                "2. Check for available updates\n"
                "3. Clear your cache and temporary files\n"
                "If the problem persists, please contact technical support with your error details."
            ),
        }

        response = dummy_responses.get(
            domain_id,
            f"This is a response for the {domain_id} domain regarding your query. "
            f"[Note: This is a dummy response for testing purposes]"
        )

        # Estimate tokens (roughly 1 token per 4 characters)
        tokens_generated = len(response) // 4

        logger.debug(f"Generated dummy response for domain '{domain_id}'")

        return response, tokens_generated

    def _calculate_confidence(
        self,
        response: str,
        query: str,
        config: DomainConfig
    ) -> float:
        """
        Calculate confidence score for response.

        This is a simple heuristic. In production, use a proper
        confidence estimation model.

        Args:
            response: Generated response
            query: Original query
            config: Domain configuration

        Returns:
            Confidence score between 0 and 1
        """
        confidence = 0.5  # Base confidence

        # Increase confidence if response has good length
        if config.min_response_length <= len(response) <= config.max_response_length:
            confidence += 0.2

        # Increase confidence if response is relevant
        if self.validator.check_relevance(response, config, query):
            confidence += 0.2

        # Decrease confidence if response appears incomplete
        if self.validator._appears_incomplete(response):
            confidence -= 0.1

        # Decrease confidence if has repetition
        if self.validator._has_excessive_repetition(response):
            confidence -= 0.2

        # Clamp to [0, 1]
        confidence = max(0.0, min(1.0, confidence))

        return confidence

    def _format_tool_results(self, tool_results: List[ToolResult]) -> str:
        """Format tool results for inclusion in model context.

        Args:
            tool_results: List of ToolResult objects

        Returns:
            Formatted string of tool results
        """
        if not tool_results:
            return ""

        formatted = ["[Tool Results]:"]
        for result in tool_results:
            if result.success:
                formatted.append(f"- {result.tool_name}: {result.result}")
            else:
                formatted.append(f"- {result.tool_name}: FAILED ({result.error})")

        return "\n".join(formatted)

    def __repr__(self) -> str:
        return f"<DomainExecutor manager={self.model_manager}>"
