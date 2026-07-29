from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app import models


def ajustar_fuso(data_utc):
    """Converte UTC para UTC-3"""
    return data_utc - timedelta(hours=3)


def criar_fechamento(db: Session, usuario_id: int):
    """Cria um fechamento de caixa e zera o período atual"""
    
    ultimo = db.query(models.FechamentoCaixa).order_by(
        models.FechamentoCaixa.data_fechamento.desc()
    ).first()
    
    if ultimo:
        vendas = db.query(models.Venda).filter(
            models.Venda.data > ultimo.data_fechamento
        ).all()
    else:
        vendas = db.query(models.Venda).all()
    
    if not vendas:
        return None
    
    total = sum(v.valor for v in vendas)
    total_dinheiro = sum(v.valor for v in vendas if v.forma_pagamento == "DINHEIRO")
    total_pix = sum(v.valor for v in vendas if v.forma_pagamento == "PIX")
    total_cartao = sum(v.valor for v in vendas if v.forma_pagamento in ["CARTAO_CREDITO", "CARTAO_DEBITO"])
    
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


def get_ranking_gerentes(db: Session):
    """Retorna o ranking de desempenho dos gerentes com a data do turno (UTc-3)"""
    
    ranking = db.query(
        models.Usuario.nome,
        models.Usuario.id,
        models.FechamentoCaixa.total_vendas,
        models.FechamentoCaixa.quantidade_vendas,
        models.FechamentoCaixa.data_fechamento
    ).join(
        models.Usuario, models.FechamentoCaixa.usuario_id == models.Usuario.id
    ).order_by(
        models.FechamentoCaixa.total_vendas.desc()
    ).all()
    
    resultado = []
    for r in ranking:
        ticket_medio = r[2] / r[3] if r[3] > 0 else 0
        # Ajustar a data para UTC-3 (Brasil)
        data_br = ajustar_fuso(r[4]) if r[4] else None
        resultado.append({
            "nome": r[0],
            "usuario_id": r[1],
            "total": float(r[2]),
            "quantidade": r[3],
            "ticket_medio": float(ticket_medio),
            "data": data_br.strftime("%d/%m/%Y") if data_br else "N/A"
        })
    
    return resultado
