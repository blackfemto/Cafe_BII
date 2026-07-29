from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.database import get_db
from app import models

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def ajustar_fuso(data_utc):
    return data_utc - timedelta(hours=3)


@router.get("/", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    db: Session = Depends(get_db)
):
    hoje = datetime.now()
    inicio_dia = datetime(hoje.year, hoje.month, hoje.day, 0, 0, 0) - timedelta(hours=3)
    amanha = inicio_dia + timedelta(days=1)

    # =============================================
    # 1. DADOS DO DIA
    # =============================================
    vendas_hoje = db.query(models.Venda).filter(
        models.Venda.data >= inicio_dia,
        models.Venda.data < amanha
    ).all()

    faturamento_hoje = sum(v.valor for v in vendas_hoje) if vendas_hoje else 0
    clientes_hoje = len(vendas_hoje)
    ticket_medio = faturamento_hoje / clientes_hoje if clientes_hoje > 0 else 0

    comandas_abertas = db.query(models.Comanda).filter(models.Comanda.status == "ABERTA").count()

    # =============================================
    # 2. PRODUTOS MAIS VENDIDOS
    # =============================================
    produtos_top = db.query(
        models.Produto.nome,
        func.sum(models.ItemComanda.quantidade).label('qtd'),
        func.sum(models.ItemComanda.subtotal).label('faturamento')
    ).join(
        models.ItemComanda, models.Produto.id == models.ItemComanda.produto_id
    ).join(
        models.Comanda, models.ItemComanda.comanda_id == models.Comanda.id
    ).filter(
        models.Comanda.status == "FECHADA"
    ).group_by(
        models.Produto.id
    ).order_by(
        func.sum(models.ItemComanda.quantidade).desc()
    ).limit(5).all()

    produtos_top_list = [
        {"nome": p[0], "quantidade": p[1], "faturamento": float(p[2])}
        for p in produtos_top
    ]

    # =============================================
    # 3. HORÁRIOS
    # =============================================
    horarios = {}
    for h in range(6, 23):
        hora_inicio = datetime(hoje.year, hoje.month, hoje.day, h, 0, 0) - timedelta(hours=3)
        hora_fim = hora_inicio + timedelta(hours=1)
        vendas_hora = db.query(models.Venda).filter(
            models.Venda.data >= hora_inicio,
            models.Venda.data < hora_fim
        ).all()
        horarios[f"{h:02d}:00"] = len(vendas_hora)

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
            "faturamento_hoje": faturamento_hoje,
            "clientes_hoje": clientes_hoje,
            "comandas_abertas": comandas_abertas,
            "ticket_medio": ticket_medio,
            "produtos_top": produtos_top_list,
            "horarios": horarios,
            "now": datetime.now
        }
    )
