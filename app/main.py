# app/main.py

import sys
import os
import time
import json
import logging
from contextlib import asynccontextmanager

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
import redis.asyncio as redis

from app.config import settings
from app.d1_client import init_db, execute_sql
from app.routers import auth, admin, dashboard, pricing, analysis
from app.rate_limit import init_redis

# Configuração de logging
logging.basicConfig(
    level=logging.INFO if settings.APP_ENV == "prod" else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Inicializando aplicação MeuCFO.ai")
    
    # Inicializar banco de dados
    await init_db()
    logger.info("Banco de dados D1 inicializado")
    
    # Inicializar Redis
    try:
        app.state.redis = await init_redis()
        logger.info("Redis inicializado para rate limiting")
    except Exception as e:
        logger.warning(f"Não foi possível conectar ao Redis: {e}")
        # Mock redis for dev without redis
        class MockRedis:
            async def get(self, *args, **kwargs): return None
            async def set(self, *args, **kwargs): return None
            async def close(self): pass
            async def incr(self, *args, **kwargs): return 1
            async def expire(self, *args, **kwargs): pass
            async def ttl(self, *args, **kwargs): return 0
            async def delete(self, *args, **kwargs): pass
        app.state.redis = MockRedis()
    
    yield
    
    # Shutdown
    if hasattr(app.state, 'redis'):
        await app.state.redis.close()
        logger.info("Redis fechado")

# Criação da aplicação FastAPI
app = FastAPI(
    title="MeuCFO.ai - Dashboard de Análise Financeira",
    description="Sistema completo de análise financeira para PMEs",
    version="1.0.0",
    docs_url="/api/docs" if settings.APP_ENV == "dev" else None,
    redoc_url="/api/redoc" if settings.APP_ENV == "dev" else None,
    lifespan=lifespan
)

# Middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.APP_ENV == "dev" else [settings.APP_HOST],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar arquivos estáticos e templates se diretórios existirem
if os.path.exists("app/static"):
    app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Configurar templates
if os.path.exists("app/templates"):
    templates = Jinja2Templates(directory="app/templates")
else:
    # Fallback to avoid crash if templates dir missing during dev
    templates = None

# Middleware personalizado para logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    try:
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(
            f"{request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Tempo: {process_time:.3f}s"
        )
        return response
    except Exception as e:
        logger.error(f"Request failed: {e}")
        import traceback
        traceback.print_exc()
        raise e

# Incluir routers
app.include_router(auth.router, prefix="/api/auth", tags=["Autenticação"])
app.include_router(admin.router, prefix="/api/admin", tags=["Administração"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(pricing.router, prefix="/api/pricing", tags=["Precificação"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Análise"])


# Rotas principais
@app.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    if templates:
        return templates.TemplateResponse(
            "landing.html",
            {"request": request, "title": "MeuCFO.ai - Inteligência Financeira", "current_user": None}
        )
    return "Templates not loaded"

@app.get("/dashboard", response_class=HTMLResponse, name="dashboard")
async def dashboard_page(request: Request):
    if templates:
        return templates.TemplateResponse(
            "dashboard.html",
            {"request": request, "title": "MeuCFO.ai - Dashboard", "current_user": None}
        )
    return "Templates not loaded"

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "MeuCFO.ai",
        "version": "1.0.0",
        "timestamp": time.time()
    }

@app.get("/api/config")
async def get_config():
    """Retorna configurações não sensíveis para o frontend"""
    return {
        "app_name": "MeuCFO.ai",
        "environment": settings.APP_ENV,
        "features": {
            "pricing_calculator": True,
            "competitive_analysis": True,
            "market_analysis": False,
            "webhook_integration": True
        }
    }

from pydantic import BaseModel
class D1Query(BaseModel):
    sql: str
    params: list = []

@app.post("/api/d1/query")
async def proxy_d1_query(query: D1Query):
    """
    Proxy temporário para permitir que o frontend execute SQL diretamente.
    ATENÇÃO: Isso deve ser substituído por rotas específicas no futuro por segurança.
    """
    try:
        # Usar o cliente D1 já configurado
        result = await execute_sql(query.sql, query.params)
        
        # O cliente D1 retorna o objeto 'result' interno da Cloudflare ou um dict customizado
        # Precisamos garantir que retorne no formato que o frontend espera (envelope Cloudflare)
        
        # Se result já tem "success", provavelmente é a resposta crua
        if "success" in result:
             return result
             
        # Caso contrário, encapsular (o execute_sql as vezes retorna só o data)
        # Verificando app/d1_client.py: execute() retorna result.get("result", [])[0] se sucesso
        # O frontend espera a resposta COMPLETA da API da Cloudflare: { success: true, part: ..., result: [...] }
        
        # Vamos usar o client diretamente para ter a resposta crua para esse proxy
        from app.d1_client import d1_client
        raw_response = await d1_client.execute(query.sql, query.params)
        
        # Verificar se houve erro no execute
        if isinstance(raw_response, dict) and "success" in raw_response and raw_response["success"] is False:
            return raw_response

        # O d1_client.execute atual já retorna a estrutura processada das linhas
        # O frontend espera: { success: true, result: [ { results: [rows], meta: ... } ] }
        return {"success": True, "result": [raw_response]}
        
    except Exception as e:
        logger.error(f"Erro no proxy D1: {e}")
        return {"success": False, "errors": [{"message": str(e)}]}

@app.get("/api/debug/users")
async def debug_users():
    """Rota temporária para listar usuários"""
    return await execute_sql("SELECT * FROM users")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.APP_PORT,
        reload=settings.APP_ENV == "dev"
    )
