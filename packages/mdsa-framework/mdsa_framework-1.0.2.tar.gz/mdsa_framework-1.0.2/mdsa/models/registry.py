"""
Model Registry Module

Tracks loaded models, their configurations, and usage statistics.
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from threading import Lock

from mdsa.models.config import ModelConfig

logger = logging.getLogger(__name__)


@dataclass
class ModelInfo:
    """
    Information about a loaded model.

    Attributes:
        model_id: Unique identifier for the model
        config: Model configuration
        model: The loaded model object
        tokenizer: The loaded tokenizer object (if applicable)
        load_time: Time when model was loaded
        last_used: Last access time
        use_count: Number of times model was accessed
        memory_mb: Estimated memory usage in MB
    """
    model_id: str
    config: ModelConfig
    model: Any
    tokenizer: Optional[Any] = None
    load_time: float = field(default_factory=time.time)
    last_used: float = field(default_factory=time.time)
    use_count: int = 0
    memory_mb: float = 0.0

    def mark_used(self):
        """Mark model as recently used."""
        self.last_used = time.time()
        self.use_count += 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (excluding actual model objects)."""
        return {
            'model_id': self.model_id,
            'config': self.config.to_dict(),
            'load_time': self.load_time,
            'last_used': self.last_used,
            'use_count': self.use_count,
            'memory_mb': self.memory_mb,
            'age_seconds': time.time() - self.load_time
        }


