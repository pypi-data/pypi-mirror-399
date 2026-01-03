"""
Tests for MDSA Model Loading and Management

Tests cover:
- Model configuration
- Model loading and caching
- Model registry
- Memory management
- Device selection
"""

import pytest
from mdsa.models.config import ModelConfig, ModelTier, QuantizationType
from mdsa.models.loader import ModelLoader
from mdsa.models.registry import ModelRegistry, ModelInfo
from mdsa.models.manager import ModelManager


# ============================================================================
# Model Configuration Tests
# ============================================================================

@pytest.mark.unit
class TestModelConfig:
    """Test ModelConfig creation and validation."""

    def test_model_config_creation(self):
        """Test creating a basic model configuration."""
        config = ModelConfig(
            model_name="gpt2",
            tier=ModelTier.TIER1,
            device="cpu",
            quantization=QuantizationType.NONE
        )
        assert config.model_name == "gpt2"
        assert config.tier == ModelTier.TIER1
        assert config.device == "cpu"
        assert config.quantization == QuantizationType.NONE

    def test_model_config_to_dict(self):
        """Test converting ModelConfig to dictionary."""
        config = ModelConfig(
            model_name="gpt2",
            tier=ModelTier.TIER1,
            device="cpu",
            quantization=QuantizationType.NONE
        )
        config_dict = config.to_dict()
        assert isinstance(config_dict, dict)
        assert config_dict['model_name'] == "gpt2"
        assert config_dict['tier'] == "tier1"

    def test_quantization_types(self):
        """Test different quantization types."""
        quantizations = [
            QuantizationType.NONE,
            QuantizationType.INT4,
            QuantizationType.INT8,
            QuantizationType.FP16,
            QuantizationType.BFLOAT16
        ]
        for quant in quantizations:
            config = ModelConfig(
                model_name="test",
                tier=ModelTier.TIER1,
                device="cpu",
                quantization=quant
            )
            assert config.quantization == quant


# ============================================================================
# Model Loader Tests
# ============================================================================

@pytest.mark.unit
class TestModelLoader:
    """Test ModelLoader functionality."""

    def test_loader_creation(self):
        """Test creating ModelLoader instance."""
        loader = ModelLoader()
        assert loader is not None

    def test_estimate_memory(self, tiny_model_config):
        """Test memory estimation for models."""
        loader = ModelLoader()
        estimated_mb = loader.estimate_memory(tiny_model_config)
        assert estimated_mb > 0
        assert estimated_mb < 10000  # Should be reasonable

    def test_estimate_memory_with_quantization(self):
        """Test memory estimation with different quantizations."""
        loader = ModelLoader()

        # FP32 (no quantization)
        config_fp32 = ModelConfig(
            model_name="gpt2",
            tier=ModelTier.TIER1,
            device="cpu",
            quantization=QuantizationType.NONE
        )
        mem_fp32 = loader.estimate_memory(config_fp32)

        # INT8 quantization
        config_int8 = ModelConfig(
            model_name="gpt2",
            tier=ModelTier.TIER1,
            device="cpu",
            quantization=QuantizationType.INT8
        )
        mem_int8 = loader.estimate_memory(config_int8)

        # INT8 should use less memory than FP32
        assert mem_int8 < mem_fp32


# ============================================================================
# Model Registry Tests
# ============================================================================

