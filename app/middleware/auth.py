from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import RedirectResponse
import os

# Rotas públicas (não precisam de login)
PUBLIC_ROUTES = [
    "/login",
    "/static",
    "/favicon.ico",
    "/criar-admin",
    "/docs",
    "/openapi.json"
]

# Rotas que exigem SuperRoot
SUPER_ROOT_ROUTES = [
    "/admin/super-root",
    "/usuarios"
]


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Verificar se é rota pública
        if any(request.url.path.startswith(route) for route in PUBLIC_ROUTES):
            return await call_next(request)

        # Verificar se o usuário está logado
        user_id = request.cookies.get("user_id")
        user_nivel = request.cookies.get("user_nivel")

        if not user_id:
            # Redirecionar para login
            return RedirectResponse(url=f"/login?next={request.url.path}")

        # Verificar se a rota exige SuperRoot
        if any(request.url.path.startswith(route) for route in SUPER_ROOT_ROUTES):
            if user_nivel != "SUPER_ROOT":
                return RedirectResponse(
                    url="/login?erro=Você não tem permissão para acessar esta página!",
                    status_code=303
                )

        return await call_next(request)
