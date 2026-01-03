# MDSA Framework Documentation Hub

**Version**: 1.0.0
**Last Updated**: December 2025

Welcome to the MDSA (Multi-Domain Specialized Agentic Orchestration) Framework documentation. This guide will help you navigate our comprehensive documentation to find exactly what you need.

---

## 🚀 Quick Start Guides

**New to MDSA?** Start here:

1. **[Setup Guide](SETUP_GUIDE.md)** - Install and run MDSA in 5 minutes
2. **[User Guide](USER_GUIDE.md)** - Complete walkthrough of creating domains, agents, and integrations
3. **[Architecture Overview](ARCHITECTURE.md)** - Understand how MDSA works under the hood

**Want to try a working example?**
- **[Medical Chatbot Example](../examples/medical_chatbot/README.md)** - Production-ready medical information chatbot
- **[Medical Chatbot Quick Start](../examples/medical_chatbot/QUICKSTART.md)** - Get it running in 5 minutes

---

## 📚 Documentation by User Type

### 👤 For End Users

**Getting Started**
- [Setup Guide](SETUP_GUIDE.md) - Installation, prerequisites, and first run
- [User Guide](USER_GUIDE.md) - Creating domains, adding models, configuring RAG
- Coming Soon: [FAQ](FAQ.md) - Frequently asked questions
- Coming Soon: [Glossary](GLOSSARY.md) - Technical terms and definitions

