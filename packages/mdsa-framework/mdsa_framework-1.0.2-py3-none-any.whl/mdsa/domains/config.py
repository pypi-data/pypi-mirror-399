"""
Domain Configuration Module

Defines domain-specific settings, models, and execution parameters.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

from mdsa.models.config import ModelTier, QuantizationType
from mdsa.utils.device_config import DeviceStrategy


@dataclass
class DomainConfig:
    """
    Configuration for a domain-specific SLM.

    Defines the model, prompts, and execution settings for a specific domain.
    """

    # Domain identification
    domain_id: str
    name: str
    description: str
    keywords: List[str] = field(default_factory=list)

    # Model configuration
    model_name: str = "gpt2"  # Default to small model for testing
    model_tier: ModelTier = ModelTier.TIER3
    quantization: QuantizationType = QuantizationType.NONE  # Default to no quant for testing
    device: str = "auto"  # Will be auto-detected based on hardware availability

    # Prompt configuration
    system_prompt: str = ""
    prompt_template: str = "{query}"
    max_tokens: int = 512
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 50

    # Execution settings
    timeout_seconds: int = 30
    max_retries: int = 2
    batch_size: int = 1

    # Validation settings
    min_response_length: int = 10
    max_response_length: int = 2048
    check_toxicity: bool = False  # Requires additional package
    use_model_validation: bool = False  # Enable Phi-2 semantic validation (Tier 2)

    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate configuration after initialization."""
        if not self.domain_id:
            raise ValueError("domain_id cannot be empty")
        if not self.name:
            raise ValueError("name cannot be empty")
        if not self.model_name:
            raise ValueError("model_name cannot be empty")
        if self.max_tokens <= 0:
            raise ValueError("max_tokens must be positive")
        if not 0.0 <= self.temperature <= 2.0:
            raise ValueError("temperature must be between 0 and 2")

        # Auto-detect device if set to "auto"
        if self.device == "auto":
            self.device = self._auto_detect_device()

    def _auto_detect_device(self) -> str:
        """Auto-detect best available device based on model tier and hardware."""
        try:
            # Use DeviceStrategy for smart device selection
            device, _ = DeviceStrategy.select_for_phi2(prefer_gpu=True)
            return device
        except Exception:
            # Fallback: try HardwareDetector directly
            try:
                from mdsa.utils.hardware import HardwareDetector
                hw = HardwareDetector()
                if self.model_tier == ModelTier.TIER1:
                    return hw.best_device_for_tier1()
                elif self.model_tier == ModelTier.TIER2:
                    return hw.best_device_for_tier2()
                else:
                    return hw.best_device_for_tier3()
            except Exception:
                return "cpu"

    def __repr__(self) -> str:
        return (
            f"<DomainConfig {self.domain_id} "
            f"model={self.model_name} "
            f"tier={self.model_tier.value} "
            f"quant={self.quantization.value}>"
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert DomainConfig to dictionary."""
        return {
            'domain_id': self.domain_id,
            'name': self.name,
            'description': self.description,
            'keywords': self.keywords,
            'model_name': self.model_name,
            'model_tier': self.model_tier.value,
            'quantization': self.quantization.value,
            'device': self.device,
            'system_prompt': self.system_prompt,
            'prompt_template': self.prompt_template,
            'max_tokens': self.max_tokens,
            'temperature': self.temperature,
            'top_p': self.top_p,
            'top_k': self.top_k,
            'timeout_seconds': self.timeout_seconds,
            'max_retries': self.max_retries,
            'batch_size': self.batch_size,
            'min_response_length': self.min_response_length,
            'max_response_length': self.max_response_length,
            'check_toxicity': self.check_toxicity,
            'use_model_validation': self.use_model_validation,
            'metadata': self.metadata,
        }


#
# Predefined Domain Configurations
#

def create_finance_domain(
    prefer_gpu: bool = True,
    force_device: Optional[str] = None
) -> DomainConfig:
    """
    Create configuration for finance domain with smart device selection.

    Args:
        prefer_gpu: Prefer GPU if available (default True)
        force_device: Force specific device ('cpu', 'cuda:0', etc.)

    Returns:
        DomainConfig with optimized device and quantization settings
    """
    # Import here to avoid circular dependency
    from mdsa.domains.prompts import get_enhanced_prompt

    # Smart device selection based on available hardware
    device, quantization = DeviceStrategy.select_for_phi2(prefer_gpu, force_device)

    return DomainConfig(
        domain_id="finance",
        name="Financial Services",
        description="Banking, transactions, payments, and financial queries",
        keywords=[
            "money", "transfer", "payment", "balance", "account",
            "transaction", "deposit", "withdraw", "bank", "finance",
            "credit", "debit", "loan", "interest", "investment"
        ],
        model_name="microsoft/phi-2",
        model_tier=ModelTier.TIER2,
        device=device,  # Smart selection (GPU or CPU)
        quantization=quantization,  # Smart quantization (INT8 or INT4)
        system_prompt=get_enhanced_prompt("finance"),
        prompt_template="{query}",
        max_tokens=256,
        temperature=0.3,
    )


def create_medical_domain(
    prefer_gpu: bool = True,
    force_device: Optional[str] = None
) -> DomainConfig:
    """
    Create configuration for medical domain with smart device selection.

    Args:
        prefer_gpu: Prefer GPU if available (default True)
        force_device: Force specific device ('cpu', 'cuda:0', etc.)

    Returns:
        DomainConfig with optimized device and quantization settings
    """
    # Import here to avoid circular dependency
    from mdsa.domains.prompts import get_enhanced_prompt

    # Smart device selection based on available hardware
    device, quantization = DeviceStrategy.select_for_phi2(prefer_gpu, force_device)

    return DomainConfig(
        domain_id="medical",
        name="Medical Information",
        description="Health, symptoms, and medical guidance",
        keywords=[
            "health", "symptom", "doctor", "medicine", "pain",
            "fever", "illness", "disease", "treatment", "hospital",
            "diagnosis", "prescription", "medical", "sick", "hurt"
        ],
        model_name="microsoft/phi-2",
        model_tier=ModelTier.TIER2,
        device=device,  # Smart selection (GPU or CPU)
        quantization=quantization,  # Smart quantization (INT8 or INT4)
        system_prompt=get_enhanced_prompt("medical"),
        prompt_template="{query}",
        max_tokens=256,
        temperature=0.3,
    )


def create_support_domain(
    prefer_gpu: bool = True,
    force_device: Optional[str] = None
) -> DomainConfig:
    """
    Create configuration for customer support domain with smart device selection.

    Args:
        prefer_gpu: Prefer GPU if available (default True)
        force_device: Force specific device ('cpu', 'cuda:0', etc.)

    Returns:
        DomainConfig with optimized device and quantization settings
    """
    # Import here to avoid circular dependency
    from mdsa.domains.prompts import get_enhanced_prompt

    # Smart device selection based on available hardware
    device, quantization = DeviceStrategy.select_for_phi2(prefer_gpu, force_device)

    return DomainConfig(
        domain_id="support",
        name="Customer Support",
        description="General customer service and support queries",
        keywords=[
            "help", "support", "issue", "problem", "question",
            "how", "what", "why", "when", "where",
            "cancel", "refund", "return", "order", "service"
        ],
        model_name="microsoft/phi-2",
        model_tier=ModelTier.TIER2,
        device=device,  # Smart selection (GPU or CPU)
        quantization=quantization,  # Smart quantization (INT8 or INT4)
        system_prompt=get_enhanced_prompt("support"),
        prompt_template="{query}",
        max_tokens=256,
        temperature=0.3,
    )


def create_technical_domain(
    prefer_gpu: bool = True,
    force_device: Optional[str] = None
) -> DomainConfig:
    """
    Create configuration for technical support domain with smart device selection.

    Args:
        prefer_gpu: Prefer GPU if available (default True)
        force_device: Force specific device ('cpu', 'cuda:0', etc.)

    Returns:
        DomainConfig with optimized device and quantization settings
    """
    # Import here to avoid circular dependency
    from mdsa.domains.prompts import get_enhanced_prompt

    # Smart device selection based on available hardware
    device, quantization = DeviceStrategy.select_for_phi2(prefer_gpu, force_device)

    return DomainConfig(
        domain_id="technical",
        name="Technical Support",
        description="IT support, troubleshooting, and technical queries",
        keywords=[
            "error", "bug", "crash", "install", "update",
            "software", "hardware", "computer", "app", "program",
            "troubleshoot", "fix", "configure", "setup", "technical"
        ],
        model_name="microsoft/phi-2",
        model_tier=ModelTier.TIER2,
        device=device,  # Smart selection (GPU or CPU)
        quantization=quantization,  # Smart quantization (INT8 or INT4)
        system_prompt=get_enhanced_prompt("technical"),
        prompt_template="{query}",
        max_tokens=256,
        temperature=0.3,
    )


# Registry of predefined domains
PREDEFINED_DOMAINS = {
    "finance": create_finance_domain,
    "medical": create_medical_domain,
    "support": create_support_domain,
    "technical": create_technical_domain,
}


def get_predefined_domain(
    domain_id: str,
    prefer_gpu: bool = True,
    force_device: Optional[str] = None
) -> Optional[DomainConfig]:
    """
    Get a predefined domain configuration by ID with smart device selection.

    Args:
        domain_id: Domain identifier
        prefer_gpu: Prefer GPU if available (default True)
        force_device: Force specific device ('cpu', 'cuda:0', None)

    Returns:
        DomainConfig if found, None otherwise

    Examples:
        # Auto-detect (uses GPU if RTX 3050 available)
        >>> config = get_predefined_domain('finance')

        # Force CPU (for CPU-only projects)
        >>> config = get_predefined_domain('finance', force_device='cpu')

        # Force GPU (for GPU-accelerated projects)
        >>> config = get_predefined_domain('finance', force_device='cuda:0')

        # Prefer CPU even if GPU available
        >>> config = get_predefined_domain('finance', prefer_gpu=False)
    """
    creator = PREDEFINED_DOMAINS.get(domain_id)
    return creator(prefer_gpu=prefer_gpu, force_device=force_device) if creator else None


def list_predefined_domains() -> List[str]:
    """
    Get list of available predefined domains.

    Returns:
        List of domain IDs
    """
    return list(PREDEFINED_DOMAINS.keys())
