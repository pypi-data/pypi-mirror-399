"""
Enhanced Medical Chatbot with Integrated Dashboard

Production-ready medical assistant with integrated FastAPI monitoring dashboard.
Combines Gradio chat interface (port 7860) with FastAPI metrics API (port 5000).

Features:
- Dual RAG system (Global + Local knowledge)
- Hybrid orchestration (TinyBERT + Phi-2 reasoning)
- Multi-domain expertise with 5 specialized medical SLMs
- Real-time statistics and monitoring
- Integrated FastAPI dashboard for system metrics
"""

import os
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import gradio as gr
from typing import List, Tuple, Dict, Any, Optional
import json
from datetime import datetime
import asyncio
import threading

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, File, Form, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# MDSA Framework imports
from mdsa.core.orchestrator import TinyBERTOrchestrator as Orchestrator
from mdsa.memory.dual_rag import DualRAG
from mdsa.ui.enhanced_dashboard import EnhancedDashboard

# Medical-specific imports
from chatbot_app.medical_app.domains.enhanced_medical_domains import (
    get_all_enhanced_medical_domains,
    DOMAIN_PRIORITY
)
from chatbot_app.medical_app.knowledge_base.enhanced_medical_kb import (
    initialize_medical_knowledge_base,
    get_code_by_number,
    search_codes_by_description
)


# ============================================================================
# Pydantic Models for FastAPI
# ============================================================================

class QueryRequest(BaseModel):
    """Query request model for API"""
    query: str
    context: Optional[Dict] = None


class DomainInfo(BaseModel):
    """Domain information model"""
    domain_id: str
    model_name: str
    description: str
    keywords: List[str]
    status: str


# ============================================================================
# Enhanced Medical Chatbot (Core Logic)
# ============================================================================

