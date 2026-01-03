"""
Ollama Adapter for MDSA Framework

Provides wrapper classes that make Ollama models compatible with the MDSA
framework's HuggingFace-based interface. This enables using Ollama-hosted
models as drop-in replacements without modifying the DomainExecutor.

Usage:
    # In DomainConfig:
    model_name="ollama://llama3.2:3b-instruct-q4_0"

    # The ModelLoader will detect the "ollama://" prefix and use this adapter.

Prerequisites:
    1. Ollama must be running: `ollama serve`
    2. Model must be pulled: `ollama pull llama3.2:3b-instruct-q4_0`

Author: MDSA Framework Team
Date: 2025-12-09
"""

import logging
import time
from typing import Dict, List, Optional, Any, Iterator

logger = logging.getLogger(__name__)

# Try to import requests
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logger.warning("requests library not available. Ollama integration disabled.")


class OllamaConnectionError(Exception):
    """Raised when Ollama server is unreachable."""
    pass


class OllamaModelNotFoundError(Exception):
    """Raised when specified model is not available in Ollama."""
    pass


class OllamaGenerationError(Exception):
    """Raised when generation fails."""
    pass


class OllamaPseudoTensor:
    """
    Pseudo-tensor that carries text through the HuggingFace-style pipeline.

    The MDSA DomainExecutor expects tensors, but Ollama handles tokenization
    server-side. This class wraps text to pass through the pipeline.
    """

    def __init__(self, text: str):
        """
        Initialize pseudo-tensor with text.

        Args:
            text: The prompt text to carry through the pipeline
        """
        self.text = text

    def to(self, device: str) -> "OllamaPseudoTensor":
        """No-op device transfer - Ollama handles device placement."""
        return self

    def __repr__(self) -> str:
        return f"<OllamaPseudoTensor text_len={len(self.text)}>"


class OllamaGeneratedOutput:
    """
    Output container matching HuggingFace generate() output format.

    Allows tokenizer.decode(outputs[0]) to work correctly.
    Supports tool calling information when tools are used.
    """

    def __init__(
        self,
        text: str,
        generated_text: str,
        prompt_length: int,
        tool_calls: Optional[List[Dict]] = None
    ):
        """
        Initialize generated output.

        Args:
            text: Full text (prompt + generation)
            generated_text: Only the generated portion
            prompt_length: Length of original prompt
            tool_calls: Optional list of tool calls made by the model
                       Format: [{"name": "tool_name", "arguments": {...}}]
        """
        self.text = text
        self.generated_text = generated_text
        self.prompt_length = prompt_length
        self.tool_calls = tool_calls or []

    def __getitem__(self, idx: int) -> "OllamaGeneratedOutput":
        """Support indexing for tokenizer.decode(outputs[0])."""
        if idx == 0:
            return self
        raise IndexError(f"Index {idx} out of range")

    def has_tool_calls(self) -> bool:
        """Check if the output contains tool calls."""
        return len(self.tool_calls) > 0

    def __repr__(self) -> str:
        tool_info = f", tool_calls={len(self.tool_calls)}" if self.tool_calls else ""
        return f"<OllamaGeneratedOutput gen_len={len(self.generated_text)}{tool_info}>"


class OllamaPseudoParameter:
    """
    Pseudo-parameter for device detection.

    The DomainExecutor uses next(model.parameters()).device to detect
    where the model is located. This provides that interface.
    """

    def __init__(self, device: str = "ollama"):
        """
        Initialize pseudo-parameter.

        Args:
            device: Device identifier (default: "ollama")
        """
        self.device = device


