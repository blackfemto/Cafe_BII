from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.crud.caixa import get_resumo_caixa
from app.crud.fechamento import criar_fechamento, listar_fechamentos

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
    """Gera um relatório com TODAS as vendas (total acumulado)"""
    
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    # 🔥 BUSCA TODAS AS VENDAS (não apenas do período)
    from app import models
    vendas = db.query(models.Venda).all()
    
    if not vendas:
        return RedirectResponse(
            url="/caixa?erro=Não há vendas para gerar relatório!",
            status_code=303
        )
    
    # Calcular totais de TODAS as vendas
    total = sum(v.valor for v in vendas)
    total_dinheiro = sum(v.valor for v in vendas if v.forma_pagamento == "DINHEIRO")
    total_pix = sum(v.valor for v in vendas if v.forma_pagamento == "PIX")
    total_cartao = sum(v.valor for v in vendas if v.forma_pagamento in ["CARTAO_CREDITO", "CARTAO_DEBITO"])
    
    # Salvar o relatório no histórico
    from app.models import FechamentoCaixa
    fechamento = FechamentoCaixa(
        data_fechamento=datetime.now(),
        total_vendas=total,
        total_dinheiro=total_dinheiro,
        total_pix=total_pix,
        total_cartao=total_cartao,
        quantidade_vendas=len(vendas),
        usuario_id=int(user_id)
    )
    db.add(fechamento)
    db.commit()
    db.refresh(fechamento)

    return RedirectResponse(
        url=f"/caixa/fechamentos?sucesso=Relatório gerado com sucesso! Total: R$ {total:.2f}",
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
