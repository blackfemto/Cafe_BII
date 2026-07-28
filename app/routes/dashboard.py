from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.crud.caixa import get_resumo_caixa

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    db: Session = Depends(get_db)
):
    dados = get_resumo_caixa(db)
    
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
            "now": datetime.now,
            "faturamento": dados["total"],
            "total_vendas": dados["quantidade"],
            "ticket_medio": dados["ticket_medio"],
            "vendas_hoje": dados["vendas"]
        }
    )
