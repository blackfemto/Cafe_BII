from pydantic import BaseModel


class ProdutoCreate(BaseModel):
    nome: str
    descricao: str | None = None
    preco: float
    categoria_id: int