class EnhancedMedicalChatbot:
    """
    Enhanced medical chatbot with specialized SLMs, RAG, and integrated dashboard.
    """

    def __init__(
        self,
        enable_reasoning: bool = True,
        prefer_gpu: bool = True,
        force_device: str = None
    ):
        """
        Initialize enhanced medical chatbot.

        Args:
            enable_reasoning: Enable hybrid orchestration with Phi-2 reasoning
            prefer_gpu: Prefer GPU if available
            force_device: Force specific device (cpu/cuda)
        """
        print("[INIT] Initializing Enhanced Medical Chatbot with Dashboard...")

        # Initialize orchestrator with hybrid reasoning
        # Lower threshold from 0.3 to 0.2 to trigger reasoning more frequently
        # Configurable via MDSA_COMPLEXITY_THRESHOLD environment variable
        complexity_threshold = float(os.getenv('MDSA_COMPLEXITY_THRESHOLD', '0.2'))
        self.orchestrator = Orchestrator(
            enable_reasoning=enable_reasoning,
            complexity_threshold=complexity_threshold  # Queries >threshold use Phi-2
        )
        print(f"[INIT] Reasoning complexity threshold: {complexity_threshold}")

        # Initialize Dual RAG system (10k global docs, default 1k local docs)
        self.dual_rag = DualRAG(max_global_docs=10000)
        print("[INIT] Initializing medical knowledge base...")
        initialize_medical_knowledge_base(self.dual_rag)

        # Register all medical domains
        print("[INIT] Registering medical domains...")
        self.domains = get_all_enhanced_medical_domains(prefer_gpu, force_device)
        self.domain_configs = {}  # Store domain configs for dashboard
        for domain in self.domains:
            print(f"  - {domain.name} ({domain.model_name})")
            # Register domain with orchestrator (extract fields from DomainConfig)
            self.orchestrator.register_domain(
                name=domain.name,
                description=domain.description,
                keywords=domain.keywords if hasattr(domain, 'keywords') else []
            )
            # CRITICAL FIX: Register domain with DualRAG for local knowledge
            if not hasattr(self.dual_rag, 'local_rags') or domain.name not in self.dual_rag.local_rags:
                try:
                    # Register domain to create LocalRAG instance
                    self.dual_rag.register_domain(domain.name)
                except Exception as e:
                    print(f"  Warning: Could not register domain with RAG for {domain.name}: {e}")
            # Store config for dashboard API
            self.domain_configs[domain.name] = {
                'domain_id': domain.name,
                'model_name': domain.model_name,
                'description': getattr(domain, 'description', domain.name),
                'keywords': getattr(domain, 'keywords', []),
                'status': 'active'
            }

        # Initialize dashboard for monitoring
        self.dashboard = EnhancedDashboard(output_dir="./dashboard_output")

        # Conversation history (shared between Gradio and API)
        self.conversation_history: List[Dict[str, Any]] = []

        # Request history for API/dashboard
        self.request_history: List[Dict] = []
        self.MAX_HISTORY = 1000

        # Performance optimization: Response cache for repeated queries
        self.response_cache: Dict[str, Tuple] = {}
        self.MAX_CACHE_SIZE = 100  # Cache last 100 unique queries
        print("[INIT] Response caching enabled (max 100 queries)")

        # Register this app with MDSA app registry for dashboard discovery
        self._register_with_dashboard()

        print("[INIT] Enhanced Medical Chatbot ready!")
        print(f"[INIT] Registered {len(self.domains)} specialized medical domains")
        print(f"[INIT] Knowledge base: {len(self.dual_rag.global_rag._documents)} global documents")

    def _register_with_dashboard(self):
        """Register this medical chatbot app with MDSA dashboard for discovery."""
        try:
            from mdsa.core.app_registry import register_current_app

            # Register with app registry
            register_current_app(
                app_id="medical-chatbot",
                app_name="Enhanced Medical Chatbot",
                framework="fastapi+gradio",
                port=5000,  # FastAPI port
                base_path=""
            )

            print("[INIT] Registered with MDSA Control Dashboard (port 9000)")

        except Exception as e:
            print(f"[WARN] Could not register with dashboard: {e}")
            # Non-fatal - chatbot can still work standalone

    def _cache_key(self, message: str) -> str:
        """
        Generate cache key for message.

        Args:
            message: User message

        Returns:
            str: MD5 hash of normalized message
        """
        import hashlib
        # Normalize: lowercase, strip whitespace
        normalized = message.lower().strip()
        return hashlib.md5(normalized.encode()).hexdigest()

    def _track_to_dashboard(self, request_data: Dict):
        """
        Send request tracking to dashboard (async, non-blocking).

        This allows the dashboard monitoring page to display real-time
        chatbot request data instead of only showing demo data.

        Args:
            request_data: Request metadata to track
        """
        def _send():
            try:
                import requests
                requests.post(
                    "http://localhost:9000/api/requests/track",
                    json=request_data,
                    timeout=1
                )
            except Exception as e:
                # Dashboard tracking is optional - don't fail if unavailable
                pass

        # Send in background thread to avoid blocking
        thread = threading.Thread(target=_send, daemon=True)
        thread.start()

    def process_message(
        self,
        message: str,
        history: List[Dict[str, str]] = None
    ) -> Tuple[List[Dict[str, str]], str, str]:
        """
        Process user message and return response with metadata.

        Args:
            message: User's input message
            history: Chat history (optional, for Gradio)

        Returns:
            Tuple of (updated_history, metadata_json, rag_context)
        """
        if history is None:
            history = []

        try:
            # Check cache for repeated queries (skip for special commands)
            if not message.startswith("/"):
                cache_k = self._cache_key(message)
                if cache_k in self.response_cache:
                    cached_history, cached_metadata, cached_rag = self.response_cache[cache_k]
                    print(f"[CACHE HIT] Returning cached response for query")
                    # Return copy of cached data with updated history
                    return history + cached_history[-2:], cached_metadata, cached_rag

            # Check for special commands
            if message.startswith("/code "):
                code = message.split(" ", 1)[1].strip()
                return self._handle_code_lookup(code, history)

            # Process through orchestrator
            start_time = datetime.now()
            result = self.orchestrator.process_request(message)
            latency_ms = (datetime.now() - start_time).total_seconds() * 1000

            # Get domain from result - FIX: handle both dictionary structures
            domain = result.get('domain', result.get('metadata', {}).get('domain', 'unknown'))

            # Get RAG context if available
            rag_context = self._get_rag_context(message, domain)

            # CRITICAL FIX: Orchestrator only routes, need to call model directly
            if 'response' not in result and 'output' not in result:
                # Get domain config
                domain_model = None
                for d in self.domains:
                    if d.name == domain:
                        domain_model = d.model_name
                        break

                if domain_model and domain_model.startswith('ollama://'):
                    # Call Ollama model directly
                    import ollama
                    model_name = domain_model.replace('ollama://', '')
                    try:
                        ollama_response = ollama.chat(
                            model=model_name,
                            messages=[{'role': 'user', 'content': message + '\n\nContext:\n' + rag_context}]
                        )
                        response = ollama_response['message']['content']
                    except Exception as e:
                        response = f"Model execution error: {str(e)}"
                else:
                    response = "Sorry, model configuration error."
            else:
                # Extract response - FIX: handle both response structures
                response = result.get('response', result.get('output', 'Sorry, I could not process your request.'))

            # Update dashboard
            self.dashboard.track_request(
                query=message,
                domain=domain,
                model=result.get('model', result.get('metadata', {}).get('model', 'unknown')),
                latency_ms=latency_ms,
                success=(result.get('status', 'success') == 'success'),
                correlation_id=f"req_{len(self.conversation_history)}"
            )

            # Format metadata
            metadata = {
                "domain": domain,
                "model": result.get('model', result.get('metadata', {}).get('model', 'unknown')),
                "latency_ms": round(latency_ms, 2),
                "complexity": result.get('complexity', 'N/A'),
                "used_reasoning": result.get('used_reasoning', False),
                "status": result.get('status', 'success')
            }

            # Save to history
            conv_entry = {
                "timestamp": datetime.now().isoformat(),
                "query": message,
                "response": response,
                "metadata": metadata
            }
            self.conversation_history.append(conv_entry)

            # Save to request history for API
            self.request_history.append({
                "timestamp": conv_entry["timestamp"],
                "query": message,
                "domain": domain,
                "status": metadata["status"],
                "latency_ms": latency_ms,
                "response_preview": response[:100]
            })
            if len(self.request_history) > self.MAX_HISTORY:
                self.request_history.pop(0)

            # Track to dashboard (non-blocking)
            self._track_to_dashboard({
                "timestamp": conv_entry["timestamp"],
                "query": message,
                "domain": domain,
                "status": metadata["status"],
                "latency_ms": latency_ms,
                "response_preview": response[:100],
                "app_id": "medical-chatbot"
            })

            # Update gradio history with Gradio 6.1.0 format
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": response})

            # Cache response for future identical queries
            if not message.startswith("/"):
                cache_k = self._cache_key(message)
                metadata_json = json.dumps(metadata, indent=2)
                self.response_cache[cache_k] = (history.copy(), metadata_json, rag_context)

                # Limit cache size (FIFO eviction)
                if len(self.response_cache) > self.MAX_CACHE_SIZE:
                    # Remove oldest entry (first key)
                    oldest_key = next(iter(self.response_cache))
                    del self.response_cache[oldest_key]
                    print(f"[CACHE] Evicted oldest entry, cache size: {len(self.response_cache)}")

            return history, json.dumps(metadata, indent=2), rag_context

        except Exception as e:
            import traceback
            traceback.print_exc()
            error_msg = f"Error: {str(e)}"
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": error_msg})
            return history, json.dumps({"error": str(e)}, indent=2), ""

    def _handle_code_lookup(
        self,
        code: str,
        history: List[Dict[str, str]]
    ) -> Tuple[List[Dict[str, str]], str, str]:
        """Handle special /code command for direct code lookup."""
        code_info = get_code_by_number(code.upper())

        if code_info:
            response = f"""
**{code_info.code_type}: {code_info.code}**

**Description:** {code_info.description}

**Category:** {code_info.category}

**Billable:** {"Yes" if code_info.billable else "No"}

**Typical Charge:** ${code_info.typical_charge:.2f}

**Medical Necessity:** {code_info.medical_necessity if code_info.medical_necessity else "N/A"}

**Authorization Required:** {"Yes" if code_info.requires_auth else "No"}
            """
        else:
            response = f"Code '{code}' not found in knowledge base. Try a general search or ask me about it!"

        # Append user command and assistant response in Gradio 6.1.0 format
        history.append({"role": "user", "content": f"/code {code}"})
        history.append({"role": "assistant", "content": response})
        metadata = {"command": "code_lookup", "code": code, "found": code_info is not None}

        return history, json.dumps(metadata, indent=2), ""

    def _get_rag_context(self, query: str, domain: str) -> str:
        """Get RAG context for the query."""
        try:
            # Search both global and local RAG
            results = self.dual_rag.retrieve(
                query=query,
                domain_id=domain,
                search_local=True,
                search_global=True,
                top_k=3
            )

            context_parts = []

            if results['global'].documents:
                context_parts.append("**Global Knowledge:**")
                for doc in results['global'].documents[:2]:
                    context_parts.append(f"- {doc.content[:200]}...")

            if results['local'].documents:
                context_parts.append("\n**Domain-Specific Knowledge:**")
                for doc in results['local'].documents[:2]:
                    context_parts.append(f"- {doc.content[:200]}...")

            return "\n".join(context_parts) if context_parts else "No RAG context retrieved"

        except Exception as e:
            return f"RAG context unavailable: {str(e)}"

    def get_statistics(self) -> Dict:
        """Get chatbot statistics."""
        stats = self.orchestrator.get_stats()
        return stats

    def search_codes(self, search_term: str) -> str:
        """Search medical codes by description."""
        results = search_codes_by_description(search_term)

        if not results:
            return f"No codes found matching '{search_term}'"

        output = f"**Found {len(results)} codes matching '{search_term}':**\n\n"
        for code in results[:10]:  # Limit to top 10
            output += f"- **{code.code}** ({code.code_type}): {code.description}\n"

        return output

    def export_conversation(self) -> str:
        """Export conversation history as JSON."""
        return json.dumps(self.conversation_history, indent=2)