class ModelRegistry:
    """
    Registry for tracking loaded models.

    Thread-safe registry that maintains loaded models and their metadata.
    Supports model lookup, statistics, and cleanup.

    Example:
        >>> registry = ModelRegistry()
        >>> registry.register(model_id, config, model, tokenizer)
        >>> model_info = registry.get("tinybert")
        >>> stats = registry.get_stats()
    """

    def __init__(self, max_models: int = 2):
        """
        Initialize model registry.

        Args:
            max_models: Maximum number of models to keep loaded (default 2)
                       Reduced from 10 to prevent memory exhaustion:
                       - 10 × Phi-2 (5.4GB) = 54GB attempted allocation
                       - 2 × Phi-2 (INT8 ~3GB) = 6GB safe for 16GB RAM systems
        """
        self._models: Dict[str, ModelInfo] = {}
        self._lock = Lock()
        self.max_models = max_models
        logger.debug(f"ModelRegistry initialized (max_models={max_models})")

    def register(
        self,
        model_id: str,
        config: ModelConfig,
        model: Any,
        tokenizer: Optional[Any] = None,
        memory_mb: float = 0.0
    ) -> ModelInfo:
        """
        Register a loaded model.

        Args:
            model_id: Unique identifier for the model
            config: Model configuration
            model: Loaded model object
            tokenizer: Loaded tokenizer (optional)
            memory_mb: Estimated memory usage

        Returns:
            ModelInfo: Information about the registered model

        Raises:
            ValueError: If model_id already exists
        """
        with self._lock:
            if model_id in self._models:
                raise ValueError(f"Model '{model_id}' already registered")

            # Proactive eviction at 70% capacity (prevents hitting hard limit)
            if self.check_memory_pressure():
                logger.info("Proactive eviction triggered at 70% capacity")
                self._unload_least_recently_used()

            # Check if we need to unload old models (hard limit)
            if len(self._models) >= self.max_models:
                self._unload_least_recently_used()

            model_info = ModelInfo(
                model_id=model_id,
                config=config,
                model=model,
                tokenizer=tokenizer,
                memory_mb=memory_mb
            )

            self._models[model_id] = model_info
            logger.info(f"Model '{model_id}' registered ({memory_mb:.1f}MB)")

            return model_info

    def get(self, model_id: str) -> Optional[ModelInfo]:
        """
        Get model information by ID.

        Args:
            model_id: Model identifier

        Returns:
            ModelInfo if found, None otherwise
        """
        with self._lock:
            model_info = self._models.get(model_id)
            if model_info:
                model_info.mark_used()
            return model_info

    def is_loaded(self, model_id: str) -> bool:
        """
        Check if a model is loaded.

        Args:
            model_id: Model identifier

        Returns:
            bool: True if model is loaded
        """
        with self._lock:
            return model_id in self._models

    def check_memory_pressure(self) -> bool:
        """
        Check if registry is approaching memory limits.

        Proactively monitors registry capacity and warns when approaching
        the maximum model limit. This helps prevent hitting hard limits
        and enables early eviction strategies.

        Returns:
            bool: True if at 70%+ capacity threshold, False otherwise

        Note:
            This method does not acquire the lock - caller should hold it.
        """
        threshold = max(1, int(self.max_models * 0.7))  # 70% threshold
        current_count = len(self._models)

        if current_count >= threshold:
            logger.warning(
                f"Registry approaching capacity: {current_count}/{self.max_models} models loaded "
                f"(threshold: {threshold})"
            )
            return True
        return False

    def _cleanup_device_memory(self):
        """
        Clean up GPU memory after model unload.

        Calls torch.cuda.empty_cache() to free unused GPU memory.
        Safe to call even if CUDA is not available.
        """
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                logger.debug("CUDA cache cleared")
        except Exception as e:
            logger.debug(f"Could not clear CUDA cache: {e}")

    def unregister(self, model_id: str) -> bool:
        """
        Unregister and remove a model.

        Args:
            model_id: Model identifier

        Returns:
            bool: True if model was removed
        """
        with self._lock:
            if model_id in self._models:
                model_info = self._models.pop(model_id)
                logger.info(f"Model '{model_id}' unregistered")

                # Clear references to help garbage collection
                del model_info.model
                if model_info.tokenizer:
                    del model_info.tokenizer

                # Clean up GPU memory if applicable
                self._cleanup_device_memory()

                return True
            return False

    def _unload_least_recently_used(self):
        """
        Unload the least recently used model.

        Note: This is an internal method called from register() which already holds the lock.
        Do NOT call unregister() as it would try to acquire the lock again (deadlock).
        """
        if not self._models:
            return

        # Find LRU model
        lru_id = min(self._models.keys(), key=lambda k: self._models[k].last_used)
        logger.warning(
            f"Registry full ({self.max_models} models). Unloading LRU model: {lru_id}"
        )

        # Unregister without acquiring lock (we already have it)
        if lru_id in self._models:
            model_info = self._models.pop(lru_id)
            logger.info(f"Model '{lru_id}' unregistered (LRU eviction)")

            # Clear references to help garbage collection
            del model_info.model
            if model_info.tokenizer:
                del model_info.tokenizer

            # Clean up GPU memory if applicable
            self._cleanup_device_memory()

    def list_models(self) -> List[str]:
        """
        Get list of loaded model IDs.

        Returns:
            list: List of model IDs
        """
        with self._lock:
            return list(self._models.keys())

    def get_stats(self) -> Dict[str, Any]:
        """
        Get registry statistics.

        Returns:
            dict: Statistics including model count, memory usage, etc.
        """
        with self._lock:
            total_memory = sum(info.memory_mb for info in self._models.values())
            total_uses = sum(info.use_count for info in self._models.values())

            stats = {
                'models_loaded': len(self._models),
                'max_models': self.max_models,
                'total_memory_mb': total_memory,
                'total_uses': total_uses,
                'models': {
                    model_id: info.to_dict()
                    for model_id, info in self._models.items()
                }
            }

            return stats

    def clear(self):
        """Clear all models from registry."""
        with self._lock:
            model_ids = list(self._models.keys())
            for model_id in model_ids:
                self.unregister(model_id)
            logger.info("ModelRegistry cleared")

    def __len__(self) -> int:
        """Return number of loaded models."""
        return len(self._models)

    def __contains__(self, model_id: str) -> bool:
        """Check if model is in registry."""
        return model_id in self._models

    def __repr__(self) -> str:
        return f"<ModelRegistry loaded={len(self._models)} max={self.max_models}>"
