from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.database import get_db
from app import models

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/relatorio-total", response_class=HTMLResponse)
def relatorio_total(
    request: Request,
    db: Session = Depends(get_db)
):
    # =============================================
    # 1. DADOS GERAIS
    # =============================================
    vendas = db.query(models.Venda).all()
    total_vendas = len(vendas)
    faturamento_total = sum(v.valor for v in vendas) if vendas else 0

    # =============================================
    # 2. FATURAMENTO POR MÊS
    # =============================================
    faturamento_mes = {}
    for v in vendas:
        mes = v.data.strftime("%Y-%m")
        faturamento_mes[mes] = faturamento_mes.get(mes, 0) + v.valor

    # =============================================
    # 3. FATURAMENTO POR DIA DA SEMANA
    # =============================================
    dias_semana = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
    faturamento_dia = {dia: 0 for dia in dias_semana}
    for v in vendas:
        dia = dias_semana[v.data.weekday()]
        faturamento_dia[dia] += v.valor

    # =============================================
    # 4. HORÁRIO DE PICO
    # =============================================
    horarios = {}
    for v in vendas:
        hora = v.data.hour
        horarios[hora] = horarios.get(hora, 0) + v.valor
    hora_pico = max(horarios, key=horarios.get) if horarios else None

    # =============================================
    # 5. PRODUTO MAIS VENDIDO
    # =============================================
    produto_top = db.query(
        models.Produto.nome,
        models.Produto.preco,
        models.ItemComanda.produto_id,
        models.ItemComanda.quantidade
    ).join(
        models.ItemComanda, models.Produto.id == models.ItemComanda.produto_id
    ).order_by(
        models.ItemComanda.quantidade.desc()
    ).first()

    if produto_top:
        produto_mais_vendido = {
            "nome": produto_top[0],
            "preco": produto_top[1],
            "quantidade": produto_top[3]
        }
    else:
        produto_mais_vendido = {"nome": "Nenhum", "preco": 0, "quantidade": 0}

    return templates.TemplateResponse(
        request=request,
        name="relatorio_total.html",
        context={
            "request": request,
            "total_vendas": total_vendas,
            "faturamento_total": faturamento_total,
            "faturamento_mes": faturamento_mes,
            "faturamento_dia": faturamento_dia,
            "hora_pico": hora_pico,
            "produto_mais_vendido": produto_mais_vendido,
            "data_geracao": datetime.now().strftime("%d/%m/%Y %H:%M")
        }
    )
