from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.crud.auditoria import listar_auditoria
from app.crud.relatorios import get_resumo_geral
from app import models

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/admin/super-root", response_class=HTMLResponse)
def painel_super_root(
    request: Request,
    db: Session = Depends(get_db)
):
    # USANDO COOKIES EM VEZ DE SESSION
    user_nivel = request.cookies.get("user_nivel")
    
    if user_nivel != "SUPER_ROOT":
        return RedirectResponse(url="/login?erro=Acesso negado!", status_code=303)
    
    resumo = get_resumo_geral(db)
    auditoria = listar_auditoria(db, 50)
    usuarios = db.query(models.Usuario).all()
    total_vendas = db.query(models.Venda).count()
    
    return templates.TemplateResponse(
        request=request,
        name="super_root.html",
        context={
            "request": request,
            "resumo": resumo,
            "auditoria": auditoria,
            "usuarios": usuarios,
            "total_vendas": total_vendas,
            "now": datetime.now
        }
    )
