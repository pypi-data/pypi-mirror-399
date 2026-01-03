# MDSA Framework - Complete Reference

**Multi-Domain Specialized Agentic Orchestration Framework**
**Version**: 1.0.0
**Date**: 2025-12-06

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Core Components](#core-components)
4. [Domain System](#domain-system)
5. [Model Management](#model-management)
6. [Async Execution](#async-execution)
7. [Tools System](#tools-system)
8. [Memory & RAG](#memory--rag)
9. [Monitoring & Logging](#monitoring--logging)
10. [UI & Dashboards](#ui--dashboards)
11. [Utilities](#utilities)
12. [API Reference](#api-reference)
13. [Configuration](#configuration)
14. [Examples](#examples)

---

## Overview

### What is MDSA?

MDSA (Multi-Domain Specialized Agentic Orchestration) is a production-ready orchestration framework for deploying multiple specialized language models across different domains. It intelligently routes user queries to the most appropriate domain and model, enabling efficient, accurate responses.

### Key Features

- **Intelligent Routing**: TinyBERT-based classification (< 50ms)
- **Hybrid Orchestration**: Simple queries → TinyBERT, Complex queries → Phi-2 reasoning
- **Domain Specialization**: Finance, Medical, Support, Technical domains
- **Dual RAG System**: Local (domain-specific) + Global (shared) knowledge bases
- **Model Management**: LRU caching, quantization, GPU optimization
- **Async Execution**: Concurrent request processing
- **Tool Integration**: Extensible tool system for enhanced capabilities
- **Real-time Monitoring**: Enhanced dashboard with D3.js visualizations
- **Validation**: Two-tier validation (rule-based + semantic)

### Architecture Principles

1. **Modularity**: Each component is independent and testable
2. **Scalability**: Async execution for high throughput
3. **Efficiency**: Model caching, quantization, GPU acceleration
4. **Flexibility**: Easy to add new domains, models, tools
5. **Observability**: Comprehensive logging and monitoring

---

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                          │
│                    (CLI / Web Dashboard)                        │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Orchestrator (Core)                        │
│  ┌───────────────┐  ┌──────────────┐  ┌────────────────────┐  │
│  │ TinyBERT      │  │ Phi-2        │  │ State Machine      │  │
│  │ Router        │  │ Reasoner     │  │ (Workflow)         │  │
│  │ (< 50ms)      │  │ (Complex)    │  │                    │  │
│  └───────────────┘  └──────────────┘  └────────────────────┘  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Domain Executor                           │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐  │
│  │ Finance   │  │ Medical   │  │ Support   │  │ Technical │  │
│  │ Domain    │  │ Domain    │  │ Domain    │  │ Domain    │  │
│  └───────────┘  └───────────┘  └───────────┘  └───────────┘  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Model Manager                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │ Model Loader │  │ LRU Cache    │  │ Quantization        │ │
│  │              │  │ (max 3 mods) │  │ (INT8/INT4)         │ │
│  └──────────────┘  └──────────────┘  └──────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Supporting Systems                          │
│  ┌──────────┐  ┌───────────┐  ┌──────────┐  ┌──────────────┐  │
│  │ Dual RAG │  │ Tools     │  │ Metrics  │  │ Dashboard    │  │
│  │ System   │  │ Registry  │  │ Logger   │  │ (D3.js)      │  │
│  └──────────┘  └───────────┘  └──────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Request Flow

```
1. User Query
   ↓
2. Complexity Analysis
   ├─ Simple (score < 0.3) → TinyBERT Router → Domain
   └─ Complex (score ≥ 0.3) → Phi-2 Reasoner → Task Decomposition
   ↓
3. Domain Selection
   ├─ Finance (money, transfer, payment)
   ├─ Medical (health, symptom, doctor)
   ├─ Support (help, issue, question)
   └─ Technical (error, bug, install)
   ↓
4. Model Execution
   ├─ Load Model (with LRU caching)
   ├─ Apply Quantization (INT8/INT4)
   ├─ RAG Retrieval (Local + Global)
   └─ Generate Response
   ↓
5. Validation
   ├─ Tier 1: Rule-based (< 10ms)
   └─ Tier 2: Phi-2 semantic (< 100ms, optional)
   ↓
6. Response
```

---

## Core Components

### 1. Orchestrator

**File**: `mdsa/core/orchestrator.py`

The central coordinator that manages request routing and execution.

#### Key Features

- **Intelligent routing** via TinyBERT classifier
- **Hybrid orchestration** (simple vs complex queries)
- **State machine** workflow management
- **Communication bus** for inter-component messaging
- **Metrics tracking** and logging

#### Usage

```python
from mdsa.core.orchestrator import Orchestrator

# Create orchestrator
orchestrator = Orchestrator(
    enable_reasoning=True,      # Enable Phi-2 for complex queries
    complexity_threshold=0.3    # Threshold for complex routing
)

# Process request
result = orchestrator.process_request(
    query="Transfer $100 to account 123 and check balance",
    context={'user_id': 'user123'}
)

# Result structure
{
    'status': 'success',
    'domain': 'finance',
    'model': 'microsoft/phi-2',
    'response': 'Transfer initiated...',
    'latency_ms': 145.3,
    'correlation_id': 'req_abc123',
    'complexity_score': 0.45,
    'reasoning_used': True
}
```

#### Methods

**`process_request(query, context)`**
- Main entry point for request processing
- Returns complete result dictionary

**`get_stats()`**
- Returns orchestrator statistics
- Includes routing distribution, average latency, etc.

**`shutdown()`**
- Cleanup and shutdown
- Releases models, closes connections

### 2. Router

**File**: `mdsa/core/router.py`

TinyBERT-based classification for domain routing.

#### Key Features

- **Fast classification** (< 50ms)
- **Keyword-based fallback** for robustness
- **Confidence thresholding**
- **Statistics tracking**

#### Usage

```python
from mdsa.core.router import Router

router = Router()

# Classify query
domain, confidence = router.classify("How do I transfer money?")
# Returns: ('finance', 0.98)

# Get routing statistics
stats = router.get_stats()
# {
#     'total_classifications': 100,
#     'average_confidence': 0.92,
#     'domain_distribution': {'finance': 35, 'medical': 25, ...}
# }
```

### 3. Complexity Analyzer

**File**: `mdsa/core/complexity_analyzer.py`

Analyzes query complexity to determine routing strategy.

#### Complexity Scoring

```python
from mdsa.core.complexity_analyzer import ComplexityAnalyzer

analyzer = ComplexityAnalyzer(complexity_threshold=0.3)

result = analyzer.analyze("Transfer money and then check balance")

# ComplexityResult:
# {
#     'is_complex': True,
#     'complexity_score': 0.45,
#     'indicators': ['multi_domain', 'sequential'],
#     'requires_reasoning': True,
#     'requires_multi_domain': True,
#     'requires_sequential': True
# }
```

#### Scoring Factors

| Factor | Weight | Keywords |
|--------|--------|----------|
| Multi-domain | 0.30 | "and then", "then", "after that" |
| Conditional | 0.25 | "if", "when", "unless" |
| Sequential | 0.20 | "first", "second", "third" |
| Reasoning | 0.15 | "why", "how", "explain", "compare" |
| Comparison | 0.10 | "versus", "better", "different" |

### 4. Phi-2 Reasoner

**File**: `mdsa/core/reasoner.py`

Task decomposition and planning for complex queries.

#### Usage

```python
from mdsa.core.reasoner import Phi2Reasoner

reasoner = Phi2Reasoner()

result = reasoner.analyze_and_plan(
    query="Transfer $100, then check balance, and if balance is low, notify me"
)

# ReasoningResult:
# {
#     'tasks': [
#         Task(task_id=1, description="Transfer $100", domain="finance"),
#         Task(task_id=2, description="Check balance", domain="finance", dependencies=[1]),
#         Task(task_id=3, description="Notify if low", domain="support", dependencies=[2])
#     ],
#     'execution_plan': "Sequential: 1 → 2 → 3",
#     'estimated_time_ms': 450.0
# }
```

### 5. State Machine

**File**: `mdsa/core/state_machine.py`

Workflow state management for request processing.

#### State Transitions

```
START
  ↓
VALIDATE_PRE (input validation)
  ↓
CLASSIFY (domain routing)
  ↓
LOAD_SLM (model loading)
  ↓
EXECUTE (model execution)
  ↓
VALIDATE_POST (output validation)
  ↓
COMPLETE
```

#### Usage

```python
from mdsa.core.state_machine import StateMachine, WorkflowState

machine = StateMachine()

# Transition through states
machine.transition(WorkflowState.VALIDATE_PRE)
machine.transition(WorkflowState.CLASSIFY)
machine.transition(WorkflowState.LOAD_SLM)
machine.transition(WorkflowState.EXECUTE)
machine.transition(WorkflowState.VALIDATE_POST)
machine.transition(WorkflowState.COMPLETE)

# Get current state
current = machine.get_current_state()  # WorkflowState.COMPLETE

# Get transition history
history = machine.get_history()
# [
#     ('START', 'VALIDATE_PRE', timestamp),
#     ('VALIDATE_PRE', 'CLASSIFY', timestamp),
#     ...
# ]
```

---

## Domain System

### Domain Configuration

**File**: `mdsa/domains/config.py`

Defines domain-specific settings and models.

#### DomainConfig

```python
from mdsa.domains.config import DomainConfig
from mdsa.models.config import ModelTier, QuantizationType

config = DomainConfig(
    # Domain identification
    domain_id="finance",
    name="Financial Services",
    description="Banking and financial queries",
    keywords=["money", "transfer", "payment", "balance"],

    # Model configuration
    model_name="microsoft/phi-2",
    model_tier=ModelTier.TIER2,
    quantization=QuantizationType.INT8,
    device="cuda:0",  # or "cpu"

    # Prompt configuration
    system_prompt="You are a financial assistant...",
    prompt_template="{query}",
    max_tokens=256,
    temperature=0.3,

    # Validation settings
    min_response_length=10,
    max_response_length=2048,
    use_model_validation=True,  # Enable Phi-2 semantic validation
)
```

### Predefined Domains

#### Finance Domain

```python
from mdsa.domains.config import get_predefined_domain

finance = get_predefined_domain('finance')

# Keywords:
# money, transfer, payment, balance, account, transaction,
# deposit, withdraw, bank, credit, debit, loan, interest
```

#### Medical Domain

```python
medical = get_predefined_domain('medical')

# Keywords:
# health, symptom, doctor, medicine, pain, fever, illness,
# disease, treatment, hospital, diagnosis, prescription
```

#### Support Domain

```python
support = get_predefined_domain('support')

# Keywords:
# help, support, issue, problem, question, how, what,
# cancel, refund, return, order, service
```

#### Technical Domain

```python
technical = get_predefined_domain('technical')

# Keywords:
# error, bug, crash, install, update, software, hardware,
# troubleshoot, fix, configure, setup
```

### Domain Executor

**File**: `mdsa/domains/executor.py`

Executes queries within a specific domain.

```python
from mdsa.domains.executor import DomainExecutor
from mdsa.models.manager import ModelManager

model_manager = ModelManager(max_models=3)
executor = DomainExecutor(model_manager)

# Execute in domain
result = await executor.execute(
    query="Transfer $100 to account 123",
    domain_config=finance_config
)

# Result:
# {
#     'status': 'success',
#     'response': 'Transfer initiated...',
#     'latency_ms': 145.3,
#     'domain': 'finance',
#     'model': 'microsoft/phi-2'
# }
```

---

## Model Management

### Model Configuration

**File**: `mdsa/models/config.py`

#### ModelConfig

```python
from mdsa.models.config import ModelConfig, ModelTier, QuantizationType

config = ModelConfig(
    model_name="microsoft/phi-2",
    tier=ModelTier.TIER2,
    device="cuda:0",
    quantization=QuantizationType.INT8,
    max_tokens=512,
    temperature=0.7,
    top_p=0.9,
    top_k=50
)
```

#### Model Tiers

```python
class ModelTier(Enum):
    TIER1 = "tier1"  # Smallest (< 1B params) - GPT-2, TinyBERT
    TIER2 = "tier2"  # Medium (1-3B params) - Phi-2, Llama-2-7B
    TIER3 = "tier3"  # Large (> 3B params) - Future expansion
```

#### Quantization Types

```python
class QuantizationType(Enum):
    NONE = "none"    # No quantization (full precision)
    INT8 = "int8"    # 8-bit quantization (~50% memory)
    INT4 = "int4"    # 4-bit quantization (~75% memory)
    FP16 = "fp16"    # Half precision
```

### Model Manager

**File**: `mdsa/models/manager.py`

LRU cache-based model management.

#### Usage

```python
from mdsa.models.manager import ModelManager

manager = ModelManager(max_models=3)  # Keep max 3 models in memory

# Load model (cached if already loaded)
model = manager.load_model(config)

# Unload specific model
manager.unload_model("microsoft/phi-2")

# Get statistics
stats = manager.get_stats()
# {
#     'loaded_models': 2,
#     'max_models': 3,
#     'cache_hits': 15,
#     'cache_misses': 3
# }

# Cleanup
manager.cleanup()
```

### Model Loader

**File**: `mdsa/models/loader.py`

Low-level model loading with optimization.

```python
from mdsa.models.loader import ModelLoader

loader = ModelLoader()

# Load with quantization
model = loader.load_model(
    model_name="microsoft/phi-2",
    device="cuda:0",
    quantization=QuantizationType.INT8
)

# Generate text
output = model.generate(
    prompt="Translate to French: Hello",
    max_tokens=50,
    temperature=0.7
)
```

---

## Async Execution

### Async Executor

**File**: `mdsa/async_/executor.py`

Concurrent request processing with ThreadPoolExecutor.

#### Usage

```python
from mdsa.async_.executor import AsyncExecutor
from mdsa.domains.executor import DomainExecutor

domain_executor = DomainExecutor(model_manager)
async_executor = AsyncExecutor(
    domain_executor,
    max_workers=5  # Concurrent threads
)

# Execute single request
result = await async_executor.execute_async(query, domain_config)

# Execute batch
queries = ["Query 1", "Query 2", "Query 3"]
results = await async_executor.execute_batch_async(queries, domain_config)

# Shutdown
await async_executor.shutdown_async()
```

### Async Manager

**File**: `mdsa/async_/manager.py`

Higher-level async orchestration.

```python
from mdsa.async_.manager import AsyncManager

manager = AsyncManager(
    domain_executor,
    max_concurrent=10  # Max concurrent requests
)

# Process batch with timeout
results = await manager.process_batch(
    queries=["Q1", "Q2", "Q3"],
    domain_config=config,
    timeout=30.0  # seconds
)

# Graceful shutdown
await manager.shutdown()
```

---

## Tools System

### Tool Base

**File**: `mdsa/tools/base.py`

Base class for all tools.

```python
from mdsa.tools.base import Tool, ToolParameter, ToolResult

class CustomTool(Tool):
    def __init__(self):
        super().__init__(
            name="custom_tool",
            description="My custom tool",
            parameters=[
                ToolParameter(
                    name="input",
                    type="string",
                    description="Input text",
                    required=True
                )
            ]
        )

    async def execute(self, **kwargs) -> ToolResult:
        input_text = kwargs.get('input')
        result = self.process(input_text)

        return ToolResult(
            success=True,
            data={'output': result},
            metadata={'execution_time': 0.5}
        )
```

### Builtin Tools

**File**: `mdsa/tools/builtin.py`

```python
from mdsa.tools.builtin import (
    WebSearchTool,
    CalculatorTool,
    DateTimeTool,
    TextAnalysisTool
)

# Web search
search = WebSearchTool()
result = await search.execute(query="MDSA framework")

# Calculator
calc = CalculatorTool()
result = await calc.execute(expression="2 + 2 * 3")

# DateTime
dt = DateTimeTool()
result = await dt.execute(operation="current_time")

# Text analysis
analyzer = TextAnalysisTool()
result = await analyzer.execute(
    text="Hello world",
    operations=["word_count", "sentiment"]
)
```

### Tool Registry

**File**: `mdsa/tools/registry.py`

```python
from mdsa.tools.registry import ToolRegistry

registry = ToolRegistry()

# Register tool
registry.register(CustomTool())

# Get tool
tool = registry.get_tool("custom_tool")

# List all tools
tools = registry.list_tools()

# Execute tool
result = await registry.execute_tool(
    "custom_tool",
    input="test data"
)
```

---

## Memory & RAG

### Dual RAG System

**File**: `mdsa/memory/dual_rag.py`

Combines LocalRAG (domain-specific) and GlobalRAG (shared).

#### LocalRAG

Domain-isolated knowledge base.

```python
from mdsa.memory.dual_rag import LocalRAG

# Create LocalRAG for domain
local_rag = LocalRAG(domain_id="medical", max_documents=1000)

# Add documents
doc_id = local_rag.add_document(
    "ICD-10 code E11.9: Type 2 diabetes",
    metadata={'type': 'diagnosis'}
)

# Retrieve
result = local_rag.retrieve(
    query="diabetes ICD code",
    top_k=5,
    metadata_filter={'type': 'diagnosis'}
)

# Result:
# RAGResult(
#     source='local',
#     documents=[RAGDocument(...)],
#     retrieval_time_ms=12.3
# )
```

#### GlobalRAG

Shared knowledge base across all domains.

```python
from mdsa.memory.dual_rag import GlobalRAG

global_rag = GlobalRAG(max_documents=10000)

# Add document with tags
doc_id = global_rag.add_document(
    "Diabetes is a metabolic disorder",
    tags=['medical', 'general'],
    metadata={'category': 'definition'}
)

# Retrieve (accessible by all domains)
result = global_rag.retrieve(
    query="diabetes definition",
    requesting_domain="medical",  # Track access
    top_k=5
)
```

#### DualRAG

Unified interface combining both.

```python
from mdsa.memory.dual_rag import DualRAG

dual_rag = DualRAG()

# Register domain
local_rag = dual_rag.register_domain("medical")

# Add to LocalRAG (domain-specific)
dual_rag.add_to_local(
    "medical",
    "ICD-10 E11.9: Diabetes",
    metadata={'type': 'code'}
)

# Add to GlobalRAG (shared)
dual_rag.add_to_global(
    "Diabetes is a chronic disease",
    tags=['medical', 'definition']
)

# Retrieve from both
results = dual_rag.retrieve(
    query="diabetes",
    domain_id="medical",
    search_local=True,   # Search domain-specific
    search_global=True,  # Search shared
    top_k=5
)

# Returns:
# {
#     'local': RAGResult(...),   # From medical's LocalRAG
#     'global': RAGResult(...)   # From GlobalRAG
# }
```

#### Domain Isolation

```python
# Domain A cannot access Domain B's LocalRAG
dual_rag.register_domain("domain_a")
dual_rag.register_domain("domain_b")

dual_rag.add_to_local("domain_a", "Secret data for A")

# Domain B tries to access
results = dual_rag.retrieve(
    query="secret data",
    domain_id="domain_b",
    search_local=True,
    search_global=False
)

# Results: empty (domain isolation enforced)
assert len(results['local'].documents) == 0
```

---

## Monitoring & Logging

### Metrics Logger

**File**: `mdsa/monitoring/metrics.py`

```python
from mdsa.monitoring.metrics import MetricsCollector

collector = MetricsCollector()

# Record request
collector.record_request(
    domain="finance",
    latency_ms=145.3,
    success=True,
    model="microsoft/phi-2"
)

# Get statistics
stats = collector.get_stats()
# {
#     'total_requests': 100,
#     'success_rate': 0.95,
#     'avg_latency_ms': 132.5,
#     'domain_distribution': {'finance': 35, 'medical': 25, ...}
# }

# Export to file
collector.export_metrics("metrics.json")
```

### System Logger

**File**: `mdsa/monitoring/logger.py`

```python
from mdsa.monitoring.logger import setup_logger

logger = setup_logger(
    name="mdsa",
    level="INFO",
    log_file="mdsa.log"
)

logger.info("Request processed", extra={
    'domain': 'finance',
    'latency_ms': 145.3
})

logger.error("Model loading failed", extra={
    'model': 'phi-2',
    'error': str(e)
})
```

---

## UI & Dashboards

### Enhanced Dashboard

**File**: `mdsa/ui/enhanced_dashboard.py`

D3.js-powered real-time monitoring dashboard.

```python
from mdsa.ui.enhanced_dashboard import EnhancedDashboard

dashboard = EnhancedDashboard(output_dir="./dashboard_output")

# Track request
dashboard.track_request(
    query="Transfer money",
    domain="finance",
    model="phi-2",
    latency_ms=145.3,
    success=True,
    correlation_id="req_123"
)

# Get metrics
metrics = dashboard.get_current_metrics()
# {
#     'total_requests': 100,
#     'success_rate': 0.95,
#     'avg_latency_ms': 130.5,
#     'active_domains': ['finance', 'medical'],
#     'routing_distribution': {'finance': 40, 'medical': 30, ...}
# }

# Generate HTML dashboard
html_file = dashboard.generate_html_dashboard()
# Opens browser with real-time D3.js visualizations
```

### Dashboard Features

- **Real-time flow diagrams** (D3.js node-link)
- **Routing distribution charts** (D3.js bar chart)
- **Live metrics** (auto-refresh every 5s)
- **Interactive nodes** (hover effects)
- **Beautiful UI** (gradient design)

---

## Utilities

### Device Configuration

**File**: `mdsa/utils/device_config.py`

Smart device selection for optimal performance.

```python
from mdsa.utils.device_config import get_recommended_config, DeviceStrategy

# Auto-detect optimal configuration
config = get_recommended_config(prefer_gpu=True)
# {
#     'device': 'cuda:0',
#     'quantization': QuantizationType.INT8,
#     'max_models': 3,
#     'max_workers': 5
# }

# Force CPU
config = get_recommended_config(prefer_gpu=False)
# {
#     'device': 'cpu',
#     'quantization': QuantizationType.INT4,
#     'max_models': 2,
#     'max_workers': 4
# }

# Select for Phi-2
device, quant = DeviceStrategy.select_for_phi2(
    prefer_gpu=True,
    force_device=None
)
```

### Hardware Detection

**File**: `mdsa/utils/hardware.py`

```python
from mdsa.utils.hardware import get_system_info, get_gpu_info

# System info
info = get_system_info()
# {
#     'cpu_count': 8,
#     'memory_gb': 16.0,
#     'platform': 'Windows',
#     'python_version': '3.13.3'
# }

# GPU info
gpu_info = get_gpu_info()
# {
#     'has_cuda': True,
#     'cuda_version': '12.1',
#     'gpu_name': 'NVIDIA GeForce RTX 3050',
#     'gpu_memory_gb': 4.0
# }
```

### Configuration Loader

**File**: `mdsa/utils/config_loader.py`

```python
from mdsa.utils.config_loader import ConfigLoader

loader = ConfigLoader()

# Load YAML config
config = loader.load("config.yaml")

# Load JSON config
config = loader.load("config.json")

# Save config
loader.save(config, "output.yaml", format="yaml")
```

---

## API Reference

### Quick Reference

#### Create Orchestrator

```python
from mdsa.core.orchestrator import Orchestrator

orchestrator = Orchestrator(
    enable_reasoning=True,
    complexity_threshold=0.3
)
```

#### Process Request

```python
result = orchestrator.process_request(
    query="Your query here",
    context={'user_id': 'user123'}
)
```

#### Create Custom Domain

```python
from mdsa.domains.config import DomainConfig
from mdsa.models.config import ModelTier, QuantizationType

domain = DomainConfig(
    domain_id="custom",
    name="Custom Domain",
    description="Custom domain",
    keywords=["custom", "keywords"],
    model_name="microsoft/phi-2",
    model_tier=ModelTier.TIER2,
    quantization=QuantizationType.INT8
)
```

#### Use RAG

```python
from mdsa.memory.dual_rag import DualRAG

dual_rag = DualRAG()
dual_rag.register_domain("finance")

# Add knowledge
dual_rag.add_to_local("finance", "Domain-specific knowledge")
dual_rag.add_to_global("Shared knowledge", tags=['general'])

# Retrieve
results = dual_rag.retrieve("query", "finance")
```

---

## Configuration

### YAML Config Example

```yaml
# config.yaml

orchestrator:
  enable_reasoning: true
  complexity_threshold: 0.3
  max_workers: 5

domains:
  - domain_id: finance
    name: Financial Services
    keywords:
      - money
      - transfer
      - payment
    model_name: microsoft/phi-2
    model_tier: tier2
    quantization: int8
    device: cuda:0
    max_tokens: 256
    temperature: 0.3

  - domain_id: medical
    name: Medical Information
    keywords:
      - health
      - symptom
      - doctor
    model_name: microsoft/phi-2
    model_tier: tier2
    quantization: int8
    device: cuda:0

models:
  max_models: 3
  cache_strategy: lru

monitoring:
  enable_metrics: true
  enable_dashboard: true
  log_level: INFO
```

### Python Config

```python
# config.py

CONFIG = {
    'orchestrator': {
        'enable_reasoning': True,
        'complexity_threshold': 0.3,
        'max_workers': 5
    },
    'models': {
        'max_models': 3,
        'cache_strategy': 'lru'
    },
    'monitoring': {
        'enable_metrics': True,
        'enable_dashboard': True,
        'log_level': 'INFO'
    }
}
```

---

## Examples

### Example 1: Basic Usage

```python
from mdsa.core.orchestrator import Orchestrator

# Create orchestrator
orchestrator = Orchestrator()

# Process query
result = orchestrator.process_request("How do I transfer money?")

print(f"Domain: {result['domain']}")
print(f"Response: {result['response']}")
print(f"Latency: {result['latency_ms']}ms")
```

### Example 2: Custom Domain

```python
from mdsa.domains.config import DomainConfig
from mdsa.domains.executor import DomainExecutor
from mdsa.models.manager import ModelManager

# Create custom domain
custom_domain = DomainConfig(
    domain_id="legal",
    name="Legal Domain",
    description="Legal advice and information",
    keywords=["law", "legal", "court", "lawyer"],
    model_name="microsoft/phi-2",
    max_tokens=512
)

# Execute in domain
model_manager = ModelManager()
executor = DomainExecutor(model_manager)

result = await executor.execute(
    "What is a contract?",
    custom_domain
)
```

### Example 3: Batch Processing

```python
from mdsa.async_.manager import AsyncManager

manager = AsyncManager(domain_executor, max_concurrent=10)

queries = [
    "Transfer $100",
    "Check my balance",
    "What are flu symptoms?",
    "Fix my password"
]

results = await manager.process_batch(queries, domain_config)

for query, result in zip(queries, results):
    print(f"{query}: {result['response']}")
```

### Example 4: RAG Integration

```python
from mdsa.memory.dual_rag import DualRAG

dual_rag = DualRAG()
dual_rag.register_domain("medical")

# Add medical codes
dual_rag.add_to_local(
    "medical",
    "ICD-10 E11.9: Type 2 diabetes without complications",
    metadata={'type': 'diagnosis_code'}
)

# Add general medical knowledge
dual_rag.add_to_global(
    "Diabetes is a chronic metabolic disorder",
    tags=['medical', 'definition']
)

# Query with RAG
results = dual_rag.retrieve(
    query="diabetes code",
    domain_id="medical",
    top_k=5
)

print("Local:", results['local'].documents)
print("Global:", results['global'].documents)
```

### Example 5: Dashboard Integration

```python
from mdsa.core.orchestrator import Orchestrator
from mdsa.ui.enhanced_dashboard import EnhancedDashboard

orchestrator = Orchestrator()
dashboard = EnhancedDashboard()

# Process requests
queries = ["Query 1", "Query 2", "Query 3"]

for query in queries:
    result = orchestrator.process_request(query)

    # Track in dashboard
    dashboard.track_request(
        query=query,
        domain=result['domain'],
        model=result['model'],
        latency_ms=result['latency_ms'],
        success=result['status'] == 'success',
        correlation_id=result['correlation_id']
    )

# Generate dashboard
html_file = dashboard.generate_html_dashboard()
print(f"Dashboard: {html_file}")
```

---

## Best Practices

### Performance

1. **Use GPU** when available (5-10x faster)
2. **Enable quantization** (INT8 or INT4)
3. **Set max_models=3** for optimal memory usage
4. **Use async execution** for batches
5. **Enable model caching** (LRU)

### Scalability

1. **Increase max_workers** for higher throughput
2. **Use async manager** for concurrent requests
3. **Monitor metrics** to identify bottlenecks
4. **Optimize prompts** for faster generation

### Accuracy

1. **Fine-tune prompts** per domain
2. **Use Phi-2 validation** (Tier 2)
3. **Enable RAG** for domain knowledge
4. **Set appropriate temperature** (0.3 for factual, 0.7 for creative)

### Maintainability

1. **Use configuration files** (YAML/JSON)
2. **Enable comprehensive logging**
3. **Monitor with dashboard**
4. **Write tests** for custom components

---

## Troubleshooting

### Common Issues

#### 1. Model Loading Slow

**Problem**: First model load takes 3-4 seconds

**Solution**:
- Enable quantization (INT8 or INT4)
- Use GPU if available
- Models are cached after first load

#### 2. Out of Memory

**Problem**: GPU/CPU runs out of memory

**Solution**:
```python
# Reduce max models
manager = ModelManager(max_models=2)

# Use quantization
config = ModelConfig(quantization=QuantizationType.INT4)

# Force CPU
config = ModelConfig(device="cpu")
```

#### 3. Low Accuracy

**Problem**: Responses not accurate

**Solution**:
- Enable RAG for domain knowledge
- Fine-tune system prompts
- Use Phi-2 validation (Tier 2)
- Adjust temperature (lower = more factual)

#### 4. Slow Routing

**Problem**: Classification takes > 100ms

**Solution**:
- TinyBERT should be < 50ms
- Check GPU availability
- Verify model is cached
- Monitor with `router.get_stats()`

---

## License

MDSA Framework is released under MIT License.

---

## Support

For issues, questions, or contributions:
- GitHub: https://github.com/mdsa-framework
- Documentation: https://mdsa-docs.readthedocs.io
- Email: support@mdsa-framework.org

---

**Version**: 1.0.0
**Last Updated**: 2025-12-06
**Author**: MDSA Framework Team
