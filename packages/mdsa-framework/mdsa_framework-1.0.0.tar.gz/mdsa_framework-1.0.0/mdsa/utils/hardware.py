"""
Hardware Detection Module

Auto-detects available compute devices (CPU, CUDA, MPS, ROCm) and provides
optimal device selection for each tier of the MDSA framework.
"""

import logging
import platform
from typing import Dict, Optional, Tuple

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

logger = logging.getLogger(__name__)


class HardwareDetector:
    """
    Auto-detect hardware capabilities and recommend optimal device placement.

    Detects:
    - CPU (cores, threads, memory)
    - CUDA GPUs (NVIDIA)
    - MPS (Apple Silicon)
    - ROCm (AMD GPUs)

    Example:
        >>> detector = HardwareDetector()
        >>> print(detector.get_summary())
        >>> device = detector.best_device_for_tier1()
    """

    def __init__(self):
        """Initialize hardware detector and scan available devices."""
        self.cpu_count = self._get_cpu_count()
        self.memory_gb = self._get_memory_gb()
        self.has_cuda = self._check_cuda()
        self.has_mps = self._check_mps()
        self.has_rocm = self._check_rocm()
        self.cuda_devices = self._get_cuda_devices()
        self.platform = platform.system()
        self.python_version = platform.python_version()

        logger.info(f"Hardware detected: {self.get_summary()}")

    def _get_cpu_count(self) -> int:
        """Get CPU core count."""
        if PSUTIL_AVAILABLE:
            return psutil.cpu_count(logical=False) or 1
        else:
            import os
            return os.cpu_count() or 1

    def _get_memory_gb(self) -> float:
        """Get system memory in GB."""
        if PSUTIL_AVAILABLE:
            return psutil.virtual_memory().total / (1024 ** 3)
        else:
            return 0.0

    def _check_cuda(self) -> bool:
        """Check if CUDA is available."""
        if not TORCH_AVAILABLE:
            logger.warning("PyTorch not installed - CUDA unavailable")
            return False

        cuda_available = torch.cuda.is_available()

        if cuda_available:
            device_count = torch.cuda.device_count()
            logger.info(f"CUDA available: {device_count} device(s) detected")
            for i in range(device_count):
                device_name = torch.cuda.get_device_name(i)
                logger.info(f"  Device {i}: {device_name}")

            if hasattr(torch.version, 'cuda') and torch.version.cuda:
                logger.info(f"  CUDA version: {torch.version.cuda}")
        else:
            logger.warning("CUDA not available - GPU acceleration disabled")
            logger.warning("Check PyTorch installation: pip install torch --index-url https://download.pytorch.org/whl/cu121")

        return cuda_available

    def _check_mps(self) -> bool:
        """Check if MPS (Apple Silicon) is available."""
        if not TORCH_AVAILABLE:
            return False
        return hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()

    def _check_rocm(self) -> bool:
        """
        Check if ROCm (AMD) is available.

        Note: ROCm uses the same CUDA API in PyTorch, so we check for
        torch.cuda.is_available() and AMD-specific environment variables.
        """
        if not TORCH_AVAILABLE or not self.has_cuda:
            return False

        # Check for ROCm-specific environment variables
        import os
        rocm_vars = ['ROCM_PATH', 'ROCM_HOME', 'HIP_PATH']
        return any(os.getenv(var) for var in rocm_vars)

    def _get_cuda_devices(self) -> list:
        """Get list of CUDA devices with their properties."""
        if not self.has_cuda or not TORCH_AVAILABLE:
            return []

        devices = []
        try:
            for i in range(torch.cuda.device_count()):
                props = torch.cuda.get_device_properties(i)
                devices.append({
                    'id': i,
                    'name': props.name,
                    'memory_gb': props.total_memory / (1024 ** 3),
                    'compute_capability': (props.major, props.minor)
                })
        except Exception as e:
            logger.warning(f"Error getting CUDA device properties: {e}")

        return devices

    def _cuda_memory_gb(self, device_id: int = 0) -> float:
        """Get CUDA memory for specific device in GB."""
        if not self.has_cuda or not TORCH_AVAILABLE:
            return 0.0

        try:
            props = torch.cuda.get_device_properties(device_id)
            return props.total_memory / (1024 ** 3)
        except Exception:
            return 0.0

    def best_device_for_tier1(self) -> str:
        """
        Tier 1 (TinyBERT Orchestrator): Always CPU for consistency and low latency.

        TinyBERT is 67M params and runs efficiently on CPU with <50ms latency.

        Returns:
            str: Device string (always "cpu")
        """
        return "cpu"

    def best_device_for_tier2(self) -> str:
        """
        Tier 2 (Phi-1.5 Validation): GPU if available with 3GB+ VRAM, else CPU.

        Phi-1.5 is 1.3B params and benefits from GPU acceleration.

        Returns:
            str: Device string ("cuda:0", "mps", or "cpu")
        """
        # Prefer CUDA GPU
        if self.has_cuda:
            cuda_vram = self._cuda_memory_gb()
            logger.info(f"Tier 2 device selection: CUDA detected with {cuda_vram:.2f}GB VRAM")

            if cuda_vram >= 3:
                logger.info("Using CUDA GPU for Tier 2 (Phi-2 reasoning model)")
                return "cuda:0"
            else:
                logger.warning(f"CUDA VRAM ({cuda_vram:.2f}GB) below 3GB threshold for Tier 2. Falling back to CPU.")

        # Fall back to MPS (Apple Silicon)
        if self.has_mps:
            logger.info("Using MPS (Apple Silicon) for Tier 2")
            return "mps"

        # Final fallback to CPU (will be slower)
        logger.warning("No GPU with 3GB+ VRAM found for Tier 2. Using CPU (slower).")
        return "cpu"

    def best_device_for_tier3(self) -> str:
        """
        Tier 3 (Domain SLMs): Requires GPU with 8GB+ VRAM or 32GB+ system RAM.

        Domain SLMs are 7-13B params and need significant memory.

        Returns:
            str: Device string ("cuda:0", "mps", or "cpu")

        Raises:
            RuntimeError: If insufficient resources are available
        """
        # Prefer CUDA GPU with 8GB+ VRAM
        if self.has_cuda and self._cuda_memory_gb() >= 8:
            return "cuda:0"

        # MPS for Apple Silicon (check system RAM)
        if self.has_mps and self.memory_gb >= 16:
            return "mps"

        # CPU with high RAM (32GB+)
        if self.memory_gb >= 32:
            logger.warning("Using CPU for Tier 3 (requires 32GB+ RAM).")
            return "cpu"

        # Insufficient resources
        raise RuntimeError(
            f"Domain SLMs (Tier 3) require either:\n"
            f"  - 8GB+ GPU VRAM (found: {self._cuda_memory_gb():.1f}GB), or\n"
            f"  - 32GB+ system RAM (found: {self.memory_gb:.1f}GB)\n"
            f"Please upgrade your hardware or use smaller models."
        )

    def get_optimal_device(self, min_memory_gb: float = 0) -> str:
        """
        Get optimal device for given memory requirements.

        Args:
            min_memory_gb: Minimum memory required in GB

        Returns:
            str: Best available device string
        """
        # CUDA with sufficient memory
        if self.has_cuda and self._cuda_memory_gb() >= min_memory_gb:
            return "cuda:0"

        # MPS (Apple Silicon)
        if self.has_mps and self.memory_gb >= min_memory_gb:
            return "mps"

        # CPU (check system RAM)
        if self.memory_gb >= min_memory_gb:
            return "cpu"

        # Fallback to CPU even if insufficient (will warn later)
        logger.warning(
            f"Insufficient memory ({self.memory_gb:.1f}GB) for requirement ({min_memory_gb}GB). "
            "Performance may be degraded."
        )
        return "cpu"

    def get_summary(self) -> Dict:
        """
        Get comprehensive hardware summary.

        Returns:
            dict: Hardware capabilities and recommendations
        """
        summary = {
            'platform': self.platform,
            'python_version': self.python_version,
            'cpu_cores': self.cpu_count,
            'memory_gb': round(self.memory_gb, 2),
            'has_cuda': self.has_cuda,
            'has_mps': self.has_mps,
            'has_rocm': self.has_rocm,
            'cuda_devices': self.cuda_devices,
            'tier1_device': self.best_device_for_tier1(),
            'tier2_device': self.best_device_for_tier2(),
        }

        # Try to get tier3 device (might fail)
        try:
            summary['tier3_device'] = self.best_device_for_tier3()
        except RuntimeError as e:
            summary['tier3_device'] = f"Error: {str(e)}"

        return summary

    def print_summary(self):
        """Print hardware summary to console."""
        summary = self.get_summary()

        print("\n" + "=" * 70)
        print("MDSA Hardware Detection Summary")
        print("=" * 70)
        print(f"Platform:        {summary['platform']}")
        print(f"Python:          {summary['python_version']}")
        print(f"CPU Cores:       {summary['cpu_cores']}")
        print(f"System Memory:   {summary['memory_gb']} GB")
        print(f"\nAccelerators:")
        print(f"  CUDA (NVIDIA): {'Yes' if summary['has_cuda'] else 'No'}")
        print(f"  MPS (Apple):   {'Yes' if summary['has_mps'] else 'No'}")
        print(f"  ROCm (AMD):    {'Yes' if summary['has_rocm'] else 'No'}")

        if summary['cuda_devices']:
            print(f"\nCUDA Devices:")
            for dev in summary['cuda_devices']:
                print(f"  [{dev['id']}] {dev['name']}")
                print(f"      Memory: {dev['memory_gb']:.2f} GB")
                print(f"      Compute: {dev['compute_capability']}")

        print(f"\nRecommended Devices:")
        print(f"  Tier 1 (TinyBERT):  {summary['tier1_device']}")
        print(f"  Tier 2 (Phi-1.5):   {summary['tier2_device']}")
        print(f"  Tier 3 (SLMs):      {summary['tier3_device']}")
        print("=" * 70 + "\n")

    def check_requirements(self, tier: int = 3) -> Tuple[bool, str]:
        """
        Check if hardware meets requirements for specified tier.

        Args:
            tier: Tier level (1, 2, or 3)

        Returns:
            tuple: (meets_requirements, message)
        """
        if tier == 1:
            # Tier 1 always works (CPU-only)
            return True, "Tier 1 requirements met (CPU)"

        elif tier == 2:
            # Tier 2 prefers GPU but works on CPU
            device = self.best_device_for_tier2()
            if device != "cpu":
                return True, f"Tier 2 requirements met ({device})"
            else:
                return True, "Tier 2 will run on CPU (GPU recommended for better performance)"

        elif tier == 3:
            # Tier 3 requires significant resources
            try:
                device = self.best_device_for_tier3()
                return True, f"Tier 3 requirements met ({device})"
            except RuntimeError as e:
                return False, str(e)

        else:
            return False, f"Invalid tier: {tier} (must be 1, 2, or 3)"


# Convenience function for quick hardware check
def get_hardware_info() -> Dict:
    """
    Quick hardware info getter.

    Returns:
        dict: Hardware summary

    Example:
        >>> from mdsa.utils import get_hardware_info
        >>> info = get_hardware_info()
        >>> print(info['tier1_device'])
    """
    detector = HardwareDetector()
    return detector.get_summary()


if __name__ == "__main__":
    # Demo usage
    detector = HardwareDetector()
    detector.print_summary()
