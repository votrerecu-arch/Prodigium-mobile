"""
KmerSource AI - API FastAPI
===========================
Assistant pour l'import-export Chine-Cameroun
"""
from prodigium_config import settings
from prodigium_models import (
    ChatRequest, ChatResponse, ReasonRequest,
    StatusResponse, AuthRequest, AuthResponse,
    ErrorResponse, ToolExecuteRequest
)
from prodigium_libertas import LibertAS
from prodigium_cortex import CortexEngine
from prodigium_agentarium import Orchestrator
from prodigium_nexus import Nexus

from fastapi import FastAPI, HTTPException, Depends, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from typing import Optional
import time
import uuid
import os

# ====================
#  INITIALISATION
# ====================
start_time = time.time()

# Singletons
libertas = LibertAS()
cortex = CortexEngine()
orchestrator = Orchestrator()
nexus = Nexus()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialisation et nettoyage."""
    print(f"🇨🇲 {settings.AI_NAME} v{settings.AI_VERSION} — INITIALISATION")
    print(f"🔧 Mode : {settings.DEPLOY_MODE}")
    print(f"🤖 AGENTARIUM : {orchestrator.agent_count} agents")
    print(f"✅ {settings.AI_NAME} prêt.")
    yield
    print(f"🛑 {settings.AI_NAME} arrêté.")

app = FastAPI(
    title=f"🇨🇲 {settings.AI_NAME}",
    version=settings.AI_VERSION,
    description="Assistant IA pour l'achat et la logistique Chine-Cameroun.",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.API_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files for frontend
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# ====================
#  DÉPENDANCES
# ====================
async def get_auth(
    authorization: Optional[str] = Header(None),
    x_api_key: Optional[str] = Header(None),
    x_certificate: Optional[str] = Header(None)
):
    """Extrait et vérifie l'authentification."""
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
        auth = libertas.verify_session_token(token)
        if auth:
            return auth
    if x_api_key:
        auth = libertas.authorize(api_key=x_api_key)
        if auth.is_authenticated:
            return auth
    return libertas.authorize()


# ====================
#  ENDPOINTS
# ====================
@app.get("/")
async def serve_home():
    """Sert la page d'accueil (frontend)."""
    if os.path.exists("static/index.html"):
        return FileResponse("static/index.html")
    return {
        "ai": settings.AI_NAME,
        "message": "Bienvenue sur KmerSource AI. Le frontend n'est pas encore déployé.",
        "api_docs": "/docs"
    }

@app.get("/health", tags=["Status"])
async def health():
    return {"status": "online", "ai": settings.AI_NAME}

@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest, auth=Depends(get_auth)):
    """Chat principal avec routage automatique des agents."""
    conv_id = request.conversation_id or str(uuid.uuid4())
    response, agents_used, thinking = await orchestrator.route(
        request.message, auth, request.thinking_mode
    )
    return ChatResponse(
        response=response,
        conversation_id=conv_id,
        thinking=thinking,
        tokens_used=len(response.split()),
        mode="standard",
        agents_activated=agents_used
    )

@app.get("/status", response_model=StatusResponse, tags=["Status"])
async def get_status(auth=Depends(get_auth)):
    return StatusResponse(
        status="online",
        version=settings.AI_VERSION,
        mode=settings.DEPLOY_MODE,
        cortex_connected=True,
        agents_ready=orchestrator.agent_count,
        uptime_seconds=round(time.time() - start_time, 2)
    )

# ====================
#  LANCEMENT DIRECT
# ====================
if __name__ == "__main__":
    import uvicorn
    import sys

    print(f"🇨🇲 {settings.AI_NAME} v{settings.AI_VERSION}")

    if settings.DEPLOY_MODE in ("console", "hybrid"):
        from rich.console import Console
        from rich.markdown import Markdown
        import asyncio
        console = Console()

        async def console_loop():
            auth = libertas.authorize()
            print("\n🧪 Mode console. Tapez 'exit' pour quitter.\n")
            while True:
                try:
                    user_input = console.input("[bold cyan]🇨🇲 [/bold cyan] ").strip()
                    if not user_input: continue
                    if user_input.lower() in ("exit", "quit", "q"): break

                    request = ChatRequest(message=user_input)
                    response, agents_used, _ = await orchestrator.route(request.message, auth)
                    console.print(f"\n[bold yellow]🤖 Agents :[/bold yellow] {', '.join(agents_used)}")
                    console.print(Markdown(response))
                    print()
                except KeyboardInterrupt: break
                except Exception as e: console.print(f"[red]❌ Erreur : {e}[/red]")

        try: asyncio.run(console_loop())
        except KeyboardInterrupt: pass
    else:
        uvicorn.run("main:app", host=settings.API_HOST, port=settings.API_PORT)
