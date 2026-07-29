from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.database import get_db
from app.crud.relatorios import (
    get_vendas_ultimos_7_dias,
    get_produtos_mais_vendidos,
    get_faturamento_por_categoria,
    get_resumo_geral
)

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def ajustar_fuso(data_utc):
    """Converte UTC para UTC-3 (horário de Brasília)"""
    return data_utc - timedelta(hours=3)


@router.get("/relatorios", response_class=HTMLResponse)
def pagina_relatorios(
    request: Request,
    db: Session = Depends(get_db)
):
    # =============================================
    # VENDAS DOS ÚLTIMOS 7 DIAS (COM FUSO CORRETO)
    # =============================================
    hoje = datetime.now()
    vendas_7_dias = []
    
    for i in range(7, -1, -1):
        dia = datetime(hoje.year, hoje.month, hoje.day) - timedelta(days=i)
        dia_inicio = dia - timedelta(hours=3)  # Ajuste para UTC-3
        dia_fim = dia_inicio + timedelta(days=1)
        
        # Buscar vendas do dia (usando a data UTC-3)
        vendas = db.query(models.Venda).filter(
            models.Venda.data >= dia_inicio,
            models.Venda.data < dia_fim
        ).all()
        
        total = sum(v.valor for v in vendas) if vendas else 0
        vendas_7_dias.append({
            "data": dia.strftime("%d/%m"),
            "total": float(total)
        })
    
    # =============================================
    # DADOS DO RELATÓRIO
    # =============================================
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
