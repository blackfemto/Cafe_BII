from pydantic import BaseModel


# ==========================
# CATEGORIA
# ==========================

class CategoriaCreate(BaseModel):

    nome: str



# ==========================
# PRODUTO
# ==========================

class ProdutoCreate(BaseModel):

    nome: str

    descricao: str | None = None

    preco: float

    categoria_id: int