from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Numeric
)

from sqlalchemy.orm import relationship

from app.database import Base


class ItemComanda(Base):
    __tablename__ = "itens_comanda"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    comanda_id = Column(
        Integer,
        ForeignKey("comandas.id"),
        nullable=False
    )

    produto_id = Column(
        Integer,
        ForeignKey("produtos.id"),
        nullable=False
    )

    quantidade = Column(
        Integer,
        default=1
    )

    preco_unitario = Column(
        Numeric(10, 2),
        nullable=False
    )

    subtotal = Column(
        Numeric(10, 2),
        nullable=False
    )

    comanda = relationship(
        "Comanda",
        back_populates="itens"
    )

    produto = relationship(
        "Produto",
        back_populates="itens"
    )