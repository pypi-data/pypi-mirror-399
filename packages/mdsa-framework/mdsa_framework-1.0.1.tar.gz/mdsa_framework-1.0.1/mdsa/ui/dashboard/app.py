"""
MDSA Framework Monitoring Dashboard

FastAPI-based real-time monitoring UI for Multi-Domain Specialized Agentic Orchestration framework.
Provides visualization of domains, models, RAG, metrics, and request flows.

Routes:
- GET /welcome - Landing page
- GET /monitor - Real-time monitoring dashboard
- GET /api/health - Health check
- GET /api/domains - List all domains
- GET /api/models - List loaded models
- GET /api/metrics - System metrics
- GET /api/requests - Request history
- POST /api/query - Process query through MDSA
- WS /ws/metrics - WebSocket for real-time metrics

Usage:
    python mdsa/ui/dashboard/app.py

Then open: http://localhost:9000/welcome
"""

import os
import sys
import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

# Load environment variables from .env file (if exists)
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent.parent.parent.parent / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        print(f"[INFO] Loaded environment variables from: {env_file}")
    else:
        print(f"[INFO] No .env file found at: {env_file}")
        print("[INFO] Using environment variables from system")
except ImportError:
    print("[WARN] python-dotenv not installed. Using system environment variables only.")
except Exception as e:
    print(f"[WARN] Could not load .env file: {e}")

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Response, File, Form, UploadFile
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.requests import Request
from pydantic import BaseModel
import uvicorn

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from mdsa.core.orchestrator import TinyBERTOrchestrator
from mdsa.config.ports import MDSA_DASHBOARD_PORT
from mdsa.domains.registry import DomainRegistry
from mdsa.models.loader import ModelLoader
from mdsa.memory.dual_rag import DualRAG
from mdsa.auth import (
    create_access_token,
    authenticate_user,
    get_current_user_from_cookie,
    require_auth,
    require_admin,
    session_manager
)

# Initialize logger
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="MDSA Monitoring Dashboard",
    description="Real-time monitoring and visualization for Multi-Domain Specialized Agentic Orchestration Framework",
    version="1.0.0"
)

# Setup templates and static files
BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Global MDSA instance (will be initialized on startup)
mdsa_orchestrator: Optional[TinyBERTOrchestrator] = None
domain_registry: Optional[DomainRegistry] = None
model_loader: Optional[ModelLoader] = None
dual_rag: Optional[DualRAG] = None

# Request history storage
request_history: List[Dict] = []
MAX_HISTORY = 1000

# Response cache for performance optimization
from functools import lru_cache
import hashlib

response_cache: Dict[str, Dict] = {}
CACHE_MAX_SIZE = 100

def cache_key(query: str, context: Optional[Dict] = None) -> str:
    """Generate cache key from query and context"""
    content = query + str(sorted(context.items()) if context else "")
    return hashlib.md5(content.encode()).hexdigest()

# WebSocket connections
active_connections: List[WebSocket] = []


# ============================================================================
# Pydantic Models
# ============================================================================

class QueryRequest(BaseModel):
    """Query request model"""
    query: str
    context: Optional[Dict] = None


class DomainInfo(BaseModel):
    """Domain information model"""
    domain_id: str
    model_name: str
    description: str
    keywords: List[str]
    status: str


class LoginRequest(BaseModel):
    """Login request model"""
    username: str
    password: str


class LoginResponse(BaseModel):
    """Login response model"""
    access_token: str
    token_type: str = "bearer"
    username: str


# ============================================================================
# Startup/Shutdown Events
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize MDSA components on startup"""
    global mdsa_orchestrator, domain_registry, model_loader, dual_rag

    # Fix Windows console encoding
    import sys
    if sys.platform == 'win32':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except:
            pass

    print("="*60)
    print("MDSA Monitoring Dashboard Starting...")
    print("="*60)

    try:
        # Initialize orchestrator (it creates its own internal components)
        mdsa_orchestrator = TinyBERTOrchestrator(
            enable_reasoning=True,
            complexity_threshold=0.3
        )

        # Access orchestrator's internal components for API endpoints
        domain_registry = mdsa_orchestrator.domains  # Access internal domain registry

        # Initialize DualRAG system for document management
        dual_rag = DualRAG(max_global_docs=10000, max_local_docs=1000)

        print("[OK] MDSA orchestrator initialized")
        print("[OK] DualRAG system initialized")
        print("[OK] Dashboard ready")
        print("\nAccess dashboard at: http://localhost:9000/welcome")
        print("="*60)

    except Exception as e:
        print(f"[ERROR] Initialization error: {e}")
        import traceback
        traceback.print_exc()


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("\nShutting down MDSA Dashboard...")


# ============================================================================
# WebSocket Manager
# ============================================================================

async def broadcast_metrics():
    """Broadcast metrics to all connected WebSocket clients"""
    while True:
        if active_connections:
            metrics = get_current_metrics()
            for connection in active_connections:
                try:
                    await connection.send_json(metrics)
                except:
                    active_connections.remove(connection)
        await asyncio.sleep(2)  # Update every 2 seconds


# ============================================================================
# Page Routes
# ============================================================================

@app.get("/", response_class=HTMLResponse)
@app.get("/welcome", response_class=HTMLResponse)
async def welcome_page(request: Request):
    """Landing page with framework overview"""
    # Get aggregated data from all registered apps
    domains_response = await list_domains()
    models_response = await list_models()
    rag_response = await get_rag_stats()
    metrics_response = await get_metrics()
    apps_response = await list_registered_apps()

    domains_list = domains_response.get('domains', [])

    stats = {
        "total_domains": domains_response.get('count', 0),
        "total_requests": metrics_response.get('total_requests', 0),
        "active_models": models_response.get('count', 0),
        "rag_documents": rag_response.get('total_documents', 0),
        "total_apps": apps_response.get('count', 0)
    }

    # Get registered apps for display
    apps_list = apps_response.get('apps', [])

    return templates.TemplateResponse(
        "welcome.html",
        {
            "request": request,
            "stats": stats,
            "domains": domains_list,
            "apps": apps_list
        }
    )


@app.get("/admin/monitor", response_class=HTMLResponse)
@require_auth()
async def admin_monitor_page(request: Request):
    """Real-time monitoring dashboard with visualizations (admin)"""
    user = get_current_user_from_cookie(request)
    return templates.TemplateResponse(
        "monitor.html",
        {"request": request, "user": user}
    )


@app.get("/monitor", response_class=RedirectResponse)
async def monitor_page_redirect():
    """Redirect /monitor to /admin/monitor"""
    return RedirectResponse(url="/admin/monitor", status_code=301)


@app.get("/admin/domains", response_class=HTMLResponse)
@require_auth()
async def admin_domains_page(request: Request):
    """Domains management UI page (admin)"""
    user = get_current_user_from_cookie(request)
    domains_response = await list_domains()
    domains_list = domains_response.get('domains', [])

    return templates.TemplateResponse(
        "domains.html",
        {
            "request": request,
            "user": user,
            "domains": domains_list,
            "count": domains_response.get('count', 0)
        }
    )


@app.get("/domains", response_class=RedirectResponse)
async def domains_page_redirect():
    """Redirect /domains to /admin/domains"""
    return RedirectResponse(url="/admin/domains", status_code=301)


@app.get("/models", response_class=RedirectResponse)
async def models_page_redirect():
    """Redirect /models to /admin/models"""
    return RedirectResponse(url="/admin/models", status_code=301)


@app.get("/rag", response_class=RedirectResponse)
async def rag_page_redirect():
    """Redirect /rag to /admin/rag"""
    return RedirectResponse(url="/admin/rag", status_code=301)


# ============================================================================
# Authentication Routes
# ============================================================================

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page"""
    # Check if already logged in
    user = get_current_user_from_cookie(request)
    if user:
        return RedirectResponse(url="/welcome", status_code=302)

    return templates.TemplateResponse(
        "login.html",
        {"request": request}
    )


