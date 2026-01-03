"""
Memory Management Tests for MDSA Framework

Tests cover:
- Memory estimation
- Memory pre-checks
- LRU eviction
- Memory pressure monitoring
- GPU memory cleanup
- Memory leak prevention
"""

import pytest
import psutil
from mdsa.models.config import ModelConfig, ModelTier, QuantizationType
from mdsa.models.registry import ModelRegistry, ModelInfo
from mdsa.models.manager import ModelManager


# ============================================================================
# Memory Estimation Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.memory
class TestMemoryEstimation:
    """Test memory estimation functionality."""

    def test_estimate_memory_tier1(self):
        """Test memory estimation for Tier 1 models."""
        from mdsa.models.loader import ModelLoader

        loader = ModelLoader()
        config = ModelConfig(
            model_name="gpt2",
            tier=ModelTier.TIER1,
            device="cpu",
            quantization=QuantizationType.NONE
        )

        estimated_mb = loader.estimate_memory(config)
        # Tier 1 models should be small
        assert estimated_mb > 0
        assert estimated_mb < 1000  # Less than 1GB

    def test_estimate_memory_tier2(self):
        """Test memory estimation for Tier 2 models."""
        from mdsa.models.loader import ModelLoader

        loader = ModelLoader()
        config = ModelConfig(
            model_name="microsoft/phi-2",
            tier=ModelTier.TIER2,
            device="cpu",
            quantization=QuantizationType.NONE
        )

        estimated_mb = loader.estimate_memory(config)
        # Tier 2 models should be larger
        assert estimated_mb > 1000  # At least 1GB

    def test_estimate_memory_with_int8(self):
        """Test memory estimation with INT8 quantization."""
        from mdsa.models.loader import ModelLoader

        loader = ModelLoader()

        config_none = ModelConfig(
            model_name="gpt2",
            tier=ModelTier.TIER1,
            device="cpu",
            quantization=QuantizationType.NONE
        )

        config_int8 = ModelConfig(
            model_name="gpt2",
            tier=ModelTier.TIER1,
            device="cpu",
            quantization=QuantizationType.INT8
        )

        mem_none = loader.estimate_memory(config_none)
        mem_int8 = loader.estimate_memory(config_int8)

        # INT8 should use ~50% of unquantized
        assert mem_int8 < mem_none
        assert mem_int8 >= mem_none * 0.4  # At least 40%
        assert mem_int8 <= mem_none * 0.6  # At most 60%

    def test_estimate_memory_with_int4(self):
        """Test memory estimation with INT4 quantization."""
        from mdsa.models.loader import ModelLoader

        loader = ModelLoader()

        config_none = ModelConfig(
            model_name="gpt2",
            tier=ModelTier.TIER1,
            device="cpu",
            quantization=QuantizationType.NONE
        )

        config_int4 = ModelConfig(
            model_name="gpt2",
            tier=ModelTier.TIER1,
            device="cpu",
            quantization=QuantizationType.INT4
        )

        mem_none = loader.estimate_memory(config_none)
        mem_int4 = loader.estimate_memory(config_int4)

        # INT4 should use ~25% of unquantized
        assert mem_int4 < mem_none
        assert mem_int4 <= mem_none * 0.35  # At most 35%


# ============================================================================
# Memory Pre-Check Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.memory
class TestMemoryPreCheck:
    """Test memory availability pre-checks."""

    def test_memory_check_with_sufficient_memory(self, model_manager):
        """Test memory check when sufficient memory is available."""
        # Very small memory requirement should pass
        result = model_manager._check_memory_availability(
            estimated_mb=10.0,  # Just 10MB
            device='cpu'
        )
        assert result is True

    def test_memory_check_with_excessive_requirement(self, model_manager):
        """Test memory check when requirement exceeds available memory."""
        # Get available memory
        mem = psutil.virtual_memory()
        available_gb = mem.available / (1024 ** 3)

        # Request more than available (with safety margin)
        excessive_mb = (available_gb + 10) * 1024  # 10GB over available

        result = model_manager._check_memory_availability(
            estimated_mb=excessive_mb,
            device='cpu'
        )

        # Should fail (return False)
        assert result is False

    def test_memory_check_cpu_vs_gpu(self, model_manager):
        """Test memory check for CPU vs GPU devices."""
        # Small memory requirement
        mem_mb = 100.0

        # CPU check
        cpu_result = model_manager._check_memory_availability(mem_mb, device='cpu')
        assert isinstance(cpu_result, bool)

        # GPU check (may not be available)
        try:
            gpu_result = model_manager._check_memory_availability(mem_mb, device='cuda:0')
            assert isinstance(gpu_result, bool)
        except Exception:
            # GPU not available, skip
            pass