class OllamaTokenizer:
    """
    Tokenizer adapter for Ollama models.

    Provides interface compatible with HuggingFace tokenizers but operates
    locally without actual tokenization - Ollama handles tokenization server-side.
    """

    def __init__(self, model_name: str):
        """
        Initialize Ollama tokenizer.

        Args:
            model_name: Ollama model name (without "ollama://" prefix)
        """
        self.model_name = model_name
        self.eos_token_id = 0  # Placeholder - not used by Ollama
        self.pad_token_id = 0

        logger.debug(f"OllamaTokenizer initialized for model: {model_name}")

    def __call__(
        self,
        text: str,
        return_tensors: str = "pt",
        truncation: bool = True,
        max_length: int = 512,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Simulate tokenizer call.

        Returns dict with 'input_ids' containing pseudo-tensor with raw text.
        Ollama handles actual tokenization server-side.

        Args:
            text: Input text to "tokenize"
            return_tensors: Tensor format (ignored - always returns pseudo-tensor)
            truncation: Whether to truncate (handled by Ollama)
            max_length: Maximum length (passed to Ollama)
            **kwargs: Additional arguments (ignored)

        Returns:
            Dict with 'input_ids' and 'attention_mask' pseudo-tensors
        """
        # Truncate text if needed (rough approximation)
        if truncation and len(text) > max_length * 4:  # ~4 chars per token
            text = text[:max_length * 4]
            logger.debug(f"Truncated input to ~{max_length} tokens")

        pseudo_tensor = OllamaPseudoTensor(text)

        return {
            'input_ids': pseudo_tensor,
            'attention_mask': pseudo_tensor
        }

    def encode(self, text: str, **kwargs) -> List[int]:
        """
        Rough token count estimation.

        Used for hasattr check - returns approximate token count.

        Args:
            text: Text to "encode"
            **kwargs: Additional arguments (ignored)

        Returns:
            List of pseudo token IDs (length approximates token count)
        """
        # Estimate: ~4 characters per token (rough approximation)
        estimated_tokens = len(text) // 4 + 1
        return list(range(estimated_tokens))

    def decode(
        self,
        token_ids: Any,
        skip_special_tokens: bool = True,
        **kwargs
    ) -> str:
        """
        Return the generated text.

        OllamaModel.generate() returns text directly wrapped in OllamaGeneratedOutput.

        Args:
            token_ids: OllamaGeneratedOutput or raw output
            skip_special_tokens: Whether to skip special tokens (ignored)
            **kwargs: Additional arguments (ignored)

        Returns:
            Generated text string
        """
        if isinstance(token_ids, OllamaGeneratedOutput):
            return token_ids.text
        if hasattr(token_ids, 'text'):
            return token_ids.text
        return str(token_ids)


class OllamaModel:
    """
    Model adapter for Ollama API.

    Provides HuggingFace-compatible generate() interface that delegates
    to Ollama HTTP API for actual inference.

    Example:
        >>> model = OllamaModel("llama3.2:3b-instruct-q4_0")
        >>> inputs = OllamaPseudoTensor("What is 2+2?")
        >>> outputs = model.generate(input_ids=inputs, max_new_tokens=100)
        >>> print(outputs[0].generated_text)
    """

    def __init__(
        self,
        model_name: str,
        base_url: str = "http://localhost:11434",
        timeout: int = 120,
        api_key: Optional[str] = None
    ):
        """
        Initialize Ollama model adapter.

        Args:
            model_name: Ollama model name (without "ollama://" prefix)
            base_url: Ollama server URL (default: http://localhost:11434)
            timeout: Request timeout in seconds (default: 120)
            api_key: Optional API key for cloud Ollama authentication

        Raises:
            OllamaConnectionError: If Ollama server is unreachable
        """
        if not REQUESTS_AVAILABLE:
            raise RuntimeError(
                "requests library is required for Ollama integration. "
                "Install with: pip install requests"
            )

        self.model_name = model_name
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.api_key = api_key
        self._device = "ollama"

        # Verify connection
        self._verify_connection()

        logger.info(f"OllamaModel initialized: {model_name} at {base_url}")

    def _verify_connection(self) -> None:
        """
        Verify Ollama is running and model is available.

        Raises:
            OllamaConnectionError: If server is unreachable
        """
        # Build headers with authentication if API key provided
        headers = {}
        if self.api_key:
            headers['Authorization'] = f"Bearer {self.api_key}"

        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                headers=headers,
                timeout=5
            )
            response.raise_for_status()

            available_models = [
                m.get('name', '')
                for m in response.json().get('models', [])
            ]

            # Check if our model is available (handle tag variations)
            model_found = any(
                self.model_name in m or m.startswith(self.model_name.split(':')[0])
                for m in available_models
            )

            if not model_found and available_models:
                logger.warning(
                    f"Model '{self.model_name}' not found in Ollama. "
                    f"Available models: {available_models}. "
                    f"Will attempt to use anyway (may auto-pull)."
                )
            elif not available_models:
                logger.warning(
                    f"No models found in Ollama. "
                    f"Pull model with: ollama pull {self.model_name}"
                )

        except requests.exceptions.ConnectionError as e:
            raise OllamaConnectionError(
                f"Cannot connect to Ollama at {self.base_url}. "
                f"Please ensure Ollama is running:\n"
                f"  1. Start Ollama: `ollama serve`\n"
                f"  2. Pull model: `ollama pull {self.model_name}`\n"
                f"  3. Verify: `ollama list`\n"
                f"Original error: {e}"
            )
        except requests.exceptions.Timeout:
            raise OllamaConnectionError(
                f"Ollama server at {self.base_url} is not responding. "
                f"Server may be overloaded or starting up."
            )
        except requests.exceptions.RequestException as e:
            raise OllamaConnectionError(f"Ollama connection error: {e}")

    def generate(
        self,
        input_ids: Optional[Any] = None,
        attention_mask: Optional[Any] = None,
        max_new_tokens: int = 256,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 50,
        do_sample: bool = True,
        repetition_penalty: float = 1.0,
        no_repeat_ngram_size: int = 0,
        pad_token_id: Optional[int] = None,
        eos_token_id: Optional[int] = None,
        use_cache: bool = True,
        tools: Optional[List[Dict]] = None,
        tool_choice: str = "auto",
        **kwargs
    ) -> List[OllamaGeneratedOutput]:
        """
        Generate text using Ollama API with optional tool calling support.

        Args:
            input_ids: OllamaPseudoTensor containing prompt text
            attention_mask: Ignored (Ollama handles attention)
            max_new_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-2.0)
            top_p: Nucleus sampling probability
            top_k: Top-k sampling
            do_sample: Whether to use sampling (ignored - always samples)
            repetition_penalty: Penalty for repetition
            no_repeat_ngram_size: Ignored (not supported by Ollama)
            pad_token_id: Ignored
            eos_token_id: Ignored
            use_cache: Ignored
            tools: Optional list of tool definitions for function calling
                   Format: [{"type": "function", "function": {"name": "...", "description": "...", "parameters": {...}}}]
            tool_choice: How to use tools - "auto", "none", or specific tool name (default: "auto")
            **kwargs: Additional arguments (may contain input_ids)

        Returns:
            List with single OllamaGeneratedOutput (matches HuggingFace format)
            If tools are used, the generated_text may contain tool call information

        Raises:
            OllamaGenerationError: If generation fails
        """
        # Extract prompt from pseudo-tensor
        prompt = self._extract_prompt(input_ids, kwargs)

        # Choose endpoint and payload based on whether tools are used
        if tools:
            # Use /api/chat endpoint for tool calling
            return self._generate_with_tools(
                prompt=prompt,
                tools=tools,
                tool_choice=tool_choice,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                repetition_penalty=repetition_penalty
            )
        else:
            # Use /api/generate endpoint for standard generation
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "top_p": top_p,
                    "top_k": top_k,
                    "num_predict": max_new_tokens,
                    "repeat_penalty": repetition_penalty
                }
            }

            logger.debug(f"Ollama generate request: model={self.model_name}, prompt_len={len(prompt)}")

            start_time = time.time()

            # Build headers with authentication if API key provided
            headers = {}
            if self.api_key:
                headers['Authorization'] = f"Bearer {self.api_key}"

            try:
                response = requests.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    headers=headers,
                    timeout=self.timeout
                )
                response.raise_for_status()
                result = response.json()

                generated_text = result.get('response', '')

                elapsed_ms = (time.time() - start_time) * 1000
                logger.debug(
                    f"Ollama generation complete: "
                    f"gen_len={len(generated_text)}, time={elapsed_ms:.1f}ms"
                )

                # Return in HuggingFace-compatible format
                # Note: HuggingFace returns prompt + generated text
                full_text = prompt + generated_text

                return [OllamaGeneratedOutput(
                    text=full_text,
                    generated_text=generated_text,
                    prompt_length=len(prompt)
                )]

            except requests.exceptions.Timeout:
                raise OllamaGenerationError(
                    f"Ollama generation timed out after {self.timeout}s. "
                    f"Try increasing timeout or reducing max_new_tokens."
                )
            except requests.exceptions.HTTPError as e:
                raise OllamaGenerationError(
                    f"Ollama API error: {e}. "
                    f"Response: {e.response.text if e.response else 'No response'}"
                )
            except requests.exceptions.RequestException as e:
                raise OllamaGenerationError(f"Ollama request failed: {e}")
            except (KeyError, ValueError) as e:
                raise OllamaGenerationError(f"Invalid Ollama response format: {e}")

    def _extract_prompt(self, input_ids: Any, kwargs: Dict) -> str:
        """
        Extract prompt text from input.

        Args:
            input_ids: Primary input (OllamaPseudoTensor or None)
            kwargs: Additional kwargs that may contain input_ids

        Returns:
            Prompt text string

        Raises:
            ValueError: If prompt cannot be extracted
        """
        # Try input_ids first
        if input_ids is not None:
            if hasattr(input_ids, 'text'):
                return input_ids.text
            if isinstance(input_ids, str):
                return input_ids

        # Try kwargs
        if 'input_ids' in kwargs:
            ids = kwargs['input_ids']
            if hasattr(ids, 'text'):
                return ids.text
            if isinstance(ids, str):
                return ids

        # Try inputs key (some frameworks use this)
        if 'inputs' in kwargs:
            inputs = kwargs['inputs']
            if hasattr(inputs, 'text'):
                return inputs.text
            if isinstance(inputs, str):
                return inputs

        raise ValueError(
            "Cannot extract prompt from inputs. "
            "Expected OllamaPseudoTensor or string."
        )

    def _generate_with_tools(
        self,
        prompt: str,
        tools: List[Dict],
        tool_choice: str,
        max_new_tokens: int,
        temperature: float,
        top_p: float,
        top_k: int,
        repetition_penalty: float
    ) -> List[OllamaGeneratedOutput]:
        """
        Generate text with tool calling support using Ollama's chat API.

        Args:
            prompt: The input prompt
            tools: List of tool definitions
            tool_choice: How to use tools ("auto", "none", or specific tool name)
            max_new_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Nucleus sampling probability
            top_k: Top-k sampling
            repetition_penalty: Penalty for repetition

        Returns:
            List with single OllamaGeneratedOutput containing tool calls if any

        Raises:
            OllamaGenerationError: If generation fails
        """
        # Build payload for /api/chat endpoint
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "stream": False,
            "tools": tools,
            "options": {
                "temperature": temperature,
                "top_p": top_p,
                "top_k": top_k,
                "num_predict": max_new_tokens,
                "repeat_penalty": repetition_penalty
            }
        }

        # Add tool_choice if specified
        if tool_choice and tool_choice != "auto":
            if tool_choice == "none":
                payload["tools"] = []  # Disable tools
            else:
                # Specific tool requested
                payload["tool_choice"] = tool_choice

        logger.debug(
            f"Ollama chat request with tools: model={self.model_name}, "
            f"prompt_len={len(prompt)}, num_tools={len(tools)}"
        )

        start_time = time.time()

        # Build headers with authentication if API key provided
        headers = {}
        if self.api_key:
            headers['Authorization'] = f"Bearer {self.api_key}"

        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()

            # Extract message from response
            message = result.get('message', {})
            generated_text = message.get('content', '')
            tool_calls_raw = message.get('tool_calls', [])

            # Parse tool calls into standardized format
            tool_calls = []
            if tool_calls_raw:
                for tc in tool_calls_raw:
                    tool_calls.append({
                        'name': tc.get('function', {}).get('name', ''),
                        'arguments': tc.get('function', {}).get('arguments', {})
                    })

            elapsed_ms = (time.time() - start_time) * 1000
            logger.debug(
                f"Ollama chat complete: gen_len={len(generated_text)}, "
                f"tool_calls={len(tool_calls)}, time={elapsed_ms:.1f}ms"
            )

            # Return in HuggingFace-compatible format with tool calls
            full_text = prompt + generated_text

            return [OllamaGeneratedOutput(
                text=full_text,
                generated_text=generated_text,
                prompt_length=len(prompt),
                tool_calls=tool_calls
            )]

        except requests.exceptions.Timeout:
            raise OllamaGenerationError(
                f"Ollama chat timed out after {self.timeout}s. "
                f"Try increasing timeout or reducing max_new_tokens."
            )
        except requests.exceptions.HTTPError as e:
            raise OllamaGenerationError(
                f"Ollama API error: {e}. "
                f"Response: {e.response.text if e.response else 'No response'}"
            )
        except requests.exceptions.RequestException as e:
            raise OllamaGenerationError(f"Ollama request failed: {e}")
        except (KeyError, ValueError) as e:
            raise OllamaGenerationError(f"Invalid Ollama response format: {e}")

    def parameters(self) -> Iterator[OllamaPseudoParameter]:
        """
        Return iterator for device detection.

        The DomainExecutor uses next(model.parameters()).device
        to detect model device. This provides that interface.

        Yields:
            OllamaPseudoParameter with device="ollama"
        """
        yield OllamaPseudoParameter(self._device)

    def eval(self) -> "OllamaModel":
        """No-op: Ollama models are always in eval mode."""
        return self

    def to(self, device: str) -> "OllamaModel":
        """No-op: Ollama handles device placement server-side."""
        return self

    def __repr__(self) -> str:
        return f"<OllamaModel model={self.model_name} url={self.base_url}>"


def is_ollama_model(model_name: str) -> bool:
    """
    Check if model name indicates an Ollama model.

    Args:
        model_name: Model name string to check

    Returns:
        True if model_name starts with "ollama://"
    """
    return model_name.startswith("ollama://")


def parse_ollama_model_name(model_name: str) -> str:
    """
    Parse Ollama model name from prefixed string.

    Args:
        model_name: Model name with "ollama://" prefix

    Returns:
        Model name without prefix

    Example:
        >>> parse_ollama_model_name("ollama://llama3.2:3b")
        'llama3.2:3b'
    """
    return model_name.replace("ollama://", "")


# Convenience function for creating Ollama model/tokenizer pair
def load_ollama_model(
    model_name: str,
    base_url: str = "http://localhost:11434",
    timeout: int = 120,
    api_key: Optional[str] = None
) -> tuple:
    """
    Load Ollama model and tokenizer pair.

    Args:
        model_name: Model name (with or without "ollama://" prefix)
        base_url: Ollama server URL
        timeout: Request timeout in seconds
        api_key: Optional API key for cloud Ollama authentication

    Returns:
        Tuple of (OllamaModel, OllamaTokenizer)

    Example:
        >>> model, tokenizer = load_ollama_model("llama3.2:3b-instruct-q4_0")
        >>> # With cloud authentication:
        >>> model, tokenizer = load_ollama_model(
        ...     "deepseek-v3.1:671b-cloud",
        ...     api_key="your-api-key"
        ... )
    """
    # Strip prefix if present
    clean_name = parse_ollama_model_name(model_name) if is_ollama_model(model_name) else model_name

    model = OllamaModel(
        model_name=clean_name,
        base_url=base_url,
        timeout=timeout,
        api_key=api_key
    )
    tokenizer = OllamaTokenizer(model_name=clean_name)

    return model, tokenizer


__all__ = [
    "OllamaModel",
    "OllamaTokenizer",
    "OllamaPseudoTensor",
    "OllamaGeneratedOutput",
    "OllamaPseudoParameter",
    "OllamaConnectionError",
    "OllamaModelNotFoundError",
    "OllamaGenerationError",
    "is_ollama_model",
    "parse_ollama_model_name",
    "load_ollama_model",
]