@app.post("/api/auth/login", response_model=LoginResponse)
async def login(login_request: LoginRequest, response: Response):
    """
    Authenticate user and create session.

    Returns JWT token in response body and sets HTTP-only cookie.
    """
    user = authenticate_user(login_request.username, login_request.password)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    # Create JWT token
    access_token = create_access_token(
        data={
            "sub": user["username"],
            "username": user["username"],
            "role": user["role"],
            "name": user["name"]
        }
    )

    # Create session
    session_manager.create_session(user["username"], access_token)

    # Set HTTP-only cookie
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=28800,  # 8 hours
        samesite="lax"
    )

    return LoginResponse(
        access_token=access_token,
        username=user["username"]
    )


@app.post("/api/auth/logout")
async def logout(request: Request, response: Response):
    """Logout user and invalidate session."""
    user = get_current_user_from_cookie(request)

    if user:
        session_manager.invalidate_session(user.get("username"))

    # Clear cookie
    response.delete_cookie("access_token")

    return {"message": "Logged out successfully"}


@app.get("/api/auth/me")
async def get_current_user(request: Request):
    """Get current authenticated user info."""
    user = get_current_user_from_cookie(request)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated"
        )

    return user


# ============================================================================
# Admin Routes (Protected)
# ============================================================================

@app.get("/admin/rag", response_class=HTMLResponse)
@require_auth()
async def admin_rag_page(request: Request):
    """RAG management admin page (protected)"""
    # Get user from request state (set by require_auth decorator)
    user = get_current_user_from_cookie(request)

    # Get list of domains for local RAG selection
    domains_response = await list_domains()
    domain_names = [d['domain_id'] for d in domains_response.get('domains', [])]

    # Get RAG stats
    rag_response = await get_rag_stats()

    return templates.TemplateResponse(
        "admin_rag.html",
        {
            "request": request,
            "user": user,
            "domains": domain_names,
            "global_documents": rag_response.get('global_documents', 0),
            "local_documents": rag_response.get('local_documents', 0),
            "total_documents": rag_response.get('total_documents', 0)
        }
    )


@app.get("/api/admin/rag/documents")
@require_auth(redirect_to_login=False)
async def list_rag_documents(request: Request, source_filter: Optional[str] = None):
    """
    List all RAG documents from centralized RAG system (API endpoint)

    Args:
        source_filter: Optional filter - 'user', 'system', or None for all
    """
    if not dual_rag:
        logger.warning("[RAG Documents] DualRAG not initialized")
        return {
            "documents": [],
            "total_documents": 0,
            "global_documents": 0,
            "local_documents": 0
        }

    try:
        all_documents = []

        # Get global documents from centralized RAG
        logger.info(f"[RAG Documents] Fetching from global RAG: {len(dual_rag.global_rag._documents)} documents")
        for doc_id, doc in dual_rag.global_rag._documents.items():
            # Apply source filter if specified
            doc_source = doc.metadata.get('source', 'unknown')
            if source_filter and doc_source != source_filter:
                continue

            all_documents.append({
                'doc_id': doc_id,
                'content': doc.content[:500] + '...' if len(doc.content) > 500 else doc.content,  # Truncate for UI
                'full_content': doc.content,
                'metadata': doc.metadata,
                'type': 'global',
                'domain': None,
                'source': 'centralized_rag'
            })

        # Get local documents from centralized RAG
        for domain_id, local_rag in dual_rag.local_rags.items():
            logger.info(f"[RAG Documents] Fetching from domain '{domain_id}': {len(local_rag._documents)} documents")
            for doc_id, doc in local_rag._documents.items():
                # Apply source filter if specified
                doc_source = doc.metadata.get('source', 'unknown')
                if source_filter and doc_source != source_filter:
                    continue

                all_documents.append({
                    'doc_id': doc_id,
                    'content': doc.content[:500] + '...' if len(doc.content) > 500 else doc.content,  # Truncate for UI
                    'full_content': doc.content,
                    'metadata': doc.metadata,
                    'type': 'local',
                    'domain': domain_id,
                    'source': 'centralized_rag'
                })

        filter_msg = f" (filtered by source={source_filter})" if source_filter else ""
        logger.info(f"[RAG Documents] Returning {len(all_documents)} total documents{filter_msg}")

        return {
            "documents": all_documents,
            "total_documents": len(all_documents),
            "global_documents": len(dual_rag.global_rag._documents),
            "local_documents": sum(len(rag._documents) for rag in dual_rag.local_rags.values())
        }

    except Exception as e:
        logger.error(f"[RAG Documents] Error fetching documents: {e}", exc_info=True)
        return {
            "documents": [],
            "total_documents": 0,
            "global_documents": 0,
            "local_documents": 0,
            "error": str(e)
        }


