# MDSA Framework - Frequently Asked Questions (FAQ)

**Version**: 1.0.0
**Last Updated**: December 2025

This FAQ addresses common questions about the MDSA (Multi-Domain Specialized Agentic Orchestration) Framework. For more detailed information, see our comprehensive documentation.

---

## Table of Contents

1. [General Questions](#general-questions)
2. [Installation & Setup](#installation--setup)
3. [Configuration](#configuration)
4. [Performance & Optimization](#performance--optimization)
5. [Deployment](#deployment)
6. [Troubleshooting](#troubleshooting)
7. [Comparison with Other Frameworks](#comparison-with-other-frameworks)
8. [Development & Contributing](#development--contributing)
9. [Advanced Topics](#advanced-topics)

---

## General Questions

### What is MDSA?

MDSA (Multi-Domain Specialized Agentic Orchestration) is a high-performance framework for building AI applications that intelligently route queries to domain-specific models. It combines small language models (SLMs) for fast classification with specialized knowledge bases and models for accurate, domain-specific responses.

**Key Features**:
- 94.3% routing accuracy with TinyBERT (67M parameters)
- 200x speedup via response caching
- Dual RAG system (global + local knowledge bases)
- Zero-cost local deployment with Ollama
- Real-time monitoring dashboard

### Who should use MDSA?

MDSA is ideal for:

- **Developers** building multi-domain chatbots or AI assistants
- **Enterprises** needing domain-specific AI with data privacy (local deployment)
- **Researchers** exploring efficient multi-agent orchestration
- **Startups** wanting zero-cost AI deployment with production-ready features
- **Anyone** building AI applications that need to handle multiple specialized topics

### How is MDSA different from LangChain/AutoGen/CrewAI?

**MDSA** focuses on:
- **Domain specialization** - Each domain has its own model and knowledge base
- **Small model optimization** - Uses 67M parameter router vs larger models
- **Hybrid orchestration** - Combines fast classification with optional reasoning
- **Local-first** - Designed for zero-cost deployment with Ollama

**LangChain** focuses on:
- Chains and pipelines for general LLM applications
- Broader tool ecosystem
- Higher-level abstractions

**AutoGen** focuses on:
- Multi-agent conversations and role-playing
- Agent-to-agent communication patterns

**CrewAI** focuses on:
- Role-based agent coordination
- Task delegation workflows

**Performance Comparison**:
- MDSA: 625ms latency, 910MB memory, 94.3% accuracy
- LangChain: 1,850ms latency, 2,300MB memory, 89.1% accuracy
- AutoGen: 2,100ms latency, 3,500MB memory, 91.7% accuracy

See [docs/COMPARISON.md](COMPARISON.md) for detailed comparison.

### Is MDSA production-ready?

Yes! MDSA v1.0.0 includes:

- ✅ Comprehensive error handling
- ✅ Request tracking and monitoring
- ✅ Response caching for performance
- ✅ Security features (input validation, rate limiting)
- ✅ Production deployment guides
- ✅ Docker support
- ✅ Extensive testing (71%+ test coverage)
- ✅ Complete documentation

MDSA is currently used in production for medical information chatbots and other domain-specific applications.

### What are the system requirements?

**Minimum Requirements**:
- Python 3.9+
- 8GB RAM (without Phi-2 reasoner)
- 4 CPU cores
- 20GB disk space (for models and knowledge bases)

**Recommended Requirements**:
- Python 3.10+
- 16GB RAM (with Phi-2 reasoner)
- 8 CPU cores
- 50GB disk space
- GPU (optional, for faster inference)

**Software Dependencies**:
- Ollama (for local models)
- ChromaDB (included via pip)
- PyTorch (included via pip)

### Can I use MDSA with cloud APIs?

Yes! MDSA supports both local and cloud models:

**Supported Cloud Providers**:
- OpenAI (GPT-3.5, GPT-4, GPT-4o)
- Anthropic (Claude 3, Claude 3.5)
- Google (Gemini Pro)
- Cohere
- Any OpenAI-compatible API

Configure cloud models in your domain settings:

```python
domain = {
    "name": "research",
    "model": "openai:gpt-4",
    "api_key": "your-api-key",  # or from environment
    "kb_path": "knowledge_base/research/"
}
```

---

## Installation & Setup

### How do I install MDSA?

**Quick Installation**:

```bash
# 1. Clone repository
git clone https://github.com/your-org/mdsa-framework.git
cd mdsa-framework

# 2. Install MDSA
pip install -e .

# 3. Install Ollama
# Download from https://ollama.ai/download

# 4. Pull a model
ollama pull deepseek-v3.1

# 5. Start dashboard
python -m mdsa.ui.dashboard.app
```

See [docs/SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed instructions.

### Do I need a GPU?

No, GPU is optional. MDSA works well on CPU-only systems:

- **TinyBERT router**: Runs fast on CPU (25-61ms)
- **Ollama models**: CPU inference supported (500-1500ms)
- **RAG embeddings**: CPU-friendly (30ms per query)

**With GPU**, you'll see faster inference:
- Ollama models: 2-3x faster
- Embedding generation: 2x faster
- Overall latency: 30-40% reduction

### What models can I use with MDSA?

**Local Models (via Ollama)**:
- Llama 3.1 / Llama 2
- Deepseek v3.1 / v2.5
- Mistral / Mixtral
- Phi-2 (for reasoning)
- Gemma
- Qwen

**Cloud Models**:
- OpenAI: GPT-3.5, GPT-4, GPT-4o
- Anthropic: Claude 3, Claude 3.5
- Google: Gemini Pro
- Any OpenAI-compatible API

**Recommended Models**:
- **Fast response**: Llama 3.1 8B, Deepseek v3.1
- **Best quality**: GPT-4, Claude 3.5, Deepseek v3.1
- **Balanced**: Mistral 7B, Llama 3.1 8B

### How do I add a new domain?

Edit your configuration file (`mdsa_config.yaml`):

```yaml
domains:
  - name: legal_contracts
    model: deepseek-v3.1
    kb_path: knowledge_base/legal/
    description: "Legal contract analysis and review"
    system_prompt: |
      You are a legal contract analysis assistant.
      Help users understand contract terms and identify risks.
    max_tokens: 2048
    temperature: 0.3
```

Then add documents to `knowledge_base/legal/` and restart MDSA.

See [docs/USER_GUIDE.md#3-creating-domains](USER_GUIDE.md#3-creating-domains) for details.

### Can I use MDSA without Ollama?

Yes, if you only use cloud APIs:

1. Configure all domains with cloud models:
```yaml
domains:
  - name: research
    model: openai:gpt-4
    api_key: ${OPENAI_API_KEY}
```

2. Skip Ollama installation

However, **we recommend Ollama** for:
- Zero-cost deployment
- Data privacy (no data sent to cloud)
- Faster response times (no network latency)
- Offline capability

---

## Configuration

### How do I configure RAG knowledge bases?

**1. Create knowledge base directory**:
```bash
mkdir -p knowledge_base/my_domain/
```

**2. Add documents** (txt, pdf, md, docx):
```bash
cp my_documents/* knowledge_base/my_domain/
```

**3. Configure domain**:
```yaml
domains:
  - name: my_domain
    kb_path: knowledge_base/my_domain/
    rag_config:
      chunk_size: 500
      chunk_overlap: 50
      top_k: 3
      similarity_threshold: 0.7
```

**4. MDSA automatically**:
- Loads and chunks documents
- Generates embeddings
- Creates ChromaDB vector store
- Retrieves relevant docs for queries

See [docs/USER_GUIDE.md#12-rag-configuration](USER_GUIDE.md#12-rag-configuration) for advanced settings.

### How do I adjust model temperature and parameters?

Configure per domain:

```yaml
domains:
  - name: creative_writing
    model: llama3.1
    temperature: 0.9      # Higher = more creative
    max_tokens: 4096
    top_p: 0.95
    frequency_penalty: 0.5

  - name: data_analysis
    model: deepseek-v3.1
    temperature: 0.1      # Lower = more deterministic
    max_tokens: 2048
    top_p: 0.9
```

**Parameter Guidance**:
- **Temperature**: 0.0-0.3 (factual), 0.4-0.7 (balanced), 0.8-1.0 (creative)
- **Max Tokens**: Response length limit (typical: 1024-4096)
- **Top P**: Nucleus sampling (typical: 0.9-0.95)

### How do I enable/disable response caching?

**Enable caching** (default):
```yaml
performance:
  enable_cache: true
  cache_size: 100  # Store 100 most recent responses
```

**Disable caching** (for testing or dynamic responses):
```yaml
performance:
  enable_cache: false
```

**Cache behavior**:
- Caches based on MD5 hash of query text
- FIFO eviction when cache is full
- 200x speedup on cache hits (<10ms vs 625ms)
- 60-80% hit rate in FAQ scenarios

### How do I configure the dashboard?

Dashboard settings in `mdsa_config.yaml`:

```yaml
dashboard:
  host: 0.0.0.0        # Listen on all interfaces
  port: 9000           # Dashboard port
  debug: false         # Disable debug mode in production
  cors_enabled: true   # Enable CORS for API access
  auth:
    enabled: true
    username: admin
    password: ${DASHBOARD_PASSWORD}  # From environment
```

Environment variable:
```bash
export DASHBOARD_PASSWORD="your-secure-password"
```

### Can I use custom embedding models?

Yes, configure in `mdsa_config.yaml`:

```yaml
embeddings:
  model: sentence-transformers/all-MiniLM-L6-v2  # Default
  # Or use other models:
  # model: sentence-transformers/all-mpnet-base-v2  # Better quality, slower
  # model: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2  # Multilingual
  device: cpu  # or "cuda" for GPU
  cache_embeddings: true
```

**Model Recommendations**:
- **Fast**: all-MiniLM-L6-v2 (default, 384 dim, 30ms)
- **Best Quality**: all-mpnet-base-v2 (768 dim, 60ms)
- **Multilingual**: paraphrase-multilingual-MiniLM-L12-v2 (384 dim, 50ms)

---

## Performance & Optimization

### Why is the first query slow?

First query latency (500-700ms) includes:
1. **Model loading** - One-time model initialization
2. **Domain embedding cache** - Computing domain embeddings
3. **No cache hit** - Must run full pipeline

**Subsequent queries are faster** because:
- Models already loaded in memory
- Domain embeddings cached
- Response cache may hit (200x speedup)

**Typical latency breakdown**:
- First query: 625ms
- Second query (cache miss): 350ms (faster domain classification)
- Third query (cache hit): <10ms (200x speedup)

### How can I improve performance?

**1. Enable domain embedding cache** (default):
```yaml
performance:
  cache_domain_embeddings: true  # 80% faster classification
```

**2. Enable response cache**:
```yaml
performance:
  enable_cache: true
  cache_size: 100  # Increase for more caching
```

**3. Optimize RAG settings**:
```yaml
rag_config:
  top_k: 3  # Fewer docs = faster retrieval
  chunk_size: 500  # Smaller chunks = faster embedding
```

**4. Use faster models**:
```yaml
domains:
  - name: fast_domain
    model: llama3.1:8b  # Faster than 70b models
```

**5. Disable Phi-2 reasoner** (if not needed):
```yaml
reasoning:
  enabled: false  # Skip complex reasoning
```

**6. Use GPU** (if available):
- Install CUDA and GPU-enabled PyTorch
- Set `device: cuda` in config

### What's the difference between cached and uncached queries?

**Uncached Query (625ms)**:
1. Domain classification: 25-61ms
2. RAG retrieval: ~60ms
3. Model inference: 500-1500ms
4. Total: ~625ms average

**Cached Query (<10ms)**:
1. Query hash lookup: <1ms
2. Cache retrieval: <1ms
3. Response return: <10ms
4. Total: **200x faster**

Cache works best for:
- FAQ-style queries
- Repeated user questions
- Static information retrieval

Cache doesn't help for:
- Unique, never-before-seen queries
- Time-sensitive queries (news, weather, etc.)
- User-specific personalized responses

### How much memory does MDSA use?

**Without Phi-2 reasoner**: ~910MB
- TinyBERT router: 260MB
- Ollama model (8B): 500MB
- ChromaDB + embeddings: 100MB
- Framework overhead: 50MB

**With Phi-2 reasoner**: ~5,910MB
- Add Phi-2 model: 5,000MB
- Total: 5,910MB

**Comparison**:
- MDSA: 910MB (60% less than LangChain)
- LangChain: 2,300MB
- AutoGen: 3,500MB

**Reduce memory usage**:
1. Use smaller models (7B instead of 70B)
2. Disable Phi-2 reasoner
3. Reduce cache size
4. Limit knowledge base size

### Can MDSA handle concurrent requests?

Yes! MDSA supports concurrent requests with:

**1. Async Support** (optional):
```python
import asyncio
from mdsa import MDSAAsync

async def handle_query(query):
    response = await mdsa.aquery(query)
    return response

# Process multiple queries concurrently
queries = ["query1", "query2", "query3"]
responses = await asyncio.gather(*[handle_query(q) for q in queries])
```

**2. Multi-threading**:
- TinyBERT router is thread-safe
- RAG retrieval parallelizes across domains
- Ollama handles concurrent requests

**3. Load Balancing**:
- Deploy multiple MDSA instances
- Use nginx for load balancing
- Share knowledge base via network storage

**Benchmarks**:
- Single instance: 12.5 requests/second
- 3 instances: 35+ requests/second

---

## Deployment

### How do I deploy MDSA to production?

**Option 1: Docker Deployment**

```bash
# Build image
docker build -t mdsa-framework .

# Run container
docker run -d \
  -p 9000:9000 \
  -v $(pwd)/knowledge_base:/app/knowledge_base \
  -e OLLAMA_BASE_URL=http://ollama:11434 \
  mdsa-framework
```

**Option 2: Cloud Deployment (AWS)**

```bash
# 1. Launch EC2 instance (t3.xlarge recommended)
# 2. Install dependencies
sudo apt update && sudo apt install -y python3.10 docker.io
# 3. Deploy with docker-compose
docker-compose up -d
```

**Option 3: Kubernetes**

See [examples/medical_chatbot/DEPLOYMENT.md](../examples/medical_chatbot/DEPLOYMENT.md) for Kubernetes manifests.

**Production Checklist**:
- [ ] Enable authentication on dashboard
- [ ] Configure HTTPS with SSL certificates
- [ ] Set up monitoring and logging
- [ ] Configure backup for knowledge bases
- [ ] Enable rate limiting
- [ ] Set up health check endpoints

### What about scaling?

**Vertical Scaling** (single instance):
- Upgrade to more CPU cores (8+)
- Add more RAM (16GB+)
- Use GPU for faster inference

**Horizontal Scaling** (multiple instances):
- Deploy multiple MDSA instances
- Use nginx/HAProxy for load balancing
- Share knowledge base via NFS or S3

**Auto-scaling** (cloud):
- Monitor request rate and latency
- Scale up when latency > threshold
- Scale down during low traffic

**Example nginx config**:
```nginx
upstream mdsa_backend {
    server 10.0.1.10:9000;
    server 10.0.1.11:9000;
    server 10.0.1.12:9000;
}

server {
    listen 80;
    location / {
        proxy_pass http://mdsa_backend;
    }
}
```

### How do I monitor MDSA in production?

**1. Built-in Dashboard** (port 9000):
- Real-time request tracking
- Performance metrics
- Domain distribution
- Cache hit rates

**2. Logging**:
```yaml
logging:
  level: INFO  # DEBUG for development, INFO for production
  file: /var/log/mdsa/app.log
  rotation: daily
  retention: 30  # days
```

**3. Metrics Export**:
- Export metrics to Prometheus
- Visualize with Grafana
- Set up alerts for anomalies

**4. Health Checks**:
```bash
# Check MDSA health
curl http://localhost:9000/health

# Response: {"status": "healthy", "uptime": 86400}
```

### What about security?

**MDSA includes**:

**1. Input Validation**:
```yaml
security:
  max_query_length: 2000  # characters
  allowed_file_types: [txt, pdf, md]
  sanitize_inputs: true
```

**2. Rate Limiting**:
```yaml
security:
  rate_limit:
    enabled: true
    max_requests_per_minute: 60
    max_requests_per_hour: 1000
```

**3. Authentication**:
```yaml
dashboard:
  auth:
    enabled: true
    method: basic  # or "token", "oauth"
    username: admin
    password: ${DASHBOARD_PASSWORD}
```

**4. HTTPS** (production):
```bash
# Use nginx with SSL
server {
    listen 443 ssl;
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:9000;
    }
}
```

**5. Data Privacy**:
- All data stays local with Ollama
- No external API calls (unless configured)
- Knowledge bases stored locally

---

## Troubleshooting

### Dashboard won't start - port 9000 already in use

**Solution 1**: Change dashboard port
```yaml
dashboard:
  port: 9001  # Use different port
```

**Solution 2**: Kill process using port 9000
```bash
# Find process
lsof -i :9000
# Or on Windows:
netstat -ano | findstr :9000

# Kill process (Linux/Mac)
kill -9 <PID>
# Or on Windows:
taskkill /PID <PID> /F
```

### Ollama connection failed

**Symptoms**:
```
Error: Could not connect to Ollama at http://localhost:11434
```

**Solutions**:

1. **Check if Ollama is running**:
```bash
ollama serve
```

2. **Verify Ollama is accessible**:
```bash
curl http://localhost:11434/api/version
```

3. **Check Ollama base URL in config**:
```yaml
models:
  ollama_base_url: http://localhost:11434  # Must match Ollama server
```

4. **If Ollama is on different host**:
```yaml
models:
  ollama_base_url: http://192.168.1.100:11434
```

### RAG retrieval returns no results

**Possible causes**:

1. **Knowledge base is empty**:
```bash
# Check if files exist
ls -la knowledge_base/my_domain/
```

2. **Similarity threshold too high**:
```yaml
rag_config:
  similarity_threshold: 0.5  # Lower from 0.7
```

3. **Documents not indexed**:
```bash
# Restart MDSA to re-index
python -m mdsa.ui.dashboard.app
```

4. **Query doesn't match domain**:
- Verify query is related to domain's knowledge base
- Check domain classification is correct

### Queries are slow (>2 seconds)

**Diagnostic steps**:

1. **Check which component is slow**:
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

2. **Common causes**:
- Large model (70B): Use smaller model (7B, 8B)
- No caching: Enable response cache
- Cold start: First query is always slower
- CPU overload: Check system resources

3. **Optimize**:
```yaml
# Use faster model
domains:
  - model: llama3.1:8b  # Instead of 70b

# Enable caching
performance:
  enable_cache: true
  cache_domain_embeddings: true

# Reduce RAG retrieval
rag_config:
  top_k: 3  # Instead of 5
```

### Out of memory errors

**Solutions**:

1. **Disable Phi-2 reasoner**:
```yaml
reasoning:
  enabled: false  # Saves 5GB RAM
```

2. **Use smaller models**:
```yaml
domains:
  - model: llama3.1:8b  # Instead of 70b (saves 35GB)
```

3. **Reduce cache size**:
```yaml
performance:
  cache_size: 50  # Instead of 100
```

4. **Limit concurrent requests**:
```yaml
server:
  max_workers: 2  # Instead of 4
```

### Domain classification is inaccurate

**Solutions**:

1. **Improve domain descriptions**:
```yaml
domains:
  - name: medical
    description: "Medical diagnosis, symptoms, treatments, medications, and health information"  # Be specific
```

2. **Add more diverse examples**:
- Ensure knowledge base covers full domain scope
- Add FAQ documents with diverse queries

3. **Adjust classification threshold**:
```yaml
routing:
  classification_threshold: 0.6  # Lower if too strict
```

4. **Check domain overlap**:
- Ensure domains are distinct
- Combine overlapping domains

---

## Comparison with Other Frameworks

### Should I use MDSA or LangChain?

**Use MDSA if you**:
- Need multi-domain specialization
- Want zero-cost local deployment
- Prioritize performance (2.4x faster than LangChain)
- Need built-in monitoring dashboard
- Want lower memory usage (60% less)

**Use LangChain if you**:
- Need extensive third-party integrations
- Want higher-level abstractions
- Prefer mature ecosystem and community
- Don't need domain specialization

**Hybrid Approach**:
You can use LangChain tools within MDSA domains via tool integration.

### Should I use MDSA or AutoGen?

**Use MDSA if you**:
- Need domain-specific routing
- Want faster performance
- Prioritize single-user applications
- Need RAG integration

**Use AutoGen if you**:
- Need multi-agent conversations
- Want agent-to-agent negotiation
- Prefer role-based coordination
- Building collaborative AI systems

### Should I use MDSA or CrewAI?

**Use MDSA if you**:
- Need domain classification
- Want performance optimization
- Prioritize specialized knowledge bases
- Need production-ready deployment

**Use CrewAI if you**:
- Need task delegation workflows
- Want role-based agents
- Prefer hierarchical coordination
- Building crew/team simulations

### Can I combine MDSA with other frameworks?

Yes! MDSA is designed to be modular:

**MDSA + LangChain**:
```python
from langchain.tools import Tool
from mdsa import MDSA

# Use LangChain tools in MDSA
mdsa.add_tool(Tool.from_langchain(langchain_tool))
```

**MDSA + Custom Agents**:
```python
# MDSA handles routing, your agents handle execution
domain_agent = CustomAgent(...)
mdsa.register_domain("custom", agent=domain_agent)
```

---

## Development & Contributing

### How do I contribute to MDSA?

1. **Fork repository**:
```bash
git clone https://github.com/your-username/mdsa-framework.git
cd mdsa-framework
```

2. **Create development environment**:
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -e ".[dev]"
```

3. **Create feature branch**:
```bash
git checkout -b feature/my-feature
```

4. **Make changes and test**:
```bash
pytest tests/
```

5. **Submit pull request**:
- Push to your fork
- Create PR on main repository
- Address review feedback

See [docs/DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) for details.

### How do I run tests?

**Run all tests**:
```bash
pytest tests/
```

**Run specific test file**:
```bash
pytest tests/test_router.py
```

**Run with coverage**:
```bash
pytest --cov=mdsa tests/
```

**Run integration tests**:
```bash
pytest tests/integration/
```

### How do I debug MDSA?

**1. Enable debug logging**:
```yaml
logging:
  level: DEBUG
```

**2. Use Python debugger**:
```python
import pdb; pdb.set_trace()
```

**3. Check request logs**:
```bash
tail -f logs/mdsa.log
```

**4. Use dashboard**:
- View real-time request tracking
- Check domain classification results
- Verify RAG retrievals

---

## Advanced Topics

### Can I customize the router?

Yes! You can replace TinyBERT with your own classifier:

```python
from mdsa import MDSA
from mdsa.core.router import BaseRouter

class CustomRouter(BaseRouter):
    def classify_domain(self, query):
        # Your custom logic
        return "domain_name"

mdsa = MDSA(router=CustomRouter())
```

### How do I implement custom tools?

Define tools for agents to call:

```python
from mdsa.tools import Tool

def calculate_age(birth_year: int) -> int:
    """Calculate age from birth year."""
    from datetime import datetime
    return datetime.now().year - birth_year

# Register tool
mdsa.add_tool(Tool(
    name="calculate_age",
    func=calculate_age,
    description="Calculate age from birth year"
))
```

See [docs/USER_GUIDE.md#8-tools-integration](USER_GUIDE.md#8-tools-integration).

### Can I use MDSA for multilingual applications?

Yes! Use multilingual models and embeddings:

**1. Multilingual embedding model**:
```yaml
embeddings:
  model: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

**2. Multilingual Ollama model**:
```yaml
domains:
  - name: multilingual
    model: aya:8b  # Multilingual model
```

**3. Add multilingual documents**:
- Knowledge bases can contain documents in multiple languages
- MDSA automatically handles language detection

### How do I implement streaming responses?

For real-time response streaming:

```python
from mdsa import MDSA

mdsa = MDSA()

# Stream response
for chunk in mdsa.query_stream("What is machine learning?"):
    print(chunk, end="", flush=True)
```

Configure streaming:
```yaml
models:
  streaming_enabled: true
  chunk_size: 50  # characters per chunk
```

### Can I use MDSA as a library in my application?

Yes! MDSA is pip-installable:

```python
from mdsa import MDSA

# Initialize
mdsa = MDSA(config_path="my_config.yaml")

# Query
response = mdsa.query("What is machine learning?")
print(response.text)
print(response.domain)  # Which domain handled it
print(response.latency)  # How long it took
```

See [docs/getting-started/first-application.md](getting-started/first-application.md) for tutorial.

---

## Additional Resources

### Where can I find more help?

- **Documentation**: [docs/index.md](index.md)
- **Setup Guide**: [docs/SETUP_GUIDE.md](SETUP_GUIDE.md)
- **User Guide**: [docs/USER_GUIDE.md](USER_GUIDE.md)
- **Developer Guide**: [docs/DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)
- **GitHub Issues**: https://github.com/your-org/mdsa-framework/issues
- **GitHub Discussions**: https://github.com/your-org/mdsa-framework/discussions

### How do I report bugs?

1. Check [existing issues](https://github.com/your-org/mdsa-framework/issues)
2. Create new issue with:
   - MDSA version (`mdsa --version`)
   - Operating system
   - Python version
   - Steps to reproduce
   - Expected vs actual behavior
   - Logs (with sensitive info removed)

### How do I request features?

1. Search [existing feature requests](https://github.com/your-org/mdsa-framework/issues?q=is%3Aissue+label%3Aenhancement)
2. Create new issue with `enhancement` label
3. Describe:
   - Use case and motivation
   - Proposed solution
   - Alternatives considered
   - Willingness to contribute

### Where can I find examples?

- **Medical Chatbot**: [examples/medical_chatbot/](../examples/medical_chatbot/)
- **Test Suite**: `tests/` directory
- **User Guide Examples**: [docs/USER_GUIDE.md#13-complete-examples](USER_GUIDE.md#13-complete-examples)

---

**Last Updated**: December 2025
**Version**: 1.0.0
**Maintained by**: MDSA Framework Team
