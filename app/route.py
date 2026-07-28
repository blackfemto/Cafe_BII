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

from app.schemas import (
    CategoriaCreate,
    ProdutoCreate
)



router = APIRouter()



templates = Jinja2Templates(
    directory="templates"
)



# ==========================
# CATEGORIAS
# ==========================


@router.get(
    "/categorias",
    response_class=HTMLResponse
)
def pagina_categorias(
    request: Request,
    db: Session = Depends(get_db)
):

    categorias = crud.listar_categorias(db)


    return templates.TemplateResponse(
        request=request,
        name="categorias.html",
        context={
            "categorias": categorias
        }
    )



@router.get("/api/categorias")
def listar_categorias(
    db: Session = Depends(get_db)
):

    return crud.listar_categorias(db)



@router.post("/categorias/criar")
def criar_categoria_form(
    nome: str = Form(...),
    db: Session = Depends(get_db)
):

    categoria = CategoriaCreate(
        nome=nome
    )


    crud.criar_categoria(
        db,
        categoria
    )


    return RedirectResponse(
        "/categorias",
        status_code=303
    )



# ==========================
# PRODUTOS
# ==========================


@router.get("/produtos")
def listar_produtos(
    db: Session = Depends(get_db)
):

    return crud.listar_produtos(db)



@router.post("/produtos/criar")
def criar_produto(
    produto: ProdutoCreate,
    db: Session = Depends(get_db)
):

    return crud.criar_produto(
        db,
        produto
    )