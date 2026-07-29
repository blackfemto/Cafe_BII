from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class FechamentoCaixa(Base):
    __tablename__ = "fechamentos_caixa"

    id = Column(Integer, primary_key=True, index=True)

    data_fechamento = Column(DateTime, default=datetime.now)

    total_vendas = Column(Numeric(10, 2), default=0)
    total_dinheiro = Column(Numeric(10, 2), default=0)
    total_pix = Column(Numeric(10, 2), default=0)
    total_cartao = Column(Numeric(10, 2), default=0)

    quantidade_vendas = Column(Integer, default=0)

    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    usuario = relationship("Usuario", back_populates="fechamentos")
    comandas = relationship("HistoricoComanda", back_populates="fechamento")