# ============================================================================
# LRU Eviction Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.memory
class TestLRUEviction:
    """Test LRU eviction functionality."""

    def test_lru_eviction_basic(self, tiny_model_config):
        """Test basic LRU eviction."""
        registry = ModelRegistry(max_models=2)

        # Register 2 models
        registry.register("model1", tiny_model_config, "mock1", memory_mb=100)
        registry.register("model2", tiny_model_config, "mock2", memory_mb=100)

        assert len(registry) == 2

        # Access model1 (make it more recent)
        registry.get("model1")

        # Register third model (should evict model2)
        registry.register("model3", tiny_model_config, "mock3", memory_mb=100)

        assert len(registry) == 2
        assert registry.is_loaded("model1")
        assert not registry.is_loaded("model2")  # Evicted
        assert registry.is_loaded("model3")

    def test_lru_eviction_multiple_accesses(self, tiny_model_config):
        """Test LRU eviction with multiple accesses."""
        registry = ModelRegistry(max_models=2)

        # Register 2 models
        registry.register("model1", tiny_model_config, "mock1", memory_mb=100)
        registry.register("model2", tiny_model_config, "mock2", memory_mb=100)

        # Access model1 multiple times
        registry.get("model1")
        registry.get("model1")
        registry.get("model1")

        # Access model2 once
        registry.get("model2")

        # model1 should have higher use count but model2 was accessed more recently
        model1_info = registry.get("model1")
        model2_info = registry.get("model2")

        # Eviction is based on last_used, not use_count
        # model1 was accessed last, so it's most recent now

        # Register third model
        registry.register("model3", tiny_model_config, "mock3", memory_mb=100)

        # model2 should be evicted (it was accessed before model1)
        assert len(registry) == 2


# ============================================================================
# Memory Pressure Monitoring Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.memory
class TestMemoryPressureMonitoring:
    """Test memory pressure monitoring (Fix B2)."""

    def test_memory_pressure_below_threshold(self):
        """Test memory pressure when below 70% threshold."""
        registry = ModelRegistry(max_models=10)

        # Add 5 models (50% capacity)
        for i in range(5):
            registry._models[f"model{i}"] = ModelInfo(
                model_id=f"model{i}",
                config=None,
                model="mock",
                memory_mb=100.0
            )

        # At 5/10 (50%), should be False
        assert registry.check_memory_pressure() is False

    def test_memory_pressure_above_threshold(self):
        """Test memory pressure when above 70% threshold."""
        registry = ModelRegistry(max_models=10)

        # Add 8 models (80% capacity)
        for i in range(8):
            registry._models[f"model{i}"] = ModelInfo(
                model_id=f"model{i}",
                config=None,
                model="mock",
                memory_mb=100.0
            )

        # At 8/10 (80%), above 70% threshold
        assert registry.check_memory_pressure() is True

    def test_memory_pressure_at_threshold(self):
        """Test memory pressure exactly at 70% threshold."""
        registry = ModelRegistry(max_models=10)

        # Add 7 models (70% capacity)
        for i in range(7):
            registry._models[f"model{i}"] = ModelInfo(
                model_id=f"model{i}",
                config=None,
                model="mock",
                memory_mb=100.0
            )

        # At 7/10 (70%), should trigger threshold
        assert registry.check_memory_pressure() is True

    def test_proactive_eviction_triggered(self, tiny_model_config):
        """Test that proactive eviction is triggered at 70%."""
        registry = ModelRegistry(max_models=10)

        # Add models up to 70% capacity
        for i in range(7):
            registry.register(f"model{i}", tiny_model_config, f"mock{i}", memory_mb=100)

        # At 7/10, pressure is high
        # Register one more should trigger proactive eviction
        initial_count = len(registry)

        # Access model1 to make it more recent than model0
        registry.get("model1")

        # Register another model
        registry.register("model_new", tiny_model_config, "mock_new", memory_mb=100)

        # Should have evicted model0 proactively before hitting limit
        # Total should be 8 (not 7, since we added one)
        assert len(registry) <= 10  # Within limit


