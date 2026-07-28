from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Numeric,
    ForeignKey
)
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class Comanda(Base):
    __tablename__ = "comandas"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    codigo = Column(
        String(20),
        unique=True,
        nullable=False
    )

    nome_cliente = Column(
        String(120),
        nullable=False
    )

    observacao = Column(
        String(255),
        nullable=True
    )

    status = Column(
        String(30),
        default="ABERTA"
    )

    data_abertura = Column(
        DateTime,
        default=datetime.now
    )

    data_fechamento = Column(
        DateTime,
        nullable=True
    )

    total = Column(
        Numeric(10, 2),
        default=0
    )

    fechada_por = Column(
        Integer,
        nullable=True
    )

    # CHAVE ESTRANGEIRA PARA USUÁRIO
    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id"),
        nullable=True
    )

    itens = relationship(
        "ItemComanda",
        back_populates="comanda",
        cascade="all, delete-orphan"
    )

    venda = relationship(
        "Venda",
        back_populates="comanda",
        uselist=False,
        cascade="all, delete-orphan"
    )

    usuario = relationship(
        "Usuario",
        back_populates="comandas"
    )

    auditoria = relationship(
        "Auditoria",
        back_populates="comanda"
    )
