from sqlalchemy import Column, Integer, String, DateTime, Numeric, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class HistoricoComanda(Base):
    __tablename__ = "historico_comandas"

    id = Column(Integer, primary_key=True, index=True)
    
    # Dados da comanda
    comanda_id = Column(Integer, nullable=False)
    cliente = Column(String(120), nullable=False)
    codigo = Column(String(20), nullable=False)
    total = Column(Numeric(10, 2), nullable=False)
    data_abertura = Column(DateTime, nullable=False)
    data_fechamento = Column(DateTime, nullable=False)
    
    # Dados da venda
    forma_pagamento = Column(String(20), nullable=False)
    valor_pago = Column(Numeric(10, 2), nullable=False)
    
    # Itens da comanda (salvos como JSON)
    itens = Column(JSON, nullable=False)  # lista de {produto, quantidade, subtotal}
    
    # Relacionamento com o fechamento
    fechamento_id = Column(Integer, ForeignKey("fechamentos_caixa.id"), nullable=False)
    fechamento = relationship("FechamentoCaixa", back_populates="comandas")
