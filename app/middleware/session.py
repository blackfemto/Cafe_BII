from starlette.middleware.base import BaseHTTPMiddleware
from itsdangerous import URLSafeTimedSerializer
from fastapi import Request
import json

SECRET_KEY = "cafe-bii-super-secret-key-2026"
serializer = URLSafeTimedSerializer(SECRET_KEY)


class CookieSessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        session_data = {}
        
        session_cookie = request.cookies.get("session")
        if session_cookie:
            try:
                session_data = serializer.loads(session_cookie)
            except:
                session_data = {}
        
        request.session = session_data
        
        response = await call_next(request)
        
        if hasattr(request, "_session_modified") and request._session_modified:
            cookie_data = serializer.dumps(request.session)
            response.set_cookie(
                key="session",
                value=cookie_data,
                httponly=True,
                max_age=86400,
                path="/"
            )
        
        return response
