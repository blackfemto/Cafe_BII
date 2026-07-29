from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.crud.caixa import get_resumo_caixa
from app.crud.fechamento import criar_fechamento, listar_fechamentos
from app.crud.historico import salvar_comandas_fechadas, listar_historico_por_fechamento
from app.crud.comandas import limpar_comandas_fechadas

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
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    # 1. Criar o fechamento
    fechamento = criar_fechamento(db, int(user_id))

    if fechamento is None:
        return RedirectResponse(
            url="/caixa?erro=Não há vendas para fechar!",
            status_code=303
        )

    # 2. 🔥 SALVAR AS COMANDAS FECHADAS NO HISTÓRICO
    historico = salvar_comandas_fechadas(db, fechamento.id)

    # 3. 🔥 LIMPAR AS COMANDAS FECHADAS DA LISTA PRINCIPAL
    qtd_removidas = limpar_comandas_fechadas(db)

    return RedirectResponse(
        url=f"/caixa?sucesso=Caixa fechado! Total: R$ {fechamento.total_vendas:.2f}. {qtd_removidas} comandas removidas.",
        status_code=303
    )


@router.get("/caixa/fechamentos")
def historico_fechamentos(
    request: Request,
    db: Session = Depends(get_db)
):
    fechamentos = listar_fechamentos(db)

    return templates.TemplateResponse(
        request=request,
        name="fechamentos.html",
        context={
            "request": request,
            "fechamentos": fechamentos
        }
    )
