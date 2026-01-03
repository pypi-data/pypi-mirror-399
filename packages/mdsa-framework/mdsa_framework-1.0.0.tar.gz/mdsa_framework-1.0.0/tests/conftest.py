"""
Pytest Configuration and Shared Fixtures for MDSA Test Suite

Provides reusable fixtures for testing MDSA framework components.
"""

import pytest
import pytest_asyncio
import asyncio
import logging
from typing import Dict, Any
from mdsa.models.config import ModelConfig, ModelTier, QuantizationType
from mdsa.domains.config import DomainConfig, get_predefined_domain
from mdsa.models.manager import ModelManager
from mdsa.domains.executor import DomainExecutor
from mdsa.async_.executor import AsyncExecutor
from mdsa.async_.manager import AsyncManager
from mdsa.utils.device_config import get_recommended_config

# Configure logging for tests
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


# ============================================================================
# Hardware Configuration Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def hardware_config() -> Dict[str, Any]:
    """Get hardware configuration for current system."""
    return get_recommended_config(prefer_gpu=True)


@pytest.fixture(scope="session")
def test_device(hardware_config) -> str:
    """Get device to use for testing (CPU or GPU)."""
    return hardware_config['device']


@pytest.fixture(scope="session")
def test_quantization(hardware_config) -> QuantizationType:
    """Get quantization type to use for testing."""
    return hardware_config['quantization']


# ============================================================================
# Model Configuration Fixtures
# ============================================================================

@pytest.fixture
def tiny_model_config(test_device, test_quantization) -> ModelConfig:
    """Create configuration for tiny test model (GPT-2)."""
    return ModelConfig(
        model_name="gpt2",
        tier=ModelTier.TIER1,
        device=test_device,
        quantization=test_quantization,
        max_length=50,
        temperature=0.7
    )


@pytest.fixture
def phi2_model_config(test_device, test_quantization) -> ModelConfig:
    """Create configuration for Phi-2 model."""
    return ModelConfig(
        model_name="microsoft/phi-2",
        tier=ModelTier.TIER2,
        device=test_device,
        quantization=test_quantization,
        max_length=128,
        temperature=0.3
    )


# ============================================================================
# Domain Configuration Fixtures
# ============================================================================

@pytest.fixture
def support_domain(test_device) -> DomainConfig:
    """Create support domain configuration."""
    return get_predefined_domain('support', force_device=test_device)


@pytest.fixture
def finance_domain(test_device) -> DomainConfig:
    """Create finance domain configuration."""
    return get_predefined_domain('finance', force_device=test_device)


@pytest.fixture
def medical_domain(test_device) -> DomainConfig:
    """Create medical domain configuration."""
    return get_predefined_domain('medical', force_device=test_device)


@pytest.fixture
def technical_domain(test_device) -> DomainConfig:
    """Create technical domain configuration."""
    return get_predefined_domain('technical', force_device=test_device)


@pytest.fixture
def all_domains(support_domain, finance_domain, medical_domain, technical_domain):
    """Get all predefined domains."""
    return [support_domain, finance_domain, medical_domain, technical_domain]


# ============================================================================
# Component Fixtures (Function Scope - Fresh for Each Test)
# ============================================================================

@pytest.fixture
def model_manager(hardware_config):
    """Create fresh ModelManager for each test."""
    return ModelManager(max_models=hardware_config['max_models'])


@pytest.fixture
def domain_executor(model_manager):
    """Create DomainExecutor with fresh ModelManager."""
    return DomainExecutor(model_manager)


@pytest_asyncio.fixture
async def async_executor(domain_executor, hardware_config):
    """Create AsyncExecutor with cleanup."""
    executor = AsyncExecutor(
        domain_executor,
        max_workers=hardware_config['max_workers']
    )
    yield executor
    # Cleanup
    await executor.shutdown_async()


@pytest_asyncio.fixture
async def async_manager(async_executor):
    """Create AsyncManager with cleanup."""
    manager = AsyncManager(async_executor, max_concurrent=5)
    yield manager
    # Cleanup
    await manager.shutdown()


# ============================================================================
# Test Data Fixtures
# ============================================================================

@pytest.fixture
def sample_queries():
    """Sample queries for testing."""
    return [
        "What is the weather today?",
        "How do I transfer money?",
        "What are the symptoms of flu?",
        "How do I fix my computer?",
        "Can you help me with my account?"
    ]


@pytest.fixture
def batch_queries():
    """Batch of queries for concurrent testing."""
    return [
        "Query 1: Test question",
        "Query 2: Another test",
        "Query 3: Third query",
        "Query 4: Fourth question",
        "Query 5: Fifth query",
    ]


# ============================================================================
# Markers and Configuration
# ============================================================================

def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "unit: Unit tests (fast, isolated)"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests (slower, multiple components)"
    )
    config.addinivalue_line(
        "markers", "e2e: End-to-end tests (slowest, full system)"
    )
    config.addinivalue_line(
        "markers", "slow: Tests that take a long time to run"
    )
    config.addinivalue_line(
        "markers", "gpu: Tests that require GPU"
    )
    config.addinivalue_line(
        "markers", "memory: Tests that stress memory usage"
    )


# ============================================================================
# Event Loop Configuration (for async tests)
# ============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# Helper Functions
# ============================================================================

def assert_valid_result(result: Dict[str, Any]):
    """Assert that a result dictionary is valid."""
    assert result is not None, "Result should not be None"
    assert isinstance(result, dict), "Result should be a dictionary"
    assert 'status' in result, "Result should have 'status' key"
    assert 'response' in result, "Result should have 'response' key"
    assert 'latency_ms' in result, "Result should have 'latency_ms' key"
    assert 'domain' in result, "Result should have 'domain' key"
    assert 'model' in result, "Result should have 'model' key"


def assert_success_result(result: Dict[str, Any]):
    """Assert that a result indicates success."""
    assert_valid_result(result)
    assert result['status'] == 'success', f"Expected success, got {result['status']}: {result.get('error', '')}"
    assert result['response'], "Response should not be empty"
    assert result['latency_ms'] > 0, "Latency should be positive"


# Export helper functions
__all__ = ['assert_valid_result', 'assert_success_result']
