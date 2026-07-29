from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app import models
from app.crud.caixa import get_resumo_caixa


def criar_fechamento(db: Session, usuario_id: int):
    """Cria um fechamento de caixa, apenas se houver vendas novas desde o último fechamento"""
    
    # Verificar o último fechamento
    ultimo = db.query(models.FechamentoCaixa).order_by(
        models.FechamentoCaixa.data_fechamento.desc()
    ).first()
    
    # Se houver um fechamento recente (menos de 5 minutos), não criar outro
    if ultimo:
        tempo_decorrido = datetime.now() - ultimo.data_fechamento
        if tempo_decorrido.total_seconds() < 300:  # 5 minutos
            return ultimo  # Retorna o mesmo fechamento
    
    # Buscar vendas após o último fechamento
    if ultimo:
        vendas = db.query(models.Venda).filter(
            models.Venda.data > ultimo.data_fechamento
        ).all()
    else:
        vendas = db.query(models.Venda).all()
    
    # Se não houver vendas novas, não criar fechamento
    if not vendas:
        return None
    
    # Calcular totais
    total = sum(v.valor for v in vendas)
    total_dinheiro = sum(v.valor for v in vendas if v.forma_pagamento == "DINHEIRO")
    total_pix = sum(v.valor for v in vendas if v.forma_pagamento == "PIX")
    total_cartao = sum(v.valor for v in vendas if v.forma_pagamento in ["CARTAO_CREDITO", "CARTAO_DEBITO"])
    
    # Criar novo fechamento
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


def listar_fechamentos(db: Session, limite: int = 30):
    return db.query(models.FechamentoCaixa).order_by(
        models.FechamentoCaixa.data_fechamento.desc()
    ).limit(limite).all()
