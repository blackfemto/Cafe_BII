from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
)

from sqlalchemy.orm import relationship

from app.database import Base


# ==========================
# CATEGORIAS
# ==========================

class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True)

    nome = Column(String(100), nullable=False, unique=True)

    produtos = relationship(
        "Produto",
        back_populates="categoria"
    )


# ==========================
# PRODUTOS
# ==========================

class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)

    nome = Column(String(120), nullable=False)

    descricao = Column(String(255))

    preco = Column(Numeric(10, 2), nullable=False)

    ativo = Column(Boolean, default=True)

    ordem = Column(Integer, default=0)

    categoria_id = Column(
        Integer,
        ForeignKey("categorias.id"),
        nullable=False
    )

    categoria = relationship(
        "Categoria",
        back_populates="produtos"
    )

    itens = relationship(
        "ItemComanda",
        back_populates="produto"
    )


# ==========================
# COMANDAS
# ==========================

class Comanda(Base):
    __tablename__ = "comandas"

    id = Column(Integer, primary_key=True, index=True)

    codigo = Column(String(20), unique=True, nullable=False)

    nome_cliente = Column(String(120), nullable=False)

    observacao = Column(String(255))

    status = Column(String(30), default="ABERTA")

    data_abertura = Column(
        DateTime,
        default=datetime.now
    )

    data_fechamento = Column(DateTime)

    total = Column(
        Numeric(10, 2),
        default=0
    )

    itens = relationship(
        "ItemComanda",
        back_populates="comanda",
        cascade="all, delete-orphan"
    )


# ==========================
# ITENS DA COMANDA
# ==========================

class ItemComanda(Base):
    __tablename__ = "itens_comanda"

    id = Column(Integer, primary_key=True, index=True)

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
        nullable=False,
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


# ==========================
# FECHAMENTO DE CAIXA
# ==========================

class FechamentoCaixa(Base):
    __tablename__ = "fechamentos_caixa"

    id = Column(Integer, primary_key=True, index=True)

    data = Column(
        DateTime,
        default=datetime.now
    )

    total = Column(
        Numeric(10, 2),
        default=0
    )

    pix = Column(
        Numeric(10, 2),
        default=0
    )

    dinheiro = Column(
        Numeric(10, 2),
        default=0
    )

    cartao = Column(
        Numeric(10, 2),
        default=0
    )