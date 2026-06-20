"""NeuroAcolhe REST API — FastAPI application."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from neuro_api.config import settings
from neuro_api.routes import pacientes, procedimentos, orientacoes, historico


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    # Startup: validate Supabase connection
    from neuro_api.database import get_supabase

    try:
        db = get_supabase()
        result = db.table("procedimentos").select("id").limit(1).execute()
        count = len(result.data)
        print(f"✅ Supabase conectado — {count} procedimento(s) encontrado(s)")
    except Exception as e:
        print(f"⚠️  Erro ao conectar ao Supabase: {e}")

    yield
    # Shutdown
    print("👋 NeuroAcolhe API encerrada")


app = FastAPI(
    title="NeuroAcolhe API",
    description="API REST para o NeuroAcolhe — orientações para atendimento de pacientes neurodivergentes.",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — allow the Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(pacientes.router, prefix=settings.api_prefix)
app.include_router(procedimentos.router, prefix=settings.api_prefix)
app.include_router(orientacoes.router, prefix=settings.api_prefix)
app.include_router(historico.router, prefix=settings.api_prefix)


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {
        "app": "NeuroAcolhe API",
        "version": "0.1.0",
        "status": "healthy",
    }
