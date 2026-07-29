from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

from app.database import get_db
from app import models

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def ajustar_fuso(data_utc):
    """Converte UTC para UTC-3 (horário de Brasília)"""
    return data_utc - timedelta(hours=3)


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
    # 2. FATURAMENTO POR MÊS (COM FUSO CORRETO)
    # =============================================
    faturamento_mes = {}
    for v in vendas:
        data_br = ajustar_fuso(v.data)
        mes = data_br.strftime("%Y-%m")
        faturamento_mes[mes] = faturamento_mes.get(mes, 0) + v.valor

    # =============================================
    # 3. FATURAMENTO POR DIA DA SEMANA (COM FUSO CORRETO)
    # =============================================
    # Mapeamento correto: 0=Segunda, 1=Terça, ..., 6=Domingo
    dias_semana = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
    faturamento_dia = {dia: 0 for dia in dias_semana}
    
    for v in vendas:
        data_br = ajustar_fuso(v.data)
        # .weekday() retorna 0=Segunda, 6=Domingo
        dia_index = data_br.weekday()
        dia = dias_semana[dia_index]
        faturamento_dia[dia] += v.valor

    # =============================================
    # 4. HORÁRIO DE PICO (COM FUSO CORRETO)
    # =============================================
    horarios = {}
    for v in vendas:
        data_br = ajustar_fuso(v.data)
        hora = data_br.hour
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
