"""
MDSA Framework - Multi-Domain Small Language Model Agentic Orchestration Framework

A production-ready Python framework for orchestrating domain-specialized small language models.
"""

__version__ = "1.0.0"
__author__ = "MDSA Team"
__license__ = "Apache 2.0"

# Core imports (Phase 2 - Complete)
from mdsa.core.orchestrator import TinyBERTOrchestrator as MDSA
from mdsa.core import IntentRouter, StateMachine, WorkflowState, MessageBus

# Utils (Phase 2 - Complete)
from mdsa.utils import HardwareDetector, ConfigLoader, setup_logger

# Models (Phase 3 - Complete)
from mdsa.models import ModelManager, ModelConfig, QuantizationType, ModelTier

# Domains (Phase 4 - Complete)
from mdsa.domains import (
    DomainConfig,
    DomainRegistry,
    DomainExecutor,
    PromptBuilder,
    ResponseValidator,
    create_finance_domain,
    create_medical_domain,
    create_support_domain,
    create_technical_domain,
)

# Monitoring (Phase 5 - Complete)
from mdsa.monitoring import (
    MonitoringService,
    RequestMetric,
)

__all__ = [
    # Metadata
    "__version__",
    "__author__",
    "__license__",
    # Main Class
    "MDSA",
    # Core Components (Phase 2)
    "IntentRouter",
    "StateMachine",
    "WorkflowState",
    "MessageBus",
    # Utilities (Phase 2)
    "HardwareDetector",
    "ConfigLoader",
    "setup_logger",
    # Model Management (Phase 3)
    "ModelManager",
    "ModelConfig",
    "QuantizationType",
    "ModelTier",
    # Domain Execution (Phase 4)
    "DomainConfig",
    "DomainRegistry",
    "DomainExecutor",
    "PromptBuilder",
    "ResponseValidator",
    "create_finance_domain",
    "create_medical_domain",
    "create_support_domain",
    "create_technical_domain",
    # Monitoring & Logging (Phase 5)
    "MonitoringService",
    "RequestMetric",
]
