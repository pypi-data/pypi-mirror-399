"""Smart device selection for MDSA framework.

This module provides intelligent device selection based on available hardware,
automatically choosing between CPU and GPU with appropriate quantization settings.
"""

import logging
from typing import Tuple, Optional
from mdsa.models.config import QuantizationType

logger = logging.getLogger(__name__)

# Lazy import to avoid circular dependencies
_hardware_detector = None

def _get_hardware_detector():
    """Get or create hardware detector instance."""
    global _hardware_detector
    if _hardware_detector is None:
        from mdsa.utils.hardware import HardwareDetector
        _hardware_detector = HardwareDetector()
    return _hardware_detector


class DeviceStrategy:
    """Smart device selection strategy for model deployment."""

    @staticmethod
    def select_for_phi2(
        prefer_gpu: bool = True,
        force_device: Optional[str] = None
    ) -> Tuple[str, QuantizationType]:
        """
        Select best device and quantization for Phi-2 model (2.7B parameters).

        This method intelligently selects the optimal hardware configuration
        based on available resources:
        - RTX 3050 4GB: GPU with INT8 quantization (~2.7GB VRAM)
        - 16GB RAM: CPU with INT8 quantization (~3GB RAM, leaves 13GB free)
        - 8-16GB RAM: CPU with INT4 quantization (~1.5GB RAM)
        - <8GB RAM: CPU with INT4 quantization (aggressive memory saving)

        Args:
            prefer_gpu: Prefer GPU if available (default True).
            force_device: Force specific device ('cpu', 'cuda:0', 'cuda', etc.).
                         If specified, overrides auto-detection.

        Returns:
            Tuple of (device_string, quantization_type)

        Examples:
            >>> device, quant = DeviceStrategy.select_for_phi2()
            >>> print(f"Using {device} with {quant.name}")
            Using cuda:0 with INT8

            >>> device, quant = DeviceStrategy.select_for_phi2(force_device='cpu')
            >>> print(f"Using {device} with {quant.name}")
            Using cpu with INT8
        """
        # Force device if specified
        if force_device:
            device = force_device
            # Normalize cuda device
            if device == 'cuda':
                device = 'cuda:0'

            if device.startswith('cuda'):
                # GPU: Use INT8 for 4GB VRAM (Phi-2 = 2.7GB)
                logger.info(f"Force device: {device} with INT8 quantization")
                return (device, QuantizationType.INT8)
            else:
                # CPU: Use INT8 for 16GB RAM (Phi-2 = 3GB)
                logger.info(f"Force device: {device} with INT8 quantization")
                return (device, QuantizationType.INT8)

        # Auto-detect best device
        if prefer_gpu:
            try:
                hw = _get_hardware_detector()
                if hw.has_cuda and hw.cuda_devices:
                    # Found GPU (e.g., RTX 3050)
                    gpu_info = hw.cuda_devices[0]
                    vram_gb = gpu_info.get('memory_gb', 0)

                    if vram_gb >= 4:
                        # 4GB+ VRAM: Phi-2 INT8 = 2.7GB, fits comfortably!
                        logger.info(
                            f"Using GPU with {vram_gb:.1f}GB VRAM (INT8 quantization)"
                        )
                        return ('cuda:0', QuantizationType.INT8)
                    elif vram_gb >= 2:
                        # 2-4GB VRAM: Use INT4 to be safe (1.5GB)
                        logger.info(
                            f"Using GPU with {vram_gb:.1f}GB VRAM (INT4 quantization)"
                        )
                        return ('cuda:0', QuantizationType.INT4)
                    else:
                        # <2GB VRAM: Too small, fall back to CPU
                        logger.warning(
                            f"GPU has only {vram_gb:.1f}GB VRAM, falling back to CPU"
                        )
            except Exception as e:
                logger.debug(f"GPU detection failed: {e}, falling back to CPU")

        # Fallback to CPU (NOTE: INT4/INT8 requires bitsandbytes with Intel CPU or GPU)
        try:
            hw = _get_hardware_detector()
            system_ram_gb = hw.memory_gb

            # Check if we have enough RAM for unquantized model
            # Phi-2 unquantized = 5.4GB, with overhead = 6-7GB
            # With 16GB RAM, we need at least 10GB available after OS

            try:
                import psutil
                mem = psutil.virtual_memory()
                available_gb = mem.available / (1024 ** 3)

                if available_gb < 6:
                    logger.error(
                        f"Insufficient memory for CPU inference: {available_gb:.1f}GB available. "
                        "Recommendations:\n"
                        "  1. Install PyTorch with CUDA to use GPU (RTX 3050): "
                        "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121\n"
                        "  2. Close background applications to free up RAM\n"
                        "  3. Use a smaller model"
                    )
                    # Return NONE but caller should handle the memory error
                    return ('cpu', QuantizationType.NONE)
            except:
                pass

            if system_ram_gb >= 16:
                # 16GB RAM: Use FP16 (half precision) instead of INT8
                # FP16 is ~2.7GB and works without bitsandbytes
                logger.info(
                    f"Using CPU with {system_ram_gb:.1f}GB RAM (FP16 quantization)"
                )
                return ('cpu', QuantizationType.FP16)
            elif system_ram_gb >= 8:
                # 8-16GB RAM: Use FP16
                logger.info(
                    f"Using CPU with {system_ram_gb:.1f}GB RAM (FP16 quantization)"
                )
                return ('cpu', QuantizationType.FP16)
            else:
                # <8GB RAM: Very tight, suggest GPU
                logger.warning(
                    f"Low RAM ({system_ram_gb:.1f}GB). Install PyTorch with CUDA for GPU support."
                )
                return ('cpu', QuantizationType.FP16)
        except Exception as e:
            # If detection fails, use safe defaults
            logger.warning(f"RAM detection failed: {e}, using safe defaults")
            return ('cpu', QuantizationType.FP16)

    @staticmethod
    def get_safe_max_models(device: str) -> int:
        """
        Get safe max_models limit based on device and available memory.

        This prevents memory exhaustion by limiting the number of models
        that can be cached simultaneously.

        Args:
            device: Device string ('cpu', 'cuda:0', etc.)

        Returns:
            Recommended max_models for ModelManager

        Examples:
            >>> max_models = DeviceStrategy.get_safe_max_models('cuda:0')
            >>> print(f"Can cache {max_models} models")
            Can cache 1 models
        """
        if device.startswith('cuda'):
            # GPU: Limited by VRAM, keep only 1-2 models
            try:
                hw = _get_hardware_detector()
                if hw.cuda_devices:
                    vram_gb = hw.cuda_devices[0].get('memory_gb', 0)
                    if vram_gb >= 6:
                        return 2  # 6GB+: Can fit 2 Phi-2 models (INT8)
                    else:
                        return 1  # 4GB: Only 1 model safely
            except Exception:
                return 1  # Safe default for GPU

        # CPU: Based on system RAM
        try:
            hw = _get_hardware_detector()
            system_ram_gb = hw.memory_gb
            if system_ram_gb >= 16:
                return 2  # 16GB: 2 models safe (2 × 3GB = 6GB, leaves 10GB)
            elif system_ram_gb >= 8:
                return 1  # 8-16GB: 1 model only
            else:
                return 1  # <8GB: Definitely 1 model
        except Exception:
            return 2  # Safe default for CPU


