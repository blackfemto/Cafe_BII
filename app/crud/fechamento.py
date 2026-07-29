from sqlalchemy.orm import Session
from datetime import datetime
from app import models


def criar_fechamento(db: Session, usuario_id: int):
    """Cria um fechamento de caixa e zera o período atual"""
    
    # Buscar o último fechamento
    ultimo = db.query(models.FechamentoCaixa).order_by(
        models.FechamentoCaixa.data_fechamento.desc()
    ).first()
    
    # Buscar vendas a partir do último fechamento
    if ultimo:
        vendas = db.query(models.Venda).filter(
            models.Venda.data > ultimo.data_fechamento
        ).all()
    else:
        vendas = db.query(models.Venda).all()
    
    if not vendas:
        return None  # Não há vendas para fechar
    
    # Calcular totais
    total = sum(v.valor for v in vendas)
    total_dinheiro = sum(v.valor for v in vendas if v.forma_pagamento == "DINHEIRO")
    total_pix = sum(v.valor for v in vendas if v.forma_pagamento == "PIX")
    total_cartao = sum(v.valor for v in vendas if v.forma_pagamento in ["CARTAO_CREDITO", "CARTAO_DEBITO"])
    
    # Criar fechamento
    fechamento = models.FechamentoCaixa(
        data_fechamento=datetime.now(),
        total_vendas=total,
        total_dinheiro=total_dinheiro,
        total_pix=total_pix,
        total_cartao=total_cartao,
        quantidade_vendas=len(vendas),
        usuario_id=usuario_id
    )
    
    db.add(fechamento)
    db.commit()
    db.refresh(fechamento)
    
    return fechamento


def get_ultimo_fechamento(db: Session):
    return db.query(models.FechamentoCaixa).order_by(
        models.FechamentoCaixa.data_fechamento.desc()
    ).first()


def listar_fechamentos(db: Session, limite: int = 30):
    return db.query(models.FechamentoCaixa).order_by(
        models.FechamentoCaixa.data_fechamento.desc()
    ).limit(limite).all()
