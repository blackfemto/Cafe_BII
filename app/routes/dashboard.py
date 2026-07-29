from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.database import get_db
from app import models

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    db: Session = Depends(get_db)
):
    # =============================================
    # DADOS TOTAIS (TODAS AS VENDAS)
    # =============================================
    total_vendas = db.query(models.Venda).count()
    faturamento_total = db.query(models.Venda).with_entities(
        models.Venda.valor
    ).all()
    faturamento_total = sum([v[0] for v in faturamento_total]) if faturamento_total else 0
    ticket_medio = faturamento_total / total_vendas if total_vendas > 0 else 0

    # =============================================
    # FATURAMENTO DOS ÚLTIMOS 10 MINUTOS
    # =============================================
    agora = datetime.now()
    dez_min_atras = agora - timedelta(minutes=10)
    
    vendas_10min = db.query(models.Venda).filter(
        models.Venda.data >= dez_min_atras
    ).all()
    
    faturamento_10min = sum([v.valor for v in vendas_10min]) if vendas_10min else 0

    # Últimas 5 vendas
    ultimas_vendas = db.query(models.Venda).order_by(
        models.Venda.data.desc()
    ).limit(5).all()

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
            "now": datetime.now,
            # Totais
            "faturamento_total": faturamento_total,
            "total_vendas": total_vendas,
            "ticket_medio": ticket_medio,
            # Últimos 10 minutos
            "faturamento_10min": faturamento_10min,
            "quantidade_10min": len(vendas_10min),
            # Últimas vendas
            "ultimas_vendas": ultimas_vendas
        }
    )
