from sqlalchemy.orm import Session
from datetime import datetime
from app import models
from app.crud.caixa import get_resumo_caixa


def criar_fechamento(db: Session, usuario_id: int):
    """Cria um fechamento de caixa com os dados do dia"""
    dados = get_resumo_caixa(db)

    fechamento = models.FechamentoCaixa(
        data_fechamento=datetime.now(),
        total_vendas=dados["total"],
        total_dinheiro=dados["total_dinheiro"],
        total_pix=dados["total_pix"],
        total_cartao=dados["total_cartao"],
        quantidade_vendas=dados["quantidade"],
        usuario_id=usuario_id
    )

    db.add(fechamento)
    db.commit()
    db.refresh(fechamento)
    return fechamento


def listar_fechamentos(db: Session, limite: int = 30):
    """Lista os últimos fechamentos"""
    return db.query(models.FechamentoCaixa).order_by(
        models.FechamentoCaixa.data_fechamento.desc()
    ).limit(limite).all()