@app.post("/api/admin/rag/upload")
@require_admin()
async def upload_rag_document(
    request: Request,
    file: UploadFile = File(...),
    rag_type: str = Form(...),
    domain: Optional[str] = Form(None)
):
    """
    Upload a document to RAG with disk persistence and ChromaDB integration.

    Supports: TXT, PDF, DOCX, MD, CSV, XLSX files
    """
    from mdsa.config.platform_detector import detect_platform_kb_path, create_rag_subdirectories
    from mdsa.utils.file_extractors import extract_text_from_file, is_supported_file
    import aiofiles
    import uuid
    from datetime import datetime

    try:
        # Validate file type
        if not is_supported_file(file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Supported: TXT, PDF, DOCX, MD, CSV, XLSX"
            )

        # Validate RAG type
        if rag_type not in ['global', 'local']:
            raise HTTPException(status_code=400, detail="rag_type must be 'global' or 'local'")

        # Validate domain for local RAG
        if rag_type == 'local' and not domain:
            raise HTTPException(status_code=400, detail="domain is required for local RAG")

        # Read file content
        file_content = await file.read()

        # Extract text from file
        text_content = extract_text_from_file(file_content, file.filename)
        if not text_content:
            raise HTTPException(
                status_code=400,
                detail=f"Could not extract text from {file.filename}"
            )

        # Detect knowledge base path
        kb_path = detect_platform_kb_path()
        create_rag_subdirectories(kb_path)

        # Determine save directory
        if rag_type == 'global':
            save_dir = kb_path / 'global'
        else:
            save_dir = kb_path / 'local' / domain
        save_dir.mkdir(parents=True, exist_ok=True)

        # Generate unique filename to avoid collisions
        file_stem = Path(file.filename).stem
        file_ext = Path(file.filename).suffix
        unique_filename = f"{file_stem}_{uuid.uuid4().hex[:8]}{file_ext}"
        file_path = save_dir / unique_filename

        # Save file to disk
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)

        # Prepare metadata
        metadata = {
            'source': 'user',  # Tag user uploads vs system documents
            'filename': file.filename,
            'original_filename': file.filename,
            'saved_filename': unique_filename,
            'file_path': str(file_path),
            'file_size': len(file_content),
            'file_type': file_ext,
            'upload_time': datetime.now().isoformat(),
            'rag_type': rag_type
        }

        if rag_type == 'local':
            metadata['domain'] = domain

        # Add to RAG system (with ChromaDB persistence)
        if rag_type == 'global':
            doc_id = dual_rag.add_to_global(
                content=text_content,
                metadata=metadata,
                tags=[file_ext.replace('.', '')]
            )
        else:
            # Ensure domain is registered
            if domain not in dual_rag.local_rags:
                dual_rag.register_domain(domain)

            doc_id = dual_rag.add_to_local(
                domain_id=domain,
                content=text_content,
                metadata=metadata
            )

        logger.info(
            f"[RAG Upload] {rag_type.upper()} document uploaded: {file.filename} "
            f"-> {doc_id} (saved to {file_path})"
        )

        return {
            "success": True,
            "doc_id": doc_id,
            "filename": file.filename,
            "saved_as": unique_filename,
            "file_path": str(file_path),
            "rag_type": rag_type,
            "domain": domain if rag_type == 'local' else None,
            "text_length": len(text_content),
            "persisted_to_chromadb": dual_rag.chroma_client is not None
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[RAG Upload] Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


class DeleteDocumentRequest(BaseModel):
    """Delete document request model"""
    type: str  # 'global' or 'local'
    domain: Optional[str] = None


@app.delete("/api/admin/rag/document/{doc_id}")
@require_admin()
async def delete_rag_document(request: Request, doc_id: str, delete_request: DeleteDocumentRequest):
    """Delete a document from RAG"""
    from mdsa.core.app_registry import get_registry
    import requests

    registry = get_registry()
    apps = registry.list_apps()

    if not apps:
        raise HTTPException(status_code=400, detail="No MDSA applications registered")

    # Try to delete from all apps (in case document exists in multiple)
    deleted = False
    for app in apps:
        try:
            delete_url = f"{app['endpoint']}/api/rag/document/{doc_id}"

            response = requests.delete(
                delete_url,
                json=delete_request.dict(),
                timeout=5
            )

            if response.status_code == 200:
                deleted = True

        except Exception as e:
            print(f"[WARN] Error deleting from {app['name']}: {e}")
            continue

    if deleted:
        return {"message": "Document deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Document not found or could not be deleted")


@app.get("/admin/models", response_class=HTMLResponse)
@require_auth()
async def admin_models_page(request: Request):
    """Model configuration admin page (protected)"""
    user = get_current_user_from_cookie(request)

    # Get current configuration
    config_path = Path(__file__).parent.parent.parent / "config" / "mdsa_config.json"

    # Default config
    config = {
        "reasoning_model": "microsoft/phi-2",
        "complexity_threshold": 0.2,
        "enable_reasoning": True
    }

    # Load existing config if available
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                saved_config = json.load(f)
                config.update(saved_config.get('orchestration', {}))
        except Exception as e:
            print(f"[WARN] Error loading config: {e}")

    # Get list of domains
    domains_response = await list_domains()
    domains_list = domains_response.get('domains', [])

    return templates.TemplateResponse(
        "admin_models.html",
        {
            "request": request,
            "user": user,
            "config": config,
            "config_json": json.dumps(config),
            "domains_json": json.dumps(domains_list)
        }
    )


class ModelConfigRequest(BaseModel):
    """Model configuration request"""
    orchestration: Dict[str, Any]
    domain_models: Dict[str, str]


@app.post("/api/admin/models/config")
@require_admin()
async def save_model_config(request: Request, config_request: ModelConfigRequest):
    """Save model configuration to file"""
    config_dir = Path(__file__).parent.parent.parent / "config"
    config_dir.mkdir(exist_ok=True)

    config_path = config_dir / "mdsa_config.json"

    # Load existing config or create new
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
    else:
        config = {}

    # Update orchestration settings
    config['orchestration'] = config_request.orchestration

    # Update domain models
    if 'domain_models' not in config:
        config['domain_models'] = {}
    config['domain_models'].update(config_request.domain_models)

    # Save to file
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

    return {
        "message": "Configuration saved successfully",
        "config_path": str(config_path)
    }


@app.post("/api/admin/models/config/reset")
@require_admin()
async def reset_model_config(request: Request):
    """Reset model configuration to defaults"""
    config_dir = Path(__file__).parent.parent.parent / "config"
    config_path = config_dir / "mdsa_config.json"

    # Default configuration
    default_config = {
        "orchestration": {
            "orchestrator_model": "google/bert_uncased_L-2_H-128_A-2",
            "reasoning_model": "microsoft/phi-2",
            "complexity_threshold": 0.2,
            "enable_reasoning": True
        },
        "domain_models": {}
    }

    # Save default config
    config_dir.mkdir(exist_ok=True)
    with open(config_path, 'w') as f:
        json.dump(default_config, f, indent=2)

    return {
        "message": "Configuration reset to defaults",
        "config": default_config
    }


@app.post("/api/admin/reload-config")
@require_admin()
async def reload_configuration(request: Request):
    """Reload configuration from mdsa_config.json without restarting"""
    global mdsa_orchestrator, domain_registry

    try:
        # Path to config file
        config_path = Path(__file__).parent.parent.parent / "config" / "mdsa_config.json"

        if not config_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Configuration file not found: {config_path}"
            )

        # Load config file
        with open(config_path, 'r') as f:
            config = json.load(f)

        # Reload domains in orchestrator
        if mdsa_orchestrator:
            # Clear existing domains
            mdsa_orchestrator.domains.clear()
            mdsa_orchestrator.router.domains.clear()

            # Register domains from config
            domains = config.get('domains', [])
            for domain in domains:
                if domain.get('enabled', True):
                    mdsa_orchestrator.register_domain(
                        name=domain['domain_id'],
                        description=domain.get('description', ''),
                        keywords=domain.get('keywords', [])
                    )

            logger.info(f"[Config Reload] Reloaded {len(domains)} domains from configuration")

            return {
                "success": True,
                "message": f"Configuration reloaded successfully",
                "domains_loaded": len(domains),
                "config_path": str(config_path)
            }
        else:
            raise HTTPException(
                status_code=503,
                detail="Orchestrator not initialized"
            )

    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid JSON in configuration file: {str(e)}"
        )
    except Exception as e:
        logger.error(f"[Config Reload] Error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reload configuration: {str(e)}"
        )


