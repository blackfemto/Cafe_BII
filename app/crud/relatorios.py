from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from app import models


def get_vendas_ultimos_7_dias(db: Session):
    """Retorna vendas dos últimos 7 dias"""
    hoje = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    dados = []
    
    for i in range(7, -1, -1):
        dia = hoje - timedelta(days=i)
        amanha = dia + timedelta(days=1)
        
        total = db.query(func.sum(models.Venda.valor)).filter(
            models.Venda.data >= dia,
            models.Venda.data < amanha
        ).scalar() or 0
        
        dados.append({
            "data": dia.strftime("%d/%m"),
            "total": float(total)
        })
    
    return dados


def get_produtos_mais_vendidos(db: Session, limite: int = 5):
    """Retorna os produtos mais vendidos"""
    resultados = db.query(
        models.Produto.nome,
        func.sum(models.ItemComanda.quantidade).label('quantidade_total'),
        func.sum(models.ItemComanda.subtotal).label('faturamento_total')
    ).join(
        models.ItemComanda,
        models.Produto.id == models.ItemComanda.produto_id
    ).join(
        models.Comanda,
        models.ItemComanda.comanda_id == models.Comanda.id
    ).filter(
        models.Comanda.status == "FECHADA"
    ).group_by(
        models.Produto.id
    ).order_by(
        desc('quantidade_total')
    ).limit(limite).all()
    
    return [
        {
            "nome": r[0],
            "quantidade": r[1],
            "faturamento": float(r[2])
        }
        for r in resultados
    ]


def get_faturamento_por_categoria(db: Session):
    """Retorna faturamento agrupado por categoria"""
    resultados = db.query(
        models.Categoria.nome,
        func.sum(models.ItemComanda.subtotal).label('total')
    ).join(
        models.Produto,
        models.Categoria.id == models.Produto.categoria_id
    ).join(
        models.ItemComanda,
        models.Produto.id == models.ItemComanda.produto_id
    ).join(
        models.Comanda,
        models.ItemComanda.comanda_id == models.Comanda.id
    ).filter(
        models.Comanda.status == "FECHADA"
    ).group_by(
        models.Categoria.id
    ).order_by(
        desc('total')
    ).all()
    
    return [
        {
            "categoria": r[0],
            "total": float(r[1])
        }
        for r in resultados
    ]


def get_resumo_geral(db: Session):
    """Retorna resumo geral do sistema"""
    # Total de vendas
    total_vendas = db.query(func.sum(models.Venda.valor)).scalar() or 0
    
    # Total de comandas
    total_comandas = db.query(models.Comanda).count()
    comandas_abertas = db.query(models.Comanda).filter(models.Comanda.status == "ABERTA").count()
    comandas_fechadas = db.query(models.Comanda).filter(models.Comanda.status == "FECHADA").count()
    
    # Total de produtos
    total_produtos = db.query(models.Produto).filter(models.Produto.ativo == True).count()
    
    # Ticket médio geral
    ticket_medio = total_vendas / comandas_fechadas if comandas_fechadas > 0 else 0
    
    return {
        "total_vendas": float(total_vendas),
        "total_comandas": total_comandas,
        "comandas_abertas": comandas_abertas,
        "comandas_fechadas": comandas_fechadas,
        "total_produtos": total_produtos,
        "ticket_medio": float(ticket_medio)
    }
