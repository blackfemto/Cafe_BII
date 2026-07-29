from sqlalchemy.orm import Session
from app import models
from datetime import datetime


def salvar_comandas_fechadas(db: Session, fechamento_id: int):
    """Salva todas as comandas FECHADAS no histórico"""
    
    comandas_fechadas = db.query(models.Comanda).filter(
        models.Comanda.status == "FECHADA"
    ).all()
    
    registros = []
    for comanda in comandas_fechadas:
        # Buscar a venda associada
        venda = db.query(models.Venda).filter(
            models.Venda.comanda_id == comanda.id
        ).first()
        
        if not venda:
            continue
        
        # Buscar os itens da comanda
        itens = []
        for item in comanda.itens:
            itens.append({
                "produto": item.produto.nome,
                "quantidade": item.quantidade,
                "subtotal": float(item.subtotal)
            })
        
        # Salvar no histórico
        historico = models.HistoricoComanda(
            comanda_id=comanda.id,
            cliente=comanda.nome_cliente,
            codigo=comanda.codigo,
            total=comanda.total,
            data_abertura=comanda.data_abertura,
            data_fechamento=comanda.data_fechamento,
            forma_pagamento=venda.forma_pagamento,
            valor_pago=venda.valor,
            itens=itens,
            fechamento_id=fechamento_id
        )
        db.add(historico)
        registros.append(historico)
    
    db.commit()
    return registros


def listar_historico_por_fechamento(db: Session, fechamento_id: int):
    """Lista todas as comandas de um fechamento específico"""
    return db.query(models.HistoricoComanda).filter(
        models.HistoricoComanda.fechamento_id == fechamento_id
    ).all()
