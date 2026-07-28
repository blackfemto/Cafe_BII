from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Numeric,
    String,
    DateTime
)
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class Venda(Base):
    __tablename__ = "vendas"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    comanda_id = Column(
        Integer,
        ForeignKey("comandas.id"),
        nullable=False,
        unique=True
    )

    valor = Column(
        Numeric(10, 2),
        nullable=False
    )

    forma_pagamento = Column(
        String(20),
        nullable=False
    )

    data = Column(
        DateTime,
        default=datetime.now
    )

    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id"),
        nullable=True
    )

    comanda = relationship(
        "Comanda",
        back_populates="venda"
    )

    usuario = relationship(
        "Usuario",
        back_populates="vendas"
    )
