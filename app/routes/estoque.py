from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.crud.produtos import (
    listar_produtos,
    listar_produtos_com_estoque_baixo,
    repor_estoque,
    buscar_produto
)

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/estoque", response_class=HTMLResponse)
def pagina_estoque(
    request: Request,
    db: Session = Depends(get_db)
):
    produtos = listar_produtos(db)
    produtos_baixo = listar_produtos_com_estoque_baixo(db)
    
    return templates.TemplateResponse(
        request=request,
        name="estoque.html",
        context={
            "request": request,
            "produtos": produtos,
            "produtos_baixo": produtos_baixo
        }
    )


@router.post("/estoque/{produto_id}/repor")
def repor_estoque_route(
    request: Request,
    produto_id: int,
    quantidade: int = Form(...),
    db: Session = Depends(get_db)
):
    if repor_estoque(db, produto_id, quantidade):
        return RedirectResponse(
            url="/estoque?sucesso=Estoque reposto com sucesso!",
            status_code=303
        )
    return RedirectResponse(
        url="/estoque?erro=Erro ao repor estoque!",
        status_code=303
    )
