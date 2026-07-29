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
    # 1. FATURAMENTO TOTAL
    # =============================================
    vendas = db.query(models.Venda).all()
    faturamento_total = sum(v.valor for v in vendas) if vendas else 0
    total_vendas = len(vendas)

    # =============================================
    # 2. VENDAS DE HOJE
    # =============================================
    hoje = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    vendas_hoje = db.query(models.Venda).filter(models.Venda.data >= hoje).all()
    faturamento_hoje = sum(v.valor for v in vendas_hoje) if vendas_hoje else 0

    # =============================================
    # 3. COMANDAS ABERTAS
    # =============================================
    comandas_abertas = db.query(models.Comanda).filter(models.Comanda.status == "ABERTA").count()

    # =============================================
    # 4. PRODUTO MAIS VENDIDO
    # =============================================
    produto_mais_vendido = db.query(
        models.Produto.nome,
        models.Produto.preco,
        models.ItemComanda.produto_id,
        models.ItemComanda.quantidade
    ).join(
        models.ItemComanda, models.Produto.id == models.ItemComanda.produto_id
    ).order_by(
        models.ItemComanda.quantidade.desc()
    ).first()

    if produto_mais_vendido:
        produto_top = {
            "nome": produto_mais_vendido[0],
            "preco": produto_mais_vendido[1],
            "quantidade": produto_mais_vendido[3]
        }
    else:
        produto_top = {"nome": "Nenhum", "preco": 0, "quantidade": 0}

    # =============================================
    # 5. VENDAS DOS ÚLTIMOS 10 MIN
    # =============================================
    dez_min_atras = datetime.now() - timedelta(minutes=10)
    vendas_10min = db.query(models.Venda).filter(
        models.Venda.data >= dez_min_atras
    ).all()
    faturamento_10min = sum(v.valor for v in vendas_10min) if vendas_10min else 0

    # =============================================
    # 6. ÚLTIMAS VENDAS (5)
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
            # Totais
            "faturamento_total": faturamento_total,
            "total_vendas": total_vendas,
            "faturamento_hoje": faturamento_hoje,
            "comandas_abertas": comandas_abertas,
            "produto_top": produto_top,
            "faturamento_10min": faturamento_10min,
            "ultimas_vendas": ultimas_vendas
        }
    )
