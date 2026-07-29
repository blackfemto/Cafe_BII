from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.crud.caixa import get_resumo_caixa

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/caixa", response_class=HTMLResponse)
def pagina_caixa(
    request: Request,
    db: Session = Depends(get_db)
):
    dados = get_resumo_caixa(db)
    
    return templates.TemplateResponse(
        request=request,
        name="caixa.html",
        context={
            "request": request,
            "vendas": dados["vendas"],
            "total": dados["total"],
            "total_dinheiro": dados["total_dinheiro"],
            "total_pix": dados["total_pix"],
            "total_cartao": dados["total_cartao"],
            "quantidade": dados["quantidade"],
            "ticket_medio": dados["ticket_medio"]
        }
    )

@router.post("/caixa/fechar")
def fechar_caixa(
    request: Request,
    db: Session = Depends(get_db)
):
    from app.crud.fechamento import criar_fechamento
    from app.crud.caixa import get_resumo_caixa

    # Verifica se é SuperRoot ou Gerente
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    # Criar fechamento
    fechamento = criar_fechamento(db, int(user_id))

    return RedirectResponse(
        url="/caixa?sucesso=Caixa fechado com sucesso! Total: R$ {:.2f}".format(fechamento.total_vendas),
        status_code=303
    )


@router.get("/caixa/fechamentos")
def historico_fechamentos(
    request: Request,
    db: Session = Depends(get_db)
):
    from app.crud.fechamento import listar_fechamentos

    fechamentos = listar_fechamentos(db)

    return templates.TemplateResponse(
        request=request,
        name="fechamentos.html",
        context={
            "request": request,
            "fechamentos": fechamentos
        }
    )

@router.post("/caixa/fechar")
def fechar_caixa(
    request: Request,
    db: Session = Depends(get_db)
):
    from app.crud.fechamento import criar_fechamento

    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    fechamento = criar_fechamento(db, int(user_id))

    return RedirectResponse(
        url=f"/caixa?sucesso=Caixa fechado com sucesso! Total: R$ {fechamento.total_vendas:.2f}",
        status_code=303
    )
