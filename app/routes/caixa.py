from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.crud.caixa import get_resumo_caixa

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/caixa", response_class=HTMLResponse)
def pagina_caixa(
    request: Request,
    db: Session = Depends(get_db)
):
    dados = get_resumo_caixa(db)
    
    return templates.TemplateResponse(
        request=request,
        name="caixa.html",
        context={
            "request": request,
            "vendas": dados["vendas"],
            "total": dados["total"],
            "total_dinheiro": dados["total_dinheiro"],
            "total_pix": dados["total_pix"],
            "total_cartao": dados["total_cartao"],
            "quantidade": dados["quantidade"],
            "ticket_medio": dados["ticket_medio"]
        }
    )
