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
    """Converte UTC para UTC-3"""
    return data_utc - timedelta(hours=3)


@router.get("/", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    db: Session = Depends(get_db)
):
    # =============================================
    # 1. DADOS DO DIA (COM FUSO CORRETO)
    # =============================================
    hoje = datetime.now()
    inicio_dia = datetime(hoje.year, hoje.month, hoje.day, 0, 0, 0) - timedelta(hours=3)
    amanha = inicio_dia + timedelta(days=1)

    vendas_hoje = db.query(models.Venda).filter(
        models.Venda.data >= inicio_dia,
        models.Venda.data < amanha
    ).all()

    faturamento_hoje = sum(v.valor for v in vendas_hoje) if vendas_hoje else 0
    clientes_hoje = len(vendas_hoje)
    ticket_medio = faturamento_hoje / clientes_hoje if clientes_hoje > 0 else 0

    comandas_abertas = db.query(models.Comanda).filter(models.Comanda.status == "ABERTA").count()

    # =============================================
    # 2. COMPARAÇÕES
    # =============================================
    # Ontem
    ontem_inicio = inicio_dia - timedelta(days=1)
    ontem_fim = inicio_dia
    vendas_ontem = db.query(models.Venda).filter(
        models.Venda.data >= ontem_inicio,
        models.Venda.data < ontem_fim
    ).all()
    faturamento_ontem = sum(v.valor for v in vendas_ontem) if vendas_ontem else 0

    # Mesmo dia da semana passada
    semana_passada_inicio = inicio_dia - timedelta(days=7)
    semana_passada_fim = inicio_dia - timedelta(days=6)
    vendas_semana_passada = db.query(models.Venda).filter(
        models.Venda.data >= semana_passada_inicio,
        models.Venda.data < semana_passada_fim
    ).all()
    faturamento_semana_passada = sum(v.valor for v in vendas_semana_passada) if vendas_semana_passada else 0

    # Média do mês
    mes_inicio = datetime(hoje.year, hoje.month, 1)
    vendas_mes = db.query(models.Venda).filter(models.Venda.data >= mes_inicio).all()
    dias_do_mes = (hoje - mes_inicio).days + 1
    media_mes = sum(v.valor for v in vendas_mes) / dias_do_mes if dias_do_mes > 0 else 0

    # Melhor dia do mês
    melhor_dia = 0
    for i in range(1, dias_do_mes + 1):
        dia_inicio = datetime(hoje.year, hoje.month, i)
        dia_fim = dia_inicio + timedelta(days=1)
        vendas_dia = db.query(models.Venda).filter(
            models.Venda.data >= dia_inicio,
            models.Venda.data < dia_fim
        ).all()
        total_dia = sum(v.valor for v in vendas_dia)
        if total_dia > melhor_dia:
            melhor_dia = total_dia

    # =============================================
    # 3. PRODUTOS MAIS VENDIDOS
    # =============================================
    produtos_top = db.query(
        models.Produto.nome,
        models.Produto.preco,
        func.sum(models.ItemComanda.quantidade).label('quantidade_total'),
        func.sum(models.ItemComanda.subtotal).label('faturamento_total')
    ).join(
        models.ItemComanda, models.Produto.id == models.ItemComanda.produto_id
    ).join(
        models.Comanda, models.ItemComanda.comanda_id == models.Comanda.id
    ).filter(
        models.Comanda.status == "FECHADA",
        models.Comanda.data_fechamento >= inicio_dia,
        models.Comanda.data_fechamento < amanha
    ).group_by(
        models.Produto.id
    ).order_by(
        func.sum(models.ItemComanda.quantidade).desc()
    ).limit(5).all()

    produtos_top_list = [
        {
            "nome": p[0],
            "preco": p[1],
            "quantidade": p[2],
            "faturamento": float(p[3])
        }
        for p in produtos_top
    ]

    # =============================================
    # 4. PRODUTOS ESQUECIDOS (não vendidos hoje)
    # =============================================
    produtos_vendidos_hoje = db.query(models.ItemComanda.produto_id).join(
        models.Comanda, models.ItemComanda.comanda_id == models.Comanda.id
    ).filter(
        models.Comanda.status == "FECHADA",
        models.Comanda.data_fechamento >= inicio_dia,
        models.Comanda.data_fechamento < amanha
    ).distinct().subquery()

    produtos_esquecidos = db.query(models.Produto.nome).filter(
        models.Produto.id.notin_(produtos_vendidos_hoje),
        models.Produto.ativo == True
    ).limit(5).all()
    produtos_esquecidos_list = [p[0] for p in produtos_esquecidos]

    # =============================================
    # 5. HORÁRIOS DE MOVIMENTO
    # =============================================
    horarios = {}
    for h in range(6, 24):
        hora_inicio = datetime(hoje.year, hoje.month, hoje.day, h, 0, 0) - timedelta(hours=3)
        hora_fim = hora_inicio + timedelta(hours=1)
        vendas_hora = db.query(models.Venda).filter(
            models.Venda.data >= hora_inicio,
            models.Venda.data < hora_fim
        ).all()
        horarios[f"{h:02d}:00"] = len(vendas_hora)

    # =============================================
    # 6. INSIGHTS AUTOMÁTICOS
    # =============================================
    insights = []
    if faturamento_hoje > 0:
        crescimento = ((faturamento_hoje - faturamento_ontem) / faturamento_ontem * 100) if faturamento_ontem > 0 else 0
        if crescimento > 10:
            insights.append(f"📈 Hoje o faturamento está {crescimento:.0f}% acima do dia anterior.")
        elif crescimento < -10:
            insights.append(f"📉 Hoje o faturamento está {abs(crescimento):.0f}% abaixo do dia anterior.")

    if comandas_abertas > 10:
        insights.append(f"📋 Há {comandas_abertas} comandas abertas. Esse número está acima da média.")

    if produtos_top_list:
        p = produtos_top_list[0]
        insights.append(f"🏆 O produto mais vendido hoje é '{p['nome']}'. Já vendeu {p['quantidade']} unidades.")

    if produtos_esquecidos_list:
        produtos_str = ", ".join(produtos_esquecidos_list[:3])
        insights.append(f"💡 Produtos não vendidos hoje: {produtos_str}. Considere oferecê-los.")

    # =============================================
    # 7. PREVISÃO DO DIA (baseado na média)
    # =============================================
    previsao = faturamento_hoje * (24 / (datetime.now().hour + 1))

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
            "now": datetime.now,
            # Visão geral
            "faturamento_hoje": faturamento_hoje,
            "clientes_hoje": clientes_hoje,
            "comandas_abertas": comandas_abertas,
            "ticket_medio": ticket_medio,
            # Comparações
            "faturamento_ontem": faturamento_ontem,
            "faturamento_semana_passada": faturamento_semana_passada,
            "media_mes": media_mes,
            "melhor_dia": melhor_dia,
            # Produtos
            "produtos_top": produtos_top_list,
            "produtos_esquecidos": produtos_esquecidos_list,
            # Horários
            "horarios": horarios,
            # Insights
            "insights": insights,
            # Previsão
            "previsao": previsao
        }
    )
