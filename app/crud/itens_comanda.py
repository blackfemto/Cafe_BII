from sqlalchemy.orm import Session

from app import models


def adicionar_produto(
    db: Session,
    comanda_id: int,
    produto_id: int
):

    produto = (
        db.query(models.Produto)
        .filter(models.Produto.id == produto_id)
        .first()
    )

    if not produto:
        return None

    item = (
        db.query(models.ItemComanda)
        .filter(
            models.ItemComanda.comanda_id == comanda_id,
            models.ItemComanda.produto_id == produto_id
        )
        .first()
    )

    if item:

        item.quantidade += 1

        item.subtotal = (
            item.quantidade *
            item.preco_unitario
        )

    else:

        item = models.ItemComanda(
            comanda_id=comanda_id,
            produto_id=produto.id,
            quantidade=1,
            preco_unitario=produto.preco,
            subtotal=produto.preco
        )

        db.add(item)

    db.commit()
    db.refresh(item)

    return item


def diminuir_quantidade(
    db: Session,
    item_id: int
):

    item = (
        db.query(models.ItemComanda)
        .filter(models.ItemComanda.id == item_id)
        .first()
    )

    if not item:
        return

    if item.quantidade > 1:

        item.quantidade -= 1

        item.subtotal = (
            item.quantidade *
            item.preco_unitario
        )

    else:

        db.delete(item)

    db.commit()


def remover_item(
    db: Session,
    item_id: int
):

    item = (
        db.query(models.ItemComanda)
        .filter(models.ItemComanda.id == item_id)
        .first()
    )

    if item:

        db.delete(item)

        db.commit()