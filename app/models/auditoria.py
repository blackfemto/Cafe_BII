from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    JSON,
    ForeignKey
)
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class Auditoria(Base):
    __tablename__ = "auditoria"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id"),
        nullable=True
    )

    acao = Column(
        String(100),
        nullable=False
    )

    comanda_id = Column(
        Integer,
        ForeignKey("comandas.id"),
        nullable=True
    )

    detalhes = Column(
        JSON,
        nullable=True
    )

    ip = Column(
        String(45),
        nullable=True
    )

    data = Column(
        DateTime,
        default=datetime.now
    )

    usuario = relationship(
        "Usuario",
        back_populates="auditoria"
    )

    comanda = relationship(
        "Comanda",
        back_populates="auditoria"
    )
