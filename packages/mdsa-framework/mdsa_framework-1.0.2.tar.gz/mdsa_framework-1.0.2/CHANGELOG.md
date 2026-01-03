# Changelog

All notable changes to the MDSA (Multi-Domain Specialized Agentic Orchestration) framework will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2025-12-31

### Fixed

#### Critical Bug Fixes
- **Dashboard Authentication** (`mdsa/ui/dashboard.py`):
  - Fixed `AttributeError: 'Flask' object has no attribute 'login_manager'` crash when `enable_auth=True`
  - Root cause: LoginManager initialization order issue - now uses proper `setup_auth()` helper from `mdsa.ui.auth`
  - Fixed nested `@login_required` decorator pattern that applied too late
  - Improved import handling to prevent auth module failures from affecting other components
  - Dashboard now works correctly with authentication enabled (default)

### Added

#### Documentation
- **[docs/OLLAMA_SETUP.md](docs/OLLAMA_SETUP.md)** - Complete Ollama installation and setup guide:
  - Installation instructions for Windows, macOS, and Linux
  - Model download guide with recommended models for different use cases
  - Server configuration and startup instructions
  - MDSA integration examples with code snippets
  - Verification steps and basic troubleshooting

- **[docs/GPU_CONFIGURATION.md](docs/GPU_CONFIGURATION.md)** - Comprehensive GPU acceleration guide:
  - NVIDIA GPU (CUDA) configuration for Windows/Linux
  - AMD GPU (ROCm) configuration for Linux
  - Apple Silicon (M1/M2/M3) Metal configuration for macOS
  - Multi-GPU setup and load balancing
  - Performance benchmarks and optimization tips
  - VRAM management and model selection based on hardware

- **[docs/OLLAMA_TROUBLESHOOTING.md](docs/OLLAMA_TROUBLESHOOTING.md)** - Detailed troubleshooting guide:
  - Installation issues and solutions
  - Connection problems (MDSA ↔ Ollama)
  - Model download and loading issues
  - Performance optimization strategies
  - GPU detection and configuration problems
  - Memory management solutions
  - Platform-specific issues (Windows, macOS, Linux)
  - Advanced debugging techniques