@pytest.mark.unit
class TestModelRegistry:
    """Test ModelRegistry functionality."""

    def test_registry_creation(self):
        """Test creating ModelRegistry."""
        registry = ModelRegistry(max_models=2)
        assert len(registry) == 0
        assert registry.max_models == 2

    def test_registry_register_model(self, tiny_model_config):
        """Test registering a model."""
        registry = ModelRegistry(max_models=2)

        # Create mock model and tokenizer
        mock_model = "mock_model"
        mock_tokenizer = "mock_tokenizer"

        model_info = registry.register(
            model_id="test_model",
            config=tiny_model_config,
            model=mock_model,
            tokenizer=mock_tokenizer,
            memory_mb=500.0
        )

        assert model_info is not None
        assert model_info.model_id == "test_model"
        assert len(registry) == 1

    def test_registry_get_model(self, tiny_model_config):
        """Test retrieving a registered model."""
        registry = ModelRegistry(max_models=2)

        # Register model
        mock_model = "mock_model"
        registry.register(
            model_id="test_model",
            config=tiny_model_config,
            model=mock_model,
            memory_mb=500.0
        )

        # Retrieve model
        model_info = registry.get("test_model")
        assert model_info is not None
        assert model_info.model_id == "test_model"
        assert model_info.use_count == 1  # get() increments use count

    def test_registry_is_loaded(self, tiny_model_config):
        """Test checking if model is loaded."""
        registry = ModelRegistry(max_models=2)

        assert not registry.is_loaded("test_model")

        # Register model
        registry.register(
            model_id="test_model",
            config=tiny_model_config,
            model="mock_model",
            memory_mb=500.0
        )

        assert registry.is_loaded("test_model")

    def test_registry_unregister(self, tiny_model_config):
        """Test unregistering a model."""
        registry = ModelRegistry(max_models=2)

        # Register model
        registry.register(
            model_id="test_model",
            config=tiny_model_config,
            model="mock_model",
            memory_mb=500.0
        )

        assert len(registry) == 1

        # Unregister
        result = registry.unregister("test_model")
        assert result is True
        assert len(registry) == 0

    def test_registry_lru_eviction(self, tiny_model_config):
        """Test LRU eviction when registry is full."""
        registry = ModelRegistry(max_models=2)

        # Register 2 models (fill registry)
        registry.register("model1", tiny_model_config, "mock1", memory_mb=500.0)
        registry.register("model2", tiny_model_config, "mock2", memory_mb=500.0)

        assert len(registry) == 2

        # Access model1 to make it more recently used
        registry.get("model1")

        # Register third model (should evict model2, the LRU)
        registry.register("model3", tiny_model_config, "mock3", memory_mb=500.0)

        assert len(registry) == 2
        assert registry.is_loaded("model1")
        assert not registry.is_loaded("model2")  # Evicted (LRU)
        assert registry.is_loaded("model3")

    def test_registry_stats(self, tiny_model_config):
        """Test getting registry statistics."""
        registry = ModelRegistry(max_models=2)

        # Register models
        registry.register("model1", tiny_model_config, "mock1", memory_mb=500.0)
        registry.register("model2", tiny_model_config, "mock2", memory_mb=300.0)

        stats = registry.get_stats()
        assert stats['models_loaded'] == 2
        assert stats['max_models'] == 2
        assert stats['total_memory_mb'] == 800.0

    def test_registry_check_memory_pressure(self):
        """Test proactive memory pressure monitoring."""
        registry = ModelRegistry(max_models=2)

        # At 0/2, no pressure
        assert not registry.check_memory_pressure()

        # Add 1 model (still no pressure, 50% < 70%)
        registry._models['model1'] = ModelInfo(
            model_id='model1',
            config=None,
            model='mock',
            memory_mb=500.0
        )

        # At 1/2 (50%), still below 70% threshold
        assert not registry.check_memory_pressure()

        # Add another model
        registry._models['model2'] = ModelInfo(
            model_id='model2',
            config=None,
            model='mock',
            memory_mb=500.0
        )

        # At 2/2 (100%), above 70% threshold
        assert registry.check_memory_pressure()


# ============================================================================
# Model Manager Tests
# ============================================================================

@pytest.mark.integration
class TestModelManager:
    """Test ModelManager functionality."""

    def test_manager_creation(self):
        """Test creating ModelManager."""
        manager = ModelManager(max_models=2)
        assert manager is not None
        assert len(manager.list_models()) == 0

    def test_manager_is_loaded(self):
        """Test checking if model is loaded."""
        manager = ModelManager(max_models=2)
        assert not manager.is_loaded("test_model")

    def test_manager_stats(self):
        """Test getting manager statistics."""
        manager = ModelManager(max_models=2)
        stats = manager.get_stats()
        assert stats['models_loaded'] == 0
        assert stats['max_models'] == 2

    def test_manager_clear_all(self):
        """Test clearing all models."""
        manager = ModelManager(max_models=2)
        # Clear should work even when empty
        manager.clear_all()
        assert len(manager.list_models()) == 0


# ============================================================================
# Memory Management Tests
# ============================================================================

@pytest.mark.memory
@pytest.mark.slow
class TestMemoryManagement:
    """Test memory management functionality."""

    def test_memory_check_availability(self, model_manager, tiny_model_config):
        """Test memory availability check."""
        # Should not raise for small model
        estimated_mb = model_manager.loader.estimate_memory(tiny_model_config)
        result = model_manager._check_memory_availability(
            estimated_mb,
            tiny_model_config.device
        )
        # Result depends on available memory
        assert isinstance(result, bool)
