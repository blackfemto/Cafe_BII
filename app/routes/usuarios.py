from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.crud.usuario import (
    criar_usuario,
    listar_usuarios,
    alterar_senha,
    desativar_usuario,
    ativar_usuario
)
from app import models

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def get_user_nivel(request: Request):
    return request.cookies.get("user_nivel")


def get_user_id(request: Request):
    return request.cookies.get("user_id")


@router.get("/usuarios", response_class=HTMLResponse)
def pagina_usuarios(request: Request, db: Session = Depends(get_db)):
    if get_user_nivel(request) != "SUPER_ROOT":
        return RedirectResponse(url="/login?erro=Acesso negado!", status_code=303)
    
    usuarios = listar_usuarios(db)
    return templates.TemplateResponse(
        request=request,
        name="usuarios.html",
        context={
            "request": request,
            "usuarios": usuarios
        }
    )


@router.post("/usuarios/criar")
def criar_usuario_route(
    request: Request,
    nome: str = Form(...),
    email: str = Form(...),
    senha: str = Form(...),
    nivel: str = Form("GERENTE"),
    db: Session = Depends(get_db)
):
    if get_user_nivel(request) != "SUPER_ROOT":
        return RedirectResponse(url="/login?erro=Acesso negado!", status_code=303)
    
    usuario_existente = db.query(models.Usuario).filter(models.Usuario.email == email).first()
    if usuario_existente:
        return RedirectResponse(
            url="/usuarios?erro=Email já cadastrado!",
            status_code=303
        )
    
    criar_usuario(db, nome, email, senha, nivel)
    return RedirectResponse(url="/usuarios?sucesso=Usuário criado com sucesso!", status_code=303)


@router.post("/usuarios/{usuario_id}/alterar-senha")
def alterar_senha_route(
    request: Request,
    usuario_id: int,
    nova_senha: str = Form(...),
    db: Session = Depends(get_db)
):
    if get_user_nivel(request) != "SUPER_ROOT":
        return RedirectResponse(url="/login?erro=Acesso negado!", status_code=303)
    
    alterar_senha(db, usuario_id, nova_senha)
    return RedirectResponse(
        url="/usuarios?sucesso=Senha alterada com sucesso!",
        status_code=303
    )


@router.post("/usuarios/{usuario_id}/desativar")
def desativar_usuario_route(
    request: Request,
    usuario_id: int,
    db: Session = Depends(get_db)
):
    if get_user_nivel(request) != "SUPER_ROOT":
        return RedirectResponse(url="/login?erro=Acesso negado!", status_code=303)
    
    if str(usuario_id) == get_user_id(request):
        return RedirectResponse(
            url="/usuarios?erro=Não é possível desativar o próprio usuário!",
            status_code=303
        )
    
    desativar_usuario(db, usuario_id)
    return RedirectResponse(
        url="/usuarios?sucesso=Usuário desativado!",
        status_code=303
    )


@router.post("/usuarios/{usuario_id}/ativar")
def ativar_usuario_route(
    request: Request,
    usuario_id: int,
    db: Session = Depends(get_db)
):
    if get_user_nivel(request) != "SUPER_ROOT":
        return RedirectResponse(url="/login?erro=Acesso negado!", status_code=303)
    
    ativar_usuario(db, usuario_id)
    return RedirectResponse(
        url="/usuarios?sucesso=Usuário ativado!",
        status_code=303
    )


@router.get("/perfil", response_class=HTMLResponse)
def pagina_perfil(request: Request):
    user_nome = request.cookies.get("user_nome", "Usuário")
    user_nivel = request.cookies.get("user_nivel", "GERENTE")
    
    return templates.TemplateResponse(
        request=request,
        name="perfil.html",
        context={
            "request": request,
            "usuario": {
                "nome": user_nome,
                "nivel": user_nivel
            }
        }
    )


@router.post("/perfil/alterar-senha")
def alterar_senha_perfil(
    request: Request,
    senha_atual: str = Form(...),
    nova_senha: str = Form(...),
    db: Session = Depends(get_db)
):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)
    
    import bcrypt
    from app.crud.usuario import alterar_senha
    
    usuario = db.query(models.Usuario).filter(models.Usuario.id == int(user_id)).first()
    if not usuario:
        return RedirectResponse(url="/perfil?erro=Usuário não encontrado!", status_code=303)
    
    if not bcrypt.checkpw(senha_atual.encode('utf-8'), usuario.senha_hash.encode('utf-8')):
        return RedirectResponse(url="/perfil?erro=Senha atual incorreta!", status_code=303)
    
    alterar_senha(db, int(user_id), nova_senha)
    
    return RedirectResponse(url="/perfil?sucesso=Senha alterada com sucesso!", status_code=303)
