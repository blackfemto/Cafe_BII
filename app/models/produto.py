from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    Numeric,
    String
)
from sqlalchemy.orm import relationship

from app.database import Base


class Produto(Base):
    __tablename__ = "produtos"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    nome = Column(
        String(120),
        nullable=False
    )

    descricao = Column(
        String(255)
    )

    preco = Column(
        Numeric(10, 2),
        nullable=False
    )

    ativo = Column(
        Boolean,
        default=True
    )

    ordem = Column(
        Integer,
        default=0
    )

    categoria_id = Column(
        Integer,
        ForeignKey("categorias.id"),
        nullable=False
    )

    # NOVOS CAMPOS DE ESTOQUE
    quantidade_estoque = Column(
        Integer,
        default=0
    )

    estoque_minimo = Column(
        Integer,
        default=5
    )

    categoria = relationship(
        "Categoria",
        back_populates="produtos"
    )

    itens = relationship(
        "ItemComanda",
        back_populates="produto"
    )
