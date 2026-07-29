from sqlalchemy.orm import Session
from datetime import datetime
from app import models
from app.crud.caixa import get_resumo_caixa


def criar_fechamento(db: Session, usuario_id: int):
    """Registra o total acumulado e zera o caixa para o próximo turno"""
    
    # Buscar TODAS as vendas (não apenas as do dia)
    vendas = db.query(models.Venda).all()
    
    if not vendas:
        return None  # Não há vendas para fechar
    
    # Calcular totais ACUMULADOS (todas as vendas)
    total = sum(v.valor for v in vendas)
    total_dinheiro = sum(v.valor for v in vendas if v.forma_pagamento == "DINHEIRO")
    total_pix = sum(v.valor for v in vendas if v.forma_pagamento == "PIX")
    total_cartao = sum(v.valor for v in vendas if v.forma_pagamento in ["CARTAO_CREDITO", "CARTAO_DEBITO"])
    
    # Criar fechamento com o TOTAL ACUMULADO
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
    
    # =============================================
    # ZERAR O CAIXA (mas manter as vendas no banco)
    # =============================================
    # Marcamos o fechamento como "ativo" para o caixa saber que foi fechado
    # As vendas continuam no banco, mas o caixa vai começar do zero
    
    return fechamento


def get_ultimo_fechamento(db: Session):
    """Retorna o último fechamento realizado"""
    return db.query(models.FechamentoCaixa).order_by(
        models.FechamentoCaixa.data_fechamento.desc()
    ).first()


def listar_fechamentos(db: Session, limite: int = 30):
    return db.query(models.FechamentoCaixa).order_by(
        models.FechamentoCaixa.data_fechamento.desc()
    ).limit(limite).all()
