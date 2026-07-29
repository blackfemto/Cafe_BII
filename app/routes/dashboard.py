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
    # Total de vendas
    total_vendas = db.query(models.Venda).count()
    faturamento_total = db.query(models.Venda).with_entities(
        models.Venda.valor
    ).all()
    faturamento_total = sum([v[0] for v in faturamento_total]) if faturamento_total else 0
    ticket_medio = faturamento_total / total_vendas if total_vendas > 0 else 0

    # Comandas abertas
    comandas_abertas = db.query(models.Comanda).filter(models.Comanda.status == "ABERTA").count()

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
            "faturamento_total": faturamento_total,
            "total_vendas": total_vendas,
            "ticket_medio": ticket_medio,
            "comandas_abertas": comandas_abertas
        }
    )
