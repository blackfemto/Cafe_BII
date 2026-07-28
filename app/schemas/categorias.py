from pydantic import BaseModel


class CategoriaCreate(BaseModel):
    nome: str