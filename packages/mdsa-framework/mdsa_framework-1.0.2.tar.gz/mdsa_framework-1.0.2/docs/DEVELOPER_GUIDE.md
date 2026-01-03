# MDSA Framework - Developer Guide

**Version**: 1.0.0
**Date**: 2025-12-06
**Author**: MDSA Framework Team

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Development Setup](#development-setup)
3. [Core Concepts](#core-concepts)
4. [Creating Custom Components](#creating-custom-components)
5. [Testing](#testing)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)
8. [Contributing](#contributing)

---

## Getting Started

### Prerequisites

- Python 3.9+ (3.13 recommended)
- pip or conda package manager
- Git
- (Optional) NVIDIA GPU with CUDA support

### Installation

```bash
# Clone repository
git clone https://github.com/mdsa-framework/mdsa.git
cd mdsa

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Quick Start

```python
from mdsa.core.orchestrator import Orchestrator

# Create orchestrator
orchestrator = Orchestrator()

# Process a query
result = orchestrator.process_request("How do I transfer money?")

print(f"Domain: {result['domain']}")
print(f"Response: {result['response']}")
print(f"Latency: {result['latency_ms']}ms")
```

---

## Development Setup

### Project Structure

```
mdsa/
├── mdsa/                    # Main package
│   ├── core/               # Core orchestration components
│   ├── domains/            # Domain-specific logic
│   ├── models/             # Model management
│   ├── async_/             # Async execution
│   ├── memory/             # RAG systems
│   ├── tools/              # Tool system
│   ├── monitoring/         # Logging and metrics
│   ├── ui/                 # Dashboards and UI
│   └── utils/              # Utilities
│
├── tests/                  # Test suite
│   ├── test_core.py       # Core component tests
│   ├── test_domains.py    # Domain tests
│   ├── test_models.py     # Model tests
│   └── conftest.py        # Pytest configuration
│
├── examples/               # Example applications
│   ├── basic_usage.py
│   ├── custom_domain.py
│   └── rag_integration.py
│
├── docs/                   # Documentation
│   ├── FRAMEWORK_REFERENCE.md
│   ├── ARCHITECTURE.md
│   └── DEVELOPER_GUIDE.md
│
├── requirements.txt        # Dependencies
├── setup.py               # Package configuration
├── pytest.ini             # Pytest configuration
└── README.md              # Project README
```

### Setting Up Development Environment

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ --cov=mdsa --cov-report=html

# Format code
black mdsa/ tests/

# Lint code
pylint mdsa/

# Type checking
mypy mdsa/
```

### Environment Variables

```bash
# .env file
MDSA_LOG_LEVEL=INFO
MDSA_CACHE_DIR=./cache
MDSA_MODEL_DIR=./models
MDSA_DEVICE=cuda:0  # or cpu
MDSA_MAX_MODELS=3
MDSA_ENABLE_METRICS=true
MDSA_DASHBOARD_PORT=8080
```

---

## Core Concepts

### 1. Orchestration Flow

Every request follows this lifecycle:

```
1. Query Submission
   ↓
2. Complexity Analysis
   ├─ Simple → TinyBERT Router
   └─ Complex → Phi-2 Reasoner
   ↓
3. Domain Selection
   ↓
4. Model Execution
   ├─ Load model (with caching)
   ├─ RAG retrieval (optional)
   ├─ Generate response
   └─ Validate output
   ↓
5. Response Delivery
```

### 2. Domain System

Domains encapsulate:
- **Keywords**: For routing
- **Model**: Specific to domain needs
- **Prompts**: Domain-specific instructions
- **Validation**: Custom validation rules

### 3. Model Management

Models are:
- **Cached**: LRU cache (max 3 by default)
- **Quantized**: INT8/INT4 for memory efficiency
- **Device-aware**: Auto-select CPU/GPU

### 4. RAG System

Two-tier knowledge:
- **LocalRAG**: Domain-specific (private)
- **GlobalRAG**: Shared across domains

---

## Creating Custom Components

### Custom Domain

```python
from mdsa.domains.config import DomainConfig
from mdsa.models.config import ModelTier, QuantizationType

# Step 1: Create domain configuration
legal_domain = DomainConfig(
    domain_id="legal",
    name="Legal Domain",
    description="Legal advice and information",
    keywords=["law", "legal", "court", "lawyer", "contract"],
    model_name="microsoft/phi-2",
    model_tier=ModelTier.TIER2,
    quantization=QuantizationType.INT8,
    device="cuda:0",
    system_prompt="""You are a legal assistant. Provide accurate legal information
    while reminding users to consult professional lawyers for specific advice.""",
    max_tokens=512,
    temperature=0.3,
)

# Step 2: Register with orchestrator
from mdsa.core.orchestrator import Orchestrator

orchestrator = Orchestrator()
orchestrator.register_domain(legal_domain)

# Step 3: Use domain
result = orchestrator.process_request(
    "What is a contract?",
    context={'preferred_domain': 'legal'}
)
```

### Custom Tool

```python
from mdsa.tools.base import Tool, ToolParameter, ToolResult
from typing import Any, Dict

class WeatherTool(Tool):
    """Tool for getting weather information."""

    def __init__(self):
        super().__init__(
            name="weather",
            description="Get current weather for a location",
            parameters=[
                ToolParameter(
                    name="location",
                    type="string",
                    description="City name or coordinates",
                    required=True
                ),
                ToolParameter(
                    name="units",
                    type="string",
                    description="Temperature units (celsius/fahrenheit)",
                    required=False,
                    default="celsius"
                )
            ]
        )

    async def execute(self, **kwargs) -> ToolResult:
        """Execute weather lookup."""
        location = kwargs.get('location')
        units = kwargs.get('units', 'celsius')

        try:
            # Call weather API (example)
            weather_data = await self._fetch_weather(location, units)

            return ToolResult(
                success=True,
                data={
                    'location': location,
                    'temperature': weather_data['temp'],
                    'conditions': weather_data['conditions'],
                    'units': units
                },
                metadata={
                    'api_call_time_ms': 150
                }
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e)
            )

    async def _fetch_weather(self, location: str, units: str) -> Dict[str, Any]:
        """Fetch weather data from API."""
        # Implementation details
        pass

# Register tool
from mdsa.tools.registry import ToolRegistry

registry = ToolRegistry()
registry.register(WeatherTool())

# Use tool
result = await registry.execute_tool(
    "weather",
    location="New York",
    units="fahrenheit"
)
```

### Custom Validator

```python
from mdsa.domains.validator import ResponseValidator
from typing import Tuple, Optional

class CustomValidator(ResponseValidator):
    """Custom validator with additional checks."""

    def validate(
        self,
        response: str,
        domain_config,
        query: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> Tuple[bool, Optional[str]]:
        """Validate response with custom rules."""

        # Call parent validation (Tier 1 + Tier 2)
        is_valid, error = super().validate(
            response, domain_config, query, context
        )

        if not is_valid:
            return is_valid, error

        # Custom validation: Check for specific keywords
        required_keywords = context.get('required_keywords', [])
        if required_keywords:
            for keyword in required_keywords:
                if keyword.lower() not in response.lower():
                    return False, f"Response missing required keyword: {keyword}"

        # Custom validation: Check response format
        if context.get('require_json'):
            try:
                import json
                json.loads(response)
            except json.JSONDecodeError:
                return False, "Response must be valid JSON"

        return True, None

# Use custom validator
from mdsa.domains.executor import DomainExecutor

executor = DomainExecutor(
    model_manager,
    validator=CustomValidator(use_model_validation=True)
)
```

### Custom Complexity Analyzer

```python
from mdsa.core.complexity_analyzer import ComplexityAnalyzer, ComplexityResult
from typing import Dict, Set

class CustomComplexityAnalyzer(ComplexityAnalyzer):
    """Custom complexity analyzer with domain-specific rules."""

    def __init__(self, complexity_threshold: float = 0.3):
        super().__init__(complexity_threshold)

        # Add custom keywords
        self.CUSTOM_KEYWORDS = ['integrate', 'workflow', 'pipeline']

    def analyze(self, query: str) -> ComplexityResult:
        """Analyze query complexity with custom rules."""

        # Get base complexity
        result = super().analyze(query)

        # Add custom complexity scoring
        custom_score = 0.0
        indicators = list(result.indicators)

        # Check for custom keywords
        query_lower = query.lower()
        for keyword in self.CUSTOM_KEYWORDS:
            if keyword in query_lower:
                custom_score += 0.15
                indicators.append(f'custom_{keyword}')

        # Adjust total score
        total_score = min(1.0, result.complexity_score + custom_score)

        return ComplexityResult(
            is_complex=total_score >= self.complexity_threshold,
            complexity_score=total_score,
            indicators=indicators,
            requires_reasoning=total_score >= 0.4,
            requires_multi_domain=result.requires_multi_domain,
            requires_sequential=result.requires_sequential
        )

# Use custom analyzer
from mdsa.core.orchestrator import Orchestrator

orchestrator = Orchestrator(
    complexity_analyzer=CustomComplexityAnalyzer(complexity_threshold=0.3)
)
```

---

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_domains.py -v

# Run specific test
pytest tests/test_domains.py::TestDomainConfig::test_domain_config_creation -v

# Run with coverage
pytest tests/ --cov=mdsa --cov-report=html

# Run markers
pytest -m unit  # Run only unit tests
pytest -m integration  # Run integration tests
pytest -m e2e  # Run end-to-end tests
```

### Writing Tests

```python
import pytest
from mdsa.domains.config import DomainConfig
from mdsa.models.config import ModelTier, QuantizationType

class TestCustomDomain:
    """Test custom domain functionality."""

    @pytest.fixture
    def custom_domain(self):
        """Create custom domain fixture."""
        return DomainConfig(
            domain_id="custom",
            name="Custom Domain",
            description="Custom test domain",
            keywords=["custom", "test"],
            model_name="gpt2",
            model_tier=ModelTier.TIER1,
            quantization=QuantizationType.NONE,
            device="cpu"
        )

    def test_domain_creation(self, custom_domain):
        """Test creating custom domain."""
        assert custom_domain.domain_id == "custom"
        assert custom_domain.name == "Custom Domain"
        assert "custom" in custom_domain.keywords

    def test_domain_to_dict(self, custom_domain):
        """Test converting domain to dictionary."""
        domain_dict = custom_domain.to_dict()

        assert domain_dict['domain_id'] == "custom"
        assert domain_dict['model_name'] == "gpt2"
        assert domain_dict['quantization'] == "none"

    @pytest.mark.asyncio
    async def test_domain_execution(self, custom_domain):
        """Test executing in custom domain."""
        from mdsa.domains.executor import DomainExecutor
        from mdsa.models.manager import ModelManager

        manager = ModelManager(max_models=2)
        executor = DomainExecutor(manager)

        result = await executor.execute(
            "Test query",
            custom_domain
        )

        assert result['status'] == 'success'
        assert result['domain'] == 'custom'
        assert 'response' in result
```

### Integration Testing

```python
import pytest
from mdsa.core.orchestrator import Orchestrator

class TestIntegration:
    """Integration tests for full workflow."""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator fixture."""
        return Orchestrator(enable_reasoning=True)

    def test_simple_query_flow(self, orchestrator):
        """Test simple query processing."""
        result = orchestrator.process_request(
            "How do I transfer money?"
        )

        assert result['status'] == 'success'
        assert result['domain'] in ['finance', 'support']
        assert result['complexity_score'] < 0.3
        assert not result['reasoning_used']
        assert result['latency_ms'] > 0

    def test_complex_query_flow(self, orchestrator):
        """Test complex query processing."""
        result = orchestrator.process_request(
            "Transfer $100, then check balance, and if low notify me"
        )

        assert result['status'] == 'success'
        assert result['complexity_score'] >= 0.3
        assert result['reasoning_used']
        assert 'tasks' in result
        assert len(result['tasks']) >= 2

    def test_rag_integration(self, orchestrator):
        """Test RAG integration."""
        from mdsa.memory.dual_rag import DualRAG

        # Setup RAG
        dual_rag = DualRAG()
        dual_rag.register_domain("finance")
        dual_rag.add_to_local(
            "finance",
            "Account 123 balance: $1500"
        )

        # Inject RAG into orchestrator
        orchestrator.rag = dual_rag

        # Query
        result = orchestrator.process_request(
            "What is the balance of account 123?"
        )

        assert result['status'] == 'success'
        assert '1500' in result['response']
```

---

## Best Practices

### Code Organization

```python
# Good: Clear, modular organization
from mdsa.core.orchestrator import Orchestrator
from mdsa.domains.config import DomainConfig
from mdsa.models.config import ModelTier

orchestrator = Orchestrator()
domain = DomainConfig(...)
result = orchestrator.process_request(query)

# Bad: Importing everything
from mdsa.core.orchestrator import *
from mdsa.domains.config import *
```

### Error Handling

```python
# Good: Comprehensive error handling
from mdsa.core.orchestrator import Orchestrator

orchestrator = Orchestrator()

try:
    result = orchestrator.process_request(query)

    if result['status'] == 'success':
        print(f"Response: {result['response']}")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")

except Exception as e:
    logger.error(f"Orchestration failed: {e}")
    # Fallback logic
    result = {'status': 'error', 'error': str(e)}

# Bad: No error handling
result = orchestrator.process_request(query)
print(result['response'])  # Might fail if status != 'success'
```

### Configuration Management

```python
# Good: Use configuration files
from mdsa.utils.config_loader import ConfigLoader

loader = ConfigLoader()
config = loader.load("config.yaml")

orchestrator = Orchestrator(
    enable_reasoning=config['orchestrator']['enable_reasoning'],
    complexity_threshold=config['orchestrator']['complexity_threshold']
)

# Bad: Hardcoded values
orchestrator = Orchestrator(
    enable_reasoning=True,
    complexity_threshold=0.3
)
```

### Logging

```python
# Good: Structured logging
import logging

logger = logging.getLogger(__name__)

def process_request(query):
    logger.info("Processing request", extra={
        'query': query[:50],  # Don't log full query (privacy)
        'timestamp': time.time()
    })

    try:
        result = orchestrator.process_request(query)
        logger.info("Request completed", extra={
            'domain': result['domain'],
            'latency_ms': result['latency_ms'],
            'status': result['status']
        })
        return result
    except Exception as e:
        logger.error("Request failed", extra={
            'error': str(e),
            'query': query[:50]
        })
        raise

# Bad: Print statements
def process_request(query):
    print(f"Processing: {query}")
    result = orchestrator.process_request(query)
    print(f"Done: {result}")
    return result
```

### Resource Management

```python
# Good: Proper cleanup
from mdsa.core.orchestrator import Orchestrator
from mdsa.models.manager import ModelManager

orchestrator = Orchestrator()

try:
    # Process requests
    for query in queries:
        result = orchestrator.process_request(query)
        # Handle result

finally:
    # Cleanup
    orchestrator.shutdown()

# Even better: Context manager
class ManagedOrchestrator:
    def __enter__(self):
        self.orchestrator = Orchestrator()
        return self.orchestrator

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.orchestrator.shutdown()

with ManagedOrchestrator() as orchestrator:
    result = orchestrator.process_request(query)
```

### Performance Optimization

```python
# Good: Batch processing
from mdsa.async_.manager import AsyncManager

async def process_batch(queries):
    manager = AsyncManager(domain_executor, max_concurrent=10)

    try:
        results = await manager.process_batch(
            queries,
            domain_config,
            timeout=30.0
        )
        return results
    finally:
        await manager.shutdown()

# Bad: Sequential processing
def process_batch(queries):
    results = []
    for query in queries:
        result = orchestrator.process_request(query)
        results.append(result)
    return results  # Much slower!
```

---

## Troubleshooting

### Common Issues

#### 1. Model Loading Fails

**Symptom**: `OSError: Unable to load model`

**Solutions**:
```python
# Check model name
model_name = "microsoft/phi-2"  # Correct
# Not: "phi-2" or "phi2"

# Check device
device = "cuda:0" if torch.cuda.is_available() else "cpu"

# Check disk space
# Models require ~5GB per model

# Check HuggingFace token (for gated models)
from huggingface_hub import login
login(token="your_token_here")
```

#### 2. Out of Memory

**Symptom**: `RuntimeError: CUDA out of memory`

**Solutions**:
```python
# Reduce max_models
manager = ModelManager(max_models=1)  # Instead of 3

# Use quantization
config = ModelConfig(
    quantization=QuantizationType.INT4  # 75% memory reduction
)

# Force CPU
config = ModelConfig(device="cpu")

# Clear cache
import torch
torch.cuda.empty_cache()
```

#### 3. Slow Performance

**Symptom**: Latency > 1 second per request

**Solutions**:
```python
# Enable GPU
config = ModelConfig(device="cuda:0")

# Use quantization
config = ModelConfig(quantization=QuantizationType.INT8)

# Increase model cache
manager = ModelManager(max_models=5)

# Use async for batches
async_manager = AsyncManager(max_concurrent=10)

# Profile code
import cProfile
cProfile.run('orchestrator.process_request(query)')
```

#### 4. Incorrect Routing

**Symptom**: Queries routed to wrong domain

**Solutions**:
```python
# Check domain keywords
finance_domain = get_predefined_domain('finance')
print(finance_domain.keywords)  # Verify keywords

# Adjust keywords
custom_domain = DomainConfig(
    domain_id="finance",
    keywords=["money", "transfer", "payment", "balance", "account"]
)

# Check router confidence
result = orchestrator.process_request(query)
print(f"Confidence: {result['confidence']}")

# Force domain
result = orchestrator.process_request(
    query,
    context={'preferred_domain': 'finance'}
)
```

### Debugging Tips

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check orchestrator stats
stats = orchestrator.get_stats()
print(f"Total requests: {stats['total_requests']}")
print(f"Routing distribution: {stats['routing_distribution']}")

# Check model manager stats
manager_stats = model_manager.get_stats()
print(f"Loaded models: {manager_stats['loaded_models']}")
print(f"Cache hits: {manager_stats['cache_hits']}")

# Monitor with dashboard
from mdsa.ui.enhanced_dashboard import EnhancedDashboard

dashboard = EnhancedDashboard()
# Track requests...
html_file = dashboard.generate_html_dashboard()
# Open in browser for visualization
```

---

## Contributing

### Development Workflow

1. **Fork repository**
```bash
git clone https://github.com/your-username/mdsa.git
cd mdsa
git remote add upstream https://github.com/mdsa-framework/mdsa.git
```

2. **Create feature branch**
```bash
git checkout -b feature/my-new-feature
```

3. **Make changes**
```python
# Add your code
# Write tests
# Update documentation
```

4. **Run tests**
```bash
pytest tests/ -v
pytest tests/ --cov=mdsa
```

5. **Format code**
```bash
black mdsa/ tests/
pylint mdsa/
mypy mdsa/
```

6. **Commit changes**
```bash
git add .
git commit -m "Add feature: description"
```

7. **Push to fork**
```bash
git push origin feature/my-new-feature
```

8. **Create Pull Request**
- Go to GitHub
- Click "New Pull Request"
- Describe changes
- Link related issues

### Code Style

```python
# Follow PEP 8
# Use type hints
def process_query(query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Process a query.

    Args:
        query: The user query
        context: Optional context dictionary

    Returns:
        Result dictionary with status, response, etc.
    """
    pass

# Use docstrings
class CustomTool(Tool):
    """
    Custom tool for specific functionality.

    This tool provides...

    Attributes:
        name: Tool identifier
        description: What the tool does

    Example:
        >>> tool = CustomTool()
        >>> result = tool.execute(param="value")
    """
    pass

# Use descriptive names
# Good
user_query = "Transfer money"
domain_config = DomainConfig(...)

# Bad
q = "Transfer money"
cfg = DomainConfig(...)
```

### Pull Request Guidelines

- **Title**: Clear, concise description
- **Description**: What, why, how
- **Tests**: Add tests for new features
- **Documentation**: Update docs
- **No breaking changes** without discussion
- **Follow code style** (Black, PEP 8)

### Issue Reporting

```markdown
**Bug Report**

**Description**
Clear description of the bug

**To Reproduce**
1. Step 1
2. Step 2
3. Error occurs

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- OS: Windows 11
- Python: 3.13.3
- MDSA Version: 1.0.0
- GPU: NVIDIA RTX 3050

**Additional Context**
Any other relevant information
```

---

## Resources

### Documentation

- [Framework Reference](FRAMEWORK_REFERENCE.md) - Complete API reference
- [Architecture Guide](ARCHITECTURE.md) - System architecture
- [README](../README.md) - Quick start guide

### Community

- GitHub: https://github.com/mdsa-framework/mdsa
- Issues: https://github.com/mdsa-framework/mdsa/issues
- Discussions: https://github.com/mdsa-framework/mdsa/discussions

### Support

- Email: support@mdsa-framework.org
- Discord: https://discord.gg/mdsa-framework
- Documentation: https://mdsa-docs.readthedocs.io

---

## License

MDSA Framework is released under MIT License.

---

**Version**: 1.0.0
**Last Updated**: 2025-12-06
**Author**: MDSA Framework Team
