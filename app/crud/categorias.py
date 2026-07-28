from sqlalchemy.orm import Session

from app import models
from app.schemas import CategoriaCreate


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
def buscar_categoria(db: Session, categoria_id: int):
    return db.query(models.Categoria).filter(models.Categoria.id == categoria_id).first()


def atualizar_categoria(db: Session, categoria_id: int, nome: str):
    categoria = buscar_categoria(db, categoria_id)
    if not categoria:
        return None
    
    categoria.nome = nome
    db.commit()
    db.refresh(categoria)
    return categoria


def deletar_categoria(db: Session, categoria_id: int):
    categoria = buscar_categoria(db, categoria_id)
    if not categoria:
        return False
    
    # Verificar se tem produtos vinculados
    from app import models
    produtos = db.query(models.Produto).filter(models.Produto.categoria_id == categoria_id).count()
    if produtos > 0:
        return False  # Não pode deletar categoria com produtos
    
    db.delete(categoria)
    db.commit()
    return True
