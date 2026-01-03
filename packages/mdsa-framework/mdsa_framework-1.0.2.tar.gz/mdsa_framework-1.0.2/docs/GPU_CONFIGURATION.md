# GPU Configuration Guide for MDSA + Ollama

Complete guide to configuring GPU acceleration for Ollama models in MDSA Framework.

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [GPU Detection](#gpu-detection)
4. [NVIDIA GPU (CUDA) Configuration](#nvidia-gpu-cuda-configuration)
5. [AMD GPU (ROCm) Configuration](#amd-gpu-rocm-configuration)
6. [Apple Silicon (M1/M2/M3) Configuration](#apple-silicon-m1m2m3-configuration)
7. [Ollama GPU Settings](#ollama-gpu-settings)
8. [MDSA Integration](#mdsa-integration)
9. [Performance Optimization](#performance-optimization)
10. [Troubleshooting](#troubleshooting)

---

## Overview

GPU acceleration significantly improves inference speed for Ollama models:

| Hardware | Model Size | Speed Improvement | Typical Latency |
|----------|-----------|-------------------|-----------------|
| **CPU Only** | 1B params | Baseline | 2-5 seconds |
| **CPU Only** | 3B params | Baseline | 5-15 seconds |
| **GPU (6GB VRAM)** | 1B params | 5-10x faster | 200-500ms |
| **GPU (6GB VRAM)** | 3B params | 5-10x faster | 500-1500ms |
| **GPU (12GB+ VRAM)** | 8B params | 10-20x faster | 1-3 seconds |

**Key Benefits**:
- Lower latency (milliseconds instead of seconds)
- Higher throughput (more requests per second)
- Better user experience for interactive applications
- Ability to run larger, higher-quality models

---

## Prerequisites

### Hardware Requirements

**NVIDIA GPU (CUDA)**:
- **Minimum**: NVIDIA GPU with 3GB+ VRAM (GTX 1060, RTX 2060, etc.)
- **Recommended**: NVIDIA GPU with 6GB+ VRAM (RTX 3060, RTX 4060, etc.)
- **Best**: NVIDIA GPU with 12GB+ VRAM (RTX 3090, RTX 4090, A4000, etc.)
- **Compute Capability**: 3.5 or higher (most GPUs since 2014)

**AMD GPU (ROCm)**:
- **Supported**: AMD Radeon RX 5000+ series, Radeon Pro, MI series
- **VRAM**: 8GB+ recommended
- **OS**: Linux only (Ubuntu 20.04/22.04, RHEL 8/9)
- **Note**: Limited Ollama support compared to CUDA

**Apple Silicon (Metal)**:
- **Supported**: M1, M2, M3, M1 Pro, M1 Max, M1 Ultra, M2 Pro, M2 Max, M2 Ultra
- **Unified Memory**: 8GB+ (16GB+ recommended)
- **OS**: macOS 11.0+ (Big Sur or later)

### Software Prerequisites

**NVIDIA (CUDA)**:
- NVIDIA Driver: Latest stable (525+ recommended)
- CUDA Toolkit: 11.8 or 12.x (optional, Ollama includes runtime)

**AMD (ROCm)**:
- ROCm 5.4+ installed
- AMD GPU drivers

**Apple Silicon**:
- macOS 11.0+ (comes with Metal support)

---

## GPU Detection

### Check GPU Availability

**NVIDIA (Windows/Linux)**:
```bash
# Check GPU info
nvidia-smi

# Expected output:
# +-----------------------------------------------------------------------------+
# | NVIDIA-SMI 535.104.05   Driver Version: 535.104.05   CUDA Version: 12.2   |
# |-------------------------------+----------------------+----------------------+
# | GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
# | Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
# |===============================+======================+======================|
# |   0  NVIDIA GeForce ...  Off  | 00000000:01:00.0  On |                  N/A |
# | 30%   45C    P8    15W / 170W |    512MiB /  6144MiB |      0%      Default |
# +-------------------------------+----------------------+----------------------+
```

**AMD (Linux)**:
```bash
# Check ROCm
rocm-smi

# Check GPU
lspci | grep VGA
```

**Apple Silicon (macOS)**:
```bash
# Check system info
system_profiler SPHardwareDataType | grep Chip

# Expected output:
# Chip: Apple M1/M2/M3
```

### Verify CUDA Installation (NVIDIA)

```bash
# Check CUDA version
nvcc --version

# If not installed, Ollama will use bundled CUDA runtime
```

### MDSA Hardware Detection

```python
from mdsa.utils import HardwareDetector

detector = HardwareDetector()
summary = detector.get_summary()

print(f"Has CUDA: {summary['has_cuda']}")
print(f"GPU Count: {summary.get('gpu_count', 0)}")
print(f"GPU Memory: {summary.get('gpu_memory_gb', 0)} GB")
print(f"GPU Name: {summary.get('gpu_name', 'N/A')}")
```

Expected output (with GPU):
```
Has CUDA: True
GPU Count: 1
GPU Memory: 6.0 GB
GPU Name: NVIDIA GeForce RTX 3060
```

---

## NVIDIA GPU (CUDA) Configuration

### 1. Install NVIDIA Drivers

**Windows**:
- Download from [NVIDIA Driver Downloads](https://www.nvidia.com/download/index.aspx)
- Run installer
- Restart computer

**Linux (Ubuntu/Debian)**:
```bash
# Remove old drivers
sudo apt-get purge nvidia*

# Add PPA (for latest drivers)
sudo add-apt-repository ppa:graphics-drivers/ppa
sudo apt-get update

# Install driver (replace XXX with version, e.g., 535)
sudo apt-get install nvidia-driver-XXX

# Reboot
sudo reboot
```

**Verify Driver**:
```bash
nvidia-smi
```

### 2. Configure Ollama for CUDA

Ollama automatically detects and uses NVIDIA GPUs. Configuration via environment variables:

**Windows (PowerShell)**:
```powershell
# Use GPU 0 only
$env:CUDA_VISIBLE_DEVICES=0

# Use all GPUs
$env:CUDA_VISIBLE_DEVICES="0,1"

# Limit Ollama to use only 1 GPU layer
$env:OLLAMA_NUM_GPU=1

# Set GPU memory limit (in MB, optional)
$env:OLLAMA_MAX_LOADED_MODELS=2

# Permanent (add to PowerShell profile)
[System.Environment]::SetEnvironmentVariable('CUDA_VISIBLE_DEVICES', '0', 'User')
```

**Linux/macOS (Bash/Zsh)**:
```bash
# Temporary (current session only)
export CUDA_VISIBLE_DEVICES=0
export OLLAMA_NUM_GPU=1

# Permanent (add to ~/.bashrc or ~/.zshrc)
echo 'export CUDA_VISIBLE_DEVICES=0' >> ~/.bashrc
echo 'export OLLAMA_NUM_GPU=1' >> ~/.bashrc
source ~/.bashrc
```

### 3. Restart Ollama

After setting environment variables:

```bash
# Stop Ollama
pkill ollama  # Linux/macOS
taskkill /F /IM ollama.exe  # Windows

# Restart
ollama serve
```

### 4. Verify GPU Usage

```bash
# Run a model
ollama run gemma3:1b "Test GPU"

# Watch GPU usage in another terminal
nvidia-smi -l 1  # Update every 1 second
```

You should see GPU memory usage increase when the model runs.

---

## AMD GPU (ROCm) Configuration

**Note**: AMD GPU support via ROCm is experimental. NVIDIA GPUs are recommended for production.

### 1. Install ROCm (Linux Only)

**Ubuntu 20.04/22.04**:
```bash
# Add ROCm repository
wget https://repo.radeon.com/amdgpu-install/latest/ubuntu/focal/amdgpu-install_*_all.deb
sudo apt-get install ./amdgpu-install_*_all.deb

# Install ROCm
sudo amdgpu-install --usecase=rocm

# Add user to groups
sudo usermod -a -G render,video $USER

# Reboot
sudo reboot
```

### 2. Configure Ollama for ROCm

```bash
# Set ROCm environment
export HSA_OVERRIDE_GFX_VERSION=10.3.0  # Adjust for your GPU
export OLLAMA_NUM_GPU=1

# Start Ollama
ollama serve
```

### 3. Verify

```bash
# Check ROCm
rocm-smi

# Test model
ollama run gemma3:1b
```

---

## Apple Silicon (M1/M2/M3) Configuration

Apple Silicon automatically uses Metal Performance Shaders (MPS) for GPU acceleration.

### 1. Verify Metal Support

```bash
# Check system
system_profiler SPHardwareDataType

# Should show:
# Chip: Apple M1/M2/M3
```

### 2. Ollama Automatically Uses Metal

No configuration needed - Ollama detects and uses Metal automatically.

### 3. Optional: Adjust Memory Allocation

```bash
# Set memory limit (if needed)
export OLLAMA_MAX_LOADED_MODELS=2

# Start Ollama
ollama serve
```

### 4. Verify GPU Usage

```bash
# Run model
ollama run gemma3:1b "Test"

# Monitor GPU usage
sudo powermetrics --samplers gpu_power -i 1000
```

---

## Ollama GPU Settings

### Environment Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `CUDA_VISIBLE_DEVICES` | Which GPUs to use (NVIDIA) | All | `0` or `0,1` |
| `OLLAMA_NUM_GPU` | Number of GPU layers | Auto-detect | `1` or `999` (all) |
| `OLLAMA_MAX_LOADED_MODELS` | Max models in VRAM simultaneously | 1 | `2` or `3` |
| `OLLAMA_HOST` | Server bind address | `127.0.0.1:11434` | `0.0.0.0:11434` |
| `HSA_OVERRIDE_GFX_VERSION` | AMD GPU version override (ROCm) | - | `10.3.0` |

### Multi-GPU Configuration

**Use Specific GPUs**:
```bash
# Windows
$env:CUDA_VISIBLE_DEVICES="0,2"  # Use GPU 0 and 2, skip 1

# Linux/macOS
export CUDA_VISIBLE_DEVICES=0,2
```

**Load Balance Across GPUs**:
```bash
# Ollama automatically distributes layers across available GPUs
export CUDA_VISIBLE_DEVICES=0,1
export OLLAMA_NUM_GPU=999  # Use all available layers
```

### Memory Management

**Limit VRAM Usage**:
```bash
# Only load 2 models maximum in VRAM
export OLLAMA_MAX_LOADED_MODELS=2
```

**Force CPU Offloading**:
```bash
# Use only CPU (disable GPU)
export OLLAMA_NUM_GPU=0
```

---

## MDSA Integration

### Automatic GPU Detection

MDSA automatically detects and reports GPU availability:

```python
from mdsa import MDSA

# Initialize (auto-detects GPU)
mdsa = MDSA(
    ollama_base_url="http://localhost:11434",
    enable_rag=True,
    log_level="INFO"
)

# MDSA will log GPU detection:
# [INFO] GPU detected: NVIDIA GeForce RTX 3060 (6GB VRAM)
# [INFO] Ollama will use GPU acceleration
```

### Manual GPU Configuration

```python
from mdsa import MDSA

# Force specific configuration
mdsa = MDSA(
    ollama_base_url="http://localhost:11434",
    enable_rag=True,
    log_level="INFO",
    # GPU settings passed to Ollama
    model_kwargs={
        "num_gpu": 1,  # Use 1 GPU
        "max_new_tokens": 256  # Limit response length to save VRAM
    }
)
```

### Multi-GPU Setup

```python
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '0,1'  # Use GPUs 0 and 1
os.environ['OLLAMA_NUM_GPU'] = '999'        # Use all available

from mdsa import MDSA

mdsa = MDSA(ollama_base_url="http://localhost:11434", enable_rag=True)

# Register domains - Ollama will distribute across GPUs
mdsa.register_domain("domain1", "...", keywords=["..."], model_name="ollama://gemma3:1b")
mdsa.register_domain("domain2", "...", keywords=["..."], model_name="ollama://qwen3:1.7b")
```

---

## Performance Optimization

### Model Selection for GPU

Choose models that fit in VRAM:

| VRAM | Recommended Models | Avoid |
|------|-------------------|-------|
| 3-4GB | gemma3:1b, qwen3:1.7b | 7B+ models |
| 6-8GB | llama3.2:3b, phi3:3.8b, qwen3:1.7b | 13B+ models |
| 12GB+ | llama3.1:8b, mistral:7b, qwen2.5:7b | 70B models |
| 24GB+ | llama3.1:8b, mixtral:8x7b, qwen2.5:14b | Full precision 70B |

### Quantization

Use quantized models to fit more in VRAM:

```bash
# Q4_0 quantization - 4-bit weights (good quality, 4x smaller)
ollama pull llama3.2:3b-instruct-q4_0

# Q5_K quantization - 5-bit weights (better quality, 3x smaller)
ollama pull llama3.1:8b-q5_K_M

# Full precision (largest, best quality)
ollama pull llama3.2:3b
```

### Batch Size Optimization

```python
# MDSA doesn't expose batch size directly, but you can limit concurrent requests
from mdsa import MDSA

mdsa = MDSA(
    ollama_base_url="http://localhost:11434",
    enable_rag=True,
    model_kwargs={"max_new_tokens": 128}  # Shorter responses = more throughput
)
```

### Context Length

```python
# Reduce context length to save VRAM
mdsa.register_domain(
    "domain_name",
    "description",
    keywords=["keyword"],
    model_name="ollama://gemma3:1b",
    model_kwargs={
        "max_new_tokens": 128,  # Limit response length
        "num_ctx": 2048         # Reduce context window (default: 4096)
    }
)
```

---

## Troubleshooting

### Issue: GPU Not Detected

**Symptoms**: Ollama uses CPU despite GPU being available

**Solutions**:

1. **Verify driver installation**:
   ```bash
   nvidia-smi  # Should show GPU info
   ```

2. **Check CUDA_VISIBLE_DEVICES**:
   ```bash
   # Windows
   echo $env:CUDA_VISIBLE_DEVICES

   # Linux/macOS
   echo $CUDA_VISIBLE_DEVICES
   ```

3. **Restart Ollama**:
   ```bash
   pkill ollama && ollama serve
   ```

4. **Check Ollama logs**:
   ```bash
   # Linux/macOS
   journalctl -u ollama -f

   # Or run in foreground
   ollama serve
   ```

### Issue: Out of VRAM

**Symptoms**: Model fails to load, "CUDA out of memory" error

**Solutions**:

1. **Use smaller model**:
   ```bash
   ollama pull gemma3:1b  # Instead of llama3.1:8b
   ```

2. **Use quantized model**:
   ```bash
   ollama pull llama3.2:3b-instruct-q4_0  # Q4_0 quantization
   ```

3. **Reduce concurrent models**:
   ```bash
   export OLLAMA_MAX_LOADED_MODELS=1
   ```

4. **Offload to CPU**:
   ```bash
   export OLLAMA_NUM_GPU=0  # Force CPU mode
   ```

### Issue: Slow Performance with GPU

**Symptoms**: GPU usage is low, inference is slow

**Solutions**:

1. **Check GPU utilization**:
   ```bash
   nvidia-smi -l 1
   ```
   GPU utilization should be >50% during inference.

2. **Ensure model is on GPU**:
   ```bash
   # Run model and check nvidia-smi
   ollama run gemma3:1b "Test"
   ```

3. **Check PCIe bandwidth**:
   ```bash
   nvidia-smi -q | grep "Link Width"
   # Should be x16 or x8, not x1
   ```

4. **Disable CPU offloading**:
   ```bash
   export OLLAMA_NUM_GPU=999  # Force all layers to GPU
   ```

### Issue: Multiple GPUs Not Used

**Symptoms**: Only GPU 0 is used despite having multiple GPUs

**Solutions**:

1. **Set CUDA_VISIBLE_DEVICES**:
   ```bash
   export CUDA_VISIBLE_DEVICES=0,1
   ```

2. **Enable multi-GPU**:
   ```bash
   export OLLAMA_NUM_GPU=999  # Use all available
   ```

3. **Verify all GPUs visible**:
   ```bash
   nvidia-smi -L
   ```

---

## Performance Benchmarks

Expected performance improvements with GPU:

### gemma3:1b (1B parameters)

| Hardware | Tokens/sec | Latency (256 tokens) |
|----------|-----------|----------------------|
| CPU (12-core) | 10-20 tok/s | 12-25 seconds |
| RTX 3060 (6GB) | 80-120 tok/s | 2-3 seconds |
| RTX 4090 (24GB) | 150-200 tok/s | 1-2 seconds |

### llama3.2:3b-instruct-q4_0 (3B parameters)

| Hardware | Tokens/sec | Latency (256 tokens) |
|----------|-----------|----------------------|
| CPU (12-core) | 3-8 tok/s | 30-80 seconds |
| RTX 3060 (6GB) | 40-60 tok/s | 4-6 seconds |
| RTX 4090 (24GB) | 100-140 tok/s | 2-3 seconds |

---

## Next Steps

- [Ollama Setup Guide](OLLAMA_SETUP.md) - Install and configure Ollama
- [Ollama Troubleshooting](OLLAMA_TROUBLESHOOTING.md) - Common issues
- [MDSA User Guide](USER_GUIDE.md) - Full framework documentation

---

## Additional Resources

- **NVIDIA CUDA**: [https://developer.nvidia.com/cuda-downloads](https://developer.nvidia.com/cuda-downloads)
- **AMD ROCm**: [https://rocmdocs.amd.com/](https://rocmdocs.amd.com/)
- **Ollama GPU Docs**: [https://ollama.ai/docs/gpu](https://ollama.ai/docs/gpu)
- **MDSA GitHub**: [https://github.com/VickyVignesh2002/MDSA-Orchestration-Framework](https://github.com/VickyVignesh2002/MDSA-Orchestration-Framework)

---

**Version**: 1.0.1
**Last Updated**: December 2025
**Compatibility**: MDSA Framework v1.0.0+, Ollama 0.1.0+
