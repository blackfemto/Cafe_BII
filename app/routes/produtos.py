from fastapi import (
    APIRouter,
    Depends,
    Request,
    Form
)

from fastapi.responses import (
    HTMLResponse,
    RedirectResponse
)

from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session

from app.database import get_db
from app import crud
from app.schemas import ProdutoCreate

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get(
    "/produtos",
    response_class=HTMLResponse
)
def pagina_produtos(
    request: Request,
    db: Session = Depends(get_db)
):

    produtos = crud.listar_produtos(db)

    categorias = crud.listar_categorias(db)

    return templates.TemplateResponse(
        request=request,
        name="produtos.html",
        context={
            "request": request,
            "produtos": produtos,
            "categorias": categorias
        }
    )


@router.post("/produtos/criar")
def criar_produto_form(

    nome: str = Form(...),

    descricao: str = Form(""),

    preco: float = Form(...),

    categoria_id: int = Form(...),

    db: Session = Depends(get_db)

):

    produto = ProdutoCreate(

        nome=nome,

        descricao=descricao,

        preco=preco,

        categoria_id=categoria_id

    )

    crud.criar_produto(
        db,
        produto
    )

    return RedirectResponse(
        url="/produtos",
        status_code=303
    )
@router.post("/produtos/{produto_id}/editar")
def editar_produto(

    produto_id: int,

    nome: str = Form(...),

    descricao: str = Form(""),

    preco: float = Form(...),

    categoria_id: int = Form(...),

    db: Session = Depends(get_db)

):

    produto = ProdutoCreate(

        nome=nome,

        descricao=descricao,

        preco=preco,

        categoria_id=categoria_id

    )

    crud.atualizar_produto(
        db,
        produto_id,
        produto
    )

    return RedirectResponse(
        "/produtos",
        status_code=303
    )
@router.post("/produtos/{produto_id}/editar")
def editar_produto_route(
    produto_id: int,
    nome: str = Form(...),
    descricao: str = Form(""),
    preco: float = Form(...),
    categoria_id: int = Form(...),
    db: Session = Depends(get_db)
):
    from app.schemas import ProdutoCreate
    produto = ProdutoCreate(
        nome=nome,
        descricao=descricao,
        preco=preco,
        categoria_id=categoria_id
    )
    crud.atualizar_produto(db, produto_id, produto)
    return RedirectResponse("/produtos", status_code=303)


@router.post("/produtos/{produto_id}/deletar")
def deletar_produto(
    produto_id: int,
    db: Session = Depends(get_db)
):
    from app.crud.produtos import buscar_produto
    produto = buscar_produto(db, produto_id)
    if produto:
        produto.ativo = False
        db.commit()
    return RedirectResponse("/produtos", status_code=303)

@router.post("/produtos/{produto_id}/deletar")
def deletar_produto_route(
    produto_id: int,
    db: Session = Depends(get_db)
):
    from app.crud.produtos import deletar_produto
    if deletar_produto(db, produto_id):
        return RedirectResponse("/produtos?success=Produto removido com sucesso!", status_code=303)
    return RedirectResponse("/produtos?error=Produto não encontrado!", status_code=303)
