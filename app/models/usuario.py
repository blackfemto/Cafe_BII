from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    
    nome = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    
    nivel = Column(String(20), default="GERENTE")
    ativo = Column(Boolean, default=True)
    
    data_criacao = Column(DateTime, default=datetime.now)
    ultimo_login = Column(DateTime, nullable=True)
    
    comandas = relationship("Comanda", back_populates="usuario")
    vendas = relationship("Venda", back_populates="usuario")
    auditoria = relationship("Auditoria", back_populates="usuario")
