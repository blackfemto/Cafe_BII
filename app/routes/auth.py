from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud.usuario import autenticar_usuario, criar_usuario
from app import models

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/login", response_class=HTMLResponse)
def pagina_login(request: Request):
    return templates.TemplateResponse(request=request, name="login.html", context={"request": request})


@router.post("/login")
def fazer_login(
    request: Request,
    email: str = Form(...),
    senha: str = Form(...),
    db: Session = Depends(get_db)
):
    usuario = autenticar_usuario(db, email, senha)
    if not usuario:
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"request": request, "erro": "Email ou senha inválidos!"}
        )

    # 🔥 FORÇA O NÍVEL DO BANCO NO COOKIE
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="user_id", value=str(usuario.id), httponly=True)
    response.set_cookie(key="user_nome", value=usuario.nome, httponly=True)
    response.set_cookie(key="user_nivel", value=usuario.nivel, httponly=True)  # 🔑 ESSENCIAL

    return response


@router.get("/logout")
def fazer_logout():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("user_id")
    response.delete_cookie("user_nome")
    response.delete_cookie("user_nivel")
    return response


@router.get("/criar-admin")
def criar_admin(db: Session = Depends(get_db)):
    from app.crud.usuario import criar_usuario
    usuario = db.query(models.Usuario).filter(models.Usuario.email == "admin@cafebii.com").first()
    if usuario:
        return {"mensagem": "Admin já existe!"}
    criar_usuario(db, "Administrador", "admin@cafebii.com", "admin123", "SUPER_ROOT")
    return {"mensagem": "Admin criado! Email: admin@cafebii.com, Senha: admin123"}
