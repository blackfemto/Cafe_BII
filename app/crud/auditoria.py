from sqlalchemy.orm import Session
from app import models
from datetime import datetime


def registrar_auditoria(
    db: Session,
    usuario_id: int,
    acao: str,
    comanda_id: int = None,
    detalhes: dict = None,
    ip: str = None
):
    auditoria = models.Auditoria(
        usuario_id=usuario_id,
        acao=acao,
        comanda_id=comanda_id,
        detalhes=detalhes,
        ip=ip,
        data=datetime.now()
    )
    db.add(auditoria)
    db.commit()
    return auditoria


def listar_auditoria(db: Session, limite: int = 100):
    return db.query(models.Auditoria).order_by(
        models.Auditoria.data.desc()
    ).limit(limite).all()
