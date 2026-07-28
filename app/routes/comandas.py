from fastapi import (
    APIRouter,
    Depends,
    Request,
    Form,
    status
)

from fastapi.responses import (
    HTMLResponse,
    RedirectResponse
)

from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.comandas import ComandaCreate
from app.crud import comandas as crud
from app.crud import itens_comanda
from app import models

router = APIRouter()

templates = Jinja2Templates(
    directory="templates"
)


@router.get(
    "/comandas",
    response_class=HTMLResponse
)
def pagina_comandas(
    request: Request,
    db: Session = Depends(get_db)
):

    return templates.TemplateResponse(
        request=request,
        name="comandas.html",
        context={
            "request": request,
            "comandas": crud.listar_comandas(db)
        }
    )


@router.post("/comandas/criar")
def criar_comanda(

    cliente: str = Form(...),

    db: Session = Depends(get_db)

):

    crud.criar_comanda(

        db,

        ComandaCreate(
            cliente=cliente
        )

    )

    return RedirectResponse(
        "/comandas",
        status_code=303
    )


@router.get(
    "/comandas/{comanda_id}",
    response_class=HTMLResponse
)
def visualizar_comanda(

    comanda_id: int,

    request: Request,

    db: Session = Depends(get_db)

):

    comanda = crud.buscar_comanda(
        db,
        comanda_id
    )

    produtos = (
        db.query(models.Produto)
        .filter(
            models.Produto.ativo == True
        )
        .all()
    )

    # CALCULAR O TOTAL
    total = crud.calcular_total(db, comanda_id)

    return templates.TemplateResponse(

        request=request,

        name="comanda_detalhe.html",

        context={

            "request": request,

            "comanda": comanda,

            "produtos": produtos,

            "total": total  # <- ADICIONADO!

        }

    )


@router.post(
    "/comandas/{comanda_id}/adicionar/{produto_id}"
)
def adicionar_produto(

    comanda_id: int,

    produto_id: int,

    db: Session = Depends(get_db)

):

    itens_comanda.adicionar_produto(

        db,

        comanda_id,

        produto_id

    )

    return RedirectResponse(

        url=f"/comandas/{comanda_id}",

        status_code=status.HTTP_303_SEE_OTHER

    )


@router.post(
    "/comandas/{comanda_id}/menos/{item_id}"
)
def diminuir_item(

    comanda_id: int,

    item_id: int,

    db: Session = Depends(get_db)

):

    itens_comanda.diminuir_quantidade(
        db,
        item_id
    )

    return RedirectResponse(

        url=f"/comandas/{comanda_id}",

        status_code=status.HTTP_303_SEE_OTHER

    )


@router.post(
    "/comandas/{comanda_id}/remover/{item_id}"
)
def remover_item(

    comanda_id: int,

    item_id: int,

    db: Session = Depends(get_db)

):

    itens_comanda.remover_item(
        db,
        item_id
    )

    return RedirectResponse(

        url=f"/comandas/{comanda_id}",

        status_code=status.HTTP_303_SEE_OTHER

    )


# ========== ROTA DE FECHAR COMANDA ==========
@router.post("/comandas/{comanda_id}/fechar")
def fechar_comanda_route(
    comanda_id: int,
    forma_pagamento: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        from app.crud.comandas import fechar_comanda
        fechar_comanda(db, comanda_id, forma_pagamento)
        return RedirectResponse(
            url=f"/comandas/{comanda_id}?sucesso=Comanda fechada com sucesso!",
            status_code=303
        )
    except ValueError as e:
        return RedirectResponse(
            url=f"/comandas/{comanda_id}?erro={str(e)}",
            status_code=303
        )

# ========== ROTAS PARA SUPEROOT ==========
@router.post("/comandas/{comanda_id}/cancelar")
def cancelar_comanda_route(
    comanda_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    # Verifica se é SuperRoot
    if request.cookies.get("user_nivel") != "SUPER_ROOT":
        return RedirectResponse(url="/login?erro=Acesso negado!", status_code=303)
    
    try:
        from app.crud.comandas import cancelar_comanda
        cancelar_comanda(db, comanda_id)
        return RedirectResponse(
            url=f"/comandas/{comanda_id}?sucesso=Comanda reaberta com sucesso!",
            status_code=303
        )
    except ValueError as e:
        return RedirectResponse(
            url=f"/comandas/{comanda_id}?erro={str(e)}",
            status_code=303
        )


@router.post("/comandas/{comanda_id}/deletar")
def deletar_comanda_route(
    comanda_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    # Verifica se é SuperRoot
    if request.cookies.get("user_nivel") != "SUPER_ROOT":
        return RedirectResponse(url="/login?erro=Acesso negado!", status_code=303)
    
    try:
        from app.crud.comandas import deletar_comanda_permanente
        deletar_comanda_permanente(db, comanda_id)
        return RedirectResponse(
            url="/comandas?sucesso=Comanda deletada permanentemente!",
            status_code=303
        )
    except ValueError as e:
        return RedirectResponse(
            url=f"/comandas?erro={str(e)}",
            status_code=303
        )
