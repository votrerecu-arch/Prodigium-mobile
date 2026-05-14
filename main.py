"""
PRODIGIUM - API FastAPI principale
================================
Point d'entrée pour SnapDeploy / Render / Cloud Run
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
from contextlib import asynccontextmanager
from typing import Optional
import time
import uuid

# ====================
#  INITIALISATION
# ====================
start_time = time.time()

# Singletons (initialized outside to be available for lifespan)
libertas = LibertAS()
cortex = CortexEngine()
orchestrator = Orchestrator()
nexus = Nexus()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialisation et nettoyage."""
    print(f"🇨🇲 {settings.AI_NAME} v{settings.AI_VERSION} — INITIALISATION")
    print(f"🔧 Mode : {settings.DEPLOY_MODE}")
    print(f"🧠 CORTEX : {settings.CORTEX_MODE}")
    print(f"🔐 LIBERTAS : {settings.LIBERTAS_DEFAULT_LEVEL}")
    print(f"🤖 AGENTARIUM : {orchestrator.agent_count} agents")
    print(f"🔧 NEXUS : outils intégrés")
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


# ====================
#  DÉPENDANCES
# ====================
async def get_auth(
    authorization: Optional[str] = Header(None),
    x_api_key: Optional[str] = Header(None),
    x_certificate: Optional[str] = Header(None)
):
    """Extrait et vérifie l'authentification."""
    # Token JWT
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
        auth = libertas.verify_session_token(token)
        if auth:
            return auth
    
    # API Key
    if x_api_key:
        auth = libertas.authorize(api_key=x_api_key)
        if auth.is_authenticated:
            return auth
    
    # Certificat
    if x_certificate:
        auth = libertas.authorize(certificate=x_certificate)
        if auth.is_authenticated:
            return auth
    
    # Mode public par défaut
    return libertas.authorize()


# ====================
#  ENDPOINTS
# ====================
@app.get("/", tags=["Status"])
@app.get("/health", tags=["Status"])
async def root():
    """Page d'accueil et healthcheck."""
    return {
        "ai": settings.AI_NAME,
        "version": settings.AI_VERSION,
        "status": "✅ ONLINE",
        "message": f"{settings.AI_NAME} est opérationnel. Votre partenaire pour l'import-export.",
        "docs": "/docs",
        "endpoints": {
            "chat": "/chat (POST)",
            "reason": "/reason (POST)",
            "auth": "/auth (POST)",
            "status": "/status (GET)",
            "tools": "/tools (GET, POST)",
            "agents": "/agents (GET)"
        }
    }


@app.get("/status", response_model=StatusResponse, tags=["Status"])
async def get_status(auth=Depends(get_auth)):
    """Statut détaillé du système."""
    return StatusResponse(
        status="online",
        version=settings.AI_VERSION,
        mode=settings.DEPLOY_MODE,
        cortex_connected=cortex.model is not None or cortex.colab_url is not None,
        agents_ready=orchestrator.agent_count,
        uptime_seconds=round(time.time() - start_time, 2)
    )


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest, auth=Depends(get_auth)):
    """Chat principal avec routage automatique des agents."""
    conv_id = request.conversation_id or str(uuid.uuid4())
    
    # Routage vers les agents
    response, agents_used, thinking = await orchestrator.route(
        request.message, auth, request.thinking_mode
    )
    
    # Si mode raisonnement profond, utiliser CORTEX
    if request.thinking_mode and auth.can_reason_deep:
        cortex_result = await cortex.reason(
            ReasonRequest(prompt=request.message)
        )
        thinking = (thinking or "") + "\n\n" + cortex_result.get("thinking", "")
    
    return ChatResponse(
        response=response,
        conversation_id=conv_id,
        thinking=thinking,
        tokens_used=len(response.split()),
        mode="thinking" if request.thinking_mode else "standard",
        agents_activated=agents_used
    )


@app.post("/reason", tags=["CORTEX"])
async def deep_reason(request: ReasonRequest, auth=Depends(get_auth)):
    """Raisonnement profond via CORTEX."""
    if not auth.can_reason_deep:
        raise HTTPException(
            status_code=403,
            detail="Raisonnement profond réservé aux utilisateurs vérifiés."
        )
    
    result = await cortex.reason(request)
    return result


