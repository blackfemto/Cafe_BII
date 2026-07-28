from sqlalchemy.orm import Session

from app import models
from app.schemas import ProdutoCreate


def criar_produto(
    db: Session,
    produto: ProdutoCreate
):
    novo_produto = models.Produto(
        nome=produto.nome,
        descricao=produto.descricao,
        preco=produto.preco,
        categoria_id=produto.categoria_id,
        ativo=True,
        quantidade_estoque=0,  # Começa com 0
        estoque_minimo=5
    )
    db.add(novo_produto)
    db.commit()
    db.refresh(novo_produto)
    return novo_produto


def listar_produtos(db: Session):
    return (
        db.query(models.Produto)
        .filter(models.Produto.ativo == True)
        .order_by(models.Produto.nome)
        .all()
    )


def buscar_produto(db: Session, produto_id: int):
    return (
        db.query(models.Produto)
        .filter(models.Produto.id == produto_id)
        .first()
    )


def atualizar_produto(
    db: Session,
    produto_id: int,
    produto: ProdutoCreate
):
    produto_db = buscar_produto(db, produto_id)
    if not produto_db:
        return None

    produto_db.nome = produto.nome
    produto_db.descricao = produto.descricao
    produto_db.preco = produto.preco
    produto_db.categoria_id = produto.categoria_id

    db.commit()
    db.refresh(produto_db)
    return produto_db


def deletar_produto(db: Session, produto_id: int):
    produto = buscar_produto(db, produto_id)
    if produto:
        produto.ativo = False
        db.commit()
        return True
    return False


def baixar_estoque(db: Session, produto_id: int, quantidade: int):
    """Baixa o estoque de um produto"""
    produto = buscar_produto(db, produto_id)
    if not produto:
        return False
    
    if produto.quantidade_estoque < quantidade:
        return False  # Estoque insuficiente
    
    produto.quantidade_estoque -= quantidade
    db.commit()
    return True


def repor_estoque(db: Session, produto_id: int, quantidade: int):
    """Aumenta o estoque de um produto"""
    produto = buscar_produto(db, produto_id)
    if not produto:
        return False
    
    produto.quantidade_estoque += quantidade
    db.commit()
    return True


def listar_produtos_com_estoque_baixo(db: Session):
    """Lista produtos com estoque abaixo do mínimo"""
    return (
        db.query(models.Produto)
        .filter(
            models.Produto.ativo == True,
            models.Produto.quantidade_estoque <= models.Produto.estoque_minimo
        )
        .all()
    )

def atualizar_produto(
    db: Session,
    produto_id: int,
    produto_data
):
    """Atualiza um produto existente"""
    produto = buscar_produto(db, produto_id)
    if not produto:
        return None
    
    produto.nome = produto_data.nome
    produto.descricao = produto_data.descricao
    produto.preco = produto_data.preco
    produto.categoria_id = produto_data.categoria_id
    
    db.commit()
    db.refresh(produto)
    return produto