@app.post("/api/admin/generate-demo-data")
@require_admin()
async def generate_demo_data(request: Request):
    """Generate sample query history for chart visualization"""
    global request_history
    import random
    from datetime import datetime, timedelta

    try:
        # Clear existing history
        request_history.clear()

        # Get domains for demo data
        domains = ['clinical_diagnosis', 'medical_coding', 'biomedical_text', 'medical_qa', 'radiology']

        # Generate 30 sample requests over the past 24 hours
        now = datetime.now()
        for i in range(30):
            timestamp = now - timedelta(hours=random.randint(0, 24))

            sample_entry = {
                "timestamp": timestamp.isoformat(),
                "query": f"Sample query {i+1}",
                "domain": random.choice(domains),
                "status": "success" if random.random() > 0.1 else "failed",
                "latency_ms": random.uniform(50, 250),
                "response_preview": f"This is a sample response for query {i+1}..."
            }

            request_history.append(sample_entry)

        # Sort by timestamp
        request_history.sort(key=lambda x: x['timestamp'])

        logger.info(f"[Demo Data] Generated {len(request_history)} sample requests")

        return {
            "success": True,
            "generated": len(request_history),
            "message": f"Generated {len(request_history)} sample queries for visualization"
        }

    except Exception as e:
        logger.error(f"[Demo Data] Error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate demo data: {str(e)}"
        )


@app.get("/admin/tools", response_class=HTMLResponse)
@require_auth()
async def admin_tools_page(request: Request):
    """Tool management admin page (protected)"""
    user = get_current_user_from_cookie(request)

    return templates.TemplateResponse(
        "admin_tools.html",
        {
            "request": request,
            "user": user
        }
    )


class ToolCreateRequest(BaseModel):
    """Tool creation/update request"""
    name: str
    type: str
    endpoint: str
    api_key: str
    description: Optional[str] = ""
    params: Optional[Dict[str, Any]] = {}
    enabled: bool = True


class ToolToggleRequest(BaseModel):
    """Tool toggle request"""
    enabled: bool


@app.get("/api/admin/tools")
@require_auth(redirect_to_login=False)
async def list_tools_api(request: Request):
    """List all tools (API endpoint)"""
    from mdsa.tools import get_tool_manager

    tool_manager = get_tool_manager()
    tools = tool_manager.list_tools()

    # Return tool data without decrypted API keys
    return {
        "tools": [tool.to_dict(include_key=False) for tool in tools],
        "count": len(tools)
    }


@app.post("/api/admin/tools")
@require_admin()
async def create_tool(request: Request, tool_request: ToolCreateRequest):
    """Create a new tool"""
    from mdsa.tools import get_tool_manager

    tool_manager = get_tool_manager()

    tool = tool_manager.add_tool(
        name=tool_request.name,
        type=tool_request.type,
        endpoint=tool_request.endpoint,
        api_key=tool_request.api_key,
        description=tool_request.description,
        params=tool_request.params,
        enabled=tool_request.enabled
    )

    return {
        "message": "Tool created successfully",
        "tool": tool.to_dict(include_key=False)
    }


