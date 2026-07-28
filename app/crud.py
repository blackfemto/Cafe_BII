from sqlalchemy.orm import Session

from app import models
from app.schemas import (
    CategoriaCreate,
    ProdutoCreate
)


# ==========================
# CATEGORIAS
# ==========================


def criar_categoria(
    db: Session,
    categoria: CategoriaCreate
):

    nova_categoria = models.Categoria(
        nome=categoria.nome
    )

    db.add(nova_categoria)

    db.commit()

    db.refresh(nova_categoria)

    return nova_categoria



def listar_categorias(
    db: Session
):

    return db.query(
        models.Categoria
    ).all()



# ==========================
# PRODUTOS
# ==========================


def criar_produto(
    db: Session,
    produto: ProdutoCreate
):

    novo_produto = models.Produto(

        nome=produto.nome,

        descricao=produto.descricao,

        preco=produto.preco,

        categoria_id=produto.categoria_id

    )


    db.add(novo_produto)

    db.commit()

    db.refresh(novo_produto)


    return novo_produto




def listar_produtos(
    db: Session
):

    return db.query(
        models.Produto
    ).all()