# ============================================================================
# FastAPI Dashboard Integration
# ============================================================================

# Global chatbot instance (shared between FastAPI and Gradio)
chatbot_instance: Optional[EnhancedMedicalChatbot] = None

# Create FastAPI app for dashboard
api_app = FastAPI(
    title="MDSA Medical Dashboard API",
    description="Real-time monitoring API for Enhanced Medical Chatbot",
    version="1.0.0"
)

# Add CORS middleware to allow Gradio frontend to access API
api_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (restrict in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Active WebSocket connections
active_connections: List[WebSocket] = []


@api_app.get("/")
@api_app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "components": {
            "chatbot": chatbot_instance is not None,
            "orchestrator": chatbot_instance.orchestrator is not None if chatbot_instance else False,
            "dual_rag": chatbot_instance.dual_rag is not None if chatbot_instance else False,
            "domains": len(chatbot_instance.domains) if chatbot_instance else 0
        }
    }


@api_app.get("/welcome", response_class=HTMLResponse)
async def welcome_page():
    """Welcome page with medical chatbot overview"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>MDSA Medical Chatbot</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            h1 { color: #2c3e50; }
            .info-box { background: white; padding: 20px; border-radius: 8px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .link-box { background: #e8f4f8; padding: 15px; border-radius: 5px; margin: 10px 0; }
            a { color: #3498db; text-decoration: none; font-weight: bold; }
            a:hover { text-decoration: underline; }
            .status { color: #27ae60; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>🏥 Enhanced Medical Chatbot - MDSA Framework</h1>

        <div class="info-box">
            <h2>System Status</h2>
            <p><span class="status">✓ Running</span></p>
            <p><strong>Chat Interface:</strong> <a href="http://localhost:7860" target="_blank">http://localhost:7860</a></p>
            <p><strong>API Endpoint:</strong> http://localhost:5000</p>
        </div>

        <div class="info-box">
            <h2>Features</h2>
            <ul>
                <li>5 Specialized Medical SLMs via Ollama Cloud</li>
                <li>Dual RAG System (Global + Local Knowledge)</li>
                <li>Hybrid Orchestration (TinyBERT + Phi-2)</li>
                <li>Real-time Monitoring Dashboard</li>
            </ul>
        </div>

        <div class="link-box">
            <h3>Quick Links</h3>
            <ul>
                <li><a href="/docs">📚 API Documentation</a></li>
                <li><a href="/api/health">💚 Health Check</a></li>
                <li><a href="/api/domains">🏗️ View Domains</a></li>
                <li><a href="/api/metrics">📊 System Metrics</a></li>
                <li><a href="/monitor">📈 Live Monitor</a></li>
            </ul>
        </div>

        <p style="color: #7f8c8d; font-size: 0.9em; margin-top: 30px;">
            <strong>⚠️ Disclaimer:</strong> This is an AI assistant for educational and informational purposes only.
            Always consult licensed healthcare professionals for actual medical advice, diagnosis, and treatment.
        </p>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@api_app.get("/monitor", response_class=HTMLResponse)
async def monitor_page():
    """Real-time monitoring page with live metrics"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>MDSA Medical Chatbot - Monitor</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            h1 { color: #2c3e50; }
            .metric-card {
                background: white;
                padding: 20px;
                border-radius: 8px;
                margin: 15px 0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                display: inline-block;
                width: 250px;
                margin-right: 20px;
            }
            .metric-value { font-size: 2.5em; font-weight: bold; color: #3498db; }
            .metric-label { color: #7f8c8d; margin-top: 5px; font-size: 0.9em; }
            #metrics-container { max-width: 1200px; margin: 0 auto; }
            .refresh-btn {
                background: #3498db;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
                margin-bottom: 20px;
            }
            .refresh-btn:hover { background: #2980b9; }
            .timestamp { color: #95a5a6; font-size: 0.9em; }
        </style>
    </head>
    <body>
        <div id="metrics-container">
            <h1>📈 Medical Chatbot - Real-Time Monitor</h1>
            <button class="refresh-btn" onclick="loadMetrics()">🔄 Refresh Metrics</button>
            <p class="timestamp" id="last-update"></p>

            <div id="metrics-display"></div>
        </div>

        <script>
            async function loadMetrics() {
                try {
                    const response = await fetch('/api/metrics');
                    const data = await response.json();

                    const now = new Date().toLocaleString();
                    document.getElementById('last-update').textContent = `Last updated: ${now}`;

                    const display = document.getElementById('metrics-display');
                    display.innerHTML = `
                        <div class="metric-card">
                            <div class="metric-value">${data.domains.total}</div>
                            <div class="metric-label">Registered Domains</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">${data.requests.total}</div>
                            <div class="metric-label">Total Requests</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">${data.rag.global_documents}</div>
                            <div class="metric-label">Global RAG Documents</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">${data.rag.local_domains}</div>
                            <div class="metric-label">Local RAG Domains</div>
                        </div>
                    `;
                } catch (error) {
                    document.getElementById('metrics-display').innerHTML =
                        '<div class="metric-card" style="color: red; width: 100%;">❌ Error loading metrics: ' + error.message + '</div>';
                }
            }

            // Load metrics immediately
            loadMetrics();

            // Auto-refresh every 5 seconds
            setInterval(loadMetrics, 5000);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@api_app.get("/api/domains")
async def list_domains():
    """List all registered domains"""
    if not chatbot_instance:
        raise HTTPException(status_code=503, detail="Chatbot not initialized")

    domains = list(chatbot_instance.domain_configs.values())
    return {"domains": domains, "count": len(domains)}


@api_app.get("/api/models")
async def list_models():
    """List all loaded models"""
    if not chatbot_instance:
        raise HTTPException(status_code=503, detail="Chatbot not initialized")

    # Extract unique models from domains
    models = []
    seen_models = set()
    for config in chatbot_instance.domain_configs.values():
        model_name = config['model_name']
        if model_name not in seen_models:
            seen_models.add(model_name)
            domains_using = [d['domain_id'] for d in chatbot_instance.domain_configs.values()
                           if d['model_name'] == model_name]
            models.append({
                "model_name": model_name,
                "domains_using": domains_using,
                "status": "active"
            })

    return {"models": models, "count": len(models)}


@api_app.get("/api/metrics")
async def get_metrics():
    """Get current system metrics"""
    if not chatbot_instance:
        raise HTTPException(status_code=503, detail="Chatbot not initialized")

    orchestrator_stats = chatbot_instance.get_statistics()

    return {
        "timestamp": datetime.now().isoformat(),
        "domains": {
            "total": len(chatbot_instance.domains),
            "active": len(chatbot_instance.domains)
        },
        "requests": {
            "total": len(chatbot_instance.request_history),
            "recent": len([r for r in chatbot_instance.request_history
                          if datetime.fromisoformat(r['timestamp']) > datetime.now().replace(microsecond=0, second=0)])
        },
        "rag": {
            "global_documents": len(chatbot_instance.dual_rag.global_rag._documents),
            "local_domains": len(chatbot_instance.dual_rag.local_rags)
        },
        "orchestrator": orchestrator_stats
    }


@api_app.get("/api/requests")
async def get_requests(limit: int = 100):
    """Get request history"""
    if not chatbot_instance:
        raise HTTPException(status_code=503, detail="Chatbot not initialized")

    return {
        "requests": chatbot_instance.request_history[-limit:],
        "total": len(chatbot_instance.request_history),
        "limit": limit
    }


@api_app.post("/api/query")
async def process_query(query_request: QueryRequest):
    """Process a query through MDSA"""
    if not chatbot_instance:
        raise HTTPException(status_code=503, detail="Chatbot not initialized")

    start_time = datetime.now()

    try:
        # Process query (will also update request_history)
        _, metadata_json, rag_context = chatbot_instance.process_message(
            query_request.query,
            history=[]
        )

        metadata = json.loads(metadata_json)
        latency_ms = metadata.get('latency_ms', 0)

        # Get the response from conversation history
        response = chatbot_instance.conversation_history[-1]['response'] if chatbot_instance.conversation_history else ""

        return {
            "response": response,
            "metadata": metadata,
            "rag_context": rag_context,
            "latency_ms": latency_ms,
            "status": "success"
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@api_app.get("/api/rag/global")
async def get_global_rag_docs():
    """Get global RAG documents"""
    if not chatbot_instance:
        raise HTTPException(status_code=503, detail="Chatbot not initialized")

    docs = chatbot_instance.dual_rag.global_rag._documents
    return {
        "documents": [{"content": doc.content[:200], "metadata": doc.metadata} for doc in docs],
        "count": len(docs)
    }


@api_app.get("/api/rag/local/{domain_id}")
async def get_local_rag_docs(domain_id: str):
    """Get local RAG documents for a specific domain"""
    if not chatbot_instance:
        raise HTTPException(status_code=503, detail="Chatbot not initialized")

    if domain_id not in chatbot_instance.dual_rag.local_rags:
        raise HTTPException(status_code=404, detail=f"Domain '{domain_id}' not found")

    local_rag = chatbot_instance.dual_rag.local_rags[domain_id]
    docs = local_rag._documents

    return {
        "domain_id": domain_id,
        "documents": [{"content": doc.content[:200], "metadata": doc.metadata} for doc in docs],
        "count": len(docs)
    }


@api_app.get("/api/rag/documents")
async def list_all_rag_documents():
    """List all RAG documents (global + local) in dashboard-compatible format"""
    if not chatbot_instance:
        raise HTTPException(status_code=503, detail="Chatbot not initialized")

    all_docs = []

    # Get global RAG documents
    global_docs = chatbot_instance.dual_rag.global_rag._documents
    for doc_id, doc in global_docs.items():
        all_docs.append({
            "doc_id": doc_id,
            "content": doc.content,
            "metadata": doc.metadata,
            "type": "global",
            "domain": None
        })

    # Get local RAG documents
    for domain_id, local_rag in chatbot_instance.dual_rag.local_rags.items():
        local_docs = local_rag._documents
        for doc_id, doc in local_docs.items():
            all_docs.append({
                "doc_id": doc_id,
                "content": doc.content,
                "metadata": doc.metadata,
                "type": "local",
                "domain": domain_id
            })

    return {
        "documents": all_docs,
        "count": len(all_docs)
    }


@api_app.post("/api/rag/upload")
async def upload_rag_document(
    file: UploadFile = File(...),
    rag_type: str = Form(...),
    domain: str = Form(None)
):
    """Upload a document to RAG (global or local)"""
    if not chatbot_instance:
        raise HTTPException(status_code=503, detail="Chatbot not initialized")

    try:
        # Read file content
        content = await file.read()
        text_content = content.decode('utf-8')

        # Generate document ID
        import hashlib
        doc_id = hashlib.md5(text_content.encode()).hexdigest()[:16]

        # Add to appropriate RAG
        if rag_type == "global":
            chatbot_instance.dual_rag.add_to_global(
                content=text_content,
                metadata={
                    "source": file.filename,
                    "type": file.content_type,
                    "uploaded_at": datetime.now().isoformat()
                },
                doc_id=f"global_{doc_id}"
            )
            return {
                "message": "Document uploaded to global RAG",
                "doc_id": f"global_{doc_id}",
                "filename": file.filename
            }

        elif rag_type == "local":
            if not domain:
                raise HTTPException(status_code=400, detail="Domain required for local RAG")

            # Register domain if not exists
            if domain not in chatbot_instance.dual_rag.local_rags:
                chatbot_instance.dual_rag.register_domain(domain)

            chatbot_instance.dual_rag.add_to_local(
                domain_id=domain,
                content=text_content,
                metadata={
                    "source": file.filename,
                    "type": file.content_type,
                    "uploaded_at": datetime.now().isoformat()
                },
                doc_id=f"{domain}_{doc_id}"
            )
            return {
                "message": f"Document uploaded to local RAG for domain '{domain}'",
                "doc_id": f"{domain}_{doc_id}",
                "filename": file.filename
            }

        else:
            raise HTTPException(status_code=400, detail="Invalid rag_type. Must be 'global' or 'local'")

    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be text-based (UTF-8)")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")


class DeleteDocumentRequest(BaseModel):
    """Request model for deleting a RAG document"""
    type: str  # 'global' or 'local'
    domain: Optional[str] = None


@api_app.delete("/api/rag/document/{doc_id}")
async def delete_rag_document(doc_id: str, request: DeleteDocumentRequest):
    """Delete a document from RAG"""
    if not chatbot_instance:
        raise HTTPException(status_code=503, detail="Chatbot not initialized")

    try:
        if request.type == "global":
            # Delete from global RAG
            global_rag = chatbot_instance.dual_rag.global_rag
            # ChromaDB delete
            if hasattr(global_rag, '_collection'):
                global_rag._collection.delete(ids=[doc_id])
            return {"message": "Document deleted from global RAG"}

        elif request.type == "local":
            if not request.domain:
                raise HTTPException(status_code=400, detail="Domain required for local RAG deletion")

            if request.domain not in chatbot_instance.dual_rag.local_rags:
                raise HTTPException(status_code=404, detail=f"Domain '{request.domain}' not found")

            # Delete from local RAG
            local_rag = chatbot_instance.dual_rag.local_rags[request.domain]
            if hasattr(local_rag, '_collection'):
                local_rag._collection.delete(ids=[doc_id])
            return {"message": f"Document deleted from local RAG for domain '{request.domain}'"}

        else:
            raise HTTPException(status_code=400, detail="Invalid type. Must be 'global' or 'local'")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")


@api_app.websocket("/ws/metrics")
async def metrics_websocket(websocket: WebSocket):
    """WebSocket endpoint for real-time metrics streaming"""
    await websocket.accept()
    active_connections.append(websocket)

    try:
        while True:
            # Send metrics every 2 seconds
            metrics = await get_metrics()
            await websocket.send_json(metrics)
            await asyncio.sleep(2)

    except WebSocketDisconnect:
        active_connections.remove(websocket)


# ============================================================================
# Gradio Interface
# ============================================================================

def create_gradio_interface(chatbot: EnhancedMedicalChatbot):
    """Create Gradio interface for the chatbot"""

    with gr.Blocks() as demo:
        gr.Markdown("""
        # 🏥 Enhanced Medical Assistant (with Integrated Dashboard)

        Powered by Specialized Medical SLMs with **Ollama Cloud Models**:
        - **deepseek-v3.1:671b-cloud**: Clinical diagnosis (671B params)
        - **kimi-k2-thinking:cloud**: Medical coding and billing
        - **qwen3-coder:480b-cloud**: Biomedical text extraction
        - **qwen3-vl:235b-instruct-cloud**: Radiology support (vision-language)
        - **gpt-oss:120b-cloud**: Quick medical Q&A

        **Features**: Hybrid AI orchestration, Dual RAG knowledge base, Real-time statistics

        **Dashboard API**: Available at http://localhost:5000/api/health
        """)

        with gr.Tabs():
            # Chat Tab
            with gr.Tab("💬 Medical Chat"):
                with gr.Row():
                    with gr.Column(scale=2):
                        chatbox = gr.Chatbot(
                            label="Conversation",
                            height=500,
                            avatar_images=(None, "🏥")
                        )
                        msg = gr.Textbox(
                            label="Your Message",
                            placeholder="Ask me about diagnoses, medical codes, procedures, etc. or use /code <CODE> for direct lookup",
                            lines=2
                        )
                        with gr.Row():
                            submit = gr.Button("Send", variant="primary")
                            clear = gr.Button("Clear Chat")

                    with gr.Column(scale=1):
                        gr.Markdown("### 📊 Response Metadata")
                        metadata_box = gr.JSON(label="Metadata")

                        gr.Markdown("### 📚 RAG Context")
                        rag_box = gr.Textbox(
                            label="Knowledge Retrieved",
                            lines=8,
                            interactive=False
                        )

                # Submit handlers
                submit.click(
                    chatbot.process_message,
                    inputs=[msg, chatbox],
                    outputs=[chatbox, metadata_box, rag_box]
                )
                msg.submit(
                    chatbot.process_message,
                    inputs=[msg, chatbox],
                    outputs=[chatbox, metadata_box, rag_box]
                )
                clear.click(lambda: ([], None, ""), outputs=[chatbox, metadata_box, rag_box])

            # Code Lookup Tab
            with gr.Tab("🔍 Code Lookup"):
                gr.Markdown("### Search Medical Codes")
                search_input = gr.Textbox(
                    label="Search by description",
                    placeholder="Enter keywords (e.g., 'diabetes', 'chest pain', 'office visit')"
                )
                search_btn = gr.Button("Search", variant="primary")
                search_results = gr.Markdown(label="Results")

                search_btn.click(
                    chatbot.search_codes,
                    inputs=[search_input],
                    outputs=[search_results]
                )

                gr.Markdown("### Direct Code Lookup")
                gr.Markdown("**Quick Reference:**")
                gr.Markdown("""
                - **ICD-10**: E11.9, I10, J44.0, N18.3, E78.5
                - **CPT**: 99213, 99214, 80053, 93000, 71046
                - **HCPCS**: J3301, G0438, A4253
                """)

            # Statistics Tab
            with gr.Tab("📈 Statistics"):
                gr.Markdown("### System Performance")
                stats_box = gr.JSON(label="Orchestrator Statistics")
                refresh_stats = gr.Button("Refresh Statistics")

                def get_stats_json():
                    return json.dumps(chatbot.get_statistics(), indent=2)

                refresh_stats.click(
                    get_stats_json,
                    outputs=[stats_box]
                )

            # Export Tab
            with gr.Tab("💾 Export"):
                gr.Markdown("### Export Conversation History")
                export_box = gr.Code(language="json", label="Conversation JSON")
                export_btn = gr.Button("Export", variant="primary")

                export_btn.click(
                    chatbot.export_conversation,
                    outputs=[export_box]
                )

            # Dashboard Info Tab
            with gr.Tab("📊 Dashboard Info"):
                gr.Markdown("""
                ## Integrated Dashboard API

                The FastAPI dashboard is running on port 5000 and provides the following endpoints:

                ### API Endpoints
                - **GET /api/health** - Health check
                - **GET /api/domains** - List all registered domains
                - **GET /api/models** - List all loaded models
                - **GET /api/metrics** - System metrics
                - **GET /api/requests** - Request history
                - **POST /api/query** - Process a query
                - **GET /api/rag/global** - Global RAG documents
                - **GET /api/rag/local/{domain_id}** - Local RAG for specific domain
                - **WS /ws/metrics** - WebSocket for real-time metrics

                ### Access Dashboard
                - Base URL: http://localhost:5000
                - Swagger Docs: http://localhost:5000/docs
                - Health Check: http://localhost:5000/api/health

                ### Testing with curl
                ```bash
                # Health check
                curl http://localhost:5000/api/health

                # List domains
                curl http://localhost:5000/api/domains

                # Process query
                curl -X POST http://localhost:5000/api/query \\
                  -H "Content-Type: application/json" \\
                  -d '{"query": "What is Type 2 diabetes?"}'
                ```
                """)

            # Help Tab
            with gr.Tab("❓ Help"):
                gr.Markdown("""
                ## How to Use

                ### Chat Interface
                - Type your medical question naturally
                - The system will automatically route to the best specialized domain
                - Use `/code <CODE>` for direct code lookup (e.g., `/code E11.9`)

                ### Example Queries

                **Clinical Diagnosis:**
                - "What are the differential diagnoses for chest pain?"
                - "Explain the symptoms of Type 2 diabetes"

                **Medical Coding:**
                - "What ICD-10 code should I use for hypertension?"
                - "Suggest CPT codes for a comprehensive metabolic panel"
                - "Help me write a medical necessity statement for a chest X-ray"

                **Biomedical Extraction:**
                - "Extract diagnoses and procedures from this clinical note: [paste note]"
                - "Summarize this radiology report"

                **Quick Medical Q&A:**
                - "What is hemoglobin A1c?"
                - "Explain what COPD means"

                ### System Features
                - **Hybrid Orchestration**: Simple queries use fast TinyBERT (<50ms), complex queries use Phi-2 reasoning
                - **Dual RAG**: Shared medical codes + domain-specific knowledge
                - **Multi-Domain**: 5 specialized medical SLMs working together (Ollama Cloud)
                - **Real-Time Stats**: Monitor performance and routing decisions
                - **Integrated Dashboard**: FastAPI endpoints for programmatic access

                ### Supported Domains (Ollama Cloud Models)
                1. **Clinical Diagnosis** (deepseek-v3.1:671b-cloud) - Diagnosis, symptoms, clinical reasoning
                2. **Medical Coding** (kimi-k2-thinking:cloud) - ICD/CPT/HCPCS codes, billing
                3. **Biomedical Extraction** (qwen3-coder:480b-cloud) - Text analysis, entity extraction
                4. **Radiology Support** (qwen3-vl:235b-instruct-cloud) - Radiology reports, imaging
                5. **Medical Q&A Lite** (gpt-oss:120b-cloud) - Quick definitions, simple questions
                """)

        gr.Markdown("""
        ---
        **Disclaimer**: This is an AI assistant for educational and support purposes only.
        Always consult licensed healthcare professionals for medical advice and actual diagnosis/treatment.
        """)

    return demo


# ============================================================================
# Main Application Runner
# ============================================================================

def run_fastapi_server():
    """Run FastAPI server in a separate thread"""
    uvicorn.run(
        api_app,
        host="0.0.0.0",
        port=5000,
        log_level="info"
    )


def main(
    enable_reasoning: bool = True,
    prefer_gpu: bool = False,
    share: bool = False
):
    """
    Launch both Gradio interface and FastAPI dashboard.

    Args:
        enable_reasoning: Enable Phi-2 hybrid reasoning
        prefer_gpu: Prefer GPU if available
        share: Create public Gradio link
    """
    global chatbot_instance

    # Fix Windows console encoding for Unicode (emojis)
    if sys.platform == 'win32':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except:
            pass  # Fallback silently if reconfigure not available

    print("\n" + "="*60)
    print("🏥 ENHANCED MEDICAL CHATBOT - INTEGRATED DASHBOARD")
    print("="*60)

    # Initialize chatbot (shared between Gradio and FastAPI)
    chatbot_instance = EnhancedMedicalChatbot(
        enable_reasoning=enable_reasoning,
        prefer_gpu=prefer_gpu
    )

    print(f"\n✓ Hybrid Reasoning: {'Enabled' if enable_reasoning else 'Disabled'}")
    print(f"✓ GPU Acceleration: {'Enabled' if prefer_gpu else 'Disabled (CPU only)'}")
    print(f"✓ Registered Domains: {len(chatbot_instance.domains)}")
    print(f"✓ Using Ollama Cloud Models")
    print("="*60)

    # Start FastAPI server in background thread
    print("\n[STARTING] FastAPI Dashboard Server on port 5000...")
    api_thread = threading.Thread(target=run_fastapi_server, daemon=True)
    api_thread.start()

    # Give FastAPI time to start
    import time
    time.sleep(2)

    print("✓ FastAPI Dashboard API: http://localhost:5000")
    print("✓ API Documentation: http://localhost:5000/docs")

    # Create and launch Gradio interface
    print("\n[STARTING] Gradio Chat Interface on port 7860...")
    demo = create_gradio_interface(chatbot_instance)

    print("\n" + "="*60)
    print("🚀 BOTH SERVERS RUNNING")
    print("="*60)
    print("Gradio Chat:     http://localhost:7860")
    print("Dashboard API:   http://localhost:5000")
    print("API Docs:        http://localhost:5000/docs")
    print("="*60 + "\n")

    demo.launch(
        share=share,
        server_name="0.0.0.0",
        server_port=7860
    )


if __name__ == "__main__":
    # Launch with default settings (using Ollama cloud models)
    main(
        enable_reasoning=True,  # Enable Phi-2 hybrid orchestration
        prefer_gpu=False,  # Use CPU by default (Ollama cloud handles computation)
        share=False  # Set to True to create public link
    )
