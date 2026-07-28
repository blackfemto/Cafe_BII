from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models
from app.schemas.comandas import ComandaCreate


def criar_comanda(
    db: Session,
    comanda: ComandaCreate
):
    # Gerar código único para a comanda
    ultima = db.query(models.Comanda).order_by(models.Comanda.id.desc()).first()
    from datetime import datetime
    codigo = f"CMD-{datetime.now().strftime('%Y%m%d')}-{(ultima.id + 1) if ultima else 1:04d}"
    
    nova = models.Comanda(
        codigo=codigo,
        nome_cliente=comanda.cliente,  # ← CORRIGIDO: cliente → nome_cliente
        status="ABERTA"
    )

    db.add(nova)
    db.commit()
    db.refresh(nova)

    return nova


def listar_comandas(
    db: Session
):
    return (
        db.query(models.Comanda)
        .order_by(models.Comanda.id.desc())
        .all()
    )


def buscar_comanda(
    db: Session,
    comanda_id: int
):
    return (
        db.query(models.Comanda)
        .filter(models.Comanda.id == comanda_id)
        .first()
    )


def calcular_total(
    db: Session,
    comanda_id: int
):
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
    """Fecha uma comanda e registra a venda"""
    from datetime import datetime
    
    comanda = buscar_comanda(db, comanda_id)
    if not comanda:
        raise ValueError("Comanda não encontrada")
    
    if comanda.status != "ABERTA":
        raise ValueError("Comanda já está fechada")
    
    total = calcular_total(db, comanda_id)
    if total == 0:
        raise ValueError("Comanda vazia não pode ser fechada")
    
    # Atualizar comanda
    comanda.status = "FECHADA"
    comanda.data_fechamento = datetime.now()
    comanda.total = total
    
    # Registrar venda
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

def fechar_comanda(
    db: Session,
    comanda_id: int,
    forma_pagamento: str
):
    """Fecha uma comanda e registra a venda, baixando o estoque"""
    from datetime import datetime
    from app.crud.produtos import baixar_estoque
    
    comanda = buscar_comanda(db, comanda_id)
    if not comanda:
        raise ValueError("Comanda não encontrada")
    
    if comanda.status != "ABERTA":
        raise ValueError("Comanda já está fechada")
    
    total = calcular_total(db, comanda_id)
    if total == 0:
        raise ValueError("Comanda vazia não pode ser fechada")
    
    # Verificar e baixar estoque de cada item
    itens = db.query(models.ItemComanda).filter(
        models.ItemComanda.comanda_id == comanda_id
    ).all()
    
    for item in itens:
        if not baixar_estoque(db, item.produto_id, item.quantidade):
            raise ValueError(f"Estoque insuficiente para {item.produto.nome}")
    
    # Atualizar comanda
    comanda.status = "FECHADA"
    comanda.data_fechamento = datetime.now()
    comanda.total = total
    
    # Registrar venda
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

def cancelar_comanda(db: Session, comanda_id: int):
    """Reabre uma comanda fechada (apenas SuperRoot)"""
    comanda = buscar_comanda(db, comanda_id)
    if not comanda:
        raise ValueError("Comanda não encontrada")
    
    # Reabrir comanda
    comanda.status = "ABERTA"
    comanda.data_fechamento = None
    
    # Remover venda associada
    from app.models import Venda
    venda = db.query(Venda).filter(Venda.comanda_id == comanda_id).first()
    if venda:
        db.delete(venda)
    
    db.commit()
    db.refresh(comanda)
    return comanda


def deletar_comanda_permanente(db: Session, comanda_id: int):
    """Deleta uma comanda permanentemente (apenas SuperRoot)"""
    comanda = buscar_comanda(db, comanda_id)
    if not comanda:
        raise ValueError("Comanda não encontrada")
    
    # Deletar itens da comanda
    db.query(models.ItemComanda).filter(models.ItemComanda.comanda_id == comanda_id).delete()
    
    # Deletar venda associada
    from app.models import Venda
    db.query(Venda).filter(Venda.comanda_id == comanda_id).delete()
    
    # Deletar comanda
    db.delete(comanda)
    db.commit()
    return True