def get_recommended_config(
    prefer_gpu: bool = True,
    force_device: Optional[str] = None
) -> dict:
    """
    Get recommended hardware configuration for current system.

    This is a high-level convenience function that combines device selection,
    quantization settings, and optimal concurrency parameters.

    Args:
        prefer_gpu: Prefer GPU if available (default True)
        force_device: Force specific device ('cpu', 'cuda:0', None)

    Returns:
        Dictionary with recommended configuration:
        {
            'device': str,              # 'cuda:0' or 'cpu'
            'quantization': QuantizationType,  # INT8, INT4, etc.
            'max_models': int,          # Recommended cache size
            'max_workers': int,         # ThreadPoolExecutor size
            'reason': str               # Human-readable explanation
        }

    Examples:
        >>> config = get_recommended_config()
        >>> print(config['reason'])
        Detected: RTX 3050 4.0GB VRAM → GPU with INT8

        >>> config = get_recommended_config(force_device='cpu')
        >>> print(f"Device: {config['device']}")
        Device: cpu
    """
    device, quantization = DeviceStrategy.select_for_phi2(prefer_gpu, force_device)
    max_models = DeviceStrategy.get_safe_max_models(device)

    # Thread pool size based on device
    if device.startswith('cuda'):
        # GPU: Fewer workers (GPU-bound, not CPU-bound)
        max_workers = 5
    else:
        # CPU: More workers (can parallelize across cores)
        max_workers = 8

    # Generate human-readable reason
    reason = "Detected: "
    if device.startswith('cuda'):
        try:
            hw = _get_hardware_detector()
            if hw.cuda_devices:
                vram = hw.cuda_devices[0].get('memory_gb', 0)
                gpu_name = hw.cuda_devices[0].get('name', 'GPU')
                reason += f"{gpu_name} {vram:.1f}GB VRAM -> GPU with {quantization.name}"
            else:
                reason += f"GPU -> {quantization.name}"
        except Exception:
            reason += f"GPU -> {quantization.name}"
    else:
        try:
            hw = _get_hardware_detector()
            ram = hw.memory_gb
            import psutil
            mem = psutil.virtual_memory()
            available_gb = mem.available / (1024 ** 3)
            reason += f"{ram:.1f}GB RAM ({available_gb:.1f}GB free) -> CPU with {quantization.name}"
        except Exception:
            reason += f"CPU -> {quantization.name}"

    return {
        'device': device,
        'quantization': quantization,
        'max_models': max_models,
        'max_workers': max_workers,
        'reason': reason
    }


# Example usage and testing
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    print("=== MDSA Device Configuration Utility ===\n")

    # Test auto-detection
    print("1. Auto-detect configuration:")
    config = get_recommended_config()
    print(f"   Device: {config['device']}")
    print(f"   Quantization: {config['quantization'].name}")
    print(f"   Max Models: {config['max_models']}")
    print(f"   Max Workers: {config['max_workers']}")
    print(f"   Reason: {config['reason']}\n")

    # Test force CPU
    print("2. Force CPU configuration:")
    config_cpu = get_recommended_config(force_device='cpu')
    print(f"   Device: {config_cpu['device']}")
    print(f"   Quantization: {config_cpu['quantization'].name}\n")

    # Test force GPU
    print("3. Force GPU configuration:")
    config_gpu = get_recommended_config(force_device='cuda:0')
    print(f"   Device: {config_gpu['device']}")
    print(f"   Quantization: {config_gpu['quantization'].name}\n")

    # Test prefer CPU
    print("4. Prefer CPU (even if GPU available):")
    config_prefer_cpu = get_recommended_config(prefer_gpu=False)
    print(f"   Device: {config_prefer_cpu['device']}")
    print(f"   Quantization: {config_prefer_cpu['quantization'].name}\n")