**Using MDSA**
- [User Guide: Creating Domains](USER_GUIDE.md#3-creating-domains)
- [User Guide: Adding Models](USER_GUIDE.md#4-adding-models-to-domains)
- [User Guide: RAG Configuration](USER_GUIDE.md#12-rag-configuration)
- [User Guide: Tools Integration](USER_GUIDE.md#8-tools-integration)
- [User Guide: MCP Integration](USER_GUIDE.md#9-mcp-integration)

**Deployment**
- [Setup Guide: Production Deployment](SETUP_GUIDE.md#production-deployment)
- [Medical Chatbot Deployment Guide](../examples/medical_chatbot/DEPLOYMENT.md)

### 🔧 For Developers

**Core Documentation**
- [Developer Guide](DEVELOPER_GUIDE.md) - Development setup, testing, contributing
- [Architecture Documentation](ARCHITECTURE.md) - Technical architecture and design
- [Framework Reference](FRAMEWORK_REFERENCE.md) - Complete API reference

**Development Guides**
- [Developer Guide: Development Setup](DEVELOPER_GUIDE.md#2-development-setup)
- [Developer Guide: Core Concepts](DEVELOPER_GUIDE.md#3-core-concepts)
- [Developer Guide: Creating Custom Components](DEVELOPER_GUIDE.md#4-creating-custom-components)
- [Developer Guide: Testing](DEVELOPER_GUIDE.md#5-testing)
- [Developer Guide: Best Practices](DEVELOPER_GUIDE.md#6-best-practices)

**Integration & APIs**
- [User Guide: API Integration](USER_GUIDE.md#10-api-integration)
- Coming Soon: [REST API Integration Guide](guides/rest-api-integration.md)
- [User Guide: MCP Server Integration](USER_GUIDE.md#9-mcp-integration)

### 🔬 For Researchers

**Research & Analysis**
- [Research Paper Content](RESEARCH_PAPER_CONTENT.md) - Academic research content and findings
- [Performance Optimizations](PERFORMANCE_OPTIMIZATIONS.md) - Performance analysis and benchmarks
- Coming Soon: [Framework Comparison](COMPARISON.md) - MDSA vs LangChain/AutoGen/CrewAI
- Coming Soon: [Framework Rating](FRAMEWORK_RATING.md) - Detailed 10-dimension evaluation

**Technical Deep Dives**
- [Architecture: Router Design](ARCHITECTURE.md#router-architecture)
- [Architecture: RAG System](ARCHITECTURE.md#rag-dual-knowledge-base-system)
- [Architecture: Caching Strategy](ARCHITECTURE.md#caching-strategy)
- [Performance: Benchmarks](PERFORMANCE_OPTIMIZATIONS.md#performance-benchmarks)

---

## 📖 Core Documentation Files

### Essential Reading

#### [Setup Guide](SETUP_GUIDE.md)
Complete installation and configuration guide covering:
- Prerequisites and dependencies
- Installation steps
- Starting the dashboard and chatbot
- Configuration options
- Troubleshooting common issues
- Production deployment

**Best for**: First-time users, system administrators, DevOps engineers

---

#### [User Guide](USER_GUIDE.md)
Comprehensive guide to using MDSA Framework:
- Creating and managing domains
- Adding models to domains
- Creating and configuring agents
- System prompts and agent connections
- Tools and MCP integration
- API integration patterns
- Guardrails configuration
- RAG setup and optimization
- Complete working examples

**Best for**: Developers building applications with MDSA

---

#### [Developer Guide](DEVELOPER_GUIDE.md)
Development guide for contributors and advanced users:
- Development environment setup
- Core architectural concepts
- Creating custom components
- Testing strategies
- Best practices and patterns
- Troubleshooting development issues
- Contributing guidelines

**Best for**: Contributors, framework developers, advanced customization

---

#### [Architecture Documentation](ARCHITECTURE.md)
Technical architecture and design documentation:
- System architecture overview
- Router design and implementation
- Dual RAG system architecture
- Caching and performance optimization
- Monitoring and observability
- Security considerations

**Best for**: Architects, researchers, technical decision-makers

---

#### [Framework Reference](FRAMEWORK_REFERENCE.md)
Complete API reference documentation:
- Core classes and methods
- Configuration options
- Python API reference
- REST API endpoints
- Data structures and schemas

**Best for**: Developers needing API details

---

### Performance & Research

#### [Performance Optimizations](PERFORMANCE_OPTIMIZATIONS.md)
Detailed performance analysis:
- Benchmarking methodology
- Performance metrics and results
- Optimization techniques
- Comparison with alternatives
- Memory and resource usage
- Scaling strategies

**Best for**: Performance engineers, researchers, optimization work

---

#### [Research Paper Content](RESEARCH_PAPER_CONTENT.md)
Academic research and findings:
- Research motivation and contributions
- Experimental methodology
- Results and analysis
- Literature review
- Future research directions

**Best for**: Academic researchers, paper authors, citations

---

## 🎯 Common Use Cases

### "I want to build a chatbot for my domain"
1. Read [Setup Guide](SETUP_GUIDE.md) to install MDSA
2. Follow [User Guide: Creating Domains](USER_GUIDE.md#3-creating-domains)
3. Check [Medical Chatbot Example](../examples/medical_chatbot/README.md) for reference
4. Configure [RAG with your documents](USER_GUIDE.md#12-rag-configuration)

### "I want to integrate MDSA into my existing application"
1. Review [Architecture Documentation](ARCHITECTURE.md) to understand the system
2. Follow [User Guide: API Integration](USER_GUIDE.md#10-api-integration)
3. Check [Developer Guide: Best Practices](DEVELOPER_GUIDE.md#6-best-practices)
4. Coming Soon: Read [REST API Integration Guide](guides/rest-api-integration.md)

### "I want to deploy MDSA to production"
1. Follow [Setup Guide: Production Deployment](SETUP_GUIDE.md#production-deployment)
2. Review [Medical Chatbot Deployment Guide](../examples/medical_chatbot/DEPLOYMENT.md)
3. Configure [Monitoring Dashboard](USER_GUIDE.md#monitoring-dashboard)
4. Set up [Guardrails](USER_GUIDE.md#11-guardrails)

### "I want to contribute to MDSA"
1. Read [Developer Guide](DEVELOPER_GUIDE.md)
2. Check [Contributing Guidelines](DEVELOPER_GUIDE.md#8-contributing)
3. Review [Best Practices](DEVELOPER_GUIDE.md#6-best-practices)
4. Join the development community

### "I want to compare MDSA with other frameworks"
1. Read [Performance Optimizations](PERFORMANCE_OPTIMIZATIONS.md)
2. Coming Soon: Review [Framework Comparison](COMPARISON.md)
3. Coming Soon: Check [Framework Rating](FRAMEWORK_RATING.md)
4. Review [Research Paper Content](RESEARCH_PAPER_CONTENT.md)

### "I need help with a specific issue"
1. Check Coming Soon: [FAQ](FAQ.md) for common questions
2. Review [Setup Guide: Troubleshooting](SETUP_GUIDE.md#troubleshooting)
3. Check [Developer Guide: Troubleshooting](DEVELOPER_GUIDE.md#7-troubleshooting)
4. Search [GitHub Issues](https://github.com/your-org/mdsa-framework/issues)

---

## 📦 Examples and Templates

### Working Examples

#### [Medical Chatbot](../examples/medical_chatbot/)
Production-ready medical information chatbot demonstrating:
- Multi-domain configuration (5 medical specialties)
- Dual RAG system with medical knowledge base
- Response caching for common queries
- Dashboard integration for monitoring
- Gradio UI for user interaction

**Documentation**:
- [Complete Documentation](../examples/medical_chatbot/README.md)
- [5-Minute Quick Start](../examples/medical_chatbot/QUICKSTART.md)
- [Production Deployment](../examples/medical_chatbot/DEPLOYMENT.md)

---

## 🔍 Documentation Coming Soon

The following documentation is planned and will be added in future updates:

- **[FAQ](FAQ.md)** - Frequently asked questions and answers
- **[Glossary](GLOSSARY.md)** - Technical terms and definitions
- **[Framework Comparison](COMPARISON.md)** - Detailed comparison with LangChain, AutoGen, and CrewAI
- **[Framework Rating](FRAMEWORK_RATING.md)** - 10-dimension evaluation with 8.7/10 overall rating
- **[Getting Started Tutorial](getting-started/first-application.md)** - Step-by-step first application tutorial
- **[REST API Integration Guide](guides/rest-api-integration.md)** - Complete REST API integration guide
- **[Advanced Topics](guides/)** - Advanced configuration and optimization guides

---

## 🛠️ Additional Resources

### Code Repository
- **[GitHub Repository](https://github.com/your-org/mdsa-framework)** - Source code and issue tracking
- **[Release Notes](../CHANGELOG.md)** - Version history and changes
- **[Contributing Guide](../CONTRIBUTING.md)** - How to contribute to MDSA

### Community
- **GitHub Issues** - Bug reports and feature requests
- **GitHub Discussions** - Questions and community support
- **Pull Requests** - Code contributions

### Related Documentation
- **[README](../README.md)** - Project overview and quick start
- **[License](../LICENSE)** - Apache 2.0 license details
- **[Development Logs](../archive/development-logs/)** - Historical development records

---

## 📝 Documentation Standards

All MDSA documentation follows these standards:

- **Clear Structure**: Hierarchical organization with table of contents
- **Code Examples**: Working code snippets for all features
- **Cross-References**: Links to related documentation
- **Version Tracking**: Version numbers and last updated dates
- **Beginner-Friendly**: Assumes minimal prior knowledge
- **Production-Ready**: Real-world deployment guidance

---

## 🤝 Contributing to Documentation

We welcome documentation improvements! To contribute:

1. Fork the repository
2. Create a documentation branch
3. Make your changes following our standards
4. Submit a pull request
5. Address review feedback

See [Developer Guide: Contributing](DEVELOPER_GUIDE.md#8-contributing) for details.

---

## 📧 Getting Help

If you can't find what you're looking for:

1. Search this documentation hub
2. Check the Coming Soon: [FAQ](FAQ.md)
3. Search [GitHub Issues](https://github.com/your-org/mdsa-framework/issues)
4. Create a new issue with the `documentation` label

---

## 📊 Documentation Coverage

Current documentation status:

| Category | Status | Files |
|----------|--------|-------|
| **Getting Started** | ✅ Complete | Setup Guide, User Guide |
| **Development** | ✅ Complete | Developer Guide, Architecture |
| **API Reference** | ✅ Complete | Framework Reference |
| **Performance** | ✅ Complete | Performance Optimizations |
| **Research** | ✅ Complete | Research Paper Content |
| **Examples** | ✅ Complete | Medical Chatbot |
| **Tutorials** | 🚧 Planned | First Application Guide |
| **Integration** | 🚧 Planned | REST API Guide |
| **Comparison** | 🚧 Planned | Framework Comparison |
| **Reference** | 🚧 Planned | FAQ, Glossary |

**Overall Coverage**: 70% complete (7/10 categories)

---

**Last Updated**: December 2025
**Version**: 1.0.0
**Maintained by**: MDSA Framework Team
