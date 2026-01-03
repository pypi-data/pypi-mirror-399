"""
Model Manager Module

High-level interface for model management with caching and optimization.
"""

import logging
from typing import Tuple, Optional, Any, Dict
from threading import Lock

from mdsa.models.config import ModelConfig
from mdsa.models.loader import ModelLoader
from mdsa.models.registry import ModelRegistry, ModelInfo

logger = logging.getLogger(__name__)


class ModelManager:
    """
    High-level model management interface.

    Combines ModelLoader and ModelRegistry to provide:
    - Cached model loading
    - Automatic model lifecycle management
    - Memory tracking
    - Thread-safe operations

    Example:
        >>> manager = ModelManager()
        >>> model, tokenizer = manager.get_or_load("tinybert", config)
        >>> stats = manager.get_stats()
    """

    def __init__(
        self,
        cache_dir: Optional[str] = None,
        max_models: int = 10
    ):
        """
        Initialize model manager.

        Args:
            cache_dir: Directory for model cache
            max_models: Maximum number of models to keep loaded
        """
        self.loader = ModelLoader(cache_dir=cache_dir)
        self.registry = ModelRegistry(max_models=max_models)
        self._load_lock = Lock()  # Prevents concurrent model loading (race condition fix)
        logger.info(f"ModelManager initialized (max_models={max_models})")

    def _check_memory_availability(
        self,
        estimated_mb: float,
        device: str = 'cpu'
    ) -> bool:
        """
        Check if sufficient memory available for model load.

        Performs hardware-specific memory validation:
        - For 16GB RAM systems: Accounts for 4-6GB OS/app usage, requires 1.5x safety margin
        - For RTX 3050 4GB VRAM: Requires 1.3x safety margin, keeps 4GB free for OS

        Args:
            estimated_mb: Estimated model memory usage in MB
            device: Device string ('cpu', 'cuda:0', etc.)

        Returns:
            bool: True if sufficient memory available, False otherwise
        """
        try:
            import psutil

            if device.startswith('cuda'):
                # GPU memory check
                try:
                    import torch
                except ImportError:
                    logger.warning("PyTorch not available, skipping GPU memory check")
                    return True

                if not torch.cuda.is_available():
                    logger.error("CUDA not available but GPU device requested")
                    return False

                gpu_id = int(device.split(':')[1]) if ':' in device else 0

                # Get GPU free memory
                torch.cuda.set_device(gpu_id)
                gpu_mem_free = torch.cuda.mem_get_info()[0] / (1024 ** 3)  # GB

                required_gb = (estimated_mb * 1.3) / 1024  # 1.3x safety for GPU

                if gpu_mem_free < required_gb:
                    logger.error(
                        f"Insufficient VRAM: {gpu_mem_free:.1f}GB free, "
                        f"{required_gb:.1f}GB required (with 1.3x margin)"
                    )
                    return False

                logger.info(
                    f"GPU memory check passed: {gpu_mem_free:.1f}GB free "
                    f"(need {required_gb:.1f}GB)"
                )
                return True
            else:
                # CPU memory check (16GB RAM system)
                mem = psutil.virtual_memory()
                available_gb = mem.available / (1024 ** 3)
                total_gb = mem.total / (1024 ** 3)

                required_gb = (estimated_mb * 1.5) / 1024  # 1.5x safety for CPU

                # For 16GB system: Warn if <6GB available (OS needs headroom)
                min_free_gb = 4.0  # Keep 4GB free for OS/apps

                if available_gb < required_gb:
                    logger.error(
                        f"Insufficient RAM: {available_gb:.1f}GB available "
                        f"({total_gb:.1f}GB total), "
                        f"{required_gb:.1f}GB required (with 1.5x margin)"
                    )
                    return False

                if available_gb - required_gb < min_free_gb:
                    logger.warning(
                        f"Tight memory: {available_gb:.1f}GB available, "
                        f"loading {required_gb:.1f}GB will leave "
                        f"{available_gb - required_gb:.1f}GB free "
                        f"(recommend {min_free_gb}GB minimum)"
                    )

                logger.info(
                    f"CPU memory check passed: {available_gb:.1f}GB available "
                    f"(need {required_gb:.1f}GB)"
                )
                return True

        except Exception as e:
            logger.warning(f"Memory check failed: {e}, proceeding anyway")
            return True  # Fail-open for backward compatibility

    def get_or_load(
        self,
        model_id: str,
        config: ModelConfig
    ) -> Tuple[Any, Any]:
        """
        Get model from registry or load if not present.

        Thread-safe implementation with memory validation and atomic get-or-load.
        Prevents:
        - Race conditions (duplicate model loads)
        - OOM errors (memory checks before loading)
        - System freezes (validates available memory)

        Args:
            model_id: Unique identifier for the model
            config: Model configuration

        Returns:
            tuple: (model, tokenizer)

        Raises:
            MemoryError: If insufficient memory for model loading

        Example:
            >>> model, tokenizer = manager.get_or_load("tinybert", config)
        """
        # First check (no lock) - fast path for cache hits
        model_info = self.registry.get(model_id)
        if model_info:
            logger.debug(f"Model '{model_id}' found in registry (cache hit)")
            return model_info.model, model_info.tokenizer

        # Acquire lock for loading (prevents race conditions)
        with self._load_lock:
            # Double-check after acquiring lock (another thread may have loaded)
            model_info = self.registry.get(model_id)
            if model_info:
                logger.debug(f"Model '{model_id}' loaded by another thread")
                return model_info.model, model_info.tokenizer

            # Estimate memory BEFORE loading
            memory_mb = self.loader.estimate_memory(config)

            # Check memory availability (prevents OOM)
            if not self._check_memory_availability(memory_mb, config.device):
                raise MemoryError(
                    f"Insufficient memory to load model '{model_id}' "
                    f"(estimated {memory_mb:.0f}MB on {config.device}). "
                    f"Free up memory or use smaller quantization."
                )

            # Load model (only one thread reaches here)
            logger.info(f"Loading model '{model_id}' (cache miss)")
            model, tokenizer = self.loader.load(config)

            # Register model
            self.registry.register(
                model_id=model_id,
                config=config,
                model=model,
                tokenizer=tokenizer,
                memory_mb=memory_mb
            )

            return model, tokenizer

    def is_loaded(self, model_id: str) -> bool:
        """
        Check if model is currently loaded.

        Args:
            model_id: Model identifier

        Returns:
            bool: True if model is loaded
        """
        return self.registry.is_loaded(model_id)

    def unload(self, model_id: str) -> bool:
        """
        Unload a model from memory.

        Args:
            model_id: Model identifier

        Returns:
            bool: True if model was unloaded
        """
        return self.registry.unregister(model_id)

    def get_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a loaded model.

        Args:
            model_id: Model identifier

        Returns:
            dict: Model information or None if not loaded
        """
        model_info = self.registry.get(model_id)
        return model_info.to_dict() if model_info else None

    def list_models(self) -> list:
        """
        Get list of currently loaded models.

        Returns:
            list: List of model IDs
        """
        return self.registry.list_models()

    def get_stats(self) -> Dict[str, Any]:
        """
        Get model management statistics.

        Returns:
            dict: Statistics including memory usage, model count, etc.
        """
        return self.registry.get_stats()

    def clear_all(self):
        """Clear all loaded models from memory."""
        self.registry.clear()
        logger.info("All models cleared from memory")

    def __repr__(self) -> str:
        loaded = len(self.registry)
        return f"<ModelManager loaded={loaded} max={self.registry.max_models}>"