@app.put("/api/admin/tools/{tool_id}")
@require_admin()
async def update_tool(request: Request, tool_id: str, tool_request: ToolCreateRequest):
    """Update an existing tool"""
    from mdsa.tools import get_tool_manager

    tool_manager = get_tool_manager()

    try:
        tool = tool_manager.update_tool(
            tool_id=tool_id,
            name=tool_request.name,
            type=tool_request.type,
            endpoint=tool_request.endpoint,
            api_key=tool_request.api_key if tool_request.api_key != '••••••••••••' else None,
            description=tool_request.description,
            params=tool_request.params,
            enabled=tool_request.enabled
        )

        return {
            "message": "Tool updated successfully",
            "tool": tool.to_dict(include_key=False)
        }
    except KeyError:
        raise HTTPException(status_code=404, detail="Tool not found")


@app.delete("/api/admin/tools/{tool_id}")
@require_admin()
async def delete_tool(request: Request, tool_id: str):
    """Delete a tool"""
    from mdsa.tools import get_tool_manager

    tool_manager = get_tool_manager()

    if tool_manager.delete_tool(tool_id):
        return {"message": "Tool deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Tool not found")


@app.post("/api/admin/tools/{tool_id}/toggle")
@require_admin()
async def toggle_tool(request: Request, tool_id: str, toggle_request: ToolToggleRequest):
    """Enable or disable a tool"""
    from mdsa.tools import get_tool_manager

    tool_manager = get_tool_manager()

    try:
        tool = tool_manager.toggle_tool(tool_id, toggle_request.enabled)
        return {
            "message": f"Tool {'enabled' if toggle_request.enabled else 'disabled'} successfully",
            "tool": tool.to_dict(include_key=False)
        }
    except KeyError:
        raise HTTPException(status_code=404, detail="Tool not found")


@app.post("/api/admin/tools/{tool_id}/test")
@require_admin()
async def test_tool(request: Request, tool_id: str):
    """
    Test a tool by executing it with test parameters.
    For Weather API: tests with city="London"
    """
    import requests
    import os
    from pathlib import Path

    try:
        # Load tool configuration
        config_path = Path(__file__).parent.parent.parent / "config" / "mdsa_config.json"
        with open(config_path, 'r') as f:
            config = json.load(f)

        # Find the tool
        tool = None
        for t in config.get('tools', []):
            if t.get('tool_id') == tool_id:
                tool = t
                break

        if not tool:
            raise HTTPException(status_code=404, detail=f"Tool '{tool_id}' not found")

        if not tool.get('enabled', False):
            raise HTTPException(status_code=400, detail=f"Tool '{tool_id}' is disabled. Enable it first.")

        # Get API key from environment
        api_key = None
        if tool.get('requires_api_key', False):
            api_key_var = tool.get('api_key_env_var')
            if api_key_var:
                api_key = os.environ.get(api_key_var)
                if not api_key:
                    raise HTTPException(
                        status_code=400,
                        detail=f"API key not found. Set environment variable: {api_key_var}"
                    )

        # Build request parameters
        params = tool.get('params', {}).copy()
        params.update(tool.get('test_params', {}))
        if api_key:
            params['appid'] = api_key

        # Make API request
        endpoint = tool.get('endpoint')
        method = tool.get('method', 'GET').upper()

        if method == 'GET':
            response = requests.get(endpoint, params=params, timeout=10)
        else:
            response = requests.post(endpoint, json=params, timeout=10)

        # Return results
        return {
            "success": response.status_code == 200,
            "status_code": response.status_code,
            "tool_id": tool_id,
            "tool_name": tool.get('name'),
            "endpoint": endpoint,
            "params_used": {k: v for k, v in params.items() if k != 'appid'},  # Hide API key
            "response": response.json() if response.status_code == 200 else response.text,
            "message": "Tool test successful!" if response.status_code == 200 else f"API returned status {response.status_code}"
        }

    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Network error: {str(e)}",
            "message": "Failed to connect to API endpoint"
        }
    except Exception as e:
        logger.error(f"Tool test error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# API Routes
# ============================================================================

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "components": {
            "orchestrator": mdsa_orchestrator is not None,
            "domain_registry": domain_registry is not None,
            "model_loader": False,  # Not exposed by orchestrator
            "dual_rag": False  # Not exposed by orchestrator
        }
    }


@app.get("/api/apps")
async def list_registered_apps():
    """List all registered MDSA applications"""
    from mdsa.core.app_registry import get_registry

    registry = get_registry()
    apps = registry.list_apps()

    # Check health status of each app
    apps_with_status = []
    for app in apps:
        health_status = registry.check_health(app['app_id'])
        app_info = {
            **app,
            'health_status': health_status['status'],
            'response_time_ms': health_status.get('response_time_ms', 0)
        }
        apps_with_status.append(app_info)

    return {
        "apps": apps_with_status,
        "count": len(apps_with_status)
    }


@app.get("/api/domains")
async def list_domains():
    """List all configured domains from mdsa_config.json"""
    from pathlib import Path
    import json

    all_domains = []

    # Load domains from config file
    config_path = Path(__file__).parent.parent.parent / "config" / "mdsa_config.json"
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                configured_domains = config.get('domains', [])

                for domain in configured_domains:
                    all_domains.append({
                        "domain_id": domain.get('domain_id'),
                        "name": domain.get('name'),
                        "description": domain.get('description', ''),
                        "model": domain.get('model', ''),
                        "keywords": domain.get('keywords', []),
                        "enabled": domain.get('enabled', True),
                        "rag_enabled": domain.get('rag_enabled', False),
                        "app_name": "MDSA Dashboard",
                        "app_id": "dashboard"
                    })

                logger.info(f"[API] Loaded {len(all_domains)} domains from config")
        except Exception as e:
            logger.error(f"[API] Error loading domains from config: {e}")

    # Fallback to orchestrator if config not available
    if not all_domains and mdsa_orchestrator:
        for domain_id, config in mdsa_orchestrator.domains.items():
            all_domains.append({
                "domain_id": domain_id,
                "name": domain_id.replace('_', ' ').title(),
                "description": config.get('description', 'No description'),
                "keywords": config.get('keywords', []),
                "enabled": True,
                "rag_enabled": False,
                "app_name": "Local Dashboard",
                "app_id": "local"
            })

    return {"domains": all_domains, "count": len(all_domains)}


