from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models
from app.schemas.comandas import ComandaCreate


def criar_comanda(
    db: Session,
    comanda: ComandaCreate
):
    from datetime import datetime
    ultima = db.query(models.Comanda).order_by(models.Comanda.id.desc()).first()
    codigo = f"CMD-{datetime.now().strftime('%Y%m%d')}-{(ultima.id + 1) if ultima else 1:04d}"
    
    nova = models.Comanda(
        codigo=codigo,
        nome_cliente=comanda.cliente,
        status="ABERTA"
    )
    db.add(nova)
    db.commit()
    db.refresh(nova)
    return nova


def listar_comandas_abertas(db: Session):
    """Retorna apenas comandas ABERTAS"""
    return (
        db.query(models.Comanda)
        .filter(models.Comanda.status == "ABERTA")
        .order_by(models.Comanda.id.desc())
        .all()
    )


def buscar_comanda(db: Session, comanda_id: int):
    return (
        db.query(models.Comanda)
        .filter(models.Comanda.id == comanda_id)
        .first()
    )


def calcular_total(db: Session, comanda_id: int):
    total = (
        db.query(
            func.sum(models.ItemComanda.subtotal)
        )
        .filter(
            models.ItemComanda.comanda_id == comanda_id
        )
        .scalar()
    )
    return total or 0


def fechar_comanda(
    db: Session,
    comanda_id: int,
    forma_pagamento: str
):
    from datetime import datetime
    
    comanda = buscar_comanda(db, comanda_id)
    if not comanda:
        raise ValueError("Comanda não encontrada")
    
    if comanda.status != "ABERTA":
        raise ValueError("Comanda já está fechada")
    
    total = calcular_total(db, comanda_id)
    if total == 0:
        raise ValueError("Comanda vazia não pode ser fechada")
    
    comanda.status = "FECHADA"
    comanda.data_fechamento = datetime.now()
    comanda.total = total
    
    from app.models import Venda
    venda = Venda(
        comanda_id=comanda_id,
        valor=total,
        forma_pagamento=forma_pagamento
    )
    db.add(venda)
    
    db.commit()
    db.refresh(comanda)
    return comanda


def limpar_comandas_fechadas(db: Session):
    """Remove todas as comandas que estão FECHADAS (usado no fechamento de caixa)"""
    comandas_fechadas = db.query(models.Comanda).filter(
        models.Comanda.status == "FECHADA"
    ).all()
    
    for comanda in comandas_fechadas:
        # Remove os itens da comanda
        db.query(models.ItemComanda).filter(
            models.ItemComanda.comanda_id == comanda.id
        ).delete()
        # Remove a comanda
        db.delete(comanda)
    
    db.commit()
    return len(comandas_fechadas)