- **Known Issues Section** in [README.md](README.md#L184-L280):
  - Dashboard authentication error documentation with workaround for v1.0.0
  - Ollama connection issues with complete setup prerequisites
  - Quick-start Ollama commands for immediate productivity
  - GPU configuration examples
  - Links to detailed troubleshooting guides

### Improved

#### Documentation Enhancement
- **[docs/USER_GUIDE.md](docs/USER_GUIDE.md)** - Expanded Ollama section:
  - Added comprehensive Ollama model table with VRAM requirements and use cases
  - Documented correct `ollama://` model name format for MDSA
  - Added performance expectations for CPU vs GPU
  - Updated all code examples to use correct Ollama syntax
  - Added multi-model setup example showing Ollama + HuggingFace integration
  - Cross-referenced setup, GPU, and troubleshooting guides

#### Error Messages
- Better error reporting when UserManager/auth modules fail to import
- Clear warnings when authentication is disabled due to missing dependencies
- Improved Ollama connection error messages with actionable suggestions

### Testing

#### Test Suite Addition
- `test_dashboard_auth.py` - Comprehensive authentication test suite:
  - Dashboard initialization with `enable_auth=True` (no crashes)
  - Route registration verification
  - Login/logout flow testing
  - Protected route access control
  - API endpoint authentication
  - All tests passing on fixed implementation

### User Experience Improvements

- Users can now run dashboard with authentication enabled without crashes
- Clear documentation path: Install Ollama → Configure GPU → Troubleshoot issues
- Ollama setup reduced from "unclear" to <15 minutes with guides
- Known issues are transparent with workarounds documented
- Performance expectations clearly set for different hardware configurations

### Technical Details

#### Files Modified
- `mdsa/ui/dashboard.py` - LoginManager fix (4 edits)
- `README.md` - Added Known Issues section
- `docs/USER_GUIDE.md` - Expanded Ollama documentation

#### Files Added
- `docs/OLLAMA_SETUP.md` - 400+ lines, comprehensive guide
- `docs/GPU_CONFIGURATION.md` - 600+ lines, detailed GPU configuration
- `docs/OLLAMA_TROUBLESHOOTING.md` - 800+ lines, extensive troubleshooting
- `test_dashboard_auth.py` - Authentication test suite

### Breaking Changes

None - all changes are backward compatible.

**Migration Notes**:
- If you were using `enable_auth=False` to work around v1.0.0 bug, you can now remove that and use default `enable_auth=True`
- Ollama model names should use `ollama://` prefix (e.g., `ollama://gemma3:1b`), though old format may still work

---

## [1.0.0] - 2025-12-24

### Added

#### Core Framework
- Multi-domain orchestration with TinyBERT-based router for intelligent query routing
- Dual RAG system combining global knowledge base (10k docs) and domain-specific local knowledge (1k docs per domain)
- Hybrid reasoning with Phi-2 model for complex queries requiring multi-step logic
- 17 core framework modules implementing complete orchestration pipeline
- Real-time monitoring dashboard with interactive visualizations
- Request tracking and performance analytics

#### Performance Optimizations
- Domain embedding cache - eliminates redundant embedding computation (100-250ms savings per request)
- Response caching system with MD5 key hashing and FIFO eviction (200x speedup on cache hits)
- Lazy precomputation of domain embeddings on first classification
- Cache invalidation on domain configuration changes

#### Integration Features
- Request tracking bridge between chatbot and dashboard via `/api/requests/track` endpoint
- Non-blocking background thread communication for zero performance impact
- Real-time monitoring graph updates with live chatbot request data
- Global request history management with automatic size limiting

#### User Interface
- Modern indigo/violet color theme with gradient backgrounds
- Simplified navigation (consolidated from 8 to 6 clean links)
- Interactive monitoring dashboard with Chart.js visualizations
- Welcome page with framework overview and quick start guide
- Model configuration page with auto-reload on save
- RAG management interface with document source filtering

#### Developer Experience
- Comprehensive documentation suite
- Automated test script with 12 test cases
- Environment template (.env.example) for easy setup
- Configuration hot-reload without server restart
- Detailed implementation guides and testing instructions

### Performance

#### Latency Improvements
- Domain classification: 25-61ms (vs 125-310ms baseline) - **80% faster**
- First query response: 585-2141ms (15% faster than baseline)
- Cached query response: <10ms - **200x faster**
- Overall improvement: 15-90% depending on cache hit rate

#### Cache Efficiency
- Cache hit rate: 60-80% for FAQ scenarios
- Cache capacity: 100 unique queries (configurable)
- Cache key: MD5 hash of normalized query text
- Eviction strategy: FIFO (First-In-First-Out)

### Fixed

#### Critical Bugs
- Domain embedding regeneration on every request (now cached)
- Missing request tracking in monitoring graph (now integrated)
- Navigation confusion with duplicate/unclear links (now simplified)
- Model configuration not persisting (now with hot-reload)
- Dashboard showing static demo data instead of real requests (now live-updated)

#### UI/UX Improvements
- Inconsistent color scheme (now cohesive indigo/violet theme)
- Confusing navigation structure (now 6 clear sections)
- Document source filtering missing (now shows system vs user docs)
- No visual feedback on configuration save (now auto-reloads)

### Technical Details

#### Architecture
- **Router:** TinyBERT (67M parameters, <50ms classification)
- **Reasoner:** Phi-2 (2.7B parameters, optional for complex queries)
- **RAG:** ChromaDB with SentenceTransformers (all-MiniLM-L6-v2)
- **Dashboard:** FastAPI + Jinja2 + Chart.js
- **Chatbot:** Gradio + FastAPI backend

#### Memory Footprint
- TinyBERT: ~270MB
- SentenceTransformer: ~90MB
- ChromaDB: ~500MB (depends on document count)
- Phi-2: ~5GB (optional, loaded on-demand)
- Total (without Phi-2): ~2GB

#### Supported Domains (Example Configuration)
1. Medical Diagnosis
2. Treatment Planning
3. Symptom Analysis
4. Lab Results Interpretation
5. Patient Risk Assessment

### Security
- Environment variable management via python-dotenv
- Secure API endpoints with request validation
- Input sanitization for user queries
- CORS configuration for dashboard endpoints

---

## [0.1.0] - 2025-11-26

### Added
- Initial framework implementation
- Basic orchestrator with domain routing
- RAG integration with ChromaDB
- Simple monitoring dashboard
- Domain registration system
- Configuration file management

### Known Issues
- Performance bottlenecks in domain classification
- No response caching
- Static monitoring data
- Inconsistent UI design

---

## Versioning Strategy

- **Major version (X.0.0):** Breaking API changes, architectural redesign
- **Minor version (0.X.0):** New features, non-breaking enhancements
- **Patch version (0.0.X):** Bug fixes, performance improvements, documentation updates

---

## Upgrade Notes

### From 0.1.0 to 1.0.0

**Required Actions:**
1. Update `requirements.txt` dependencies
2. Review new `.env.example` and update your `.env` file
3. Clear any cached embeddings (will be regenerated automatically)
4. Update chatbot integration to use new tracking endpoint (optional)

**Breaking Changes:**
- None - v1.0.0 is fully backward compatible with v0.1.0

**Recommended Actions:**
1. Enable response caching by upgrading chatbot to latest version
2. Configure dashboard tracking endpoint for real-time monitoring
3. Review performance metrics in dashboard after upgrade
4. Update domain configurations to leverage new caching features

---

**Maintained by:** MDSA Research Team
**License:** MIT
**Repository:** [GitHub URL to be added]
**Documentation:** See README.md and docs/ folder