@app.get("/api/models")
async def list_models():
    """List all loaded models from all MDSA apps"""
    from mdsa.core.app_registry import get_registry
    import requests

    registry = get_registry()
    apps = registry.list_apps()

    all_models = []
    seen_models = {}

    # Fetch models from each registered app
    for app in apps:
        try:
            models_url = f"{app['endpoint']}/api/models"
            response = requests.get(models_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = data.get('models', [])
                for model in models:
                    model_name = model.get('model_name', 'unknown')
                    if model_name not in seen_models:
                        seen_models[model_name] = {
                            "model_name": model_name,
                            "device": model.get('device', 'cpu'),
                            "domains_using": model.get('domains_using', []),
                            "apps_using": [app['name']]
                        }
                    else:
                        seen_models[model_name]['apps_using'].append(app['name'])
        except Exception as e:
            print(f"Failed to fetch models from {app['name']}: {e}")
            continue

    all_models = list(seen_models.values())

    # Fallback to local orchestrator if no apps registered
    if not all_models and mdsa_orchestrator:
        seen_local = set()
        for _, config in mdsa_orchestrator.domains.items():
            model_name = config.get('model_name', 'unknown')
            if model_name not in seen_local:
                seen_local.add(model_name)
                all_models.append({
                    "model_name": model_name,
                    "device": config.get('device', 'cpu'),
                    "domains_using": [d for d, c in mdsa_orchestrator.domains.items() if c.get('model_name') == model_name],
                    "apps_using": ["Local Dashboard"]
                })

    return {
        "models": all_models,
        "count": len(all_models)
    }


@app.get("/api/rag")
async def get_rag_stats():
    """Get RAG statistics from all MDSA apps"""
    from mdsa.core.app_registry import get_registry
    import requests

    registry = get_registry()
    apps = registry.list_apps()

    total_global_docs = 0
    total_local_docs = 0
    domains_with_rag = []

    # Fetch RAG stats from each registered app
    for app in apps:
        try:
            # Try to get RAG stats (custom endpoint for medical chatbot)
            metrics_url = f"{app['endpoint']}/api/metrics"
            response = requests.get(metrics_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                rag_info = data.get('rag', {})
                total_global_docs += rag_info.get('global_documents', 0)
                total_local_docs += rag_info.get('local_documents', 0)

                # Get domains with RAG
                domains_url = f"{app['endpoint']}/api/domains"
                domains_resp = requests.get(domains_url, timeout=5)
                if domains_resp.status_code == 200:
                    domains_data = domains_resp.json()
                    for domain in domains_data.get('domains', []):
                        domains_with_rag.append({
                            'domain': domain.get('domain_id', 'unknown'),
                            'app': app['name']
                        })
        except Exception as e:
            print(f"Failed to fetch RAG stats from {app['name']}: {e}")
            continue

    return {
        "global_documents": total_global_docs,
        "local_documents": total_local_docs,
        "total_documents": total_global_docs + total_local_docs,
        "domains_with_rag": domains_with_rag,
        "rag_enabled": total_global_docs > 0 or total_local_docs > 0
    }


# ============================================================================
# CENTRALIZED RAG API ENDPOINTS (Platform-Agnostic)
# ============================================================================

@app.post("/api/rag/query")
async def query_rag(
    query: str,
    domain_id: str = "general",
    top_k: int = 5,
    search_local: bool = True,
    search_global: bool = True
):
    """
    Query the centralized RAG system (accessible by all platforms).

    This endpoint allows any registered application to query the shared RAG.
    """
    if not dual_rag:
        raise HTTPException(status_code=503, detail="RAG system not initialized")

    try:
        # Register domain if not exists
        if domain_id not in dual_rag.local_rags:
            dual_rag.register_domain(domain_id)

        # Query RAG
        results = dual_rag.retrieve(
            query=query,
            domain_id=domain_id,
            top_k=top_k,
            search_local=search_local,
            search_global=search_global
        )

        # Convert results to serializable format
        response = {}
        if 'local' in results:
            response['local'] = {
                'documents': [
                    {
                        'doc_id': doc.doc_id,
                        'content': doc.content,
                        'metadata': doc.metadata
                    }
                    for doc in results['local'].documents
                ],
                'scores': results['local'].scores,
                'retrieval_time_ms': results['local'].retrieval_time_ms
            }

        if 'global' in results:
            response['global'] = {
                'documents': [
                    {
                        'doc_id': doc.doc_id,
                        'content': doc.content,
                        'metadata': doc.metadata
                    }
                    for doc in results['global'].documents
                ],
                'scores': results['global'].scores,
                'retrieval_time_ms': results['global'].retrieval_time_ms
            }

        return response

    except Exception as e:
        logger.error(f"[RAG Query] Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/rag/documents/all")
async def get_all_rag_documents():
    """
    Get all RAG documents from the centralized system.

    Returns all documents from both global and local RAGs.
    """
    if not dual_rag:
        raise HTTPException(status_code=503, detail="RAG system not initialized")

    try:
        all_docs = []

        # Get global documents
        for doc_id, doc in dual_rag.global_rag._documents.items():
            all_docs.append({
                'doc_id': doc_id,
                'content': doc.content,
                'metadata': doc.metadata,
                'type': 'global',
                'domain': None
            })

        # Get local documents
        for domain_id, local_rag in dual_rag.local_rags.items():
            for doc_id, doc in local_rag._documents.items():
                all_docs.append({
                    'doc_id': doc_id,
                    'content': doc.content,
                    'metadata': doc.metadata,
                    'type': 'local',
                    'domain': domain_id
                })

        return {
            'documents': all_docs,
            'count': len(all_docs),
            'global_count': len(dual_rag.global_rag._documents),
            'local_count': sum(len(rag._documents) for rag in dual_rag.local_rags.values())
        }

    except Exception as e:
        logger.error(f"[RAG Documents] Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/rag/stats")
async def get_centralized_rag_stats():
    """
    Get statistics from the centralized RAG system.
    """
    if not dual_rag:
        return {
            'initialized': False,
            'global_documents': 0,
            'local_documents': 0,
            'total_documents': 0,
            'chromadb_enabled': False
        }

    try:
        stats = dual_rag.get_stats()

        return {
            'initialized': True,
            'global_documents': stats['global_rag']['document_count'],
            'local_documents': sum(
                rag_stats['document_count']
                for rag_stats in stats['local_rags'].values()
            ),
            'total_documents': stats['global_rag']['document_count'] + sum(
                rag_stats['document_count']
                for rag_stats in stats['local_rags'].values()
            ),
            'chromadb_enabled': dual_rag.chroma_client is not None,
            'vector_db_path': str(dual_rag.vector_db_path) if dual_rag.vector_db_path else None,
            'domains': list(stats['local_rags'].keys()),
            'detailed_stats': stats
        }
    except Exception as e:
        logger.error(f"[RAG Stats] Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/metrics")
async def get_metrics():
    """Get aggregated system metrics from all MDSA apps"""
    from mdsa.core.app_registry import get_registry
    import requests

    registry = get_registry()
    apps = registry.list_apps()

    aggregated_metrics = {
        "total_apps": len(apps),
        "total_domains": 0,
        "total_requests": 0,
        "total_models": 0,
        "rag_documents": 0,
        "apps_detail": []
    }

    # Fetch metrics from each app
    for app in apps:
        try:
            metrics_url = f"{app['endpoint']}/api/metrics"
            response = requests.get(metrics_url, timeout=5)
            if response.status_code == 200:
                data = response.json()

                # Handle different metric structures
                # Medical chatbot returns: {"domains": {"total": 5}, "requests": {"total": 0}, ...}
                domains_count = 0
                if isinstance(data.get('domains'), dict):
                    domains_count = data['domains'].get('total', 0)
                elif isinstance(data.get('domains'), int):
                    domains_count = data.get('domains', 0)

                requests_count = 0
                if isinstance(data.get('requests'), dict):
                    requests_count = data['requests'].get('total', 0)
                elif isinstance(data.get('requests'), int):
                    requests_count = data.get('requests', 0)
                elif isinstance(data.get('total_requests'), int):
                    requests_count = data.get('total_requests', 0)

                rag_docs = 0
                rag_info = data.get('rag', {})
                if isinstance(rag_info, dict):
                    rag_docs = rag_info.get('global_documents', 0) + rag_info.get('local_documents', 0)

                app_metrics = {
                    "app_name": app['name'],
                    "domains": domains_count,
                    "requests": requests_count,
                    "models": data.get('models', {}).get('count', 0) if isinstance(data.get('models'), dict) else 0,
                    "rag_docs": rag_docs
                }
                aggregated_metrics['apps_detail'].append(app_metrics)
                aggregated_metrics['total_domains'] += app_metrics['domains']
                aggregated_metrics['total_requests'] += app_metrics['requests']
                aggregated_metrics['rag_documents'] += app_metrics['rag_docs']
        except Exception as e:
            print(f"Failed to fetch metrics from {app['name']}: {e}")
            continue

    # Get unique models count
    models_response = await list_models()
    aggregated_metrics['total_models'] = models_response.get('count', 0)

    # Fallback to local metrics if no apps
    if not apps:
        local_metrics = get_current_metrics()
        aggregated_metrics.update({
            "total_domains": local_metrics.get('domains', 0),
            "total_requests": local_metrics.get('total_requests', 0),
            "rag_documents": 0
        })

    return aggregated_metrics


@app.get("/api/requests")
async def get_requests(limit: int = 100):
    """Get request history"""
    return {
        "requests": request_history[-limit:],
        "total": len(request_history),
        "limit": limit
    }


@app.post("/api/requests/track")
async def track_request(tracking_data: Dict):
    """
    Receive request tracking data from registered applications.

    This endpoint allows external apps (like the medical chatbot) to send
    their request data to the dashboard for centralized monitoring.

    Args:
        tracking_data: Dictionary containing request metadata

    Returns:
        Status confirmation
    """
    global request_history

    try:
        request_history.append({
            "timestamp": tracking_data.get("timestamp", datetime.now().isoformat()),
            "query": tracking_data.get("query", ""),
            "domain": tracking_data.get("domain", "unknown"),
            "status": tracking_data.get("status", "unknown"),
            "latency_ms": tracking_data.get("latency_ms", 0),
            "response_preview": tracking_data.get("response_preview", "")[:100],
            "app_id": tracking_data.get("app_id", "unknown")
        })

        # Limit history size to prevent memory issues
        if len(request_history) > 1000:
            request_history.pop(0)

        logger.debug(f"[Track] Received request from {tracking_data.get('app_id')}: {tracking_data.get('query', '')[:50]}")

        return {"status": "tracked", "history_size": len(request_history)}

    except Exception as e:
        logger.error(f"Failed to track request: {e}")
        raise HTTPException(status_code=500, detail=f"Tracking failed: {str(e)}")


@app.post("/api/query")
async def process_query(query_request: QueryRequest):
    """Process a query through MDSA with caching for performance"""
    if not mdsa_orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    # Check cache for repeated queries
    cache_k = cache_key(query_request.query, query_request.context)
    if cache_k in response_cache:
        cached = response_cache[cache_k]
        logger.info(f"[Cache Hit] Returning cached response for query: {query_request.query[:50]}...")
        return cached

    start_time = datetime.now()

    try:
        # Process query
        result = mdsa_orchestrator.process_request(
            query=query_request.query,
            context=query_request.context
        )

        # Calculate latency
        latency_ms = (datetime.now() - start_time).total_seconds() * 1000

        # Store in history
        history_entry = {
            "timestamp": start_time.isoformat(),
            "query": query_request.query,
            "domain": result.get('domain', 'unknown'),
            "status": result.get('status', 'unknown'),
            "latency_ms": latency_ms,
            "response_preview": result.get('response', '')[:100]
        }
        request_history.append(history_entry)
        if len(request_history) > MAX_HISTORY:
            request_history.pop(0)

        # Cache successful responses
        if result.get('status') == 'success':
            if len(response_cache) >= CACHE_MAX_SIZE:
                # Remove oldest entry (simple FIFO)
                response_cache.pop(next(iter(response_cache)))
            response_cache[cache_k] = result
            logger.debug(f"[Cache] Stored response for query: {query_request.query[:50]}...")

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/visualization-data")
async def get_visualization_data():
    """Get data formatted for D3.js visualizations"""
    if not mdsa_orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    # Analyze request history for visualizations
    domain_stats = {}
    latency_data = {}
    timeline_buckets = {}

    for req in request_history:
        domain = req.get('domain', 'unknown')
        latency = req.get('latency_ms', 0)
        timestamp = req.get('timestamp', '')
        status = req.get('status', 'unknown')

        # Domain statistics
        if domain not in domain_stats:
            domain_stats[domain] = {
                'requests': 0,
                'successes': 0,
                'latencies': []
            }

        domain_stats[domain]['requests'] += 1
        domain_stats[domain]['latencies'].append(latency)
        if status == 'success':
            domain_stats[domain]['successes'] += 1

        # Latency heatmap data (by hour)
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp)
                hour_bucket = dt.strftime('%H:00')
                if hour_bucket not in latency_data:
                    latency_data[hour_bucket] = {}
                if domain not in latency_data[hour_bucket]:
                    latency_data[hour_bucket][domain] = []
                latency_data[hour_bucket][domain].append(latency)
            except:
                pass

        # Timeline data (by minute)
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp)
                minute_bucket = dt.strftime('%H:%M')
                timeline_buckets[minute_bucket] = timeline_buckets.get(minute_bucket, 0) + 1
            except:
                pass

    # Format Sankey data
    sankey_domains = []
    for domain, stats in domain_stats.items():
        sankey_domains.append({
            'name': domain,
            'requests': stats['requests'],
            'success_rate': stats['successes'] / stats['requests'] if stats['requests'] > 0 else 0
        })

    # Format heatmap data
    all_domains = list(domain_stats.keys())
    time_buckets = sorted(list(latency_data.keys()))[-12:]  # Last 12 hours

    heatmap_matrix = []
    for domain in all_domains:
        row = []
        for bucket in time_buckets:
            latencies = latency_data.get(bucket, {}).get(domain, [])
            avg_latency = sum(latencies) / len(latencies) if latencies else 0
            row.append(avg_latency)
        heatmap_matrix.append(row)

    # Format RAG data (RAG not exposed by orchestrator)
    global_docs = 0
    local_docs = {}

    # Format timeline data
    timeline_data = [
        {'timestamp': datetime.now().replace(hour=int(t.split(':')[0]), minute=int(t.split(':')[1])).isoformat(), 'count': count}
        for t, count in sorted(timeline_buckets.items())[-20:]  # Last 20 minutes
    ]

    # Format pie chart data
    pie_data = [
        {'domain': domain, 'requests': stats['requests']}
        for domain, stats in domain_stats.items()
    ]

    return {
        "sankey": {
            "domains": sankey_domains,
            "total_requests": len(request_history)
        },
        "heatmap": {
            "domains": all_domains,
            "time_buckets": time_buckets,
            "latencies": heatmap_matrix
        },
        "rag": {
            "global_docs": global_docs,
            "local_docs": local_docs
        },
        "timeline": {
            "timeline": timeline_data
        },
        "pie": pie_data
    }


