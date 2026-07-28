from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session

from app.database import get_db
from app import crud
from app.schemas import CategoriaCreate

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/categorias", response_class=HTMLResponse)
def pagina_categorias(
    request: Request,
    db: Session = Depends(get_db)
):
    categorias = crud.listar_categorias(db)

    return templates.TemplateResponse(
        request=request,
        name="categorias.html",
        context={
            "request": request,
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
    categoria = CategoriaCreate(nome=nome)
    crud.criar_categoria(db, categoria)
    return RedirectResponse(url="/categorias", status_code=303)


# ========== NOVAS ROTAS ==========
@router.post("/categorias/{categoria_id}/editar")
def editar_categoria_route(
    categoria_id: int,
    nome: str = Form(...),
    db: Session = Depends(get_db)
):
    from app.crud.categorias import atualizar_categoria
    atualizar_categoria(db, categoria_id, nome)
    return RedirectResponse(url="/categorias?sucesso=Categoria atualizada!", status_code=303)


@router.post("/categorias/{categoria_id}/deletar")
def deletar_categoria_route(
    categoria_id: int,
    db: Session = Depends(get_db)
):
    from app.crud.categorias import deletar_categoria
    if deletar_categoria(db, categoria_id):
        return RedirectResponse(url="/categorias?sucesso=Categoria deletada!", status_code=303)
    return RedirectResponse(url="/categorias?erro=Não é possível deletar categoria com produtos!", status_code=303)
