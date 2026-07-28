from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.crud.relatorios import (
    get_vendas_ultimos_7_dias,
    get_produtos_mais_vendidos,
    get_faturamento_por_categoria,
    get_resumo_geral
)

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/relatorios", response_class=HTMLResponse)
def pagina_relatorios(
    request: Request,
    db: Session = Depends(get_db)
):
    # Dados para os gráficos
    vendas_7_dias = get_vendas_ultimos_7_dias(db)
    produtos_mais_vendidos = get_produtos_mais_vendidos(db)
    faturamento_categorias = get_faturamento_por_categoria(db)
    resumo = get_resumo_geral(db)
    
    return templates.TemplateResponse(
        request=request,
        name="relatorios.html",
        context={
            "request": request,
            "vendas_7_dias": vendas_7_dias,
            "produtos_mais_vendidos": produtos_mais_vendidos,
            "faturamento_categorias": faturamento_categorias,
            "resumo": resumo,
            "now": datetime.now
        }
    )
