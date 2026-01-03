"""
Unit tests for Hardware Detection module.

Tests hardware detection, device selection, and tier recommendations.
"""

import unittest
from unittest.mock import patch, MagicMock
from mdsa.utils.hardware import HardwareDetector, get_hardware_info


class TestHardwareDetector(unittest.TestCase):
    """Test suite for HardwareDetector class."""

    def setUp(self):
        """Set up test fixtures."""
        self.detector = HardwareDetector()

    def test_initialization(self):
        """Test HardwareDetector initialization."""
        self.assertIsNotNone(self.detector)
        self.assertIsInstance(self.detector.cpu_count, int)
        self.assertIsInstance(self.detector.memory_gb, float)
        self.assertIn(self.detector.platform, ['Windows', 'Linux', 'Darwin', 'Unknown'])

    def test_cpu_detection(self):
        """Test CPU detection."""
        self.assertIsInstance(self.detector.cpu_count, int)
        self.assertGreater(self.detector.cpu_count, 0)

    def test_ram_detection(self):
        """Test RAM detection."""
        self.assertIsInstance(self.detector.memory_gb, float)
        self.assertGreater(self.detector.memory_gb, 0)

    def test_platform_detection(self):
        """Test platform detection."""
        self.assertIn(self.detector.platform, ['Windows', 'Linux', 'macOS', 'Unknown'])

    @patch('mdsa.utils.hardware.torch')
    def test_cuda_detection_available(self, mock_torch):
        """Test CUDA detection when available."""
        mock_torch.cuda.is_available.return_value = True
        mock_torch.cuda.device_count.return_value = 1
        mock_torch.cuda.get_device_name.return_value = "NVIDIA RTX 3090"
        mock_torch.cuda.get_device_properties.return_value = MagicMock(total_memory=24 * 1024**3)

        detector = HardwareDetector()
        self.assertTrue(detector.has_cuda)
        self.assertEqual(len(detector.cuda_devices), 1)

    @patch('mdsa.utils.hardware.torch')
    def test_cuda_detection_unavailable(self, mock_torch):
        """Test CUDA detection when unavailable."""
        mock_torch.cuda.is_available.return_value = False

        detector = HardwareDetector()
        self.assertFalse(detector.has_cuda)
        self.assertEqual(len(detector.cuda_devices), 0)

    def test_tier1_device_always_cpu(self):
        """Test Tier 1 (TinyBERT) always uses CPU."""
        device = self.detector.best_device_for_tier1()
        self.assertEqual(device, "cpu")

    def test_tier2_device_selection(self):
        """Test Tier 2 (Phi-1.5) device selection."""
        device = self.detector.best_device_for_tier2()
        self.assertIn(device, ["cpu", "cuda:0", "mps"])

    def test_tier3_device_selection(self):
        """Test Tier 3 (Domain SLMs) device selection or raises error."""
        try:
            device = self.detector.best_device_for_tier3()
            self.assertIn(device, ["cuda:0", "cpu", "mps"])
        except RuntimeError as e:
            # Expected if insufficient hardware
            self.assertIn("GPU", str(e))

    def test_get_summary(self):
        """Test hardware summary generation."""
        summary = self.detector.get_summary()
        self.assertIsInstance(summary, dict)
        self.assertIn('cpu_cores', summary)
        self.assertIn('memory_gb', summary)

    def test_supports_tier1(self):
        """Test Tier 1 support (should always be True)."""
        meets_req, msg = self.detector.check_requirements(tier=1)
        self.assertTrue(meets_req)

    def test_supports_tier2(self):
        """Test Tier 2 support detection."""
        meets_req, msg = self.detector.check_requirements(tier=2)
        self.assertIsInstance(meets_req, bool)

    def test_supports_tier3(self):
        """Test Tier 3 support detection."""
        meets_req, msg = self.detector.check_requirements(tier=3)
        self.assertIsInstance(meets_req, bool)

    def test_get_recommended_config(self):
        """Test recommended configuration generation."""
        from mdsa.utils.device_config import get_recommended_config
        config = get_recommended_config()
        self.assertIsInstance(config, dict)
        self.assertIn('device', config)
        self.assertIn('quantization', config)

    def test_repr(self):
        """Test string representation."""
        repr_str = repr(self.detector)
        self.assertIn("HardwareDetector", repr_str)


class TestGetHardwareInfo(unittest.TestCase):
    """Test suite for get_hardware_info convenience function."""

    def test_get_hardware_info(self):
        """Test get_hardware_info returns valid dictionary."""
        info = get_hardware_info()
        self.assertIsInstance(info, dict)
        self.assertIn('platform', info)
        self.assertIn('cpu_cores', info)
        self.assertIn('memory_gb', info)
        self.assertIn('has_cuda', info)


if __name__ == '__main__':
    unittest.main()