@app.post("/auth", response_model=AuthResponse, tags=["Auth"])
async def authenticate(request: AuthRequest):
    """Authentification et obtention de token."""
    auth = libertas.authorize(
        certificate=request.certificate,
        api_key=request.api_key
    )
    
    if not auth.is_authenticated:
        return AuthResponse(
            authorized=False,
            level="PUBLIC",
            message="Non authentifié. Fournissez un certificat ou une API key."
        )
    
    token = libertas.create_session_token(auth)
    
    return AuthResponse(
        authorized=True,
        level=auth.level,
        token=token,
        message=f"Authentifié niveau {auth.level}. {'Accès complet aux outils.' if auth.can_execute_tools else 'Accès restreint.'}"
    )


@app.get("/agents", tags=["System"])
async def list_agents(auth=Depends(get_auth)):
    """Liste tous les agents disponibles."""
    agents = []
    for i, agent in enumerate(orchestrator.agents):
        agents.append({
            "id": i,
            "name": agent.name,
            "specialization": agent.specialization
        })
    return {
        "total": len(agents),
        "agents": agents,
        "orchestrator": "active"
    }


@app.get("/tools", tags=["NEXUS"])
async def list_tools(auth=Depends(get_auth)):
    """Liste les outils disponibles."""
    if not auth.can_access_nexus:
        raise HTTPException(403, "Accès NEXUS refusé.")
    
    return {
        "available_tools": nexus.tools_available,
        "count": len(nexus.tools_available)
    }


@app.post("/tools/execute", tags=["NEXUS"])
async def execute_tool(request: ToolExecuteRequest, auth=Depends(get_auth)):
    """Exécute un outil."""
    if not auth.can_execute_tools:
        raise HTTPException(
            403, 
            "Exécution d'outils réservée aux utilisateurs vérifiés."
        )
    
    result = await nexus.execute(request, auth)
    return result




# ====================
#  LANCEMENT DIRECT
# ====================
if __name__ == "__main__":
    import uvicorn
    import sys
    
    print(f"🇨🇲 {settings.AI_NAME} v{settings.AI_VERSION}")
    print("=" * 50)
    
    # Mode console interactif
    if settings.DEPLOY_MODE in ("console", "hybrid"):
        from rich.console import Console
        from rich.markdown import Markdown
        import asyncio
        
        console = Console()
        
        print("\n🧪 Mode console interactif. Tapez 'exit' pour quitter.")
        print("🔐 Tapez 'auth' pour obtenir un token.")
        print("📋 Tapez 'agents' pour voir les agents.")
        print()
        
        async def console_loop():
            auth = libertas.authorize()  # Mode public
            
            while True:
                try:
                    user_input = console.input("[bold cyan]🇨🇲 [/bold cyan] ").strip()
                    
                    if not user_input:
                        continue
                        
                    if user_input.lower() in ("exit", "quit", "q"):
                        print(f"🛑 {settings.AI_NAME} terminé.")
                        break
                    
                    if user_input.lower() == "auth":
                        cert = input("Certificat (ou laisser vide) : ").strip()
                        key = input("API Key (ou laisser vide) : ").strip()
                        auth = libertas.authorize(
                            certificate=cert if cert else None,
                            api_key=key if key else None
                        )
                        console.print(f"[green]✅ Authentifié niveau : {auth.level}[/green]")
                        continue
                    
                    if user_input.lower() == "agents":
                        for i, agent in enumerate(orchestrator.agents):
                            console.print(f"[bold]{i}.[/bold] {agent.name} — {agent.specialization}")
                        continue
                    
                    # Chat
                    request = ChatRequest(message=user_input, thinking_mode=True)
                    response, agents_used, thinking = await orchestrator.route(
                        request.message, auth, request.thinking_mode
                    )
                    
                    console.print(f"\n[bold yellow]🤖 Agents :[/bold yellow] {', '.join(agents_used)}")
                    console.print(f"[bold cyan]📝 Réponse :[/bold cyan]")
                    console.print(Markdown(response))
                    print()
                    
                except KeyboardInterrupt:
                    print("\n☠️  PRODIGIUM terminé.")
                    break
                except Exception as e:
                    console.print(f"[red]❌ Erreur : {e}[/red]")
        
        try:
            asyncio.run(console_loop())
        except KeyboardInterrupt:
            pass
    else:
        uvicorn.run(
            "main:app",
            host=settings.API_HOST,
            port=settings.API_PORT,
            reload=False,
            log_level="info"
        )
