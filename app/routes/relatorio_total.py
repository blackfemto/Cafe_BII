from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app import models

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/relatorio-total", response_class=HTMLResponse)
def relatorio_total(
    request: Request,
    db: Session = Depends(get_db)
):
    # Buscar TODAS as vendas
    vendas = db.query(models.Venda).all()
    
    if not vendas:
        return templates.TemplateResponse(
            request=request,
            name="relatorio_total.html",
            context={
                "request": request,
                "vendas": [],
                "total": 0,
                "total_dinheiro": 0,
                "total_pix": 0,
                "total_cartao": 0,
                "quantidade": 0,
                "ticket_medio": 0,
                "mensagem": "Nenhuma venda registrada ainda."
            }
        )
    
    # Calcular totais
    total = sum(v.valor for v in vendas)
    total_dinheiro = sum(v.valor for v in vendas if v.forma_pagamento == "DINHEIRO")
    total_pix = sum(v.valor for v in vendas if v.forma_pagamento == "PIX")
    total_cartao = sum(v.valor for v in vendas if v.forma_pagamento in ["CARTAO_CREDITO", "CARTAO_DEBITO"])
    ticket_medio = total / len(vendas) if vendas else 0
    
    return templates.TemplateResponse(
        request=request,
        name="relatorio_total.html",
        context={
            "request": request,
            "vendas": vendas,
            "total": total,
            "total_dinheiro": total_dinheiro,
            "total_pix": total_pix,
            "total_cartao": total_cartao,
            "quantidade": len(vendas),
            "ticket_medio": ticket_medio,
            "data_geracao": datetime.now().strftime("%d/%m/%Y %H:%M")
        }
    )
