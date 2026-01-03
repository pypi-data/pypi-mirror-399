# MDSA Setup Guide
## Quick Start to Production Deployment

---

## Table of Contents

1. [Quick Start (5 minutes)](#quick-start)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Running the Framework](#running-the-framework)
5. [Testing](#testing)
6. [Production Deployment](#production-deployment)
7. [Troubleshooting](#troubleshooting)

---

## Quick Start

### 1. Install MDSA

```bash
# Option A: From PyPI (when published)
pip install mdsa-framework

# Option B: From source
git clone https://github.com/your-org/mdsa-framework.git
cd mdsa-framework
pip install -e .
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and set your API keys (if using cloud models)
# For local-only deployment, default values work fine
```

### 3. Start Services

```bash
# Terminal 1: Start Dashboard
python mdsa/ui/dashboard/app.py

# Terminal 2: Start Chatbot (example app)
python examples/medical_chatbot/app/enhanced_medical_chatbot_fixed.py
```

### 4. Access

- **Dashboard:** http://localhost:9000
- **Chatbot:** http://localhost:7860

That's it! You're running MDSA locally with zero configuration.

---

## Installation

### Prerequisites

**System Requirements:**
- Python 3.9 or higher
- 8GB+ RAM (16GB recommended)
- CPU with 4+ cores (or GPU for better performance)
- 10GB free disk space

**Supported Platforms:**
- Windows 10/11
- Ubuntu 20.04+
- macOS 12+

### Step-by-Step Installation

#### 1. Create Virtual Environment

```bash
# Create environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Unix/Mac)
source venv/bin/activate
```

#### 2. Install Dependencies

```bash
# Core dependencies
pip install -r requirements.txt

# Optional: GPU support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Optional: Development tools
pip install -r requirements-dev.txt
```

#### 3. Install MDSA

```bash
# Development installation (editable)
pip install -e .

# Or production installation
pip install .
```

#### 4. Verify Installation

```bash
# Check imports
python -c "from mdsa import TinyBERTOrchestrator; print('Success!')"

# Run automated tests
python test_all_fixes.py
```

---

## Configuration

### Environment Variables

**File:** `.env`

```bash
# === Model Configuration ===
ROUTER_MODEL=prajjwal1/bert-tiny
EMBEDDER_MODEL=sentence-transformers/all-MiniLM-L6-v2

# === Ollama Configuration (Local Models) ===
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=deepseek-v3.1

# === Cloud API Keys (Optional) ===
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here

# === Performance Settings ===
MAX_CACHE_SIZE=100
ENABLE_RESPONSE_CACHE=true
ENABLE_EMBEDDING_CACHE=true

# === Dashboard Settings ===
DASHBOARD_HOST=0.0.0.0
DASHBOARD_PORT=9000

# === Chatbot Settings ===
CHATBOT_HOST=0.0.0.0
CHATBOT_PORT=7860
```

### Domain Configuration

**File:** `configs/framework_config.yaml`

```yaml
orchestration:
  strategy: "hybrid"  # direct, reasoning_first, hybrid
  router_model: "prajjwal1/bert-tiny"
  reasoner_model: "microsoft/phi-2"
  reasoner_enabled: false

domains:
  clinical_diagnosis:
    description: "Medical diagnosis and differential diagnosis"
    keywords: ["diagnosis", "symptoms", "condition", "disease"]
    model: "ollama:deepseek-v3.1"
    rag_enabled: true

  treatment_planning:
    description: "Treatment recommendations and therapy planning"
    keywords: ["treatment", "therapy", "medication"]
    model: "ollama:deepseek-v3.1"
    rag_enabled: true

performance:
  cache_embeddings: true
  cache_responses: true
  max_cache_size: 100
```

---

## Running the Framework

### Dashboard (Monitoring & Admin)

```bash
# Start dashboard
python mdsa/ui/dashboard/app.py

# Access at: http://localhost:9000

# Available pages:
# - /               Welcome and overview
# - /monitor        Real-time monitoring
# - /models         Model configuration
# - /domains        Domain management
# - /rag            RAG knowledge base
```

### Medical Chatbot (Example Application)

```bash
# Start chatbot
python examples/medical_chatbot/app/enhanced_medical_chatbot_fixed.py

# Access at: http://localhost:7860

# Try queries:
# - "Patient has chest pain and fever"
# - "What treatment for diabetes?"
# - "Interpret CBC results: WBC 15000"
```

### Python API Usage

```python
from mdsa import TinyBERTOrchestrator
from mdsa.memory import DualRAG

# Initialize orchestrator
orchestrator = TinyBERTOrchestrator()

# Register domain
orchestrator.register_domain(
    name="medical",
    description="Medical diagnosis and treatment",
    keywords=["diagnosis", "treatment", "symptoms"]
)

# Process query
result = orchestrator.process_request("Patient has chest pain")
print(f"Domain: {result['domain']}")
print(f"Response: {result['response']}")
```

---

## Testing

### Automated Tests

```bash
# Run all tests
python test_all_fixes.py

# Expected output:
# ✓ 9+ tests passed
# ✓ All critical fixes verified
```

### Manual Testing Checklist

**1. Performance - Domain Embedding Cache**
- [ ] Start dashboard
- [ ] Check logs for "Precomputing embeddings for X domains"
- [ ] Verify classification time <100ms

**2. Performance - Response Cache**
- [ ] Start chatbot
- [ ] Send query: "Patient has chest pain"
- [ ] Note response time (600-2000ms)
- [ ] Send SAME query again
- [ ] Verify `[CACHE HIT]` in console and <10ms response

**3. Monitoring - Request Tracking**
- [ ] Start both dashboard and chatbot
- [ ] Send chatbot query
- [ ] Open http://localhost:9000/monitor
- [ ] Verify graph shows your query (not demo data)

**4. RAG - Knowledge Retrieval**
- [ ] Send medical query in chatbot
- [ ] Check "RAG Context" section in response
- [ ] Verify relevant documents retrieved

---

## Production Deployment

### Option 1: Docker (Recommended)

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir .

# Expose ports
EXPOSE 9000 7860

# Start services
CMD ["python", "mdsa/ui/dashboard/app.py"]
```

```bash
# Build and run
docker build -t mdsa-framework .
docker run -p 9000:9000 -p 7860:7860 mdsa-framework
```

### Option 2: Systemd Service (Linux)

```ini
# /etc/systemd/system/mdsa-dashboard.service
[Unit]
Description=MDSA Dashboard
After=network.target

[Service]
Type=simple
User=mdsa
WorkingDirectory=/opt/mdsa
Environment="PATH=/opt/mdsa/venv/bin"
ExecStart=/opt/mdsa/venv/bin/python mdsa/ui/dashboard/app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl enable mdsa-dashboard
sudo systemctl start mdsa-dashboard
sudo systemctl status mdsa-dashboard
```

### Option 3: Nginx Reverse Proxy

```nginx
# /etc/nginx/sites-available/mdsa
server {
    listen 80;
    server_name mdsa.example.com;

    location / {
        proxy_pass http://localhost:9000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /chatbot {
        proxy_pass http://localhost:7860;
        proxy_set_header Host $host;
    }
}
```

### Production Checklist

- [ ] Use production WSGI server (Gunicorn, uWSGI)
- [ ] Enable HTTPS with SSL certificate
- [ ] Set up monitoring and logging
- [ ] Configure automatic restarts
- [ ] Set resource limits (memory, CPU)
- [ ] Enable firewall rules
- [ ] Set up backup strategy for knowledge base
- [ ] Configure CORS properly
- [ ] Use environment variables for secrets
- [ ] Enable rate limiting

---

## Troubleshooting

### Common Issues

#### 1. Port Already in Use

**Error:** `Address already in use: 9000`

**Solution:**
```bash
# Find process using port
lsof -i :9000  # Unix
netstat -ano | findstr :9000  # Windows

# Kill process or change port in .env
```

#### 2. Models Not Loading

**Error:** `Model prajjwal1/bert-tiny not found`

**Solution:**
```bash
# Clear Hugging Face cache
rm -rf ~/.cache/huggingface

# Re-download models
python -c "from transformers import AutoModel; AutoModel.from_pretrained('prajjwal1/bert-tiny')"
```

#### 3. Out of Memory

**Error:** `CUDA out of memory` or `MemoryError`

**Solution:**
```python
# In .env, disable Phi-2 reasoner
REASONER_ENABLED=false

# Reduce cache size
MAX_CACHE_SIZE=50

# Use CPU instead of GPU
DEVICE=cpu
```

#### 4. Ollama Connection Failed

**Error:** `Failed to connect to Ollama at http://localhost:11434`

**Solution:**
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh  # Linux/Mac
# Or download from https://ollama.com/download  # Windows

# Start Ollama
ollama serve

# Pull required model
ollama pull deepseek-v3.1
```

#### 5. Dashboard Shows Demo Data

**Symptom:** Monitoring graph doesn't update with real requests

**Check:**
1. Both dashboard and chatbot running?
2. Check dashboard console for `[Track] Received request from...`
3. Verify tracking endpoint: `curl http://localhost:9000/api/requests/track`

**Solution:**
```bash
# Restart both services
# Ensure chatbot has tracking integration (fixed in v1.0.0)
```

---

## Performance Tuning

### For Better Latency

```bash
# Use GPU
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# In .env
DEVICE=cuda

# Reduce RAG retrieval
RAG_TOP_K=3  # Default: 5
```

### For Better Accuracy

```bash
# Enable Phi-2 reasoner for complex queries
REASONER_ENABLED=true

# Increase RAG context
RAG_TOP_K=5

# Use larger embedding model
EMBEDDER_MODEL=sentence-transformers/all-mpnet-base-v2
```

### For Lower Memory

```bash
# Disable reasoner
REASONER_ENABLED=false

# Reduce cache
MAX_CACHE_SIZE=25

# Use smaller models
ROUTER_MODEL=prajjwal1/bert-tiny  # Already smallest
```

---

## Next Steps

1. **Customize Domains:** Edit `configs/framework_config.yaml`
2. **Add Knowledge:** Use dashboard RAG page to upload documents
3. **Integrate:** Use Python API in your application
4. **Monitor:** Check dashboard analytics regularly
5. **Scale:** Deploy with Docker/Kubernetes for production

---

## Support

- **Documentation:** [docs/](docs/)
- **Issues:** GitHub Issues
- **Research Paper:** [docs/RESEARCH_PAPER_CONTENT.md](docs/RESEARCH_PAPER_CONTENT.md)
- **API Reference:** [docs/API.md](docs/API.md)

---

**Version:** 1.0.0
**Last Updated:** December 24, 2025
**Status:** Production Ready
