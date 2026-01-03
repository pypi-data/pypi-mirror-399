"""
Model Configuration Module

Defines configuration structures for model loading, quantization, and optimization.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional


class QuantizationType(Enum):
    """Supported quantization types for model compression."""
    NONE = "none"
    INT8 = "int8"
    INT4 = "int4"
    FP16 = "fp16"
    BFLOAT16 = "bfloat16"


class ModelTier(Enum):
    """Model tiers in MDSA architecture."""
    TIER1 = "tier1"  # TinyBERT (67M params, CPU, <50ms)
    TIER2 = "tier2"  # Phi-1.5 (1.3B params, optional)
    TIER3 = "tier3"  # Domain SLMs (7-13B params, GPU/CPU)


@dataclass
class ModelConfig:
    """
    Configuration for loading and managing ML models.

    Attributes:
        model_name: HuggingFace model name or local path
        tier: Model tier (tier1, tier2, tier3)
        device: Target device (cpu, cuda, mps, etc.)
        quantization: Quantization type
        max_length: Maximum sequence length
        batch_size: Batch size for inference
        temperature: Sampling temperature (0.0-2.0)
        use_cache: Whether to cache model outputs
        trust_remote_code: Allow remote code execution
        torch_dtype: PyTorch data type
        compile_model: Whether to use torch.compile
        optimization_level: Optimization level (0-3)
        cache_dir: Directory for model cache
        kwargs: Additional model-specific arguments
    """
    model_name: str
    tier: ModelTier
    device: str = "auto"  # Will be auto-detected based on hardware availability
    quantization: QuantizationType = QuantizationType.NONE
    max_length: int = 512
    batch_size: int = 1
    temperature: float = 0.7
    use_cache: bool = True
    trust_remote_code: bool = False
    torch_dtype: Optional[str] = None
    compile_model: bool = False
    optimization_level: int = 1
    cache_dir: Optional[str] = None
    kwargs: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate configuration after initialization."""
        # Convert string tier to enum if needed
        if isinstance(self.tier, str):
            self.tier = ModelTier(self.tier)

        # Convert string quantization to enum if needed
        if isinstance(self.quantization, str):
            self.quantization = QuantizationType(self.quantization)

        # Auto-detect device if set to "auto"
        if self.device == "auto":
            self.device = self._auto_detect_device()

        # Validate max_length
        if self.max_length <= 0:
            raise ValueError(f"max_length must be positive, got {self.max_length}")

        # Validate batch_size
        if self.batch_size <= 0:
            raise ValueError(f"batch_size must be positive, got {self.batch_size}")

    def _auto_detect_device(self) -> str:
        """Auto-detect best available device based on tier and hardware."""
        try:
            from mdsa.utils.hardware import HardwareDetector
            hw = HardwareDetector()

            # Get best device based on model tier
            if self.tier == ModelTier.TIER1:
                return hw.best_device_for_tier1()  # Typically CPU for low latency
            elif self.tier == ModelTier.TIER2:
                return hw.best_device_for_tier2()  # GPU if available, else CPU
            else:  # TIER3
                return hw.best_device_for_tier3()  # Prefer GPU for large models
        except Exception:
            # Fallback to CPU if hardware detection fails
            return "cpu"

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            'model_name': self.model_name,
            'tier': self.tier.value,
            'device': self.device,
            'quantization': self.quantization.value,
            'max_length': self.max_length,
            'batch_size': self.batch_size,
            'temperature': self.temperature,
            'use_cache': self.use_cache,
            'trust_remote_code': self.trust_remote_code,
            'torch_dtype': self.torch_dtype,
            'compile_model': self.compile_model,
            'optimization_level': self.optimization_level,
            'cache_dir': self.cache_dir,
            'kwargs': self.kwargs
        }

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'ModelConfig':
        """Create config from dictionary."""
        return cls(**config_dict)

    @classmethod
    def for_tier1(cls, model_name: str = "huawei-noah/TinyBERT_General_6L_768D", **kwargs) -> 'ModelConfig':
        """Create Tier 1 (TinyBERT) configuration."""
        return cls(
            model_name=model_name,
            tier=ModelTier.TIER1,
            device="cpu",  # Always CPU for <50ms latency
            max_length=128,
            quantization=QuantizationType.NONE,  # Not needed for CPU inference
            **kwargs
        )

    @classmethod
    def for_tier2(cls, model_name: str = "microsoft/phi-1_5", device: str = "auto", **kwargs) -> 'ModelConfig':
        """Create Tier 2 (Phi) configuration."""
        return cls(
            model_name=model_name,
            tier=ModelTier.TIER2,
            device=device,
            max_length=512,
            quantization=QuantizationType.INT8,  # 8-bit for memory efficiency
            **kwargs
        )

    @classmethod
    def for_tier3(cls, model_name: str, device: str = "auto", **kwargs) -> 'ModelConfig':
        """Create Tier 3 (Domain SLM) configuration."""
        return cls(
            model_name=model_name,
            tier=ModelTier.TIER3,
            device=device,
            max_length=2048,
            quantization=QuantizationType.INT4,  # 4-bit for large models
            **kwargs
        )

    def __repr__(self) -> str:
        return (
            f"<ModelConfig {self.model_name} tier={self.tier.value} "
            f"device={self.device} quant={self.quantization.value}>"
        )


# Predefined configurations for common models
TIER1_TINYBERT = ModelConfig.for_tier1()
TIER2_PHI = ModelConfig.for_tier2()
