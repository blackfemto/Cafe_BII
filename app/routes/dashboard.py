from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.database import get_db
from app import models
from app.crud.fechamento import get_ranking_gerentes

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    db: Session = Depends(get_db)
):
    # =============================================
    # DADOS TOTAIS
    # =============================================
    vendas = db.query(models.Venda).all()
    faturamento_total = sum(v.valor for v in vendas) if vendas else 0
    total_vendas = len(vendas)

    # =============================================
    # RANKING DOS GERENTES
    # =============================================
    ranking = get_ranking_gerentes(db)

    # =============================================
    # ÚLTIMAS VENDAS
    # =============================================
    ultimas_vendas = db.query(models.Venda).order_by(
        models.Venda.data.desc()
    ).limit(5).all()

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
            "now": datetime.now,
            "faturamento_total": faturamento_total,
            "total_vendas": total_vendas,
            "ranking": ranking,
            "ultimas_vendas": ultimas_vendas
        }
    )
