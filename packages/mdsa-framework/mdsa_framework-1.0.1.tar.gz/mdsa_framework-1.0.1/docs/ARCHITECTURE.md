# MDSA Framework - Architecture Guide

**Version**: 1.0.0
**Date**: 2025-12-06
**Author**: Multi-Domain Specialized Agentic Orchestration Framework Team

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Component Architecture](#component-architecture)
3. [Data Flow Diagrams](#data-flow-diagrams)
4. [Sequence Diagrams](#sequence-diagrams)
5. [Module Dependency](#module-dependency)
6. [Deployment Architecture](#deployment-architecture)
7. [Scalability & Performance](#scalability--performance)

---

## System Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              MDSA Framework                                 │
│                   Multi-Domain Specialized Agents System                     │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                           Presentation Layer                                │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────────────────┐ │
│  │ CLI        │  │ Web UI     │  │ Dashboard  │  │ REST API             │ │
│  │ Interface  │  │ (Gradio)   │  │ (D3.js)    │  │ (Future)             │ │
│  └────────────┘  └────────────┘  └────────────┘  └──────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Orchestration Layer                                │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        Hybrid Orchestrator                          │   │
│  │  ┌──────────────┐     ┌──────────────┐     ┌──────────────────┐   │   │
│  │  │ Complexity   │────▶│ TinyBERT     │     │ Phi-2            │   │   │
│  │  │ Analyzer     │     │ Router       │     │ Reasoner         │   │   │
│  │  │ (0.0-1.0)    │     │ (< 50ms)     │     │ (Complex Tasks)  │   │   │
│  │  └──────────────┘     └──────────────┘     └──────────────────┘   │   │
│  │                                                                     │   │
│  │  Simple (< 0.3)  →  TinyBERT  →  Single Domain                    │   │
│  │  Complex (≥ 0.3) →  Phi-2     →  Multi-Step Execution             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            Domain Layer                                     │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐              │
│  │ Finance   │  │ Medical   │  │ Support   │  │ Technical │              │
│  │ Domain    │  │ Domain    │  │ Domain    │  │ Domain    │              │
│  │           │  │           │  │           │  │           │              │
│  │ Phi-2     │  │ Phi-2     │  │ Phi-2     │  │ Phi-2     │              │
│  │ INT8/INT4 │  │ INT8/INT4 │  │ INT8/INT4 │  │ INT8/INT4 │              │
│  └───────────┘  └───────────┘  └───────────┘  └───────────┘              │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Model Management Layer                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        Model Manager                                │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐ │   │
│  │  │ LRU Cache    │  │ Quantization │  │ Device Selection         │ │   │
│  │  │ (Max 3)      │  │ (INT8/INT4)  │  │ (CPU/GPU)               │ │   │
│  │  └──────────────┘  └──────────────┘  └──────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Supporting Systems                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐  │
│  │ Dual RAG │  │ Tools    │  │ Metrics  │  │ Logger   │  │ Validator  │  │
│  │ System   │  │ Registry │  │ Tracker  │  │          │  │ (2-Tier)   │  │
│  │          │  │          │  │          │  │          │  │            │  │
│  │ Local +  │  │ Built-in │  │ Latency  │  │ Struc-   │  │ Rules +    │  │
│  │ Global   │  │ Custom   │  │ Success  │  │ tured    │  │ Semantic   │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Component Architecture

### 1. Core Components

```
mdsa/core/
│
├── orchestrator.py          # Main orchestrator
│   ├── Hybrid routing (TinyBERT + Phi-2)
│   ├── Request lifecycle management
│   ├── State machine integration
│   └── Statistics tracking
│
├── router.py                # TinyBERT classifier
│   ├── Fast domain classification (< 50ms)
│   ├── Keyword fallback
│   └── Confidence scoring
│
├── complexity_analyzer.py   # Query complexity analysis
│   ├── Multi-domain detection
│   ├── Sequential task detection
│   ├── Conditional logic detection
│   └── Scoring (0.0-1.0)
│
├── reasoner.py             # Phi-2 task decomposition
│   ├── Complex query analysis
│   ├── Task breakdown
│   ├── Dependency resolution
│   └── Execution planning
│
├── state_machine.py        # Workflow state management
│   ├── State transitions
│   ├── Validation checkpoints
│   └── History tracking
│
└── communication_bus.py    # Inter-component messaging
    ├── Event publishing
    ├── Event subscription
    └── Async message delivery
```

### 2. Domain Components

```
mdsa/domains/
│
├── config.py               # Domain configuration
│   ├── DomainConfig dataclass
│   ├── Predefined domains (finance, medical, support, technical)
│   └── Smart device selection
│
├── executor.py             # Domain execution
│   ├── Model loading
│   ├── Prompt formatting
│   ├── Response generation
│   └── Validation
│
├── validator.py            # Two-tier validation
│   ├── Tier 1: Rule-based (< 10ms)
│   │   ├── Length check
│   │   ├── Toxicity detection
│   │   └── Repetition check
│   └── Tier 2: Phi-2 semantic (< 100ms, optional)
│       ├── Relevance validation
│       ├── Coherence check
│       └── Consistency verification
│
├── model_validator.py      # Phi-2 semantic validator
│   ├── Input validation
│   ├── Response validation
│   └── Tool usage validation
│
├── prompts.py              # Domain-specific prompts
│   └── Enhanced prompts per domain
│
└── registry.py             # Domain registry
    ├── Domain registration
    └── Domain lookup
```

### 3. Model Management

```
mdsa/models/
│
├── config.py               # Model configuration
│   ├── ModelConfig dataclass
│   ├── Model tiers (TIER1/TIER2/TIER3)
│   └── Quantization types (NONE/INT8/INT4/FP16)
│
├── manager.py              # Model lifecycle management
│   ├── LRU caching (max 3 models)
│   ├── Model loading/unloading
│   ├── Memory management
│   └── Statistics tracking
│
├── loader.py               # Low-level model loading
│   ├── HuggingFace integration
│   ├── Quantization application
│   ├── Device placement
│   └── Model optimization
│
└── registry.py             # Model registry
    ├── Model metadata
    ├── Version tracking
    └── Capability mapping
```

### 4. Async Execution

```
mdsa/async_/
│
├── executor.py             # Async execution engine
│   ├── ThreadPoolExecutor integration
│   ├── Concurrent request handling
│   ├── Batch processing
│   └── Timeout management
│
└── manager.py              # High-level async orchestration
    ├── Request queuing
    ├── Load balancing
    ├── Error handling
    └── Graceful shutdown
```

### 5. Memory & RAG

```
mdsa/memory/
│
└── dual_rag.py             # Dual RAG system
    │
    ├── LocalRAG            # Domain-specific knowledge
    │   ├── Isolated per domain
    │   ├── LRU eviction
    │   ├── Keyword indexing
    │   └── Metadata filtering
    │
    ├── GlobalRAG           # Shared knowledge
    │   ├── Cross-domain access
    │   ├── Access tracking
    │   ├── Tag-based organization
    │   └── Usage analytics
    │
    └── DualRAG             # Unified interface
        ├── Domain registration
        ├── Retrieval coordination
        └── Statistics aggregation
```

### 6. Tools System

```
mdsa/tools/
│
├── base.py                 # Tool base classes
│   ├── Tool abstract class
│   ├── ToolParameter dataclass
│   └── ToolResult dataclass
│
├── builtin.py              # Built-in tools
│   ├── WebSearchTool
│   ├── CalculatorTool
│   ├── DateTimeTool
│   └── TextAnalysisTool
│
├── registry.py             # Tool registry
│   ├── Tool registration
│   ├── Tool discovery
│   └── Tool execution
│
└── smart_executor.py       # Intelligent tool execution
    ├── Tool selection
    ├── Parameter inference
    └── Result aggregation
```

### 7. UI & Monitoring

```
mdsa/ui/
│
├── enhanced_dashboard.py   # Real-time dashboard
│   ├── D3.js flow visualization
│   ├── Metrics tracking
│   ├── HTML generation
│   └── Auto-refresh
│
├── dashboard.py            # Basic dashboard
│   └── Gradio interface
│
└── auth.py                 # Authentication
    ├── User management
    └── Session handling

mdsa/monitoring/
│
├── metrics.py              # Metrics collection
│   ├── Request tracking
│   ├── Latency measurement
│   ├── Success rate calculation
│   └── Export functionality
│
└── logger.py               # Structured logging
    ├── Log formatting
    ├── Log levels
    └── File rotation
```

---

## Data Flow Diagrams

### Simple Query Flow (TinyBERT Router)

```
┌──────────┐
│  User    │
│  Query   │
└─────┬────┘
      │
      ▼
┌──────────────────┐
│  Orchestrator    │
│  ┌────────────┐  │
│  │ Complexity │  │
│  │ Analyzer   │  │
│  └──────┬─────┘  │
│         │        │
│         ▼        │
│  Score: 0.2      │
│  (Simple)        │
│         │        │
│         ▼        │
│  ┌────────────┐  │
│  │ TinyBERT   │  │
│  │ Router     │  │
│  └──────┬─────┘  │
│         │        │
│         ▼        │
│   Domain: Finance│
│   Confidence: 0.98│
└─────────┬────────┘
          │
          ▼
┌────────────────────┐
│  Domain Executor   │
│  ┌──────────────┐  │
│  │ Load Phi-2   │  │
│  │ (Finance)    │  │
│  └──────┬───────┘  │
│         │          │
│         ▼          │
│  ┌──────────────┐  │
│  │ RAG Retrieval│  │
│  │ Local+Global │  │
│  └──────┬───────┘  │
│         │          │
│         ▼          │
│  ┌──────────────┐  │
│  │ Generate     │  │
│  │ Response     │  │
│  └──────┬───────┘  │
│         │          │
│         ▼          │
│  ┌──────────────┐  │
│  │ Validate     │  │
│  │ (2-Tier)     │  │
│  └──────┬───────┘  │
└─────────┼──────────┘
          │
          ▼
┌─────────────────┐
│   Response      │
│   to User       │
└─────────────────┘

Latency: ~150ms
```

### Complex Query Flow (Phi-2 Reasoning)

```
┌──────────┐
│  User    │
│  Complex │
│  Query   │
└─────┬────┘
      │
      ▼
┌──────────────────────┐
│  Orchestrator        │
│  ┌────────────────┐  │
│  │ Complexity     │  │
│  │ Analyzer       │  │
│  └───────┬────────┘  │
│          │           │
│          ▼           │
│    Score: 0.45       │
│    (Complex)         │
│    - Multi-domain    │
│    - Sequential      │
│          │           │
│          ▼           │
│  ┌────────────────┐  │
│  │ Phi-2          │  │
│  │ Reasoner       │  │
│  └───────┬────────┘  │
│          │           │
│          ▼           │
│  ┌────────────────┐  │
│  │ Task           │  │
│  │ Decomposition  │  │
│  └───────┬────────┘  │
│          │           │
│          ▼           │
│  Task 1: Transfer $  │
│  Task 2: Check Bal   │
│  Task 3: Notify Low  │
│          │           │
│  Dependencies:       │
│  1 → 2 → 3          │
└──────────┼───────────┘
           │
           ▼
┌─────────────────────────┐
│  Sequential Execution   │
│                         │
│  ┌─────────────────┐    │
│  │ Execute Task 1  │    │
│  │ (Finance)       │    │
│  └────────┬────────┘    │
│           │             │
│           ▼             │
│  ┌─────────────────┐    │
│  │ Execute Task 2  │    │
│  │ (Finance)       │    │
│  └────────┬────────┘    │
│           │             │
│           ▼             │
│  ┌─────────────────┐    │
│  │ Execute Task 3  │    │
│  │ (Support)       │    │
│  └────────┬────────┘    │
└───────────┼─────────────┘
            │
            ▼
┌──────────────────────┐
│  Aggregate Results   │
│  & Validate          │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│   Response to User   │
└──────────────────────┘

Latency: ~450ms (3 sequential tasks)
```

### RAG Retrieval Flow

```
┌─────────────────────┐
│  Query: "diabetes   │
│  ICD code"          │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────────┐
│        DualRAG System               │
│                                     │
│  ┌───────────────────────────────┐ │
│  │  Domain: medical              │ │
│  │  Query: "diabetes ICD code"   │ │
│  └────────┬──────────────────────┘ │
│           │                        │
│           ▼                        │
│  ┌───────────────────────────────┐ │
│  │  Search Local RAG             │ │
│  │  (Medical domain only)        │ │
│  │                               │ │
│  │  - Keyword indexing           │ │
│  │  - Metadata filtering         │ │
│  │  - Relevance scoring          │ │
│  └────────┬──────────────────────┘ │
│           │                        │
│           ▼                        │
│  ┌───────────────────────────────┐ │
│  │  Local Results:               │ │
│  │  1. "ICD-10 E11.9: Type 2     │ │
│  │      diabetes"                │ │
│  │  2. "ICD-10 E10: Type 1       │ │
│  │      diabetes"                │ │
│  └────────┬──────────────────────┘ │
│           │                        │
│           ▼                        │
│  ┌───────────────────────────────┐ │
│  │  Search Global RAG            │ │
│  │  (Shared knowledge)           │ │
│  │                               │ │
│  │  - Cross-domain search        │ │
│  │  - Tag filtering              │ │
│  │  - Access tracking            │ │
│  └────────┬──────────────────────┘ │
│           │                        │
│           ▼                        │
│  ┌───────────────────────────────┐ │
│  │  Global Results:              │ │
│  │  1. "Diabetes is a metabolic  │ │
│  │      disorder..."             │ │
│  │  2. "Diabetes management      │ │
│  │      guidelines..."           │ │
│  └────────┬──────────────────────┘ │
│           │                        │
│           ▼                        │
│  ┌───────────────────────────────┐ │
│  │  Combine Results              │ │
│  │                               │ │
│  │  Local (domain-specific):     │ │
│  │   - ICD codes                 │ │
│  │   - Medical procedures        │ │
│  │                               │ │
│  │  Global (general):            │ │
│  │   - Definitions               │ │
│  │   - Guidelines                │ │
│  └────────┬──────────────────────┘ │
└───────────┼─────────────────────────┘
            │
            ▼
┌──────────────────────────┐
│  Augmented Prompt        │
│                          │
│  Query: diabetes ICD code│
│                          │
│  Context (Local):        │
│  - ICD-10 E11.9...       │
│  - ICD-10 E10...         │
│                          │
│  Context (Global):       │
│  - Diabetes definition...│
│  - Management guide...   │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│  Model Generation        │
│  (Phi-2)                 │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│  Response:               │
│  "The ICD-10 code for    │
│  Type 2 diabetes is      │
│  E11.9..."               │
└──────────────────────────┘
```

---

## Sequence Diagrams

### Request Processing Sequence

```
User        Orchestrator    Router     DomainExec   ModelMgr     RAG       Model
 │              │              │            │          │          │         │
 │──query──────>│              │            │          │          │         │
 │              │              │            │          │          │         │
 │              │──complexity─>│            │          │          │         │
 │              │<─score: 0.2──│            │          │          │         │
 │              │              │            │          │          │         │
 │              │──classify───>│            │          │          │         │
 │              │<─finance────<│            │          │          │         │
 │              │              │            │          │          │         │
 │              │──execute────────────────>│          │          │         │
 │              │              │            │          │          │         │
 │              │              │            │─load────>│          │         │
 │              │              │            │<─model───│          │         │
 │              │              │            │          │          │         │
 │              │              │            │─retrieve──────────>│         │
 │              │              │            │<─docs────────────<│         │
 │              │              │            │          │          │         │
 │              │              │            │─generate─────────────────────>│
 │              │              │            │<─response────────────────────<│
 │              │              │            │          │          │         │
 │              │              │            │─validate>│          │         │
 │              │              │            │<─valid───│          │         │
 │              │              │            │          │          │         │
 │              │<─result──────────────────<│          │          │         │
 │<─response───<│              │            │          │          │         │
 │              │              │            │          │          │         │
```

### Async Batch Processing Sequence

```
User     AsyncMgr    Executor1   Executor2   Executor3   DomainExec
 │           │           │           │           │          │
 │─batch────>│           │           │           │          │
 │  [Q1,Q2,  │           │           │           │          │
 │   Q3]     │           │           │           │          │
 │           │           │           │           │          │
 │           │──Q1──────>│           │           │          │
 │           │──Q2─────────────────>│           │          │
 │           │──Q3───────────────────────────>│          │
 │           │           │           │           │          │
 │           │           │─exec Q1──────────────────────────>│
 │           │           │           │           │          │
 │           │           │           │─exec Q2──────────────>│
 │           │           │           │           │          │
 │           │           │           │           │─exec Q3─>│
 │           │           │           │           │          │
 │           │           │<─R1───────────────────────────────│
 │           │<─R1──────<│           │           │          │
 │           │           │           │           │          │
 │           │           │           │<─R2───────────────────│
 │           │           │<─R2──────────────────<│          │
 │           │           │           │           │          │
 │           │           │           │           │<─R3──────│
 │           │           │<─R3──────────────────────────────<│
 │           │           │           │           │          │
 │           │─aggregate>│           │           │          │
 │<─results─<│           │           │           │          │
 │  [R1,R2,  │           │           │           │          │
 │   R3]     │           │           │           │          │
 │           │           │           │           │          │

Time: Concurrent execution ~150ms (vs sequential ~450ms)
```

---

## Module Dependency

### Core Dependencies

```
mdsa/
│
├── core/                   # No external MDSA dependencies
│   ├── orchestrator.py     → router, reasoner, state_machine
│   ├── router.py           → (independent)
│   ├── complexity_analyzer.py → (independent)
│   ├── reasoner.py         → (independent)
│   ├── state_machine.py    → (independent)
│   └── communication_bus.py → (independent)
│
├── domains/                # Depends on: models
│   ├── config.py           → models.config, utils.device_config
│   ├── executor.py         → models.manager, domains.validator
│   ├── validator.py        → domains.model_validator (optional)
│   ├── model_validator.py  → (independent)
│   └── prompts.py          → (independent)
│
├── models/                 # Depends on: utils
│   ├── config.py           → (independent)
│   ├── manager.py          → models.loader
│   ├── loader.py           → models.config
│   └── registry.py         → (independent)
│
├── async_/                 # Depends on: domains
│   ├── executor.py         → domains.executor
│   └── manager.py          → async_.executor
│
├── memory/                 # No MDSA dependencies
│   └── dual_rag.py         → (independent)
│
├── tools/                  # No MDSA dependencies
│   ├── base.py             → (independent)
│   ├── builtin.py          → tools.base
│   ├── registry.py         → tools.base
│   └── smart_executor.py   → tools.registry
│
├── monitoring/             # No MDSA dependencies
│   ├── metrics.py          → (independent)
│   └── logger.py           → (independent)
│
├── ui/                     # Depends on: monitoring
│   ├── enhanced_dashboard.py → (independent)
│   ├── dashboard.py        → (independent)
│   └── auth.py             → (independent)
│
└── utils/                  # No MDSA dependencies
    ├── config_loader.py    → (independent)
    ├── device_config.py    → utils.hardware
    ├── hardware.py         → (independent)
    ├── helpers.py          → (independent)
    └── logger.py           → (independent)
```

### Dependency Graph

```
                        ┌──────────────┐
                        │  Orchestrator│
                        └──────┬───────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
                ▼              ▼              ▼
         ┌──────────┐  ┌──────────┐  ┌──────────────┐
         │  Router  │  │ Reasoner │  │ StateMachine │
         └──────────┘  └──────────┘  └──────────────┘
                               │
                               │
                               ▼
                        ┌──────────────┐
                        │   Domains    │
                        └──────┬───────┘
                               │
                               ▼
                        ┌──────────────┐
                        │    Models    │
                        └──────┬───────┘
                               │
                     ┌─────────┼─────────┐
                     │         │         │
                     ▼         ▼         ▼
              ┌──────────┬──────────┬──────────┐
              │   RAG    │  Tools   │ Metrics  │
              └──────────┴──────────┴──────────┘
```

---

## Deployment Architecture

### Single-Server Deployment

```
┌─────────────────────────────────────────────────────────┐
│                  Production Server                      │
│  ┌───────────────────────────────────────────────────┐  │
│  │              MDSA Application                     │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  │  │
│  │  │ Orchestr-  │  │ Model      │  │ RAG        │  │  │
│  │  │ ator       │  │ Manager    │  │ System     │  │  │
│  │  └────────────┘  └────────────┘  └────────────┘  │  │
│  │                                                   │  │
│  │  Models Cached in Memory (Max 3):                │  │
│  │  - TinyBERT (router)                             │  │
│  │  - Phi-2 (finance domain)                        │  │
│  │  - Phi-2 (medical domain)                        │  │
│  └───────────────────────────────────────────────────┘  │
│                                                          │
│  ┌───────────────────────────────────────────────────┐  │
│  │              Hardware Resources                   │  │
│  │  CPU: 8 cores                                     │  │
│  │  RAM: 16 GB                                       │  │
│  │  GPU: NVIDIA RTX 3050 (4GB) - Optional           │  │
│  │  Disk: 50 GB SSD                                  │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                     Users/Clients                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │ Web UI   │  │ CLI      │  │ API      │             │
│  │ Client   │  │ Client   │  │ Client   │             │
│  └──────────┘  └──────────┘  └──────────┘             │
└─────────────────────────────────────────────────────────┘
```

### Load-Balanced Deployment

```
┌─────────────────────────────────────────────────────────┐
│                   Load Balancer                         │
│                  (nginx / HAProxy)                      │
└─────────┬───────────────────────┬───────────────────────┘
          │                       │
          ▼                       ▼
┌─────────────────┐     ┌─────────────────┐
│   Server 1      │     │   Server 2      │
│   MDSA Instance │     │   MDSA Instance │
│   ┌──────────┐  │     │   ┌──────────┐  │
│   │ Finance  │  │     │   │ Medical  │  │
│   │ Medical  │  │     │   │ Support  │  │
│   │ Support  │  │     │   │ Technical│  │
│   └──────────┘  │     │   └──────────┘  │
└─────────┬───────┘     └─────────┬───────┘
          │                       │
          │                       │
          └───────────┬───────────┘
                      │
                      ▼
          ┌───────────────────────┐
          │  Shared Services      │
          │  ┌─────────────────┐  │
          │  │ Redis (Cache)   │  │
          │  │ Postgres (Data) │  │
          │  │ S3 (Models)     │  │
          │  └─────────────────┘  │
          └───────────────────────┘
```

---

## Scalability & Performance

### Performance Characteristics

| Component | Latency | Throughput | Scalability |
|-----------|---------|------------|-------------|
| TinyBERT Router | < 50ms | 1000 req/s | Linear |
| Phi-2 Reasoner | < 2s | 10 req/s | Linear |
| Domain Execution | 100-300ms | 50 req/s | Linear |
| RAG Retrieval | < 20ms | 500 req/s | Sub-linear |
| Validation Tier 1 | < 10ms | 1000 req/s | Linear |
| Validation Tier 2 | < 100ms | 100 req/s | Linear |

### Scaling Strategies

#### Vertical Scaling

```
CPU Cores:  4 → 8 → 16
RAM:        8GB → 16GB → 32GB
GPU:        None → RTX 3050 (4GB) → RTX 4090 (24GB)

Expected Throughput Increase:
- CPU-only: 2x per doubling
- GPU: 5-10x vs CPU
```

#### Horizontal Scaling

```
Instances:  1 → 2 → 4 → 8

Load Distribution:
- Round-robin
- Domain-specific routing
- Least-connections

Expected Throughput:
- Near-linear scaling up to 4 instances
- Sub-linear beyond 8 instances (overhead)
```

#### Model Caching Strategy

```
LRU Cache (Max 3 models):

Scenario 1: Balanced Load
- Router: TinyBERT (always cached)
- Domain 1: Phi-2 (cached)
- Domain 2: Phi-2 (cached)
→ Cache hit rate: ~95%

Scenario 2: Diverse Load
- Router: TinyBERT (always cached)
- Domain 1: Phi-2 (cached)
- Domain 2: Phi-2 (cached)
- Domain 3: Phi-2 (evicts oldest)
- Domain 4: Phi-2 (evicts oldest)
→ Cache hit rate: ~60-70%

Optimization:
- Increase max_models for diverse workloads
- Use domain-specific servers
```

### Resource Requirements

#### Minimal Setup (CPU-Only)

```
CPU: 4 cores
RAM: 8 GB
Disk: 20 GB
GPU: None

Performance:
- Latency: 200-400ms per request
- Throughput: ~10 requests/second
- Quantization: INT4 (75% memory reduction)
```

#### Recommended Setup (GPU-Accelerated)

```
CPU: 8 cores
RAM: 16 GB
Disk: 50 GB SSD
GPU: NVIDIA RTX 3050 (4GB)

Performance:
- Latency: 100-200ms per request
- Throughput: ~50 requests/second
- Quantization: INT8 (50% memory reduction)
```

#### Production Setup (High-Performance)

```
CPU: 16 cores
RAM: 32 GB
Disk: 100 GB NVMe SSD
GPU: NVIDIA RTX 4090 (24GB)

Performance:
- Latency: 50-100ms per request
- Throughput: ~200 requests/second
- Quantization: None (full precision)
```

---

## Security Architecture

### Authentication & Authorization

```
┌───────────┐
│  Client   │
└─────┬─────┘
      │
      │ 1. Request with API Key
      ▼
┌────────────────┐
│  Auth Middleware│
│  - Verify key   │
│  - Check perms  │
└─────┬──────────┘
      │
      │ 2. Authorized
      ▼
┌────────────────┐
│  Orchestrator  │
│  - Process req │
└────────────────┘
```

### Data Isolation

```
Domain Isolation:
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ Finance     │  │ Medical     │  │ Support     │
│ LocalRAG    │  │ LocalRAG    │  │ LocalRAG    │
│ (Private)   │  │ (Private)   │  │ (Private)   │
└─────────────┘  └─────────────┘  └─────────────┘
       ▲                ▲                ▲
       │                │                │
       └────────────────┼────────────────┘
                        │
                        ▼
                ┌───────────────┐
                │  GlobalRAG    │
                │  (Shared)     │
                └───────────────┘

Access Control:
- Finance can only access Finance LocalRAG
- Medical can only access Medical LocalRAG
- All domains can access GlobalRAG
```

---

## Conclusion

The MDSA framework provides a robust, scalable architecture for multi-domain language model orchestration. Key architectural highlights:

- **Modularity**: Independent, testable components
- **Performance**: Optimized routing and caching
- **Scalability**: Horizontal and vertical scaling support
- **Security**: Domain isolation and access control
- **Observability**: Comprehensive monitoring and logging

---

**Version**: 1.0.0
**Date**: 2025-12-06
**Author**: MDSA Framework Team
