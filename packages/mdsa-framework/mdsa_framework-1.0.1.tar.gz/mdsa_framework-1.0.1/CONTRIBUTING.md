# Contributing to MDSA

Thank you for your interest in contributing to the Multi-Domain Specialized Agentic Orchestration (MDSA) framework! This document provides guidelines for contributing to the project.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [Development Workflow](#development-workflow)
5. [Coding Standards](#coding-standards)
6. [Testing](#testing)
7. [Pull Request Process](#pull-request-process)
8. [Reporting Issues](#reporting-issues)
9. [Feature Requests](#feature-requests)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of experience level, background, or identity.

### Expected Behavior

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

### Unacceptable Behavior

- Harassment, trolling, or discriminatory comments
- Personal attacks or political arguments
- Publishing others' private information
- Other conduct that could reasonably be considered inappropriate

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git for version control
- Basic understanding of:
  - Machine learning concepts
  - NLP and transformers
  - FastAPI and web development
  - Vector databases (ChromaDB)

### Familiarize Yourself

Before contributing, please:

1. Read the [README.md](README.md) to understand the project
2. Review the [CHANGELOG.md](CHANGELOG.md) to see recent changes
3. Check existing [issues](https://github.com/your-username/mdsa-framework/issues) and [pull requests](https://github.com/your-username/mdsa-framework/pulls)
4. Read the [documentation](docs/) to understand architecture and APIs

---

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR-USERNAME/mdsa-framework.git
cd mdsa-framework
```

### 2. Create a Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On Unix/Mac:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Install all dependencies including development tools
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### 4. Set Up Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and configure your settings
# At minimum, set:
# - OPENAI_API_KEY or OLLAMA_BASE_URL
# - Model configurations
```

### 5. Verify Installation

```bash
# Run the test suite
python test_all_fixes.py

# Start the dashboard
python mdsa/ui/dashboard/app.py

# In another terminal, start the chatbot
python chatbot_app/medical_app/enhanced_medical_chatbot_fixed.py
```

---

## Development Workflow

### 1. Create a Branch

```bash
# Always create a new branch for your work
git checkout -b feature/your-feature-name

# Branch naming conventions:
# - feature/feature-name for new features
# - fix/bug-name for bug fixes
# - docs/documentation-topic for documentation
# - perf/optimization-name for performance improvements
# - refactor/component-name for refactoring
```

### 2. Make Changes

- Write clean, readable code
- Follow the coding standards (see below)
- Add tests for new features
- Update documentation as needed
- Commit regularly with clear messages

### 3. Test Your Changes

```bash
# Run all tests
python test_all_fixes.py

# Test specific components
python -m pytest tests/test_router.py

# Check code style
flake8 mdsa/

# Type checking (if using mypy)
mypy mdsa/
```

### 4. Commit Your Changes

```bash
# Stage your changes
git add .

# Commit with a descriptive message
git commit -m "Add feature: domain embedding cache with 100ms speedup"

# Push to your fork
git push origin feature/your-feature-name
```

---

## Coding Standards

### Python Style Guide

Follow [PEP 8](https://pep8.org/) with these specifics:

#### Code Formatting

```python
# Line length: 100 characters (soft limit), 120 (hard limit)
# Indentation: 4 spaces (no tabs)
# Imports: organized in 3 groups (standard, third-party, local)

# Standard library imports
import os
import sys
from typing import Dict, List, Optional

# Third-party imports
import torch
import numpy as np
from fastapi import FastAPI

# Local imports
from mdsa.core import TinyBERTOrchestrator
from mdsa.memory import DualRAG
```

#### Naming Conventions

```python
# Classes: PascalCase
class DomainRouter:
    pass

# Functions and variables: snake_case
def process_query(query_text: str) -> Dict:
    domain_scores = {}
    return domain_scores

# Constants: UPPER_SNAKE_CASE
MAX_CACHE_SIZE = 100
DEFAULT_TIMEOUT = 30

# Private methods/variables: prefix with underscore
def _internal_helper(self):
    self._cache = {}
```

#### Type Hints

Always use type hints for function signatures:

```python
from typing import Dict, List, Optional, Tuple

def classify_domain(
    self,
    query: str,
    threshold: float = 0.7
) -> Tuple[str, float]:
    """
    Classify query into a domain.

    Args:
        query: User query text
        threshold: Minimum confidence threshold

    Returns:
        Tuple of (domain_name, confidence_score)
    """
    # Implementation
    return domain_name, confidence
```

#### Docstrings

Use Google-style docstrings:

```python
def add_documents(
    self,
    domain_id: str,
    documents: List[str],
    metadata: Optional[List[Dict]] = None
) -> None:
    """
    Add documents to domain-specific knowledge base.

    This method adds documents to ChromaDB collection for the specified
    domain. Documents are embedded using SentenceTransformer and stored
    with optional metadata for filtering.

    Args:
        domain_id: Unique identifier for the domain
        documents: List of document texts to add
        metadata: Optional list of metadata dicts (one per document)

    Returns:
        None

    Raises:
        ValueError: If domain_id is not registered
        RuntimeError: If ChromaDB connection fails

    Example:
        >>> rag = DualRAG()
        >>> rag.register_domain("medical")
        >>> rag.add_documents(
        ...     domain_id="medical",
        ...     documents=["Patient has fever", "Chest pain diagnosis"],
        ...     metadata=[{"source": "kb"}, {"source": "kb"}]
        ... )
    """
    # Implementation
```

### Code Organization

#### File Structure

```
mdsa/
├── core/           # Core orchestration logic
│   ├── __init__.py
│   ├── router.py   # Domain routing
│   └── executor.py # Query execution
├── memory/         # RAG and knowledge management
│   ├── __init__.py
│   └── dual_rag.py
├── models/         # Model wrappers
├── monitoring/     # Monitoring and analytics
├── tools/          # Utility functions
└── ui/             # User interface
    └── dashboard/
```

#### Import Organization

```python
# mdsa/core/router.py

"""
Domain routing with TinyBERT.

This module implements intelligent query routing using TinyBERT for
domain classification with embedding caching for performance.
"""

# Standard library
import logging
import time
from typing import Dict, List, Optional, Tuple

# Third-party
import torch
import torch.nn.functional as F
from transformers import AutoModel, AutoTokenizer

# Local
from mdsa.tools.logging import setup_logger

logger = setup_logger(__name__)
```

---

## Testing

### Test Organization

```
tests/
├── integration/        # End-to-end tests
│   ├── test_phase1.py
│   └── test_phase2.py
├── unit/               # Unit tests
│   ├── test_router.py
│   ├── test_rag.py
│   └── test_cache.py
└── fixtures/           # Test data and fixtures
```

### Writing Tests

```python
import pytest
from mdsa.core import TinyBERTOrchestrator

def test_domain_classification():
    """Test domain classification accuracy."""
    orchestrator = TinyBERTOrchestrator()

    # Register test domain
    orchestrator.register_domain(
        name="test_domain",
        description="Test domain for unit testing",
        keywords=["test", "example"]
    )

    # Test classification
    query = "This is a test query"
    domain, confidence = orchestrator.route_query(query)

    assert domain == "test_domain"
    assert 0.0 <= confidence <= 1.0

def test_embedding_cache_performance():
    """Test that embedding cache improves performance."""
    orchestrator = TinyBERTOrchestrator()

    # Register domain
    orchestrator.register_domain("test", "Test domain", ["test"])

    # First classification (cache miss)
    start = time.time()
    orchestrator.route_query("Test query")
    first_time = time.time() - start

    # Second classification (cache hit)
    start = time.time()
    orchestrator.route_query("Test query")
    second_time = time.time() - start

    # Cache should be faster
    assert second_time < first_time
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/unit/test_router.py

# Run with coverage
pytest --cov=mdsa tests/

# Run with verbose output
pytest -v tests/
```

---

## Pull Request Process

### 1. Before Submitting

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] CHANGELOG.md updated (if applicable)
- [ ] Commits are clean and well-organized

### 2. Pull Request Template

```markdown
## Description

Brief description of changes and why they're needed.

## Type of Change

- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Performance improvement

## Testing

Describe the tests you ran and how to reproduce them.

## Performance Impact

If applicable, describe performance improvements or regressions.

## Related Issues

Closes #123
Related to #456

## Checklist

- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added to complex code
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests added and passing
- [ ] CHANGELOG.md updated
```

### 3. Review Process

1. Submit pull request
2. Wait for automated tests to pass
3. Address reviewer feedback
4. Maintainer approval required
5. Merge (squash and merge for feature branches)

---

## Reporting Issues

### Before Reporting

1. Search existing issues
2. Try to reproduce with latest version
3. Collect relevant information

### Issue Template

```markdown
## Bug Description

Clear description of the bug.

## Steps to Reproduce

1. Step 1
2. Step 2
3. Step 3

## Expected Behavior

What should happen?

## Actual Behavior

What actually happened?

## Environment

- OS: [e.g., Windows 10, Ubuntu 20.04]
- Python version: [e.g., 3.9.7]
- MDSA version: [e.g., 1.0.0]
- Relevant dependencies: [e.g., PyTorch 2.0.0]

## Additional Context

Error logs, screenshots, or other relevant information.
```

---

## Feature Requests

### Template

```markdown
## Feature Description

Clear description of the proposed feature.

## Use Case

Why is this feature needed? What problem does it solve?

## Proposed Implementation

How might this be implemented?

## Alternatives Considered

What other approaches did you consider?

## Additional Context

Any other relevant information.
```

---

## Community

### Getting Help

- **Documentation:** Check [docs/](docs/) folder
- **Issues:** Search [GitHub Issues](https://github.com/your-username/mdsa-framework/issues)
- **Discussions:** Use [GitHub Discussions](https://github.com/your-username/mdsa-framework/discussions)

### Recognition

Contributors will be:
- Listed in README.md acknowledgments
- Included in release notes
- Credited in commit history

---

## License

By contributing to MDSA, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to MDSA!**

We appreciate your time and effort in making this framework better for everyone.
