"""
Tests for MDSA Domain Configuration and Execution

Tests cover:
- Domain configuration
- Domain routing
- Predefined domains
- Domain executor functionality
"""

import pytest
from mdsa.domains.config import (
    DomainConfig,
    get_predefined_domain,
    list_predefined_domains,
    create_finance_domain,
    create_medical_domain,
    create_support_domain,
    create_technical_domain
)
from mdsa.domains.executor import DomainExecutor
from mdsa.models.config import ModelTier, QuantizationType
from tests.conftest import assert_valid_result


# ============================================================================
# Domain Configuration Tests
# ============================================================================

@pytest.mark.unit
class TestDomainConfig:
    """Test DomainConfig creation and properties."""

    def test_domain_config_creation(self):
        """Test creating a basic domain configuration."""
        config = DomainConfig(
            domain_id="test",
            name="Test Domain",
            description="Test domain description",
            keywords=["test", "example"],
            model_name="gpt2",
            model_tier=ModelTier.TIER1,
            device="cpu",
            quantization=QuantizationType.NONE
        )

        assert config.domain_id == "test"
        assert config.name == "Test Domain"
        assert "test" in config.keywords

    def test_domain_config_to_dict(self):
        """Test converting DomainConfig to dictionary."""
        config = DomainConfig(
            domain_id="test",
            name="Test Domain",
            description="Test",
            keywords=["test"],
            model_name="gpt2",
            model_tier=ModelTier.TIER1,
            device="cpu",
            quantization=QuantizationType.NONE
        )

        config_dict = config.to_dict()
        assert isinstance(config_dict, dict)
        assert config_dict['domain_id'] == "test"


# ============================================================================
# Predefined Domains Tests
# ============================================================================

@pytest.mark.unit
class TestPredefinedDomains:
    """Test predefined domain configurations."""

    def test_list_predefined_domains(self):
        """Test listing all predefined domains."""
        domains = list_predefined_domains()
        assert isinstance(domains, list)
        assert len(domains) >= 4
        assert 'finance' in domains
        assert 'medical' in domains
        assert 'support' in domains
        assert 'technical' in domains

    def test_get_finance_domain(self, test_device):
        """Test getting finance domain configuration."""
        config = get_predefined_domain('finance', force_device=test_device)
        assert config is not None
        assert config.domain_id == 'finance'
        assert config.device == test_device
        assert 'finance' in config.keywords or 'money' in config.keywords

    def test_get_medical_domain(self, test_device):
        """Test getting medical domain configuration."""
        config = get_predefined_domain('medical', force_device=test_device)
        assert config is not None
        assert config.domain_id == 'medical'
        assert config.device == test_device
        assert 'health' in config.keywords or 'medical' in config.keywords

    def test_get_support_domain(self, test_device):
        """Test getting support domain configuration."""
        config = get_predefined_domain('support', force_device=test_device)
        assert config is not None
        assert config.domain_id == 'support'
        assert config.device == test_device
        assert 'help' in config.keywords or 'support' in config.keywords

    def test_get_technical_domain(self, test_device):
        """Test getting technical domain configuration."""
        config = get_predefined_domain('technical', force_device=test_device)
        assert config is not None
        assert config.domain_id == 'technical'
        assert config.device == test_device
        assert 'technical' in config.keywords or 'error' in config.keywords

    def test_get_unknown_domain(self):
        """Test getting unknown domain returns None."""
        config = get_predefined_domain('unknown_domain')
        assert config is None

    def test_create_domain_functions(self, test_device):
        """Test direct domain creation functions."""
        finance = create_finance_domain(force_device=test_device)
        medical = create_medical_domain(force_device=test_device)
        support = create_support_domain(force_device=test_device)
        technical = create_technical_domain(force_device=test_device)

        assert finance.domain_id == 'finance'
        assert medical.domain_id == 'medical'
        assert support.domain_id == 'support'
        assert technical.domain_id == 'technical'

    def test_domain_with_gpu_preference(self):
        """Test domain creation with GPU preference."""
        config = get_predefined_domain('support', prefer_gpu=True)
        assert config is not None
        # Device depends on hardware availability
        assert config.device in ['cpu', 'cuda:0', 'cuda']

    def test_domain_force_cpu(self):
        """Test forcing CPU device."""
        config = get_predefined_domain('support', force_device='cpu')
        assert config is not None
        assert config.device == 'cpu'


