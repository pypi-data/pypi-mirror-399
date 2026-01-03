# Ollama Setup Guide for MDSA Framework

Complete guide to setting up Ollama for use with MDSA's Phase 3+ features (RAG + Domain Specialists).

---

## Table of Contents

1. [What is Ollama?](#what-is-ollama)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Starting Ollama Server](#starting-ollama-server)
5. [Downloading Models](#downloading-models)
6. [Verification](#verification)
7. [MDSA Integration](#mdsa-integration)
8. [Troubleshooting](#troubleshooting)

---

## What is Ollama?

[Ollama](https://ollama.ai) is a local LLM runtime that allows you to run large language models on your own hardware. It:

- Runs models entirely offline (no API costs)
- Supports GPU acceleration (CUDA, ROCm, Metal)
- Provides a simple HTTP API
- Manages model downloads and updates
- Works with various model architectures (Llama, Gemma, Qwen, Phi, etc.)

MDSA uses Ollama to power domain-specific models in Phase 3+.

---

## Prerequisites

### System Requirements

**Minimum (CPU Only)**:
- **CPU**: 4+ cores
- **RAM**: 8GB+ (16GB recommended)
- **Storage**: 10GB+ free space per model
- **OS**: Windows 10/11, macOS 11+, Linux (Ubuntu 18.04+, Debian, Fedora, etc.)

**Recommended (with GPU)**:
- **GPU**: NVIDIA GPU with 3GB+ VRAM (6GB+ recommended)
- **CUDA**: Version 11.8 or later (NVIDIA GPUs)
- **RAM**: 16GB+ system memory
- **Storage**: 20GB+ for multiple models

### Software Prerequisites

- **Python**: 3.9+ (for MDSA framework)
- **pip**: Latest version
- **curl** or **wget**: For verification commands

---

## Installation

### Windows

1. **Download Ollama**:
   - Visit [https://ollama.ai/download](https://ollama.ai/download)
   - Click "Download for Windows"
   - Run the installer (`OllamaSetup.exe`)

2. **Run Installer**:
   - Follow the installation wizard
   - Default installation path: `C:\Users\<YourName>\AppData\Local\Programs\Ollama`
   - Installer will add Ollama to your PATH automatically

3. **Verify Installation**:
   ```powershell
   ollama --version
   ```
   Expected output: `ollama version is X.Y.Z`

### macOS

1. **Download Ollama**:
   - Visit [https://ollama.ai/download](https://ollama.ai/download)
   - Click "Download for Mac"
   - Open the DMG file and drag Ollama to Applications

2. **Verify Installation**:
   ```bash
   ollama --version
   ```

**Alternative (Homebrew)**:
```bash
brew install ollama
```

### Linux

**Ubuntu/Debian**:
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Manual Installation**:
```bash
# Download binary
curl -L https://ollama.ai/download/ollama-linux-amd64 -o ollama

# Make executable
chmod +x ollama

# Move to PATH
sudo mv ollama /usr/local/bin/

# Verify
ollama --version
```

**Fedora/RHEL**:
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

---

## Starting Ollama Server

Ollama runs as a local HTTP server on `http://localhost:11434`.

### Windows

**Option 1: Automatic (Recommended)**:
- Ollama starts automatically after installation
- Runs in the background as a system service

**Option 2: Manual Start**:
```powershell
# Open PowerShell/Command Prompt
ollama serve
```

**Check if Running**:
```powershell
# Check process
tasklist | findstr ollama

# Or test API
curl http://localhost:11434/api/tags
```

### macOS

**Option 1: Automatic**:
- Ollama starts automatically after installation
- Managed by launchd

**Option 2: Manual Start**:
```bash
ollama serve
```

**Check if Running**:
```bash
# Check process
ps aux | grep ollama

# Or test API
curl http://localhost:11434/api/tags
```

### Linux

**Start Ollama**:
```bash
# Run in background
ollama serve &

# Or run in foreground (for debugging)
ollama serve
```

**Run as Systemd Service** (Recommended for production):

1. Create service file:
```bash
sudo nano /etc/systemd/system/ollama.service
```

2. Add content:
```ini
[Unit]
Description=Ollama LLM Server
After=network.target

[Service]
Type=simple
User=ollama
Group=ollama
ExecStart=/usr/local/bin/ollama serve
Restart=always
RestartSec=3
Environment="OLLAMA_HOST=0.0.0.0:11434"

[Install]
WantedBy=multi-user.target
```

3. Start service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable ollama
sudo systemctl start ollama
sudo systemctl status ollama
```

---

## Downloading Models

### Recommended Models for MDSA

Choose based on your hardware and latency requirements:

| Model | Size | VRAM | Speed | Quality | Use Case |
|-------|------|------|-------|---------|----------|
| `gemma3:1b` | 1GB | 2GB | Fastest | Good | High-throughput applications |
| `qwen3:1.7b` | 2GB | 3GB | Fast | Better | Balanced performance |
| `llama3.2:3b-instruct-q4_0` | 2GB | 3GB | Medium | Best (small) | Production quality |
| `phi3:3.8b` | 2.3GB | 4GB | Medium | Excellent | Reasoning tasks |
| `llama3.1:8b` | 4.7GB | 6GB | Slower | Excellent | High-quality responses |

### Downloading Models

**Basic Download**:
```bash
# Download a model
ollama pull gemma3:1b

# Download multiple models
ollama pull qwen3:1.7b
ollama pull llama3.2:3b-instruct-q4_0
```

**Check Download Progress**:
```bash
# List installed models
ollama list
```

Expected output:
```
NAME                          ID              SIZE    MODIFIED
gemma3:1b                     abc123def456    1.0 GB  2 minutes ago
qwen3:1.7b                    def789ghi012    2.0 GB  5 minutes ago
```

### Testing a Model

```bash
# Interactive chat
ollama run gemma3:1b

# One-shot query
ollama run gemma3:1b "What is the capital of France?"
```

Type `/bye` to exit interactive mode.

---

## Verification

### 1. Check Server Status

```bash
# Windows (PowerShell)
Invoke-WebRequest -Uri http://localhost:11434/api/tags | Select-Object -ExpandProperty Content

# Linux/macOS
curl http://localhost:11434/api/tags
```

Expected response:
```json
{
  "models": [
    {
      "name": "gemma3:1b",
      "modified_at": "2025-12-31T12:00:00Z",
      "size": 1000000000,
      "digest": "abc123...",
      "details": {...}
    }
  ]
}
```

### 2. Test Model Inference

```bash
curl http://localhost:11434/api/generate -d '{
  "model": "gemma3:1b",
  "prompt": "Hello, how are you?",
  "stream": false
}'
```

### 3. Check GPU Access (if available)

```bash
# This will show GPU info if detected
ollama run gemma3:1b "Test"
```

Look for output like:
```
Using GPU: NVIDIA GeForce RTX 3060 (CUDA)
```

If you see "Using CPU" but have a GPU, see [GPU Configuration Guide](GPU_CONFIGURATION.md).

---

## MDSA Integration

### Basic Setup

```python
from mdsa import MDSA

# Initialize with Ollama support
mdsa = MDSA(
    ollama_base_url="http://localhost:11434",  # Default Ollama URL
    enable_rag=True,  # Enable RAG for domain knowledge
    log_level="INFO"
)

# Register a domain with Ollama model
mdsa.register_domain(
    name="tech_support",
    description="Technical support and troubleshooting",
    keywords=["error", "bug", "crash", "fix", "troubleshoot"],
    model_name="ollama://gemma3:1b"  # Use ollama:// prefix
)

# Process a query
response = mdsa.process_request("How do I fix error code 404?")
print(response["response"])
```

### Multi-Domain Setup

```python
from mdsa import MDSA

mdsa = MDSA(ollama_base_url="http://localhost:11434", enable_rag=True)

# Domain 1: Fast responses with lightweight model
mdsa.register_domain(
    "quick_questions",
    "Simple FAQs and quick queries",
    keywords=["what", "when", "who", "where"],
    model_name="ollama://gemma3:1b"  # Fastest
)

# Domain 2: Complex reasoning with better model
mdsa.register_domain(
    "technical_analysis",
    "In-depth technical explanations",
    keywords=["analyze", "explain", "detail", "architecture"],
    model_name="ollama://llama3.2:3b-instruct-q4_0"  # Better quality
)

# Domain 3: Code generation
mdsa.register_domain(
    "code_assistant",
    "Programming help and code generation",
    keywords=["code", "function", "class", "debug", "implement"],
    model_name="ollama://qwen3:1.7b"  # Good for code
)
```

### With RAG Knowledge Bases

```python
from mdsa import MDSA

mdsa = MDSA(
    ollama_base_url="http://localhost:11434",
    enable_rag=True,
    rag_global_kb_path="./knowledge_base/global",  # Shared docs
    rag_local_kb_path="./knowledge_base/local"     # Domain-specific docs
)

# Organize your knowledge base:
# knowledge_base/
# ├── global/
# │   ├── company_policies.md
# │   └── general_faq.txt
# └── local/
#     ├── tech_support/
#     │   ├── troubleshooting.md
#     │   └── error_codes.txt
#     └── hr_policies/
#         └── leave_policy.md

mdsa.register_domain(
    "tech_support",
    "Technical support",
    keywords=["error", "bug", "issue"],
    model_name="ollama://gemma3:1b"
)

# Now queries will retrieve relevant docs from RAG and use Ollama for response
```

---

## Troubleshooting

### Issue: "ollama: command not found"

**Solution**:
1. Verify installation: Check if Ollama is installed in your Applications (macOS) or Program Files (Windows)
2. Restart your terminal to refresh PATH
3. Windows: Manually add to PATH:
   ```powershell
   $env:Path += ";C:\Users\<YourName>\AppData\Local\Programs\Ollama\bin"
   ```

### Issue: "Connection refused" from MDSA

**Symptom**: `ConnectionRefusedError: [Errno 111] Connection refused`

**Solutions**:
1. **Check if Ollama is running**:
   ```bash
   curl http://localhost:11434/api/tags
   ```

2. **Start Ollama server**:
   ```bash
   ollama serve
   ```

3. **Check port availability**:
   ```bash
   # Windows
   netstat -an | findstr 11434

   # Linux/macOS
   lsof -i :11434
   ```

### Issue: Model Download Fails

**Symptoms**: Timeout, network errors, incomplete downloads

**Solutions**:
1. **Check internet connection**
2. **Retry download**:
   ```bash
   ollama pull gemma3:1b
   ```
3. **Clear cache and retry**:
   ```bash
   # macOS/Linux
   rm -rf ~/.ollama/models/blobs/*

   # Windows
   del /s C:\Users\<YourName>\.ollama\models\blobs\*
   ```

### Issue: Model Runs Slow (CPU-only)

**Symptom**: High latency (>5 seconds per response)

**Solutions**:
1. **Use smaller model**: Switch to `gemma3:1b` instead of larger models
2. **Enable GPU**: See [GPU Configuration Guide](GPU_CONFIGURATION.md)
3. **Reduce context length** in MDSA:
   ```python
   mdsa.register_domain(
       "domain_name",
       "description",
       keywords=["keyword"],
       model_name="ollama://gemma3:1b",
       model_kwargs={"max_new_tokens": 128}  # Limit response length
   )
   ```

### Issue: Out of Memory

**Symptom**: Model fails to load, system freezes

**Solutions**:
1. **Use quantized models** (Q4_0 suffix): `llama3.2:3b-instruct-q4_0`
2. **Close other applications** to free RAM
3. **Use smaller model**: Try `gemma3:1b` (1GB) instead of `llama3.1:8b` (4.7GB)

---

## Next Steps

- [GPU Configuration Guide](GPU_CONFIGURATION.md) - Optimize GPU usage
- [Ollama Troubleshooting](OLLAMA_TROUBLESHOOTING.md) - Common issues and solutions
- [MDSA User Guide](USER_GUIDE.md) - Complete framework documentation

---

## Additional Resources

- **Ollama Official Docs**: [https://ollama.ai/docs](https://ollama.ai/docs)
- **Model Library**: [https://ollama.ai/library](https://ollama.ai/library)
- **MDSA GitHub**: [https://github.com/VickyVignesh2002/MDSA-Orchestration-Framework](https://github.com/VickyVignesh2002/MDSA-Orchestration-Framework)
- **Report Issues**: [GitHub Issues](https://github.com/VickyVignesh2002/MDSA-Orchestration-Framework/issues)

---

**Version**: 1.0.1
**Last Updated**: December 2025
**Compatibility**: MDSA Framework v1.0.0+
