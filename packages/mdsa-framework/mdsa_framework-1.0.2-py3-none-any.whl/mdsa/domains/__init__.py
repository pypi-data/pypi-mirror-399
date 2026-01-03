"""
MDSA Domain Management Module

Contains domain creation, registration, and management functionality.
"""

from mdsa.domains.config import (
    DomainConfig,
    create_finance_domain,
    create_medical_domain,
    create_support_domain,
    create_technical_domain,
    get_predefined_domain,
    list_predefined_domains,
    PREDEFINED_DOMAINS
)
from mdsa.domains.registry import DomainRegistry
from mdsa.domains.prompts import PromptBuilder
from mdsa.domains.validator import ResponseValidator
from mdsa.domains.executor import DomainExecutor

__all__ = [
    # Domain Configuration
    "DomainConfig",
    "create_finance_domain",
    "create_medical_domain",
    "create_support_domain",
    "create_technical_domain",
    "get_predefined_domain",
    "list_predefined_domains",
    "PREDEFINED_DOMAINS",
    # Domain Management
    "DomainRegistry",
    "PromptBuilder",
    "ResponseValidator",
    "DomainExecutor",
]
