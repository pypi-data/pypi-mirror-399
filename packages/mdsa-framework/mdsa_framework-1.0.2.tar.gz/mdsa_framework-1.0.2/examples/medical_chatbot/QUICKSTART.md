# Medical Chatbot - 5 Minute Quick Start

Get the medical chatbot running in 5 minutes with minimal setup.

## Prerequisites Check

```bash
# Check Python version (need 3.9+)
python --version

# Check if Ollama is installed
ollama --version
```

## Step 1: Install MDSA Framework

```bash
# Navigate to MDSA root directory
cd ../..

# Install framework
pip install -e .

# Verify installation
python -c "from mdsa import TinyBERTOrchestrator; print('MDSA installed!')"
```

## Step 2: Install Example Dependencies

```bash
# Navigate to example directory
cd examples/medical_chatbot

# Install requirements
pip install -r requirements.txt
```

Expected packages:
- gradio>=4.0.0
- python-dotenv>=1.0.0
- requests>=2.31.0

## Step 3: Start Ollama

**Terminal 1** (keep this running):
```bash
ollama serve
```

**Terminal 2**:
```bash
# Pull recommended model
ollama pull deepseek-v3.1
```

## Step 4: Run Chatbot

```bash
# From examples/medical_chatbot directory
python app/enhanced_medical_chatbot_fixed.py
```

**Expected output:**
```
Loading MDSA orchestrator...
[KB] Detected example medical chatbot: .../examples/medical_chatbot/knowledge_base
Precomputing embeddings for 5 domains... computed in 287ms
Initializing Dual RAG system...
Running on local URL: http://127.0.0.1:7860
```

## Step 5: Access Chatbot

1. Open browser: **http://localhost:7860**
2. Try these queries:
   - "Patient has chest pain and fever"
   - "What treatment for Type 2 diabetes?"
   - "Interpret CBC results: WBC 15000, RBC 4.2"
   - "Side effects of metformin 500mg?"

## Step 6: Monitor Performance (Optional)

**Terminal 3**:
```bash
# Navigate to MDSA root
cd ../..

# Start dashboard
python mdsa/ui/dashboard/app.py
```

Access dashboard: **http://localhost:9000/monitor**

You should see your chatbot queries appearing in real-time!

---

## Troubleshooting

### "Command not found: ollama"

**Install Ollama:**
```bash
# Linux/Mac
curl -fsSL https://ollama.com/install.sh | sh

# Windows
# Download from: https://ollama.com/download
```

### "Port 7860 already in use"

```bash
# Find and kill the process
netstat -ano | findstr :7860  # Windows
lsof -i :7860  # Unix/Mac

# Or change port in code
```

### "Out of memory"

**Use smaller model:**
```bash
ollama pull llama2:7b  # Instead of deepseek-v3.1
```

**Or reduce cache size in** `app/enhanced_medical_chatbot_fixed.py`:
```python
self.MAX_CACHE_SIZE = 50  # Instead of 100
```

### "Knowledge base not found"

```bash
# Create knowledge_base directory
mkdir -p knowledge_base/global
mkdir -p knowledge_base/local

# Add a sample document
echo "Sample medical knowledge" > knowledge_base/global/sample.txt

# Restart chatbot
```

---

## Next Steps

- **Customize**: Add your own medical domains in the code
- **Enhance KB**: Add medical documents to `knowledge_base/`
- **Deploy**: See [DEPLOYMENT.md](DEPLOYMENT.md) for production setup
- **Learn More**: Read [README.md](README.md) for full documentation

---

## Quick Reference

**Start Chatbot:**
```bash
python examples/medical_chatbot/app/enhanced_medical_chatbot_fixed.py
```

**Start Dashboard:**
```bash
python mdsa/ui/dashboard/app.py
```

**Access URLs:**
- Chatbot: http://localhost:7860
- Dashboard: http://localhost:9000

**Stop Services:**
- Press `Ctrl+C` in each terminal

---

**Time to completion:** ~5 minutes
**Difficulty:** Beginner-friendly
**Status:** Production Ready
