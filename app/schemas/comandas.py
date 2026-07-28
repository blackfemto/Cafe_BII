from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class ComandaCreate(BaseModel):
    cliente: str  # Mantém 'cliente' para compatibilidade com o formulário


class ItemComandaCreate(BaseModel):
    produto_id: int
    quantidade: int = 1


class ItemComandaResponse(BaseModel):
    id: int
    produto_id: int
    quantidade: int
    preco_unitario: float
    subtotal: float
    
    class Config:
        from_attributes = True


class ComandaResponse(BaseModel):
    id: int
    codigo: str
    nome_cliente: str  # ← CORRIGIDO: cliente → nome_cliente
    status: str
    data_abertura: datetime
    data_fechamento: Optional[datetime] = None
    total: float = 0
    itens: List[ItemComandaResponse] = []
    
    class Config:
        from_attributes = True