# ============================================================================
# WebSocket Route
# ============================================================================

@app.websocket("/ws/metrics")
async def metrics_websocket(websocket: WebSocket):
    """WebSocket endpoint for real-time metrics streaming"""
    await websocket.accept()
    active_connections.append(websocket)

    try:
        while True:
            # Keep connection alive and send aggregated metrics every 2 seconds
            # Use aggregated metrics from all registered apps
            aggregated = await get_metrics()

            # Format for monitor page compatibility
            metrics = {
                "timestamp": datetime.now().isoformat(),
                "domains": {
                    "total": aggregated.get('total_domains', 0),
                    "active": aggregated.get('total_domains', 0)
                },
                "requests": {
                    "total": aggregated.get('total_requests', 0),
                    "recent": 0
                },
                "models": {
                    "total": aggregated.get('total_models', 0)
                },
                "rag": {
                    "global_documents": aggregated.get('rag_documents', 0),
                    "total_documents": aggregated.get('rag_documents', 0)
                },
                "apps": {
                    "total": aggregated.get('total_apps', 0),
                    "details": aggregated.get('apps_detail', [])
                }
            }

            await websocket.send_json(metrics)
            await asyncio.sleep(2)

    except WebSocketDisconnect:
        active_connections.remove(websocket)


# ============================================================================
# Helper Functions
# ============================================================================

