# MDSA Framework Glossary

**Version**: 1.0.0
**Last Updated**: December 2025

This glossary provides definitions for technical terms, concepts, and technologies used throughout the MDSA Framework documentation.

---

## Table of Contents

- [A](#a) | [B](#b) | [C](#c) | [D](#d) | [E](#e) | [F](#f) | [G](#g) | [H](#h) | [I](#i) | [J](#j) | [K](#k) | [L](#l) | [M](#m)
- [N](#n) | [O](#o) | [P](#p) | [Q](#q) | [R](#r) | [S](#s) | [T](#t) | [U](#u) | [V](#v) | [W](#w) | [X](#x) | [Y](#y) | [Z](#z)

---

## A

### Agent
A computational entity within the MDSA framework that performs specific tasks autonomously. Agents can communicate with each other, access tools, query knowledge bases, and execute domain-specific operations. Each agent is configured with its own model, system prompt, and capabilities.

### Agent Chain
A sequence of connected agents where the output of one agent becomes the input for the next. Agent chains enable complex multi-step workflows and can implement sophisticated reasoning patterns.

### Agent Orchestration
The process of coordinating multiple agents to work together on complex tasks. MDSA's orchestration system handles task routing, resource allocation, and inter-agent communication.

### API Integration
The process of connecting MDSA with external systems using REST APIs, webhooks, or other network protocols. MDSA supports both consuming external APIs (via tools) and exposing its own REST API for integration.

### AutoGen
A Microsoft framework for building multi-agent conversational AI systems. MDSA differs from AutoGen by focusing on domain-specific routing and hybrid orchestration with smaller, faster models.

---

## B

### BERT (Bidirectional Encoder Representations from Transformers)
A transformer-based model architecture developed by Google. MDSA uses TinyBERT, a distilled version with 67M parameters, for fast domain classification.

### Baseline Performance
The performance metrics of a system without optimizations. MDSA's baseline (without caching) averages 625ms per query, which improves to <10ms with caching.

---

## C

### Cache Hit Rate
The percentage of queries that are served from cache rather than requiring full processing. MDSA achieves 60-80% cache hit rates in FAQ scenarios, resulting in 200x speedup.

### ChromaDB
An open-source vector database used by MDSA for storing and retrieving document embeddings in the RAG system. ChromaDB provides fast similarity search for knowledge base queries.

### Classification Accuracy
The percentage of queries correctly routed to their intended domain. MDSA's TinyBERT router achieves 94.3% classification accuracy across multiple domains.

### Cloud Model
An AI model accessed via API from cloud providers (OpenAI, Anthropic, Google, etc.). MDSA supports both local models (via Ollama) and cloud models for maximum flexibility.

### Complexity-Based Routing
MDSA's hybrid orchestration strategy that routes simple queries directly to domain models while sending complex queries through the Phi-2 reasoner. This optimization reduces latency and resource usage.

### Context Window
The maximum number of tokens a language model can process in a single request. MDSA manages context windows by limiting RAG retrieval results and using efficient prompting strategies.

### CrewAI
An open-source framework for orchestrating role-playing AI agents. MDSA differs by focusing on domain specialization and small language model optimization rather than role-based coordination.

---

## D

### Dashboard
The web-based monitoring interface (port 9000) that provides real-time analytics, request tracking, performance metrics, and system configuration. Built with Flask and D3.js.

### Deepseek
A family of open-source language models optimized for coding and reasoning tasks. MDSA supports Deepseek models via Ollama integration.

### Domain
A specialized area of knowledge or functionality within MDSA. Each domain has its own model, knowledge base, and configuration. Examples: "clinical_diagnosis", "legal_contracts", "financial_analysis".

### Domain Classification
The process of determining which domain a user query belongs to. MDSA uses TinyBERT embeddings and cosine similarity to classify queries in 25-61ms.

### Domain Embedding Cache
An optimization that caches domain name embeddings to avoid re-encoding them for every query. This provides 80% speedup in domain classification (from 125-310ms to 25-61ms).

### Domain Model
The language model assigned to a specific domain. Each domain can use a different model optimized for that domain's tasks (e.g., medical domain uses a medical-tuned model).

### Domain-Specific Knowledge Base
A local knowledge base containing documents relevant to a specific domain. MDSA maintains separate knowledge bases per domain for precise retrieval.

### Dual RAG System
MDSA's knowledge retrieval architecture that combines:
1. **Global Knowledge Base** - 10,000+ documents covering general knowledge
2. **Local Knowledge Bases** - 1,000 documents per domain for specialized knowledge

This architecture provides both broad coverage and deep specialization.

---

## E

### Embedding
A numerical vector representation of text that captures semantic meaning. MDSA uses SentenceTransformers (all-MiniLM-L6-v2) to generate 384-dimensional embeddings for RAG retrieval.

### Embedding Model
The model used to convert text into vector embeddings. MDSA uses `all-MiniLM-L6-v2` by default, which provides a good balance of speed (30ms) and quality.

### Embedder
The component responsible for generating embeddings from text. MDSA's embedder supports caching and batch processing for efficiency.

---

## F

### FastAPI
A modern Python web framework used by MDSA's dashboard backend. FastAPI provides high performance and automatic API documentation.

### FIFO (First In, First Out)
The cache eviction policy used by MDSA's response cache. When the cache is full, the oldest entries are removed first to make room for new ones.

### Framework
A structured platform for building applications. MDSA is a framework for building multi-domain AI applications with intelligent routing and orchestration.

---

## G

### Global Knowledge Base
The shared knowledge base accessible to all domains in MDSA. Contains 10,000+ general documents that provide broad coverage across topics.

### Gradio
A Python library for building web UIs for machine learning applications. The medical chatbot example uses Gradio for its user interface (port 7860).

### Guardrails
Safety mechanisms that validate inputs, filter outputs, and enforce constraints. MDSA supports input validation, output filtering, and content safety guardrails.

---

## H

### Hugging Face
A platform and library ecosystem for machine learning models. MDSA uses Hugging Face's `transformers` library for TinyBERT and Phi-2 models.

### Hybrid Orchestration
MDSA's orchestration strategy that combines:
- Fast domain classification (TinyBERT)
- Complexity-based routing (simple vs complex queries)
- Optional reasoning (Phi-2 for complex queries)
- Dual RAG system (global + local knowledge bases)

This hybrid approach optimizes for both speed and capability.

---

## I

### Inference
The process of running a machine learning model on input data to generate predictions or responses. MDSA's inference latency ranges from 500-1500ms depending on model size.

### Intent Classification
The process of determining what a user wants to accomplish with their query. MDSA's domain classification is a form of intent classification focused on domain routing.

---

## K

### Knowledge Base (KB)
A collection of documents used for Retrieval-Augmented Generation (RAG). MDSA maintains both global and domain-specific knowledge bases.

### Knowledge Retrieval
The process of finding relevant documents from a knowledge base to augment an LLM's response. MDSA uses vector similarity search with ChromaDB.

---

## L

### LangChain
A popular framework for building applications with language models. MDSA provides 2.4x faster performance and 60% less memory usage compared to LangChain in benchmarks.

### Latency
The time delay between sending a query and receiving a response. MDSA's average latency is 625ms for first queries and <10ms for cached queries.

### LLM (Large Language Model)
A neural network trained on vast amounts of text data to understand and generate human language. Examples: GPT-4, Claude, Llama, Deepseek.

### Local Knowledge Base
A domain-specific knowledge base containing documents relevant only to that domain. Each MDSA domain can have its own local knowledge base with up to 1,000 documents.

---

## M

### MCP (Model Context Protocol)
A standardized protocol for connecting AI applications with external tools and data sources. MDSA supports MCP server integration for extended capabilities.

### MD5 Hash
A cryptographic hash function used by MDSA to generate cache keys from query text. MD5 ensures consistent cache lookups for identical queries.

### Memory Footprint
The amount of RAM used by an application. MDSA uses 910MB without Phi-2, or 5,910MB with Phi-2 enabled, compared to 2,300MB for LangChain.

### Model
A trained neural network used for natural language processing. MDSA supports local models (via Ollama) and cloud models (via API).

### Model Context Protocol
See MCP.

### Multi-Domain
Supporting multiple specialized domains within a single framework. MDSA's core capability is routing queries to the appropriate domain-specific model and knowledge base.

---

## O

### Ollama
A tool for running large language models locally. MDSA uses Ollama to run models like Llama, Deepseek, and Phi-2 without API costs or internet dependency.

### Orchestration
The coordination and management of multiple AI agents or models to accomplish complex tasks. See [Hybrid Orchestration](#hybrid-orchestration).

---

## P

### Phi-2
A 2.7B parameter reasoning model developed by Microsoft. MDSA optionally uses Phi-2 for complex multi-step queries requiring advanced reasoning.

### Precision@K
A metric measuring the percentage of relevant documents in the top K retrieval results. MDSA achieves 87.3% Precision@3 in RAG retrieval.

### Prompt
The text input provided to a language model to generate a response. MDSA uses system prompts to configure agent behavior.

### PyTorch
An open-source machine learning framework used by MDSA for running TinyBERT and Phi-2 models locally.

---

## Q

### Query
A user's input text that needs to be processed by the MDSA framework. Queries are classified by domain, optionally enhanced with RAG, and routed to appropriate models.

### Query Latency
The time taken to process a single query from input to response. See [Latency](#latency).

---

## R

### RAG (Retrieval-Augmented Generation)
A technique that enhances LLM responses by retrieving relevant documents from a knowledge base and including them in the prompt. MDSA's dual RAG system provides both broad and specialized knowledge.

### Request Tracking
MDSA's monitoring system that logs every query, domain classification, RAG retrieval, and model response to the dashboard for analysis.

### Response Cache
A cache that stores complete responses for previously seen queries. MDSA's response cache provides 200x speedup (<10ms vs 625ms) with 60-80% hit rates.

### REST API
Representational State Transfer Application Programming Interface - a web service protocol. MDSA exposes REST APIs for integration with external systems.

### Router
The component responsible for classifying queries and routing them to appropriate domains. MDSA uses TinyBERT for fast, accurate routing (94.3% accuracy, 25-61ms).

### Routing Accuracy
The percentage of queries correctly routed to their intended domain. See [Classification Accuracy](#classification-accuracy).

---

## S

### SentenceTransformers
A Python library for generating sentence embeddings. MDSA uses `all-MiniLM-L6-v2` from SentenceTransformers for RAG embeddings.

### SLM (Small Language Model)
Language models with fewer parameters (<1B) optimized for specific tasks. MDSA uses TinyBERT (67M parameters) for routing, demonstrating SLM effectiveness.

### Specialized Agent
An agent configured for a specific domain with domain-specific models, knowledge bases, and tools. MDSA's architecture centers on specialized agents.

### System Prompt
Instructions provided to a language model that define its role, behavior, and constraints. Each MDSA agent has a configurable system prompt.

---

## T

### TinyBERT
A distilled version of BERT with 67M parameters (vs BERT's 110M). MDSA uses TinyBERT for fast domain classification with 94.3% accuracy in 25-61ms.

### Tool
An external function or API that agents can call to perform actions or retrieve information. MDSA supports custom tools, MCP tools, and API integrations.

### Tool Integration
The process of connecting external tools to MDSA agents. Tools enable agents to perform actions beyond text generation (e.g., database queries, calculations, API calls).

### Transformer
A neural network architecture based on self-attention mechanisms. All modern LLMs (BERT, GPT, Llama, etc.) use transformer architectures.

---

## U

### User Query
See [Query](#query).

---

## V

### Vector Database
A database optimized for storing and searching high-dimensional vectors (embeddings). MDSA uses ChromaDB as its vector database for RAG.

### Vector Embedding
See [Embedding](#embedding).

### Vector Similarity
A measure of how similar two vectors are, typically computed using cosine similarity or dot product. MDSA uses cosine similarity for domain classification and RAG retrieval.

---

## W

### Webhook
An HTTP callback that delivers real-time data to other applications. MDSA can send webhooks for events like query completion or domain routing.

### Workflow
A sequence of steps to accomplish a complex task. MDSA workflows can involve multiple agent calls, RAG retrievals, and tool executions.

---

## Common Acronyms

| Acronym | Full Term | Definition |
|---------|-----------|------------|
| **API** | Application Programming Interface | Interface for software communication |
| **BERT** | Bidirectional Encoder Representations from Transformers | Google's transformer model |
| **GPU** | Graphics Processing Unit | Hardware accelerator for ML |
| **KB** | Knowledge Base | Document collection for RAG |
| **LLM** | Large Language Model | Neural network for language |
| **MCP** | Model Context Protocol | Protocol for tool integration |
| **MDSA** | Multi-Domain Specialized Agentic Orchestration | This framework |
| **NLP** | Natural Language Processing | Field of AI for language |
| **RAG** | Retrieval-Augmented Generation | Technique combining retrieval + generation |
| **REST** | Representational State Transfer | Web API architecture |
| **SLM** | Small Language Model | Language model <1B parameters |
| **UI** | User Interface | Visual interface for users |

---

## Performance Terminology

### Average Latency
The mean time to process a query across all requests. MDSA's average latency is 625ms without cache, <10ms with cache.

### Cache Hit Rate
Percentage of queries served from cache. MDSA achieves 60-80% in FAQ scenarios.

### Classification Time
Time spent on domain classification. MDSA: 25-61ms with cache, 125-310ms without.

### End-to-End Latency
Total time from query input to response output, including all processing steps (classification, RAG, inference, caching).

### Inference Time
Time spent on model inference only. Typically 500-1500ms depending on model size and query complexity.

### Memory Usage
RAM consumed by the framework during operation. MDSA uses 910MB (without Phi-2) or 5,910MB (with Phi-2).

### P50/P95/P99
Percentile metrics indicating latency at 50th, 95th, and 99th percentiles. Useful for understanding tail latency.

### RAG Retrieval Time
Time spent retrieving documents from knowledge bases. MDSA averages ~60ms for RAG retrieval.

### Throughput
Number of queries processed per second. MDSA achieves 12.5 requests/second average throughput.

---

## Architecture Terminology

### Component
A modular part of the MDSA system (e.g., Router, RAG System, Dashboard, Embedder).

### Deployment
The process of installing and running MDSA in a production environment (local, Docker, cloud).

### Integration
Connecting MDSA with external systems, tools, or data sources.

### Monitoring
Tracking system performance, metrics, and health via the dashboard and logging.

### Pipeline
A sequence of processing steps (classify → retrieve → augment → infer → respond).

### Scalability
The ability to handle increased load by adding resources. MDSA supports horizontal scaling via multiple instances.

---

## Comparison Terminology

### Baseline System
The reference system for comparison. MDSA comparisons use LangChain as baseline.

### Benchmark
A standardized test for measuring performance. MDSA benchmarks measure latency, accuracy, and memory usage.

### Competitive Analysis
Comparison of MDSA with alternative frameworks (LangChain, AutoGen, CrewAI).

### Performance Gain
Improvement over baseline. MDSA shows 2.4x latency improvement and 60% memory reduction vs LangChain.

### Trade-off
Balancing competing factors (e.g., speed vs accuracy, cost vs quality). MDSA optimizes for local deployment while maintaining high accuracy.

---

## Configuration Terminology

### Domain Configuration
Settings specific to a domain: model, knowledge base path, system prompt, tools.

### Environment Variable
System-level configuration stored in `.env` files. MDSA uses env vars for API keys, ports, and feature flags.

### Model Configuration
Settings for a specific model: temperature, max tokens, timeout, API endpoint.

### RAG Configuration
Settings for knowledge retrieval: chunk size, overlap, top-k results, similarity threshold.

### System Configuration
Global MDSA settings: cache size, log level, monitoring port.

---

## Security Terminology

### API Key
Secret credential for accessing cloud APIs. MDSA stores API keys in environment variables, never in code.

### Authentication
Verifying user identity before granting access. MDSA dashboard supports basic auth and token-based auth.

### Encryption
Converting data to secure format. MDSA can encrypt stored knowledge bases and cache data.

### Input Validation
Checking user input for malicious content or format violations. MDSA guardrails include input validation.

### Rate Limiting
Restricting request frequency to prevent abuse. MDSA supports configurable rate limits per IP or user.

### Sanitization
Removing dangerous content from inputs/outputs. MDSA guardrails can sanitize inputs before processing.

---

## Development Terminology

### Contributing
Adding code, documentation, or bug fixes to the MDSA project. See [Developer Guide](DEVELOPER_GUIDE.md).

### Debug Mode
Running MDSA with verbose logging for troubleshooting. Enable with `DEBUG=true` environment variable.

### Hot Reload
Automatically restarting MDSA when code changes. Useful during development.

### Logging
Recording system events, errors, and metrics to files or console. MDSA supports configurable log levels.

### Testing
Verifying code correctness through unit tests, integration tests, and end-to-end tests.

### Version Control
Managing code changes with Git. MDSA development uses GitHub for version control.

---

## Related Technologies

### Docker
Containerization platform for packaging MDSA with all dependencies for consistent deployment.

### Flask
Python web framework used by MDSA dashboard backend.

### Nginx
Web server that can proxy requests to MDSA for production deployment.

### Python
Programming language MDSA is written in. Requires Python 3.9+.

### Redis
In-memory database that can be used for distributed caching in multi-instance MDSA deployments.

### SQLite
Lightweight database that MDSA can use for storing request history and analytics.

---

## Usage Examples

### Example: Domain
```python
# Define a medical diagnosis domain
domain = {
    "name": "clinical_diagnosis",
    "model": "deepseek-v3.1",
    "kb_path": "knowledge_base/clinical/",
    "system_prompt": "You are a clinical diagnosis assistant..."
}
```

### Example: RAG Query
```text
User: "What are symptoms of diabetes?"
→ Domain Classification: clinical_diagnosis (94% confidence)
→ RAG Retrieval: 3 docs from clinical KB
→ Augmented Prompt: [system_prompt + 3 docs + user query]
→ Model Inference: Deepseek-v3.1 generates response
→ Response: "Common symptoms include increased thirst..."
```

### Example: Cache Hit
```text
Query 1: "What is machine learning?" → 625ms (cache miss)
Query 2: "What is machine learning?" → <10ms (cache hit, 200x faster)
```

---

## Cross-References

For more information, see:

- **[Architecture Documentation](ARCHITECTURE.md)** - Technical architecture details
- **[User Guide](USER_GUIDE.md)** - Using MDSA features
- **[Developer Guide](DEVELOPER_GUIDE.md)** - Development and contribution
- **[Performance Optimizations](PERFORMANCE_OPTIMIZATIONS.md)** - Benchmark methodology
- **[Research Paper Content](RESEARCH_PAPER_CONTENT.md)** - Academic research

---

**Total Terms**: 100+
**Last Updated**: December 2025
**Maintained by**: MDSA Framework Team
