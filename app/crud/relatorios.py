from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from app import models


def ajustar_fuso(data_utc):
    return data_utc - timedelta(hours=3)


def get_vendas_ultimos_7_dias(db: Session):
    """Retorna vendas dos últimos 7 dias com fuso UTC-3"""
    hoje = datetime.now()
    dados = []
    
    for i in range(7, -1, -1):
        dia = datetime(hoje.year, hoje.month, hoje.day) - timedelta(days=i)
        dia_inicio = dia - timedelta(hours=3)
        dia_fim = dia_inicio + timedelta(days=1)
        
        total = db.query(func.sum(models.Venda.valor)).filter(
            models.Venda.data >= dia_inicio,
            models.Venda.data < dia_fim
        ).scalar() or 0
        
        dados.append({
            "data": dia.strftime("%d/%m"),
            "total": float(total)
        })
    
    return dados


def get_produtos_mais_vendidos(db: Session, limite: int = 5):
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
    total_vendas = db.query(func.sum(models.Venda.valor)).scalar() or 0
    total_comandas = db.query(models.Comanda).count()
    comandas_abertas = db.query(models.Comanda).filter(models.Comanda.status == "ABERTA").count()
    comandas_fechadas = db.query(models.Comanda).filter(models.Comanda.status == "FECHADA").count()
    total_produtos = db.query(models.Produto).filter(models.Produto.ativo == True).count()
    ticket_medio = total_vendas / comandas_fechadas if comandas_fechadas > 0 else 0
    
    return {
        "total_vendas": float(total_vendas),
        "total_comandas": total_comandas,
        "comandas_abertas": comandas_abertas,
        "comandas_fechadas": comandas_fechadas,
        "total_produtos": total_produtos,
        "ticket_medio": float(ticket_medio)
    }
