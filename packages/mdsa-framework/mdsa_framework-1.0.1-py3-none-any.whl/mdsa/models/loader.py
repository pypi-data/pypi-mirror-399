"""
Model Loader Module

Handles loading models with quantization, optimization, and caching.

Supports:
- HuggingFace models (default)
- Ollama models (prefix: "ollama://")
"""

import logging
import time
from pathlib import Path
from typing import Tuple, Optional, Any

from mdsa.models.config import ModelConfig, QuantizationType

logger = logging.getLogger(__name__)

# Check for Ollama adapter availability
try:
    from mdsa.integrations.adapters.ollama_adapter import (
        OllamaModel,
        OllamaTokenizer,
        is_ollama_model,
        parse_ollama_model_name
    )
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    is_ollama_model = lambda x: False  # Fallback: never detect Ollama
    logger.debug("Ollama adapter not available")

# Try to import torch and transformers
try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logger.warning("PyTorch/Transformers not available. Model loading disabled.")


class ModelLoader:
    """
    Loads and optimizes ML models with quantization support.

    Supports:
    - HuggingFace models
    - Local models
    - 4-bit and 8-bit quantization
    - Device placement optimization
    - Model caching

    Example:
        >>> loader = ModelLoader()
        >>> model, tokenizer = loader.load(config)
    """

    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize model loader.

        Args:
            cache_dir: Directory for caching downloaded models
        """
        self.cache_dir = cache_dir or str(Path.home() / ".mdsa" / "models")
        Path(self.cache_dir).mkdir(parents=True, exist_ok=True)
        logger.debug(f"ModelLoader initialized (cache_dir={self.cache_dir})")

    def load(self, config: ModelConfig) -> Tuple[Any, Any]:
        """
        Load model and tokenizer based on configuration.

        Supports:
        - HuggingFace models (default)
        - Ollama models (prefix: "ollama://")

        Args:
            config: Model configuration

        Returns:
            tuple: (model, tokenizer)

        Raises:
            RuntimeError: If required dependencies not available
            ValueError: If model cannot be loaded
        """
        start_time = time.time()
        logger.info(f"Loading model: {config.model_name}")

        try:
            # Check for Ollama model (prefix: "ollama://")
            if is_ollama_model(config.model_name):
                return self._load_ollama_model(config)

            # HuggingFace model loading requires PyTorch
            if not TORCH_AVAILABLE:
                raise RuntimeError("PyTorch/Transformers not available for HuggingFace models")

            # Load tokenizer
            tokenizer = self._load_tokenizer(config)

            # Load model with quantization
            model = self._load_model(config)

            # Move to device
            if config.quantization == QuantizationType.NONE:
                model = model.to(config.device)

            # Set to eval mode
            model.eval()

            elapsed = time.time() - start_time
            logger.info(f"Model loaded in {elapsed:.2f}s")

            return model, tokenizer

        except Exception as e:
            logger.error(f"Failed to load model {config.model_name}: {e}")
            raise ValueError(f"Model loading failed: {e}") from e

    def _load_ollama_model(self, config: ModelConfig) -> Tuple[Any, Any]:
        """
        Load Ollama model adapter.

        Args:
            config: Model configuration with "ollama://" prefix

        Returns:
            tuple: (OllamaModel, OllamaTokenizer)

        Raises:
            RuntimeError: If Ollama adapter not available
            ValueError: If Ollama connection fails
        """
        if not OLLAMA_AVAILABLE:
            raise RuntimeError(
                "Ollama adapter not available. "
                "Ensure mdsa.integrations.adapters.ollama_adapter is accessible."
            )

        # Parse model name (remove "ollama://" prefix)
        model_name = parse_ollama_model_name(config.model_name)

        # Get Ollama configuration from config kwargs
        base_url = config.kwargs.get('ollama_base_url', 'http://localhost:11434')
        timeout = config.kwargs.get('ollama_timeout', 120)

        logger.info(f"Loading Ollama model: {model_name} from {base_url}")

        try:
            # Create Ollama adapters
            model = OllamaModel(
                model_name=model_name,
                base_url=base_url,
                timeout=timeout
            )
            tokenizer = OllamaTokenizer(model_name=model_name)

            logger.info(f"Ollama model '{model_name}' loaded successfully")

            return model, tokenizer

        except Exception as e:
            logger.error(f"Failed to load Ollama model {model_name}: {e}")
            raise ValueError(f"Ollama model loading failed: {e}") from e

    def _load_tokenizer(self, config: ModelConfig) -> Any:
        """Load tokenizer for the model."""
        logger.debug(f"Loading tokenizer for {config.model_name}")

        tokenizer = AutoTokenizer.from_pretrained(
            config.model_name,
            cache_dir=config.cache_dir or self.cache_dir,
            trust_remote_code=config.trust_remote_code
        )

        return tokenizer

    def _load_model(self, config: ModelConfig) -> Any:
        """Load model with optional quantization and CPU optimization."""
        logger.debug(
            f"Loading model {config.model_name} "
            f"(quantization={config.quantization.value}, device={config.device})"
        )

        # Prepare loading arguments
        load_kwargs = {
            'cache_dir': config.cache_dir or self.cache_dir,
            'trust_remote_code': config.trust_remote_code,
        }

        # CPU-specific optimizations for Phi-2
        if config.device == "cpu":
            logger.info("Applying CPU-specific optimizations for Phi-2")
            # Use float32 for CPU (float16 not well-supported on CPU)
            if not config.torch_dtype:
                load_kwargs['torch_dtype'] = torch.float32
            # Memory-efficient loading on CPU
            load_kwargs['low_cpu_mem_usage'] = True
            # Enable KV cache for faster inference
            # (Note: use_cache is set during generation, not loading)
            logger.debug("CPU optimizations: torch_dtype=float32, low_cpu_mem_usage=True")

        # Add quantization config if needed
        if config.quantization in (QuantizationType.INT4, QuantizationType.INT8):
            load_kwargs['quantization_config'] = self._get_quantization_config(config)
            load_kwargs['device_map'] = 'auto'  # Required for quantization

        # Add dtype if specified (overrides CPU default)
        if config.torch_dtype:
            load_kwargs['torch_dtype'] = self._get_torch_dtype(config.torch_dtype)

        # Add custom kwargs
        load_kwargs.update(config.kwargs)

        # Load model (use AutoModelForCausalLM for text generation)
        model = AutoModelForCausalLM.from_pretrained(
            config.model_name,
            **load_kwargs
        )

        return model

    def _get_quantization_config(self, config: ModelConfig) -> Optional[Any]:
        """
        Get BitsAndBytes quantization configuration.

        Args:
            config: Model configuration

        Returns:
            BitsAndBytesConfig or None
        """
        if config.quantization == QuantizationType.INT4:
            return BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4"
            )
        elif config.quantization == QuantizationType.INT8:
            return BitsAndBytesConfig(
                load_in_8bit=True
            )
        return None

    def _get_torch_dtype(self, dtype_str: str) -> Any:
        """
        Convert dtype string to torch dtype.

        Args:
            dtype_str: Data type string (e.g., "float16", "bfloat16")

        Returns:
            torch dtype
        """
        dtype_map = {
            'float32': torch.float32,
            'float16': torch.float16,
            'bfloat16': torch.bfloat16,
            'int8': torch.int8,
        }

        return dtype_map.get(dtype_str, torch.float32)

    def estimate_memory(self, config: ModelConfig) -> float:
        """
        Estimate model memory usage in MB.

        Updated with accurate estimates for Phi-2 (2.7B params):
        - Float32: 5.4GB (model file) + overhead = ~6GB
        - INT8: ~3GB after quantization
        - INT4: ~1.5GB after quantization
        - Ollama: ~50MB (client-side only, server handles the model)

        Args:
            config: Model configuration

        Returns:
            float: Estimated memory in MB (includes 20% safety margin)
        """
        # Ollama models run on server - minimal client memory
        if is_ollama_model(config.model_name):
            return 50.0  # MB for adapter objects only

        # More accurate tier sizes based on actual models
        tier_sizes = {
            'tier1': 300,      # TinyBERT ~300MB
            'tier2': 6000,     # Phi-2 ~6GB (5.4GB + overhead) - UPDATED
            'tier3': 14000,    # Llama-2-7B ~14GB
        }

        # Handle both ModelConfig (with 'tier') and DomainConfig (with 'model_tier')
        tier = getattr(config, 'tier', None) or getattr(config, 'model_tier', None)
        base_size = tier_sizes.get(tier.value if tier else 'tier1', 1000)

        # Apply quantization reduction
        if config.quantization == QuantizationType.INT4:
            base_size *= 0.25  # 4-bit = 25% of original
        elif config.quantization == QuantizationType.INT8:
            base_size *= 0.5   # 8-bit = 50% of original
        elif config.quantization == QuantizationType.FP16:
            base_size *= 0.5   # FP16 = 50% of original
        elif config.quantization == QuantizationType.BFLOAT16:
            base_size *= 0.5   # BF16 = 50% of original

        # Add safety margin for inference activations (20%)
        base_size *= 1.2

        return base_size

    def __repr__(self) -> str:
        return f"<ModelLoader cache_dir={self.cache_dir}>"
