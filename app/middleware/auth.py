from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import RedirectResponse
from app.database import SessionLocal
from app import models

# Rotas públicas
PUBLIC_ROUTES = [
    "/login", "/static", "/favicon.ico",
    "/criar-admin", "/docs", "/openapi.json"
]

# Rotas que exigem SuperRoot
SUPER_ROOT_ROUTES = [
    "/admin/super-root", "/usuarios"
]


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Verificar se é rota pública
        if any(request.url.path.startswith(route) for route in PUBLIC_ROUTES):
            return await call_next(request)

        # Verificar se o usuário está logado
        user_id = request.cookies.get("user_id")

        if not user_id:
            return RedirectResponse(url=f"/login?next={request.url.path}")

        # 🔥 VERIFICAR O NÍVEL NO BANCO DE DADOS
        db = SessionLocal()
        try:
            usuario = db.query(models.Usuario).filter(models.Usuario.id == int(user_id)).first()
            if not usuario:
                return RedirectResponse(url="/login")
            user_nivel = usuario.nivel
        finally:
            db.close()

        # Verificar se a rota exige SuperRoot
        if any(request.url.path.startswith(route) for route in SUPER_ROOT_ROUTES):
            if user_nivel != "SUPER_ROOT":
                return RedirectResponse(
                    url="/login?erro=Você não tem permissão para acessar esta página!",
                    status_code=303
                )

        return await call_next(request)