def get_current_metrics() -> Dict:
    """Get current system metrics"""
    metrics = {
        "timestamp": datetime.now().isoformat(),
        "domains": {
            "total": len(mdsa_orchestrator.domains) if mdsa_orchestrator else 0,
            "active": 0  # TODO: Track active domains
        },
        "requests": {
            "total": len(request_history),
            "recent": len([r for r in request_history if datetime.fromisoformat(r['timestamp']) > datetime.now().replace(microsecond=0).replace(second=0)]) if request_history else 0
        },
        "rag": {"global_rag": {"document_count": 0}, "local_rags": {}},  # RAG not exposed by orchestrator
        "orchestrator": mdsa_orchestrator.get_stats() if mdsa_orchestrator else {}
    }

    return metrics


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    # Get port from environment or use default
    port = int(os.getenv('MDSA_DASHBOARD_PORT', MDSA_DASHBOARD_PORT))

    print(f"""
    ============================================================
    MDSA Control Dashboard
    ============================================================
    Dashboard URL: http://localhost:{port}
    Welcome Page: http://localhost:{port}/welcome
    Monitor Page: http://localhost:{port}/monitor

    This dashboard can control ALL applications built with MDSA,
    regardless of their framework (Flask, FastAPI, Django, etc.)
    ============================================================
    """)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