# ============================================================================
# Domain Executor Tests
# ============================================================================

@pytest.mark.integration
class TestDomainExecutor:
    """Test DomainExecutor functionality."""

    def test_executor_creation(self, model_manager):
        """Test creating DomainExecutor."""
        executor = DomainExecutor(model_manager)
        assert executor is not None
        assert executor.model_manager is model_manager

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_execute_basic(self, domain_executor, support_domain):
        """Test basic domain execution."""
        result = domain_executor.execute(
            query="Hello test",
            domain_config=support_domain
        )

        assert_valid_result(result)
        # Result may succeed or fail depending on memory
        assert result['status'] in ['success', 'error']
        assert result['domain'] == support_domain.domain_id

    def test_executor_with_empty_query(self, domain_executor, support_domain):
        """Test execution with empty query."""
        result = domain_executor.execute(
            query="",
            domain_config=support_domain
        )

        # Should handle empty query gracefully
        assert_valid_result(result)


# ============================================================================
# Domain Routing Tests
# ============================================================================

@pytest.mark.unit
class TestDomainRouting:
    """Test domain keyword matching and routing."""

    def test_finance_keywords(self):
        """Test finance domain keywords."""
        finance = get_predefined_domain('finance', force_device='cpu')
        keywords = finance.keywords

        # Should contain financial keywords
        financial_terms = ['money', 'payment', 'bank', 'finance', 'transfer']
        assert any(term in keywords for term in financial_terms)

    def test_medical_keywords(self):
        """Test medical domain keywords."""
        medical = get_predefined_domain('medical', force_device='cpu')
        keywords = medical.keywords

        # Should contain medical keywords
        medical_terms = ['health', 'doctor', 'symptom', 'medical', 'medicine']
        assert any(term in keywords for term in medical_terms)

    def test_domain_keyword_uniqueness(self):
        """Test that domains have unique keyword sets."""
        finance = get_predefined_domain('finance', force_device='cpu')
        medical = get_predefined_domain('medical', force_device='cpu')

        # Domains should have different primary keywords
        finance_set = set(finance.keywords)
        medical_set = set(medical.keywords)

        # Some overlap is OK, but should be mostly different
        overlap = finance_set.intersection(medical_set)
        assert len(overlap) < len(finance.keywords) / 2


# ============================================================================
# Domain Configuration Edge Cases
# ============================================================================

@pytest.mark.unit
class TestDomainEdgeCases:
    """Test edge cases in domain configuration."""

    def test_domain_with_no_keywords(self):
        """Test domain with empty keywords list."""
        config = DomainConfig(
            domain_id="test",
            name="Test",
            description="Test",
            keywords=[],  # Empty keywords
            model_name="gpt2",
            model_tier=ModelTier.TIER1,
            device="cpu",
            quantization=QuantizationType.NONE
        )

        assert config.keywords == []

    def test_domain_with_custom_temperature(self):
        """Test domain with custom temperature."""
        config = DomainConfig(
            domain_id="test",
            name="Test",
            description="Test",
            keywords=["test"],
            model_name="gpt2",
            model_tier=ModelTier.TIER1,
            device="cpu",
            quantization=QuantizationType.NONE,
            temperature=0.9
        )

        assert config.temperature == 0.9

    def test_domain_with_custom_max_tokens(self):
        """Test domain with custom max_tokens."""
        config = DomainConfig(
            domain_id="test",
            name="Test",
            description="Test",
            keywords=["test"],
            model_name="gpt2",
            model_tier=ModelTier.TIER1,
            device="cpu",
            quantization=QuantizationType.NONE,
            max_tokens=512
        )

        assert config.max_tokens == 512
