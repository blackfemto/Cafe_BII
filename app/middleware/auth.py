from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import RedirectResponse

PUBLIC_ROUTES = ["/login", "/static", "/favicon.ico", "/criar-admin", "/docs", "/openapi.json"]


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if any(request.url.path.startswith(route) for route in PUBLIC_ROUTES):
            return await call_next(request)

        user_id = request.cookies.get("user_id")
        if not user_id:
            return RedirectResponse(url="/login")

        return await call_next(request)
