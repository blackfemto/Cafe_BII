from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from app.database import Base, engine
from app import models

# Rotas
from app.routes.dashboard import router as dashboard_router
from app.routes.categorias import router as categorias_router
from app.routes.produtos import router as produtos_router
from app.routes.comandas import router as comandas_router
from app.routes.caixa import router as caixa_router
from app.routes.relatorios import router as relatorios_router
from app.routes.auth import router as auth_router
from app.routes.super_root import router as super_root_router
from app.routes.usuarios import router as usuarios_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Café BII", version="1.0.0")

# Middleware de autenticação simples
class SimpleAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        public_paths = ["/login", "/static", "/favicon.ico", "/criar-admin"]
        if any(request.url.path.startswith(p) for p in public_paths):
            return await call_next(request)
        
        user_id = request.cookies.get("user_id")
        if not user_id:
            return RedirectResponse(url="/login")
        
        return await call_next(request)

#app.add_middleware(SimpleAuthMiddleware)

# Rotas
app.include_router(dashboard_router)
app.include_router(categorias_router)
app.include_router(produtos_router)
app.include_router(comandas_router)
app.include_router(caixa_router)
app.include_router(relatorios_router)
app.include_router(auth_router)
app.include_router(super_root_router)
app.include_router(usuarios_router)

app.mount("/static", StaticFiles(directory="static"), name="static")
from app.routes.estoque import router as estoque_router

app.include_router(estoque_router)
