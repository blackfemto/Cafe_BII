from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime

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
    # Total de vendas
    total_vendas = db.query(models.Venda).count()
    faturamento_total = db.query(models.Venda).with_entities(
        models.Venda.valor
    ).all()
    faturamento_total = sum([v[0] for v in faturamento_total]) if faturamento_total else 0

    # Ticket médio geral
    ticket_medio = faturamento_total / total_vendas if total_vendas > 0 else 0

    # =============================================
    # DADOS DO DIA (APENAS PARA O CAIXA)
    # =============================================
    hoje = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    vendas_hoje = db.query(models.Venda).filter(models.Venda.data >= hoje).all()
    faturamento_hoje = sum([v.valor for v in vendas_hoje]) if vendas_hoje else 0

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
            # Totais (todas as vendas)
            "faturamento_total": faturamento_total,
            "total_vendas": total_vendas,
            "ticket_medio": ticket_medio,
            # Do dia (apenas para o caixa)
            "faturamento_hoje": faturamento_hoje,
            "vendas_hoje": vendas_hoje,
            "ultimas_vendas": ultimas_vendas
        }
    )
