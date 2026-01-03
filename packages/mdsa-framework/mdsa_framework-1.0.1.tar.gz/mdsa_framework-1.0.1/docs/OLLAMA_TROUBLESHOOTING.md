# Ollama Troubleshooting Guide for MDSA

Comprehensive troubleshooting guide for Ollama integration with MDSA Framework.

---

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Connection Issues](#connection-issues)
3. [Model Issues](#model-issues)
4. [Performance Issues](#performance-issues)
5. [GPU Issues](#gpu-issues)
6. [Memory Issues](#memory-issues)
7. [MDSA Integration Issues](#mdsa-integration-issues)
8. [Platform-Specific Issues](#platform-specific-issues)
9. [Advanced Debugging](#advanced-debugging)

---

## Installation Issues

### Issue: "ollama: command not found"

**Platforms**: All

**Symptoms**:
```bash
$ ollama --version
ollama: command not found
```

**Solutions**:

1. **Verify Installation**:
   - **Windows**: Check `C:\Users\<YourName>\AppData\Local\Programs\Ollama\`
   - **macOS**: Check `/Applications/Ollama.app`
   - **Linux**: Check `/usr/local/bin/ollama`

2. **Restart Terminal**: Close and reopen terminal/PowerShell

3. **Add to PATH Manually**:

   **Windows (PowerShell)**:
   ```powershell
   $env:Path += ";C:\Users\$env:USERNAME\AppData\Local\Programs\Ollama\bin"
   # Or permanent:
   [System.Environment]::SetEnvironmentVariable('Path', $env:Path + ";C:\Users\$env:USERNAME\AppData\Local\Programs\Ollama\bin", 'User')
   ```

   **Linux/macOS**:
   ```bash
   export PATH=$PATH:/usr/local/bin
   # Or add to ~/.bashrc or ~/.zshrc:
   echo 'export PATH=$PATH:/usr/local/bin' >> ~/.bashrc
   source ~/.bashrc
   ```

4. **Reinstall Ollama**:
   - Download latest from [https://ollama.ai/download](https://ollama.ai/download)
   - Run installer again

---

### Issue: Installation Fails/Hangs

**Platforms**: Windows, macOS

**Symptoms**:
- Installer freezes
- "Installation failed" error
- Incomplete installation

**Solutions**:

1. **Run as Administrator** (Windows):
   - Right-click installer → "Run as administrator"

2. **Disable Antivirus Temporarily**:
   - Some antivirus software blocks Ollama
   - Disable during installation, re-enable after

3. **Check Disk Space**:
   ```bash
   # Linux/macOS
   df -h /usr/local

   # Windows (PowerShell)
   Get-PSDrive C
   ```
   Need at least 5GB free for Ollama + models

4. **Check Prerequisites**:
   - **Windows**: .NET Framework 4.7.2+ required
   - **macOS**: macOS 11.0+ required
   - **Linux**: glibc 2.27+ required

5. **Manual Installation** (Linux):
   ```bash
   curl -L https://ollama.ai/download/ollama-linux-amd64 -o ollama
   chmod +x ollama
   sudo mv ollama /usr/local/bin/
   ```

---

## Connection Issues

### Issue: Connection Refused (MDSA → Ollama)

**Platforms**: All

**Symptoms**:
```python
ConnectionRefusedError: [Errno 111] Connection refused
requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=11434)
```

**Solutions**:

1. **Check if Ollama is Running**:
   ```bash
   # Test connection
   curl http://localhost:11434/api/tags

   # Windows: Check process
   tasklist | findstr ollama

   # Linux/macOS: Check process
   ps aux | grep ollama
   ```

2. **Start Ollama Server**:
   ```bash
   ollama serve
   ```
   Leave this running in a separate terminal.

3. **Check Port Availability**:
   ```bash
   # Windows
   netstat -an | findstr 11434

   # Linux/macOS
   lsof -i :11434
   ```
   If port is in use by another process, change Ollama port:
   ```bash
   # Linux/macOS
   export OLLAMA_HOST=0.0.0.0:11435
   ollama serve

   # Update MDSA connection:
   mdsa = MDSA(ollama_base_url="http://localhost:11435")
   ```

4. **Check Firewall**:
   - **Windows**: Add exception for Ollama in Windows Defender Firewall
   - **Linux**: Check iptables/firewalld rules
   ```bash
   sudo ufw allow 11434/tcp  # Ubuntu/Debian
   ```

5. **Verify Correct URL in MDSA**:
   ```python
   # Make sure URL matches Ollama server
   from mdsa import MDSA
   mdsa = MDSA(
       ollama_base_url="http://localhost:11434",  # Default
       enable_rag=True
   )
   ```

---

### Issue: "Ollama Not Accessible" in MDSA

**Symptoms**:
- MDSA reports "Ollama not accessible"
- Models fail to load

**Solutions**:

1. **Test Ollama Directly**:
   ```bash
   curl http://localhost:11434/api/tags
   ```
   Should return JSON with model list.

2. **Check MDSA Logs**:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)

   from mdsa import MDSA
   mdsa = MDSA(ollama_base_url="http://localhost:11434", log_level="DEBUG")
   ```
   Look for connection errors in output.

3. **Verify Model Name Format**:
   ```python
   # Correct format
   mdsa.register_domain(
       "domain",
       "description",
       keywords=["keyword"],
       model_name="ollama://gemma3:1b"  # ✓ Correct: ollama:// prefix
   )

   # Incorrect format
   model_name="gemma3:1b"  # ✗ Wrong: missing ollama:// prefix
   ```

4. **Test Model Manually**:
   ```bash
   ollama run gemma3:1b "Test"
   ```
   If this works, MDSA should work too.

---

## Model Issues

### Issue: "Model Not Found"

**Symptoms**:
```bash
Error: model 'gemma3:1b' not found
```

**Solutions**:

1. **List Installed Models**:
   ```bash
   ollama list
   ```

2. **Download Missing Model**:
   ```bash
   ollama pull gemma3:1b
   ```

3. **Check Model Name Spelling**:
   ```bash
   # Correct names:
   ollama pull gemma3:1b
   ollama pull qwen3:1.7b
   ollama pull llama3.2:3b-instruct-q4_0

   # Common mistakes:
   ollama pull gemma:1b       # ✗ Wrong: should be gemma3
   ollama pull qwen:1.7b      # ✗ Wrong: should be qwen3
   ```

4. **Use Exact Model Name**:
   ```bash
   ollama list  # Copy exact name from output
   ```

---

### Issue: Model Download Fails

**Symptoms**:
- Timeout errors
- "Failed to download" errors
- Incomplete downloads
- Network errors

**Solutions**:

1. **Check Internet Connection**:
   ```bash
   ping ollama.ai
   ```

2. **Retry Download**:
   ```bash
   ollama pull gemma3:1b
   ```
   Ollama resumes from where it stopped.

3. **Check Disk Space**:
   ```bash
   # Linux/macOS
   df -h ~/.ollama

   # Windows
   Get-PSDrive C
   ```
   Model sizes:
   - gemma3:1b → ~1GB
   - qwen3:1.7b → ~2GB
   - llama3.2:3b → ~2GB
   - llama3.1:8b → ~4.7GB

4. **Clear Cache and Retry**:
   ```bash
   # macOS/Linux
   rm -rf ~/.ollama/models/blobs/*
   ollama pull gemma3:1b

   # Windows (PowerShell)
   Remove-Item -Recurse -Force "$env:USERPROFILE\.ollama\models\blobs\*"
   ollama pull gemma3:1b
   ```

5. **Use Proxy** (if behind corporate firewall):
   ```bash
   # Linux/macOS
   export HTTP_PROXY=http://proxy.example.com:8080
   export HTTPS_PROXY=http://proxy.example.com:8080
   ollama pull gemma3:1b

   # Windows
   $env:HTTP_PROXY="http://proxy.example.com:8080"
   $env:HTTPS_PROXY="http://proxy.example.com:8080"
   ollama pull gemma3:1b
   ```

---

### Issue: Wrong Model Version Downloaded

**Symptoms**:
- Downloaded model is different than expected
- Model behaves unexpectedly

**Solutions**:

1. **Check Model Tags**:
   ```bash
   ollama list
   ```

2. **Remove and Re-download**:
   ```bash
   ollama rm gemma3:1b
   ollama pull gemma3:1b
   ```

3. **Specify Exact Tag**:
   ```bash
   # Default (usually latest)
   ollama pull llama3.2

   # Specific version
   ollama pull llama3.2:3b-instruct-q4_0
   ```

---

## Performance Issues

### Issue: Very Slow Inference (CPU Mode)

**Symptoms**:
- 5-30 seconds per response
- High CPU usage
- Low/no GPU usage

**Solutions**:

1. **Verify GPU is Available**:
   ```bash
   nvidia-smi  # NVIDIA
   system_profiler SPHardwareDataType | grep Chip  # macOS
   ```

2. **Check if Ollama is Using GPU**:
   ```bash
   # Run model and watch GPU usage
   ollama run gemma3:1b "Test" &
   nvidia-smi -l 1  # Watch GPU usage
   ```

3. **Set GPU Environment Variables**:
   ```bash
   # Windows (PowerShell)
   $env:CUDA_VISIBLE_DEVICES=0
   $env:OLLAMA_NUM_GPU=1

   # Linux/macOS
   export CUDA_VISIBLE_DEVICES=0
   export OLLAMA_NUM_GPU=1
   ```

4. **Restart Ollama**:
   ```bash
   pkill ollama && ollama serve
   ```

5. **Use Smaller Model**:
   ```bash
   # Switch from larger to smaller model
   ollama pull gemma3:1b  # Fastest
   ```

6. **See [GPU Configuration Guide](GPU_CONFIGURATION.md)** for detailed GPU setup.

---

### Issue: Slow on GPU (Lower than Expected Performance)

**Symptoms**:
- GPU is being used, but still slow
- Low GPU utilization (<50%)

**Solutions**:

1. **Check GPU Utilization**:
   ```bash
   nvidia-smi -l 1
   ```
   Should be >50% during inference.

2. **Ensure Full GPU Loading**:
   ```bash
   export OLLAMA_NUM_GPU=999  # Force all layers to GPU
   pkill ollama && ollama serve
   ```

3. **Check PCIe Bandwidth**:
   ```bash
   nvidia-smi -q | grep "Link Width"
   ```
   Should be x16 or x8. If x1, reseat GPU or use different slot.

4. **Use Quantized Model**:
   ```bash
   # Q4_0 is faster than full precision
   ollama pull llama3.2:3b-instruct-q4_0
   ```

5. **Reduce Context Length**:
   ```python
   mdsa.register_domain(
       "domain",
       "description",
       keywords=["keyword"],
       model_name="ollama://gemma3:1b",
       model_kwargs={"num_ctx": 2048}  # Reduce from 4096
   )
   ```

---

### Issue: High Memory Usage

**Symptoms**:
- System runs out of RAM
- Swap usage is high
- System becomes unresponsive

**Solutions**:

1. **Limit Models in Memory**:
   ```bash
   export OLLAMA_MAX_LOADED_MODELS=1  # Only 1 model in RAM
   pkill ollama && ollama serve
   ```

2. **Use Smaller Models**:
   ```bash
   ollama pull gemma3:1b  # 1GB instead of llama3.1:8b (4.7GB)
   ```

3. **Close Other Applications**:
   - Free up system RAM before running Ollama

4. **Add More RAM/Swap** (Linux):
   ```bash
   # Add swap space
   sudo fallocate -l 8G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

---

## GPU Issues

### Issue: GPU Not Detected

**Symptoms**:
- Ollama always uses CPU
- `nvidia-smi` shows GPU, but Ollama doesn't use it

**Solutions**:

1. **Verify CUDA Installation**:
   ```bash
   nvidia-smi
   ```
   Should show driver version and CUDA version.

2. **Set Environment Variables**:
   ```bash
   export CUDA_VISIBLE_DEVICES=0
   export OLLAMA_NUM_GPU=1
   ```

3. **Restart Ollama**:
   ```bash
   pkill ollama
   ollama serve
   ```

4. **Check Ollama Logs**:
   ```bash
   # Run in foreground to see logs
   ollama serve
   ```
   Look for CUDA/GPU detection messages.

5. **Reinstall NVIDIA Drivers**:
   - See [GPU Configuration Guide](GPU_CONFIGURATION.md)

---

### Issue: Out of VRAM

**Symptoms**:
```bash
CUDA error: out of memory
```

**Solutions**:

1. **Use Smaller Model**:
   ```bash
   ollama pull gemma3:1b  # 1GB VRAM
   ollama pull qwen3:1.7b  # 2-3GB VRAM
   ```

2. **Use Quantized Model**:
   ```bash
   # Q4_0 uses ~half the VRAM of full precision
   ollama pull llama3.2:3b-instruct-q4_0
   ```

3. **Limit Concurrent Models**:
   ```bash
   export OLLAMA_MAX_LOADED_MODELS=1
   ```

4. **Reduce Context Window**:
   ```python
   model_kwargs={"num_ctx": 2048}  # Down from 4096
   ```

5. **Offload to CPU**:
   ```bash
   export OLLAMA_NUM_GPU=0  # Force CPU mode
   ```

---

### Issue: Multiple GPUs Not Used

**Symptoms**:
- Have 2+ GPUs, but only GPU 0 is used

**Solutions**:

1. **Enable All GPUs**:
   ```bash
   export CUDA_VISIBLE_DEVICES=0,1
   export OLLAMA_NUM_GPU=999  # Use all available layers
   pkill ollama && ollama serve
   ```

2. **Verify GPUs Visible**:
   ```bash
   nvidia-smi -L
   ```
   Should list all GPUs.

3. **Check SLI/NVLink** (if applicable):
   - Some multi-GPU setups require special configuration

---

## Memory Issues

### Issue: Ollama Crashes with Out of Memory

**Symptoms**:
- Ollama process crashes
- "Out of memory" errors
- System freezes

**Solutions**:

1. **Check Available RAM**:
   ```bash
   # Linux
   free -h

   # macOS
   vm_stat

   # Windows
   systeminfo | findstr Memory
   ```

2. **Use Smaller Model**:
   ```bash
   ollama pull gemma3:1b  # Requires ~2GB RAM total
   ```

3. **Close Other Applications**:
   - Free up RAM before running Ollama

4. **Increase Swap** (Linux):
   ```bash
   sudo fallocate -l 8G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

5. **Limit Loaded Models**:
   ```bash
   export OLLAMA_MAX_LOADED_MODELS=1
   ```

---

## MDSA Integration Issues

### Issue: MDSA Can't Connect to Ollama

**Symptoms**:
```python
ConnectionError: Ollama server not accessible at http://localhost:11434
```

**Solutions**:

1. **Start Ollama First**:
   ```bash
   ollama serve
   ```
   Keep it running in a separate terminal.

2. **Test Connection Manually**:
   ```bash
   curl http://localhost:11434/api/tags
   ```

3. **Check MDSA Configuration**:
   ```python
   from mdsa import MDSA
   mdsa = MDSA(
       ollama_base_url="http://localhost:11434",  # Correct URL
       enable_rag=True,
       log_level="DEBUG"  # Enable debug logs
   )
   ```

4. **Check Firewall**:
   - Ensure localhost connections are allowed

---

### Issue: Model Name Not Recognized in MDSA

**Symptoms**:
- MDSA reports "Invalid model name"
- Model doesn't load

**Solutions**:

1. **Use Correct Format**:
   ```python
   # Correct
   model_name="ollama://gemma3:1b"  # ✓ With ollama:// prefix

   # Incorrect
   model_name="gemma3:1b"  # ✗ Missing prefix
   model_name="ollama:gemma3:1b"  # ✗ Wrong prefix format
   ```

2. **Verify Model is Downloaded**:
   ```bash
   ollama list  # Should show gemma3:1b
   ```

3. **Test Model Directly**:
   ```bash
   ollama run gemma3:1b "Test"
   ```

---

### Issue: RAG Not Working with Ollama

**Symptoms**:
- Responses don't include knowledge base information
- RAG retrieval seems to be skipped

**Solutions**:

1. **Verify RAG is Enabled**:
   ```python
   mdsa = MDSA(
       ollama_base_url="http://localhost:11434",
       enable_rag=True,  # Must be True
       rag_global_kb_path="./knowledge_base/global",
       rag_local_kb_path="./knowledge_base/local"
   )
   ```

2. **Check Knowledge Base Structure**:
   ```
   knowledge_base/
   ├── global/
   │   ├── file1.md
   │   └── file2.txt
   └── local/
       └── domain_name/
           ├── doc1.md
           └── doc2.txt
   ```

3. **Verify Documents Exist**:
   ```bash
   # Linux/macOS
   find knowledge_base -name "*.md" -o -name "*.txt"

   # Windows
   dir knowledge_base /s /b
   ```

4. **Check MDSA Logs**:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)

   from mdsa import MDSA
   mdsa = MDSA(..., log_level="DEBUG")
   ```
   Look for RAG retrieval logs.

---

## Platform-Specific Issues

### Windows-Specific Issues

#### Issue: PowerShell Execution Policy

**Symptoms**:
```powershell
ollama : File cannot be loaded because running scripts is disabled
```

**Solution**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Issue: Windows Defender Blocks Ollama

**Symptoms**:
- Installation fails
- Ollama won't start
- Files disappear after installation

**Solution**:
1. Open Windows Security
2. Virus & threat protection → Manage settings
3. Add exclusion for Ollama folder:
   `C:\Users\<YourName>\AppData\Local\Programs\Ollama`

---

### macOS-Specific Issues

#### Issue: "Ollama.app is damaged and can't be opened"

**Symptoms**:
- macOS prevents opening Ollama

**Solution**:
```bash
xattr -d com.apple.quarantine /Applications/Ollama.app
```

#### Issue: Rosetta 2 Required (M1/M2/M3)

**Symptoms**:
- Asked to install Rosetta

**Solution**:
```bash
softwareupdate --install-rosetta --agree-to-license
```

---

### Linux-Specific Issues

#### Issue: Permission Denied

**Symptoms**:
```bash
bash: /usr/local/bin/ollama: Permission denied
```

**Solution**:
```bash
chmod +x /usr/local/bin/ollama
```

#### Issue: systemd Service Won't Start

**Symptoms**:
```bash
sudo systemctl status ollama
● ollama.service - failed
```

**Solution**:
1. Check logs:
   ```bash
   sudo journalctl -u ollama -n 50
   ```

2. Verify binary location:
   ```bash
   which ollama
   ```

3. Update service file path:
   ```bash
   sudo nano /etc/systemd/system/ollama.service
   # Update ExecStart path
   sudo systemctl daemon-reload
   sudo systemctl restart ollama
   ```

---

## Advanced Debugging

### Enable Debug Logs

**Ollama**:
```bash
# Linux/macOS
OLLAMA_DEBUG=1 ollama serve

# Windows
$env:OLLAMA_DEBUG=1
ollama serve
```

**MDSA**:
```python
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from mdsa import MDSA
mdsa = MDSA(log_level="DEBUG")
```

### Test Ollama API Directly

```bash
# List models
curl http://localhost:11434/api/tags

# Generate response
curl http://localhost:11434/api/generate -d '{
  "model": "gemma3:1b",
  "prompt": "Hello!",
  "stream": false
}'

# Chat endpoint
curl http://localhost:11434/api/chat -d '{
  "model": "gemma3:1b",
  "messages": [{"role": "user", "content": "Hello!"}],
  "stream": false
}'
```

### Check Ollama Logs

**Linux (systemd)**:
```bash
sudo journalctl -u ollama -f
```

**macOS**:
```bash
log stream --predicate 'process == "ollama"' --level debug
```

**Windows**:
- Run `ollama serve` in foreground to see logs

### Network Diagnostics

```bash
# Check if Ollama port is open
telnet localhost 11434

# Check network connectivity
netstat -an | grep 11434  # Linux/macOS
netstat -an | findstr 11434  # Windows

# Test with curl
curl -v http://localhost:11434/api/tags
```

---

## Getting Help

If you've tried all solutions and still have issues:

1. **Check GitHub Issues**: [MDSA Issues](https://github.com/VickyVignesh2002/MDSA-Orchestration-Framework/issues)
2. **Check Ollama Issues**: [Ollama GitHub](https://github.com/ollama/ollama/issues)
3. **Create New Issue** with:
   - Error message (full stack trace)
   - System info (OS, GPU, RAM)
   - Ollama version (`ollama --version`)
   - MDSA version
   - Steps to reproduce
   - Relevant logs

---

## Additional Resources

- [Ollama Setup Guide](OLLAMA_SETUP.md)
- [GPU Configuration Guide](GPU_CONFIGURATION.md)
- [MDSA User Guide](USER_GUIDE.md)
- [Ollama Official Docs](https://ollama.ai/docs)
- [MDSA GitHub](https://github.com/VickyVignesh2002/MDSA-Orchestration-Framework)

---

**Version**: 1.0.1
**Last Updated**: December 2025
**Compatibility**: MDSA Framework v1.0.0+, Ollama 0.1.0+
