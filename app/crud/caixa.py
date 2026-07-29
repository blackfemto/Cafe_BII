from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app import models
from app.crud.fechamento import get_ultimo_fechamento


def get_resumo_caixa(db: Session):
    """Retorna o resumo do caixa considerando apenas vendas após o último fechamento"""
    
    # Buscar o último fechamento
    ultimo_fechamento = get_ultimo_fechamento(db)
    
    # Se houver um fechamento, considerar vendas a partir da data dele
    if ultimo_fechamento:
        data_inicio = ultimo_fechamento.data_fechamento
    else:
        # Se não houver fechamento, considerar vendas do dia
        data_inicio = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Buscar vendas a partir da data do último fechamento
    vendas = db.query(models.Venda).filter(
        models.Venda.data > data_inicio
    ).all()
    
    # Calcular totais
    total = sum(float(v.valor) for v in vendas)
    total_dinheiro = sum(float(v.valor) for v in vendas if v.forma_pagamento == "DINHEIRO")
    total_pix = sum(float(v.valor) for v in vendas if v.forma_pagamento == "PIX")
    total_cartao = sum(
        float(v.valor) for v in vendas 
        if v.forma_pagamento in ["CARTAO_CREDITO", "CARTAO_DEBITO"]
    )
    
    # Ticket médio
    ticket_medio = total / len(vendas) if vendas else 0
    
    return {
        "vendas": vendas,
        "total": total,
        "total_dinheiro": total_dinheiro,
        "total_pix": total_pix,
        "total_cartao": total_cartao,
        "quantidade": len(vendas),
        "ticket_medio": ticket_medio
    }


def get_vendas_periodo(db: Session, dias: int = 7):
    """Retorna vendas dos últimos N dias"""
    data_inicio = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=dias)
    
    vendas = db.query(models.Venda).filter(
        models.Venda.data >= data_inicio
    ).order_by(models.Venda.data.desc()).all()
    
    return vendas