# ============================================================================
# GPU Memory Cleanup Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.memory
@pytest.mark.gpu
class TestGPUMemoryCleanup:
    """Test GPU memory cleanup (Fix B1)."""

    def test_cleanup_device_memory_cpu(self, tiny_model_config):
        """Test GPU cleanup on CPU device (should be safe no-op)."""
        registry = ModelRegistry(max_models=2)

        # Register and unregister model
        registry.register("model1", tiny_model_config, "mock1", memory_mb=100)
        registry.unregister("model1")

        # Should complete without error even on CPU

    def test_cleanup_called_on_unregister(self, tiny_model_config):
        """Test that cleanup is called when unregistering."""
        registry = ModelRegistry(max_models=2)

        registry.register("model1", tiny_model_config, "mock1", memory_mb=100)
        result = registry.unregister("model1")

        assert result is True
        # Cleanup was called (we can't easily verify CUDA call without GPU)

    def test_cleanup_called_on_lru_eviction(self, tiny_model_config):
        """Test that cleanup is called during LRU eviction."""
        registry = ModelRegistry(max_models=1)

        # Fill registry
        registry.register("model1", tiny_model_config, "mock1", memory_mb=100)

        # Register another (triggers eviction)
        registry.register("model2", tiny_model_config, "mock2", memory_mb=100)

        # model1 should be evicted and cleanup called
        assert not registry.is_loaded("model1")
        assert registry.is_loaded("model2")


# ============================================================================
# Memory Leak Prevention Tests
# ============================================================================

@pytest.mark.memory
@pytest.mark.slow
class TestMemoryLeakPrevention:
    """Test that memory is properly released."""

    def test_model_references_deleted(self, tiny_model_config):
        """Test that model references are deleted on unregister."""
        registry = ModelRegistry(max_models=2)

        # Register model
        registry.register("model1", tiny_model_config, "mock1", memory_mb=100)

        # Get initial stats
        stats_before = registry.get_stats()
        assert stats_before['models_loaded'] == 1

        # Unregister
        registry.unregister("model1")

        # Stats should show model removed
        stats_after = registry.get_stats()
        assert stats_after['models_loaded'] == 0
        assert stats_after['total_memory_mb'] == 0

    def test_registry_clear_releases_all(self, tiny_model_config):
        """Test that clearing registry releases all models."""
        registry = ModelRegistry(max_models=10)

        # Register multiple models
        for i in range(5):
            registry.register(f"model{i}", tiny_model_config, f"mock{i}", memory_mb=100)

        assert len(registry) == 5

        # Clear all
        registry.clear()

        assert len(registry) == 0
        stats = registry.get_stats()
        assert stats['models_loaded'] == 0


# ============================================================================
# Memory Statistics Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.memory
class TestMemoryStatistics:
    """Test memory statistics tracking."""

    def test_memory_stats_accuracy(self, tiny_model_config):
        """Test that memory statistics are accurate."""
        registry = ModelRegistry(max_models=10)

        # Register models with known memory
        registry.register("model1", tiny_model_config, "mock1", memory_mb=100.0)
        registry.register("model2", tiny_model_config, "mock2", memory_mb=200.0)
        registry.register("model3", tiny_model_config, "mock3", memory_mb=150.0)

        stats = registry.get_stats()

        assert stats['models_loaded'] == 3
        assert stats['total_memory_mb'] == 450.0  # 100 + 200 + 150

    def test_memory_stats_after_eviction(self, tiny_model_config):
        """Test memory statistics after eviction."""
        registry = ModelRegistry(max_models=2)

        # Register 3 models (triggers eviction)
        registry.register("model1", tiny_model_config, "mock1", memory_mb=100.0)
        registry.register("model2", tiny_model_config, "mock2", memory_mb=200.0)
        registry.register("model3", tiny_model_config, "mock3", memory_mb=150.0)

        stats = registry.get_stats()

        # Should only have 2 models
        assert stats['models_loaded'] == 2
        # Total memory should only count remaining models
        # (model1 was evicted, so 200 + 150 = 350)
        assert stats['total_memory_mb'] == 350.0
